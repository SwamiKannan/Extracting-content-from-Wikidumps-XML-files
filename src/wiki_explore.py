import argparse
import bz2
import json
import logging
import multiprocessing
import os
import re
import sys
import time
import xml.sax
from multiprocessing import Process
from threading import Thread

from cleaner import Cleaner

logger = logging.getLogger(__name__)
re_mode = 0
replacements = {'[[': '', ']]': '', '==': ''}


# cleaner.py from https://github.com/CyberZHG Git repo: https://github.com/CyberZHG/wiki-dump-reader/blob/master/wiki_dump_reader/cleaner.py


class WikiReader(xml.sax.ContentHandler):
    def __init__(self, ns_filter, callback):
        super().__init__()

        self.filter = ns_filter

        self.read_stack = []
        self.read_text = ''
        self.read_title = ''
        self.read_namespace = ''

        self.status_count = 0
        self.callback = callback

    def startElement(self, tag_name, attributes):
        if tag_name == "ns":
            self.read_namespace = None

        elif tag_name == "page":
            self.read_text = None
            self.read_title = None

        elif tag_name == "title":
            self.read_title = ""

        elif tag_name == "text":
            self.read_text = ""


        else:
            return

        self.read_stack.append(tag_name)

    def endElement(self, tag_name):
        if len(self.read_stack) > 0:
            if tag_name == self.read_stack[-1]:
                del self.read_stack[-1]

        if self.filter(self.read_namespace):
            if tag_name == "page" and self.read_text is not None:
                self.status_count += 1
                self.callback((self.read_title, self.read_text))

    def characters(self, content):
        if len(self.read_stack) == 0:
            return None
        try:
            if self.read_stack[-1] == "text":
                self.read_text += content

            if self.read_stack[-1] == "title":
                self.read_title += content

            if self.read_stack[-1] == "ns":
                self.read_namespace = int(content)
        except Exception as e:
            print(f'Could not add to stack {self.read_stack[-1]}\t, {content}\t, {e}')


def process_text(text):
    rep = dict((re.escape(k), v) for k, v in replacements.items())
    pattern = re.compile("|".join(rep.keys()))
    result_cat = re.findall(r"\[Category:(.*?)\]", text)
    text = pattern.sub(lambda m: rep[re.escape(m.group(0))], text)
    text = text.split('See also')[0]

    return text, result_cat


def process_article(aq, fq, shutdown, cleaner):
    print('Initiated processing')
    print('Shutdown', shutdown)
    print('Process article status: ', not (shutdown and aq.empty()))
    while not (shutdown and aq.empty() and fq.empty()):
        page_title, doc = aq.get()
        if not doc:
            print('No text found for ', page_title)
        text, categories = process_text(doc)
        text = cleaner.clean_text(text)
        # text = doc
        print('Text post cleaning:', text)
        text == '' if not text else text
        print(f'Text for {page_title} has been overcleaned')
        text, categories = process_text(text)
        if not categories:
            categories = ['No categories']
        try:
            fq.put(json.dumps({"page": page_title, "sentences": text, 'categories': categories}, ensure_ascii=False))
        except Exception as e:
            print(f'Exception while processing article {page_title}; Exception: {e}')


def write_out(fq, shutdown):
    print('Writing out')
    while not (shutdown and fq.empty()):
        line = fq.get()
        try:
            out_file.write(line + '\n')
        except Exception as e:
            print(f'File didnt write Exception {e}')


def display(aq, fq, reader, shutdown):
    print('Shutdown status inside loop', shutdown)
    while not (shutdown and aq.empty() and fq.empty()):
        print("Queue sizes: aq={0} fq={1}. Read: {2}".format(
            aq.qsize(),
            fq.qsize(),
            reader.status_count))
        time.sleep(1)


if __name__ == "__main__":
    print(os.getcwd())
    shutdown = False

    args_parse = argparse.ArgumentParser()

    args_parse.add_argument("file", help='File name (including path where it is stored')
    args_parse.add_argument("--output", help='File name (including path where it is stored')
    args = args_parse.parse_args()

    source = args.file
    target = args.output if args.output else os.getcwd()

    manager = multiprocessing.Manager()
    fq = manager.Queue(maxsize=2000)
    aq = manager.Queue(maxsize=2000)

    c = Cleaner()

    if source[-4:] == ".bz2":
        source = bz2.BZ2File(source)
    elif source[-4:] == '.xml':
        wiki = open(source, 'rb')
    else:
        print('File should be either .bz2 or .xml format. Exiting....')
        sys.exit()

    out_file = open(target, "w+", encoding='utf-8')

    reader = WikiReader(lambda ns: ns == 0, aq.put)

    status = Thread(target=display, args=(aq, fq, reader, shutdown))
    status.start()

    processes = {}
    for i in range(15):
        processes[i] = Process(target=process_article,
                               args=(aq, fq, shutdown, c))
        processes[i].start()

    for i in range(15):
        print(f'Process {i}:\t{processes[i].is_alive()}')

    write_thread = Thread(target=write_out, args=(fq, shutdown))
    write_thread.start()
    try:
        xml.sax.parse(wiki, reader)
    except Exception as e:
        print('Error', e)
    print('Tada !')
    time.sleep(5)
    shutdown = True if aq.empty() and fq.empty() else False
    print('Shutdown status', shutdown)
