#!/usr/bin/env python
"""
File utility functions for HyperCTui.

This module provides various file-related utility functions for the HyperCTui application, including:
- File searching and listing
- Reading and writing file contents
- Path manipulation and file extension handling
- Directory creation and management
- File moving and organization
- Special directory detection for TOF and OB directories
- JSON file handling
"""

import glob
import json
import ntpath
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


def get_list_files(directory: str = "./", file_extension: List[str] = ["*.fits"]) -> List[str]:
    """
    Return the list of files in the specified directory with given file extensions.

    Parameters
    ----------
    directory : str, optional
        Directory path to search for files. Default is "./".
    file_extension : List[str], optional
        List of file extensions to search for. Default is ["*.fits"].

    Returns
    -------
    List[str]
        List of full paths to files matching the specified extensions.
    """
    full_list_files = []

    for _ext in file_extension:
        list_files = glob.glob(os.path.join(directory, _ext))
        for _file in list_files:
            full_list_files.append(_file)

    return full_list_files


def get_short_filename(full_filename: str = "") -> str:
    """
    Get the filename without the directory path and extension.

    Parameters
    ----------
    full_filename : str, optional
        Full path to the file. Default is an empty string.

    Returns
    -------
    str
        Filename stem without extension.
    """
    return str(Path(full_filename).stem)


def read_ascii(filename: str = "") -> str:
    """
    Return content of an ASCII file.

    Parameters
    ----------
    filename : str, optional
        Path to the file to read. Default is an empty string.

    Returns
    -------
    str
        Content of the file.
    """
    with open(filename, "r") as f:
        text = f.read()
    return text


def write_ascii(text: str = "", filename: str = "") -> None:
    """
    Write text content to an ASCII file.

    Parameters
    ----------
    text : str, optional
        Content to write to the file. Default is an empty string.
    filename : str, optional
        Path to the file to write. Default is an empty string.

    Returns
    -------
    None
    """
    with open(filename, "w") as f:
        f.write(text)


def path_leaf(path: str) -> str:
    """
    Get the leaf (filename) portion of a path.

    Parameters
    ----------
    path : str
        File path to extract the leaf from.

    Returns
    -------
    str
        The filename portion of the path.
    """
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def get_data_type(file_name: str) -> str:
    """
    Get the file extension from a filename.

    Parameters
    ----------
    file_name : str
        Full file name with extension.

    Returns
    -------
    str
        File extension (including the dot) e.g., ".tif", ".fits"
    """
    filename, file_extension = os.path.splitext(file_name)
    return file_extension.strip()


def get_file_extension(filename: str) -> str:
    """
    Retrieve the file extension of the filename without the leading dot.

    Parameters
    ----------
    filename : str
        Full file name with extension.

    Returns
    -------
    str
        File extension without the leading dot.
    """
    full_extension = get_data_type(filename)
    return full_extension[1:]


def get_list_file_extensions(list_filename: List[str]) -> Set[str]:
    """
    Get unique file extensions from a list of filenames.

    Parameters
    ----------
    list_filename : List[str]
        List of filenames with extensions.

    Returns
    -------
    Set[str]
        Set of unique file extensions.
    """
    list_extension = []
    for _file in list_filename:
        _extension = get_file_extension(_file)
        list_extension.append(_extension)

    return list(set(list_extension))


def make_or_reset_folder(folder_name: str) -> None:
    """
    Create a folder or reset it if it already exists.

    Parameters
    ----------
    folder_name : str
        Path to the folder to create or reset.

    Returns
    -------
    None
    """
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)
    os.makedirs(folder_name)


def make_folder(folder_name: str) -> None:
    """
    Create a folder if it doesn't exist.

    Parameters
    ----------
    folder_name : str
        Path to the folder to create.

    Returns
    -------
    None
    """
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)


def move_list_files_to_folder(list_of_files: Optional[List[str]] = None, folder: Optional[str] = None) -> None:
    """
    Move a list of files to a specified folder.

    Parameters
    ----------
    list_of_files : List[str], optional
        List of file paths to move. Default is None.
    folder : str, optional
        Destination folder path. Default is None.

    Returns
    -------
    None
    """
    if list_of_files is None:
        return

    for _file in list_of_files:
        shutil.move(_file, folder)


def list_dirs(rootdir: str) -> List[str]:
    """
    Retrieve recursively the list of all folders within rootdir.

    Parameters
    ----------
    rootdir : str
        Root directory to start the search from.

    Returns
    -------
    List[str]
        List of absolute paths to all directories within the root directory.
    """
    return [os.path.abspath(x[0]) for x in os.walk(rootdir)]


def list_tof_dirs(rootdir: str) -> List[str]:
    """
    Find TOF directories containing Spectra.txt files.

    A folder is considered as a TOF dir if it contains a _Spectra.txt file.

    Parameters
    ----------
    rootdir : str
        Root directory to start the search from.

    Returns
    -------
    List[str]
        List of paths to TOF directories.
    """
    _list_dirs = list_dirs(rootdir)
    list_tof_dirs = []
    for _dir in _list_dirs:
        list_spectra_file = glob.glob(os.path.join(_dir, "*_Spectra.txt"))
        if len(list_spectra_file) == 1:
            list_tof_dirs.append(_dir)
    return list_tof_dirs


def list_ob_dirs(rootdir: str) -> List[str]:
    """
    Find OB directories that are also TOF directories.

    A folder is considered as an OB dir if it contains a _Spectra.txt file
    and its parent directory starts with "OB_".

    Parameters
    ----------
    rootdir : str
        Root directory to start the search from.

    Returns
    -------
    List[str]
        List of paths to OB directories.
    """
    list_tof_folders = list_tof_dirs(rootdir)
    list_ob_dirs = []
    for _folder in list_tof_folders:
        if os.path.basename(os.path.dirname(_folder)).startswith("OB_"):
            list_ob_dirs.append(_folder)
    return list_ob_dirs


def read_json(file_name: str) -> Dict[str, Any]:
    """
    Read and parse a JSON file.

    Parameters
    ----------
    file_name : str
        Path to the JSON file.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing parsed JSON data.
    """
    config = {}
    with open(file_name) as f:
        config = json.load(f)
    return config


def get_list_img_files_from_top_folders(list_projections: List[str]) -> List[str]:
    """
    Find SummedImg.fits files in projection folders.

    Given a list of top folders, returns the full path of the _SummedImg.fits files
    inside their subfolders.

    Parameters
    ----------
    list_projections : List[str]
        List of top folder paths.

    Returns
    -------
    List[str]
        List of paths to SummedImg.fits files.

    Raises
    ------
    IndexError
        If a _SummedImg.fits file cannot be found in an expected location.
    """
    list_img_files = []
    for _projection in list_projections:
        _folder = glob.glob(os.path.join(_projection, "Run_*"))
        if _folder:
            img_file = glob.glob(os.path.join(_folder[0], "*_SummedImg.fits"))
            try:
                list_img_files.append(img_file[0])
            except IndexError:
                raise IndexError(_folder[0])

    return list_img_files
