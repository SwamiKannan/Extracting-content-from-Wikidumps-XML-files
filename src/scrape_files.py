import argparse
import bz2
import multiprocessing
import os
import sys
import time
import xml.sax
import shutil
from multiprocessing import Process
from threading import Thread

from scraper.wiki_explore import download_images_queue, WikiReader, display, process_article, write_out, parsing_errors, event
from scraper.resize import resize_and_update

if __name__ == "__main__":
    shutdown = False

    # Get all parsed arguments
    args_parse = argparse.ArgumentParser()

    args_parse.add_argument("file", help='File name (including path where it is stored')
    args_parse.add_argument("--output", help='File name (including path where it is stored')
    args_parse.add_argument("--image_download", help='Whether to download the images associated with the xml file')
    args_parse.add_argument("--resize_and_rebuild", help='Some objects downloaded can be ~500 MB in size. This will '
                                                         'filter only those objects less than 1 MB (images are '
                                                         'compressed) and rebuild the output file references only for '
                                                         'those files. \
                                                         NOTE: This cannot be True if image_download is False')
    args = args_parse.parse_args()

    source = args.file
    final_json = args.output if args.output else 'final_output.pkl'
    images_download = args.image_download if args.image_download else False
    resize = args.resize_and_rebuild if images_download and args.resize_and_rebuild else False

    if resize and not images_download:
        print(
            'Error ! resize_and_rebuild is True but images_download is False. To resize images, we first need to '
            'download the images. Please set images_download to True or set resize_and_rebuild to False')
        sys.exit()

    # Set all paths

    # Setting primary folder for outputs
    DATA_PATH = 'data'
    TARGET_FILE = 'interim_output.pkl'

    if DATA_PATH not in os.listdir():
        os.mkdir(os.path.join(DATA_PATH))
    data_path = os.path.join(DATA_PATH)
    # Setting up file path for json file generated
    target = os.path.join(DATA_PATH, TARGET_FILE)

    # Setting path to document errors in image downloaded. Usually 404 errors.
    error_file = 'errors.pkl'
    error = os.path.join(data_path, error_file)

    # All image related folders
    if images_download:
        INIT_IMAGE_FOLDER = 'F://images_temp' #init_images in final code
        # Create path for first folder for images downloaded (pre-resize)
        image_path = INIT_IMAGE_FOLDER #To be deleted in final code
        '''
        if INIT_IMAGE_FOLDER not in os.listdir(os.path.join(DATA_PATH)):
            os.makedirs(os.path.join(DATA_PATH, INIT_IMAGE_FOLDER))
        image_path = os.path.join(DATA_PATH, INIT_IMAGE_FOLDER) #Need to adf
        '''
    else:
        image_path = None

    # Create folder for post-resized images
    IMAGES_FOLDER = 'images'
    FINAL_JSON_FILE = final_json
    if IMAGES_FOLDER not in os.listdir(os.path.join(DATA_PATH)):
        os.makedirs(os.path.join(DATA_PATH, IMAGES_FOLDER))
    final_image_path = os.path.join(DATA_PATH, IMAGES_FOLDER)
    final_json_path = os.path.join(DATA_PATH, FINAL_JSON_FILE)

    # Setting up necessary queues
    manager = multiprocessing.Manager()
    fq = manager.Queue(maxsize=2000)
    aq = manager.Queue(maxsize=2000)
    eq = manager.Queue(maxsize=2000)
    if images_download:
        iq = manager.Queue(maxsize=10000)
        image_downloader = {}
        for i in range(20):
            image_downloader[i] = Thread(target=download_images_queue, args=(iq, eq, image_path, shutdown))
            image_downloader[i].start()

    else:
        iq = None

    # Open the requisite files
    if source[-4:] == ".bz2":
        source = bz2.BZ2File(source)
    elif source[-4:] == '.xml':
        source = open(source, 'r', encoding='utf-8')
    else:
        print('File should be either .bz2 or .xml format. Exiting....')
        sys.exit()

    out_file = open(target, "wb+")
    error_out = open(error, 'ab+')

    # Set up Wiki parser
    reader = WikiReader(lambda ns: ns == 0, aq.put)

    # Setting up threads and processes for multiprocessing
    status = Thread(target=display, args=(aq, fq, iq, eq, reader, shutdown))
    status.start()

    processes = {}
    for i in range(5):
        processes[i] = Process(target=process_article,
                               args=(aq, fq, iq, eq, image_path, images_download, shutdown))
        processes[i].start()

    write_threads = {}
    for i in range(1):
        write_threads[i] = Thread(target=write_out, args=(fq, shutdown, out_file))
        write_threads[i].start()

    write_errors = {}
    for i in range(1):
        write_errors[i] = Thread(target=parsing_errors, args=(eq, shutdown, error_out))
        write_errors[i].start()

    st_time = time.time()

    # Initiate parsing
    try:
        xml.sax.parse(source, reader)
    except Exception as e:
        print('Error', e)

    time.sleep(10)
    while not shutdown:
        if images_download:
            shutdown = True if (aq.empty() and fq.empty() and iq.empty() and eq.empty()) else False
        else:
            shutdown = True if (aq.empty() and fq.empty() and eq.empty()) else False
        time.sleep(60)
    end_time = time.time()
    print('Initiating shutdown of all scraping processes')
    # pickle.dump(content, out_file)
    if shutdown:
        event.set()
    try:
        out_file.close()
        print('Output file closed')
    except Exception as e:
        print('Output file could not be closed due to exception: ', e)
    error_out.close()
    for i in processes:
        processes[i].terminate()
    status.join()
    print('Download complete. ...')
    print(f'Time for download: {end_time - st_time} seconds')

    if resize:
        resize_and_update(image_path, final_image_path, target, final_json_path)
        time.sleep(10)
        shutil.rmtree(image_path)
        os.remove(target)
    else:
        os.rename(image_path, final_image_path)
        shutil.move(target, final_json_path)
    print('All activities complete.')
    sys.exit()
    # if shutdown:
    #     kill_processes()
