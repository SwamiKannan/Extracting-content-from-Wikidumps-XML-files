import requests
from shutil import copyfileobj
from bs4 import BeautifulSoup
import os
import itertools
import time
import shutil

HEADER = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"}
URLLIB_HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 '
                  'Safari/537.36 SE 2.X MetaSr 1.0'}

ref_list = 'abcdefghijklmnopqrstuvwxyz'
nums_list = '0123456789_'
final_ref = ref_list + ref_list.upper() + nums_list


def download_img_from_url(url, out_path):
    try:
        response = requests.get(url, stream=True, headers=URLLIB_HEADER)
    except Exception as e:
        print(f'Error in retrieval:\t{response.status_code}\tException: {e}\t URL: {url}')
    try:
        with open(out_path, 'wb') as out_file:
            copyfileobj(response.raw, out_file)
    except Exception as e:
        print('Unable to save image file. Exception:', e)


def parse_data(str_target, ref_text):
    files = []
    while str_target in ref_text:
        count = 1
        st_index = ref_text.find(str_target) + 7
        for r in range(st_index, len(ref_text) + 1):
            if ref_text[r:r + 2] == '[[':
                count += 1
            if ref_text[r:r + 2] == ']]':
                count -= 1
                if count == 0:
                    text = ref_text[st_index:r]
                    files.append(text)
                    ref_text = ref_text[r + 2:]
                    break
    return files


def process_filename(filename):
    filextn = (filename.rfind('.'))
    file_extn = filename[filextn:]
    name = filename[:filextn]
    name = "a_1" if name == "" else name
    name = name.replace(" ", "_").replace('-', "_")
    filename1 = ''.join(
        [c for c in name if c in final_ref])
    filename1 = 'a'+filename1 if filename1.startswith('_') else filename1
    name = filename1 + file_extn
    return name


def process_img_tag(text):
    parsing_errors = None
    text = text.replace('[[', '').replace(']]', '')
    text_space = text.split('|')
    name = text_space[0]
    img_file_name = '_'.join(name.split())
    filename = process_filename(name)
    link1 = 'https://commons.wikimedia.org/wiki/File:' + img_file_name + "#file"
    link2 = 'https://en.wikipedia.org/wiki/File:' + img_file_name
    link1 = link1.replace('&', '%26')
    link2 = link2.replace('&', '%26')
    if len(text_space) > 3:
        text_dict = {filename: {'image_url': [link1, link2],
                                'image_file_name': img_file_name,
                                'type': text_space[1],
                                'align': text_space[2],
                                'Caption': text_space[3],
                                'original_name': name
                                }
                     }
    elif len(text_space) == 3:
        text_dict = {filename: {'image_url': [link1, link2],
                                'image_file_name': img_file_name,
                                'type': text_space[1],
                                'align': text_space[3] if len(text_space) > 3 else None,
                                'Caption': text_space[2],
                                'original_name': name
                                }
                     }
    elif len(text_space) <= 2:
        text_dict = {filename: {'image_url': [link1, link2],
                                'image_file_name': img_file_name,
                                'type': None,
                                'align': text_space[1] if len(text_space) == 2 else None,
                                'Caption': None,
                                'original_name': name}
                     }
    else:
        parsing_errors = text_space
        print('Errored out text_space', text_space)
        text_dict = None
    return text_dict, parsing_errors


def parse_image_data(ref_text):
    img_files = parse_data("[[File:", ref_text)
    return img_files


def parse_and_download_image_from_link(response, path, name):
    parser = BeautifulSoup(response.text, 'html.parser')
    link = parser.find('div', class_="fullImageLink").find('a')
    url_img = link['href']
    if not url_img.startswith("https:"):
        url_img = 'https:' + url_img
    out_path = os.path.join(path, name)
    download_img_from_url(url_img, out_path)
    return url_img


def download_images(image_dict, path, title):
    if 'images' not in os.listdir(os.path.join(path)):
        os.mkdir(os.path.join('images'))
    img_path = os.path.join(path, 'images')
    image_links = [(k, v['image_url']) for k, v in image_dict.items()]
    for (name, urls) in image_links:
        response = requests.get(urls[0], headers=HEADER)
        if response.status_code == 200:
            img_url = parse_and_download_image_from_link(response, img_path, name)
            # print(f' {name} file written')
        elif response.status_code == 404:
            response = requests.get(urls[1], headers=HEADER)
            if response.status_code == 200:
                img_url = parse_and_download_image_from_link(response, img_path, name)
            elif response.status_code == 404:
                print('Download images (): 404 File not found: Inner url \t', img_url, '\tLink:\t', urls[1],
                      'image name:\t', name, '\tpage name:\t', title)
        else:
            continue
            # print('Image from Url not downloaded:\t', 'Response code:', response.status_code, '\timage:', url,'\tName:',name)
    return response.status_code


def extract_images(ref_text):
    parsing_error = None
    files = parse_image_data(ref_text)
    if files:
        img_files = {}
        for file in files:
            img_dict, parsing_error = process_img_tag(file)
            if img_dict:
                img_files.update(img_dict)
    else:
        img_files = None
    return img_files, parsing_error


def parse_cat_data(ref_text):
    return parse_data("[[Category:", ref_text)


def process_cat_data(cat_text):
    cat_text = cat_text.replace('| ', '').replace('ory:', '')
    return cat_text.split('|')


def extract_categories(ref_text):
    files = parse_cat_data(ref_text)
    return list(itertools.chain.from_iterable([process_cat_data(t) for t in files]))


if __name__ == "__main__":
    from texts import sample_text

    test_link = "https://en.wikipedia.org/wiki/Overview_of_gun_laws_by_nation"
    test_files = extract_categories(sample_text)
    test_img_files, parsing_errors = extract_images(sample_text)
    print('Parsing errors', parsing_errors)
    print('Test cat files', test_files)
    # print('Full image dict')
    # print(test_img_files)
    print('Test Image files')
    for k, v in test_img_files.items():
        print(k, '\n', v)
    download_images(test_img_files, os.getcwd())
