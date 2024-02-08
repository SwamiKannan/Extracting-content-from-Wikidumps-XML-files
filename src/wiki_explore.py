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
from image_scraper import extract_categories, extract_images

from cleaner import clean_text

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


# def process_text(text):
#     result_img = image_text(text)
#     final_text, result_cat = cat_text(text)
#     return final_text, result_cat, result_img
#
#
# def image_text(text):
#     # rep = dict((re.escape(k), v) for k, v in replacements.items())
#     # pattern = re.compile("|".join(rep.keys()))
#     result_img = re.findall(r"\[File:(.*?)\]", text)
#     print('Image results')
#     print(result_img)
#     return result_img
#
#
# def cat_text(text):
#     rep = dict((re.escape(k), v) for k, v in replacements.items())
#     pattern = re.compile("|".join(rep.keys()))
#     result_cat = re.findall(r"\[Category:(.*?)\]", text)
#     text = pattern.sub(lambda m: rep[re.escape(m.group(0))], text)
#     text = text.split('See also')[0]
#     print('From category')
#     print(result_cat)
#
#     return text, result_cat


def process_article(aq, fq, shutdown):
    while not (shutdown and aq.empty() and fq.empty()):
        page_title, doc = aq.get()
        image_dict = extract_images(doc)
        cat_list = extract_categories(doc)
        text = clean_text(text)
        if not cat_list:
            cat_list = []
        fq.put({"page": page_title, "sentences": text, 'categories': cat_list, "images": image_dict})


def write_out(fq, shutdown):
    while not (shutdown and fq.empty()):
        line = fq.get()
        try:
            line = json.dumps(line, ensure_ascii=False)
            out_file.write(line + '\n')
        except:
            print('File not written')


def display(aq, fq, reader, shutdown):
    while not (shutdown and aq.empty() and fq.empty()):
        print("Queue sizes: aq={0} fq={1}. Read: {2}".format(
            aq.qsize(),
            fq.qsize(),
            reader.status_count))
        time.sleep(1)


# def kill_processes():
#     status._stop()
#     for process in processes:
#         processes[process].kill()
#     for write_thread in write_threads:
#         write_threads[write_thread]._stop()


if __name__ == "__main__":
    shutdown = False

    args_parse = argparse.ArgumentParser()

    args_parse.add_argument("file", help='File name (including path where it is stored')
    args_parse.add_argument("--output", help='File name (including path where it is stored')
    args = args_parse.parse_args()

    source = args.file
    target = args.output if args.output else 'output.json'

    manager = multiprocessing.Manager()
    fq = manager.Queue(maxsize=2000)
    aq = manager.Queue(maxsize=2000)

    if source[-4:] == ".bz2":
        source = bz2.BZ2File(source)
    elif source[-4:] == '.xml':
        source = open(source, 'rb')
    else:
        print('File should be either .bz2 or .xml format. Exiting....')
        sys.exit()

    out_file = open(target, "w+", encoding='utf-8')

    reader = WikiReader(lambda ns: ns == 0, aq.put)

    status = Thread(target=display, args=(aq, fq, reader, shutdown))
    status.start()

    processes = {}
    for i in range(20):
        processes[i] = Process(target=process_article,
                               args=(aq, fq, shutdown))
        processes[i].start()

    write_threads = {}
    for i in range(10):
        write_threads[i] = Thread(target=write_out, args=(fq, shutdown))
        write_threads[i].start()
    st_time = time.time()
    try:
        xml.sax.parse(source, reader)
    except Exception as e:
        print('Error', e)
    end_time = time.time()
    print('Tada ! Processing complete. Close the window and continue...')
    print(f'Time for processing: {end_time - st_time}')
    time.sleep(5)
    shutdown = True if aq.empty() and fq.empty() else False
    # if shutdown:
    #     kill_processes()
