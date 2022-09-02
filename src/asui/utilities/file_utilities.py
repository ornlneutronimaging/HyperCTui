import glob
import os
from pathlib import Path
import ntpath
import shutil


def get_list_files(directory="./", file_extension=["*.fits"]):
    """
    return the list of files in the directory specified according to the instrument used
    """
    full_list_files = []

    for _ext in file_extension:
        list_files = glob.glob(os.path.join(directory, _ext))
        for _file in list_files:
            full_list_files.append(_file)

    return full_list_files


def get_short_filename(full_filename=""):
    return str(Path(full_filename).stem)


def read_ascii(filename=''):
    '''return contain of an ascii file'''
    with open(filename, 'r') as f:
        text = f.read()
    return text


def write_ascii(text="", filename=''):
    with open(filename, 'w') as f:
        f.write(text)


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)



def get_data_type(file_name):
    '''
    using the file name extension, will return the type of the data

    Arguments:
        full file name

    Returns:
        file extension    ex:.tif, .fits
    '''
    filename, file_extension = os.path.splitext(file_name)
    return file_extension.strip()


def get_file_extension(filename):
    '''retrieve the file extension of the filename and make sure
    we only keep the extension value and not the "dot" before it'''
    full_extension = get_data_type(filename)
    return full_extension[1:]


def get_list_file_extensions(list_filename):
    list_extension = []
    for _file in list_filename:
        _extension = get_file_extension(_file)
        list_extension.append(_extension)

    return list(set(list_extension))


def make_or_reset_folder(folder_name):
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)
    os.makedirs(folder_name)


def make_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
