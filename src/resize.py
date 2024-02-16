from PIL import Image
import PIL
import os
import shutil
# from svglib.svglib import svg2rlg
# from reportlab.graphics import renderPM


#SVG_TO_PNG_PATH = 'svgtopng'


# def svg_png(svg_file):  # NOT WORKING
#     drawing = svg2rlg(svg_file)
#     img = renderPM.drawToPIL(drawing)
#     return img


# def webp_png(webp_file):
#     im = Image.open(webp_file).convert('RGB')
#     return im

PIL.Image.MAX_IMAGE_PIXELS = int(273259100*3.5)
print(PIL.__file__)
extensions = {'JPEG', 'JPG', 'PNG', 'xcf', 'TIF',
              'tif', 'tiff', 'gif', 'jpeg', 'stl', 'jpg', 'png'}

TARGET_SIZE = (640, 480)
SOURCE_PATH = "F:\\images_temp"
TARGET_PATH = "D:\\to_do\\100daysproject\\wiki_science_categories\\wikiscrapes\\images\\resize"
errors = []
error_extns = set()
high_size_extns = set()
MAX_FILE_SIZE = 512

# Renaming tif files to tiff


for filename in os.listdir(SOURCE_PATH):
    kb_size = (os.stat(os.path.join(SOURCE_PATH, filename)).st_size)/1024
    if kb_size > 1024:
        high_size_extns.add(filename.split(".")[-1])

for filename in os.listdir(SOURCE_PATH):
    if (os.stat(os.path.join(SOURCE_PATH, filename)).st_size)/1024 > MAX_FILE_SIZE:
        if filename.split('.')[-1] == 'tif':
            # Converts .tif to .tiff that allows PIL.Image to open and process the file
            name = filename+'f'
            try:
                os.rename(os.path.join(SOURCE_PATH, filename),
                          os.path.join(SOURCE_PATH, name))
                filename = filename+'f'
            except Exception as e:
                print('File renaming failed due to ', e)
        if filename.split('.')[-1] != "pdf" and filename.split('.')[-1] != "svg":
            try:
                img = Image.open(os.path.join(SOURCE_PATH, filename))
                width, height = img.size
                try:
                    if width > TARGET_SIZE[0]:
                        mult = height / width
                        img = img.resize(
                            (TARGET_SIZE[0], int(TARGET_SIZE[0]*mult)))
                    if height > TARGET_SIZE[1]:
                        mult = width/height
                        img = img.resize(
                            (int(TARGET_SIZE[1]*mult), TARGET_SIZE[1]))
                    try:
                        img.save(os.path.join(TARGET_PATH, filename),
                                 optimize=True, quality=50, dpi=(72, 72))
                    except:
                        try:
                            img.save(os.path.join(SOURCE_PATH, filename),
                                     optimize=True, dpi=(72, 72))
                        except:
                            try:
                                img.save(os.path.join(TARGET_PATH, filename),
                                         dpi=(72, 72))
                            except:
                                try:
                                    img.save(os.path.join(
                                        TARGET_PATH, filename))
                                except Exception as e:
                                    print(
                                        'All file savers failed due to Exception ', e)
                except Exception as e:
                    print(
                        f'File {filename} loaded but could not be resized due to {e}')

            except Exception as e:
                print('Cant load', filename, 'because of ', e)
            # errors.append(filename)
            # error_extns.add(filename.split('.')[-1])
            # # shutil.copy(os.path.join(SOURCE_PATH, filename),
            # #             os.path.join(TARGET_PATH, filename))

    else:
        shutil.copyfile(os.path.join(SOURCE_PATH,filename), os.path.join(TARGET_PATH,filename))
# # print('High file size extns:', high_size_extns)
