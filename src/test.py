import requests
import urllib.request
from PIL import Image
from io import StringIO
from bs4 import BeautifulSoup
from texts import sample_text

check = "==Firearms license== [[File:Forside våpenkort.jpg|thumb|right|A Norwegian firearms license for a [[.44 " \
        "Magnum]] [[revolver]], with name and address of the owner, as well as firearm type, brand, caliber and " \
        "serial number.]]"
check_text = "==Firearms license==[[File:Forside våpenkort.jpg|thumb|right|A Norwegian firearms license for a [[.44 Magnum]] [[revolver]], " \
             "with name and address of the owner, as well as firearm type, brand, caliber and serial number.]][[" \
             "File:Kleiner Waffenschein Außen.JPG|thumb|right|A German firearms license.]] A '''firearms license'''"

for i in range(1,10):
    print(i)

files = []
end1 = 201

print(type(sample_text))
print("[[File:" in sample_text)


def process_img_tag(text):
    text = text.replace('[[', '').replace(']]', '')
    text_space = text.split('|')
    name = text_space[0]
    link = 'https://commons.wikimedia.org/wiki/File:' + '_'.join(name.split()) + "#file"
    print(link)
    print('Text space', text_space)
    if len(text_space) > 3:
        text_dict = {'filename': name,
                     'image_url': link,
                     'type': text_space[1],
                     'align': text_space[2],
                     'Caption': text_space[3]}
    else:
        text_dict = {'filename': name,
                     'image_url': link,
                     'type': text_space[1],
                     'align': text_space[3] if len(text_space) > 3 else None,
                     'Caption': text_space[2]}
    return text_dict


def parse_image_data(check2):
    while "[[File:" in check2:
        count = 1
        st_index = check2.find('[[File:') + 7
        for r in range(st_index,len(check2)+1):
            st_index = check2.find('[[File:') + 7
            if check2[r:r + 2] == '[[':
                print(check2[r:r + 10])
                count += 1
            if check2[r:r + 2] == ']]':
                print(check2[r:r - 10])
                count -= 1
                if count == 0:
                    text = check2[st_index:r]
                    files.append(process_img_tag(text))
                    check2 = check2[r + 2:]
                    print('Broken !! ')
                    break
            print('Count',count)
    return files


test_link = "https://en.wikipedia.org/wiki/Overview_of_gun_laws_by_nation"
# print(list(map(parse_image_data, check_text)))
files = parse_image_data(sample_text)
for file in files:
    for it in file.items():
        print(it)
    print('\n')

image_links = [(a['filename'], a['image_url']) for a in files]
for (name, url) in image_links:
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        parser = BeautifulSoup(response.text, 'html.parser')
        link = parser.find('div', class_="fullImageLink").find('a')
        url_img = link['href']
        print('Final URL', url)
        image_response = urllib.request.urlretrieve(url_img, name)
        print(f' {name} file written')
    else:
        print(url)
