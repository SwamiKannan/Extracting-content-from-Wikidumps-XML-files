import requests
import urllib.request
# from PIL import Image
# from io import StringIO
from bs4 import BeautifulSoup
from texts import sample_text
import os
import itertools

# check = "==Firearms license== [[File:Forside våpenkort.jpg|thumb|right|A Norwegian firearms license for a [[.44 " \
# "Magnum]] [[revolver]], with name and address of the owner, as well as firearm type, brand, caliber and " \ "serial
# number.]]" check_text = "==Firearms license==[[File:Forside våpenkort.jpg|thumb|right|A Norwegian firearms license
# for a [[.44 Magnum]] [[revolver]], " \ "with name and address of the owner, as well as firearm type, brand,
# caliber and serial number.]][[" \ "File:Kleiner Waffenschein Außen.JPG|thumb|right|A German firearms license.]] A
# '''firearms license'''"
#
# for i in range(1, 10):
#     print(i)
#
# files = []
# end1 = 201
#
# print(type(sample_text))
# print("[[File:" in sample_text)

parsing_errors = []


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


def process_img_tag(text):
    global parsing_errors
    text = text.replace('[[', '').replace(']]', '')
    text_space = text.split('|')
    name = text_space[0]
    link = 'https://commons.wikimedia.org/wiki/File:' + '_'.join(name.split()) + "#file"
    if len(text_space) > 3:
        text_dict = {name: {'image_url': link,
                            'type': text_space[1],
                            'align': text_space[2],
                            'Caption': text_space[3]
                            }
                     }
    elif len(text_space) == 3:
        text_dict = {name: {'image_url': link,
                            'type': text_space[1],
                            'align': text_space[3] if len(text_space) > 3 else None,
                            'Caption': text_space[2]}
                     }
    else:
        parsing_errors.append(text_space)
        text_dict = None
    return text_dict


def parse_image_data(ref_text):
    img_files = parse_data("[[File:", ref_text)
    return img_files


def download_images(files):
    if 'images' not in os.listdir():
        os.mkdir('images')
    img_path = os.path.join('images')
    image_links = [(key, a[key]['image_url']) for a in files for key in a.keys()]
    for (name, url) in image_links:
        response = requests.get(url)
        if response.status_code == 200:
            parser = BeautifulSoup(response.text, 'html.parser')
            link = parser.find('div', class_="fullImageLink").find('a')
            url_img = link['href']
            urllib.request.urlretrieve(url_img, os.path.join(img_path, name))
            print(f' {name} file written')
        else:
            print(url)


def extract_images(ref_text):
    files = parse_image_data(ref_text)
    img_files = [process_img_tag(file) for file in files]
    return img_files


def parse_cat_data(ref_text):
    return parse_data("[[Category:", ref_text)


def process_cat_data(cat_text):
    cat_text = cat_text.replace('| ', '').replace('ory:', '')
    return cat_text.split('|')


def extract_categories(ref_text):
    files = parse_cat_data(ref_text)
    return list(itertools.chain.from_iterable([process_cat_data(t) for t in files]))


if __name__ == "__main__":
    test_link = "https://en.wikipedia.org/wiki/Overview_of_gun_laws_by_nation"
    test_files = extract_categories(sample_text)
    test_img_files = extract_images(sample_text)
    print('Parsing errors', parsing_errors)
    print('Test cat files', test_files)
    print('Test Image files', test_img_files)
