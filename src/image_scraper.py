import requests
import urllib.request
# from PIL import Image
# from io import StringIO
from bs4 import BeautifulSoup
from texts import sample_text
import os

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
files = []


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


def parse_image_data(check2):
    global files
    while "[[File:" in check2:
        count = 1
        st_index = check2.find('[[File:') + 7
        for r in range(st_index, len(check2) + 1):
            st_index = check2.find('[[File:') + 7
            if check2[r:r + 2] == '[[':
                count += 1
            if check2[r:r + 2] == ']]':
                count -= 1
                if count == 0:
                    text = check2[st_index:r]
                    if text:
                        img_dict = process_img_tag(text)
                        files.append(img_dict)
                    check2 = check2[r + 2:]
                    break
    return files


def download_images(files):
    print(os.getcwd())
    if not 'images' in os.listdir():
        os.mkdir('images')
    img_path = os.path.join('images')
    image_links = [(key, a[key]['image_url']) for a in files for key in a.keys()]
    for (name, url) in image_links:
        response = requests.get(url)
        if response.status_code == 200:
            parser = BeautifulSoup(response.text, 'html.parser')
            link = parser.find('div', class_="fullImageLink").find('a')
            url_img = link['href']
            urllib.request.urlretrieve(url_img, os.path.join(img_path,name))
            print(f' {name} file written')
        else:
            print(url)


test_link = "https://en.wikipedia.org/wiki/Overview_of_gun_laws_by_nation"
# print(list(map(parse_image_data, check_text)))
files = parse_image_data(sample_text)
print('Parsing errors', parsing_errors)
for file in files:
    for it in file.keys():
        print(it)
        print(file[it].items())
    print('\n')
download_images(files)
if parsing_errors:
    with open('parser_errors.txt', 'a+', encoding='utf-8') as f:
        f.write('\n'.join(parsing_errors))
