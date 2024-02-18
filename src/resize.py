from PIL import Image
import PIL
import os
import shutil
import pickle
import json


# from svglib.svglib import svg2rlg
# from reportlab.graphics import renderPM


# SVG_TO_PNG_PATH = 'svgtopng'


# def svg_png(svg_file):  # NOT WORKING
#     drawing = svg2rlg(svg_file)
#     img = renderPM.drawToPIL(drawing)
#     return img
def loadall(filename):
    with open(filename, "rb") as f:
        while True:
            try:
                yield pickle.load(f)
            except EOFError:
                break


# def webp_png(webp_file):
#     im = Image.open(webp_file).convert('RGB')
#     return im
DATA_PATH = 'data'
SOURCE_FOLDER = 'init_images'
print(os.getcwd())
data_path = os.path.join(DATA_PATH)
source_path = os.path.join(DATA_PATH, SOURCE_FOLDER)
print(source_path)

TARGET_FOLDER = 'images'
if TARGET_FOLDER not in os.listdir(data_path):
    os.mkdir(os.path.join(data_path, TARGET_FOLDER))
target = os.path.join(data_path, TARGET_FOLDER)

TARGET_SIZE = (640, 480)
PIL.Image.MAX_IMAGE_PIXELS = int(1082882052 * 1.5)
MAX_FILE_SIZE = 512

extensions = {'JPEG', 'JPG', 'PNG', 'xcf', 'TIF',
              'tif', 'tiff', 'gif', 'jpeg', 'stl', 'jpg', 'png'}



errors = []
error_extns = set()
high_size_extns = set()

for filename in os.listdir(source_path):
    kb_size = os.stat(os.path.join(source_path, filename)).st_size / 1024
    if kb_size > 1024:
        high_size_extns.add(filename.split(".")[-1])
print(f"File extensions of type {', '.join(high_size_extns)} have a file size larger than {MAX_FILE_SIZE}")

for filename in os.listdir(source_path):
    if os.stat(os.path.join(source_path, filename)).st_size / 1024 > MAX_FILE_SIZE:
        if filename.split('.')[-1] == 'tif':
            print('Tiff still exists: ', filename)
            # Converts .tif to .tiff that allows PIL.Image to open and process the file
        if filename.split('.')[-1] != "pdf" and filename.split('.')[-1] != "svg":
            try:
                img = Image.open(os.path.join(source_path, filename))
                width, height = img.size
                try:
                    if width > TARGET_SIZE[0]:
                        mult = height / width
                        img = img.resize(
                            (TARGET_SIZE[0], int(TARGET_SIZE[0] * mult)))
                    if height > TARGET_SIZE[1]:
                        mult = width / height
                        img = img.resize(
                            (int(TARGET_SIZE[1] * mult), TARGET_SIZE[1]))
                    try:
                        img.save(os.path.join(target, filename),
                                 optimize=True, quality=50, dpi=(72, 72))
                    except Exception as e1:
                        print('Could not save due to Exception e1: ', e1)
                        try:
                            img.save(os.path.join(target, filename),
                                     optimize=True, dpi=(72, 72))
                        except Exception as e2:
                            print('Could not save due to Exception e2: ', e2)
                            try:
                                img.save(os.path.join(target, filename),
                                         dpi=(72, 72))
                            except Exception as e3:
                                print('Could not save due to Exception e3: ', e3)
                                try:
                                    img.save(os.path.join(
                                        target, filename))
                                except Exception as e4:
                                    print(
                                        'All file savers failed due to Exception e4 ', e4)
                except Exception as e5:
                    print(
                        f'File {filename} loaded but could not be resized due to Exception e5: {e5}')

            except Exception as e6:
                print('Cant load', filename, 'because of Exception e6', e6)
            # errors.append(filename)
            # error_extns.add(filename.split('.')[-1])
            # # shutil.copy(os.path.join(SOURCE_PATH, filename),
            # #             os.path.join(TARGET_PATH, filename))

    else:
        shutil.copy(os.path.join(source_path, filename), target)
# # print('High file size extns:', high_size_extns)

# dir_list = os.listdir('image\\resize')
# with open('output.json', 'r', encoding='utf-8') as f:
#     init_output = h
