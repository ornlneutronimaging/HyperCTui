import glob
import os
from pathlib import Path
import ntpath
import shutil
import json


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


def move_list_files_to_folder(list_of_files=None, folder=None):
    if list_of_files is None:
        return

    for _file in list_of_files:
        shutil.move(_file, folder)


def list_dirs(rootdir):
    """retrieve recursively the list of all folders within rootdir"""
    return [os.path.abspath(x[0]) for x in os.walk(rootdir)]


def list_tof_dirs(rootdir):
    """a folder is considered as a TOF dir if we can find a _Spectra.txt file in it"""
    _list_dirs = list_dirs(rootdir)
    list_tof_dirs = []
    for _dir in _list_dirs:
        list_spectra_file = glob.glob(os.path.join(_dir, "*_Spectra.txt"))
        if len(list_spectra_file) == 1:
            list_tof_dirs.append(_dir)
    return list_tof_dirs


def list_ob_dirs(rootdir):
    """a folder is considered as a OB dir if we can find a _Spectra.txt file in it,
    and it starts by ob_ """
    list_tof_folders = list_tof_dirs(rootdir)
    list_ob_dirs = []
    for _folder in list_tof_folders:
        if os.path.basename(os.path.dirname(_folder)).startswith("OB_"):
            list_ob_dirs.append(_folder)
    return list_ob_dirs


def read_json(file_name):
    config = {}
    with open(file_name) as f:
        config = json.load(f)
    return config


def get_list_img_files_from_top_folders(list_projections):
    """
    list of projections is the top folder and we need to return the full path of the _SummedImg.fits file
    inside a subfolder
    """
    list_img_files = []
    for _projection in list_projections:
        _folder = glob.glob(os.path.join(_projection, 'Run_*'))
        if _folder:
            img_file = glob.glob(os.path.join(_folder[0], '*_SummedImg.fits'))
            try:
                list_img_files.append(img_file[0])
            except IndexError:
                raise IndexError(_folder[0])

    return list_img_files
