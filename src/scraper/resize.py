from PIL import Image
import PIL
import os
import shutil
import pickle


def loadall(filename):
    with open(filename, "rb") as f:
        while True:
            try:
                yield pickle.load(f)
            except EOFError:
                break


TARGET_SIZE = (640, 480)
PIL.Image.MAX_IMAGE_PIXELS = int(1082882052 * 1.5)
MAX_FILE_SIZE = 512

errors = []
error_extns = set()
high_size_extns = set()


def get_oversized_extensions():
    for file_name in os.listdir(source_path):
        kb_size = os.stat(os.path.join(source_path, file_name)).st_size / 1024
        if kb_size > MAX_FILE_SIZE:
            high_size_extns.add(file_name.split(".")[-1])
    print(f"File extensions of type {', '.join(high_size_extns)} have a file size larger than {MAX_FILE_SIZE}")


def resize_files(sourcepath, targetpath):
    print('Resizing initiated......')
    image_list = os.listdir(sourcepath)
    list_size = len(image_list)
    for file_no in range(list_size):
        filename = image_list[file_no]
        if os.stat(os.path.join(sourcepath, filename)).st_size / 1024 > MAX_FILE_SIZE:
            if filename.split('.')[-1] != "pdf" and filename.split('.')[-1] != "svg":
                try:
                    img = Image.open(os.path.join(sourcepath, filename))
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
                            img.save(os.path.join(targetpath, filename),
                                     optimize=True, quality=50, dpi=(72, 72))
                        except Exception as e1:
                            if filename.split('.')[-1] != "jpg":
                                continue
                            else:
                                print('Could not save ', filename, ' due to Exception e1: ', e1)
                            try:
                                img.save(os.path.join(targetpath, filename),
                                         optimize=True, dpi=(72, 72))
                            except Exception as e2:
                                print('Could not save due to Exception e2: ', e2)
                                try:
                                    img.save(os.path.join(targetpath, filename),
                                             dpi=(72, 72))
                                except Exception as e3:
                                    print('Could not save due to Exception e3: ', e3)
                                    try:
                                        img.save(os.path.join(
                                            targetpath, filename))
                                    except Exception as e4:
                                        print(
                                            'All file savers failed due to Exception e4 ', e4)

                    except Exception as e5:
                        print(
                            f'File {filename} loaded but could not be resized due to Exception e5: {e5}')
                    img.close()
                    del img

                except Exception as e6:
                    print('Cant load', filename, 'because of Exception e6', e6)
                # errors.append(filename)
                # error_extns.add(filename.split('.')[-1])
                # # shutil.copy(os.path.join(SOURCE_PATH, filename),
                # #             os.path.join(TARGET_PATH, filename))
        else:
            shutil.copy(os.path.join(sourcepath, filename), targetpath)
        if file_no % (int(list_size / 10)) == 0:
            print(f"{file_no + 1} files processed. {round((100 * file_no) / list_size)} percent complete.")
    print('Resizing complete. Resized files are stored in ', targetpath)

    del img

def rebuild_output(input_file, output_file, image_path):
    print(f'Initiating updation of {input_file}')
    fo = open(output_file, 'wb')
    file_list = os.listdir(image_path)
    file_ish = input_file
    items = list(loadall(file_ish))
    print('Rebuilding json file......')
    for item_l in range(len(items)):
        item = items[item_l]
        key1 = list(item.keys())[0]
        vals = item[key1]['images']
        if isinstance(vals, dict):
            keys = vals.keys()
            for key in list(keys):
                if key not in file_list:
                    del items[item_l][key1]['images'][key]
        else:
            item[key1]['images'] = None
    print('Checking rebuilt output file....')
    recheck = True
    for item in items:
        key1 = list(item.keys())[0]
        vals = item[key1]['images']
        if isinstance(vals, dict):
            keys = vals.keys()
            for key in keys:
                if key not in file_list:
                    print('Recheck failed')
                    recheck = False
                    break
        else:
            assert vals is None
            continue
    if recheck:
        print('Rechecking complete....writing to output file')
        for item in items:
            pickle.dump(item, fo)
    else:
        print('Error in rebuilding output file.')
    fo.close()


def resize_and_update(sourcepath, targetpath, source_filepath, target_filepath):
    resize_files(sourcepath, targetpath)
    rebuild_output(source_filepath, target_filepath, targetpath)
    print('Resizing and update done !')


if __name__ == "__main__":
    DATA_PATH = '..//..//data'
    SOURCE_FOLDER = 'init_images'
    data_path = os.path.join(DATA_PATH)
    source_path = os.path.join(DATA_PATH, SOURCE_FOLDER)

    TARGET_FOLDER = 'images'
    if TARGET_FOLDER not in os.listdir(data_path):
        try:
            os.mkdir(os.path.join(data_path, TARGET_FOLDER))
        except Exception as e:
            print('Images folder could not be created because of Exception ', e)
    target = os.path.join(data_path, TARGET_FOLDER)

    SOURCE_FILE = 'output.json'
    source_file_path = os.path.join(data_path, SOURCE_FILE)
    TARGET_PKL_FILE = 'final_output.pkl'
    target_pkl_path = os.path.join(data_path, TARGET_PKL_FILE)

    resize_and_update(sourcepath=source_path, targetpath=target, source_filepath=source_file_path,
                      target_filepath=target_pkl_path)
