#!/usr/bin/env python
"""
Utility module for retrieving various types of information required by the HyperCTui application.

This module provides the Get class with methods to:
- Access configuration files and settings
- Retrieve UI state information
- Read and extract metadata from image files
- Get system information (CPU/GPU counts)
- Handle file operations like listing folders and files
- Process angle information from image metadata

The Get class inherits from Parent to access the main application instance.
"""

import glob
import multiprocessing
import os
import subprocess
from collections import OrderedDict
from os.path import expanduser

import numpy as np
from PIL import Image
from qtpy import QtGui

from hyperctui.utilities.parent import Parent
from hyperctui.utilities.status_message_config import StatusMessageStatus, show_status_message


class Get(Parent):
    def get_log_file_name(self) -> str:
        log_file_name = self.parent.config["log_file_name"]
        full_log_file_name = Get.full_home_file_name(log_file_name)
        return full_log_file_name

    def get_main_tab_selected(self) -> int:
        current_tab = self.parent.ui.top_tabWidget.currentIndex()
        return current_tab

    def algorithm_selected(self) -> str:
        """
        Get the currently selected algorithm from the pre-processing fitting procedure combobox.

        Returns
        -------
        str
            The selected algorithm identifier.
        """
        index_selected = self.parent.ui.pre_processing_fitting_procedure_comboBox.currentIndex()
        return self.parent.ui.pre_processing_fitting_procedure_comboBox.itemData(index_selected)

    def get_automatic_config_file_name(self) -> str:
        """
        Get the full path to the automatic configuration file.

        Returns
        -------
        str
            Full path to the configuration file.
        """
        config_file_name = self.parent.config["session_file_name"]
        full_config_file_name = Get.full_home_file_name(config_file_name)
        return full_config_file_name

    def list_folders_in_output_directory(self, output_folder: str = None) -> list[str]:
        """
        List all folders in the specified output directory.

        Parameters
        ----------
        output_folder : str, optional
            Path to the output directory to list folders from.

        Returns
        -------
        list[str]
            List of folder paths found in the output directory.
        """
        list_raw = glob.glob(output_folder + os.sep + "*")
        list_folders = []
        for _entry in list_raw:
            if os.path.isdir(_entry):
                list_folders.append(_entry)
        return list_folders

    def get_file_index_of_180_degree_image(self) -> int:
        """
        Find the image index with angle closest to 180 degrees.

        Returns
        -------
        int
            Index of the image with angle closest to 180 degrees.
        """
        list_angles = self.parent.input["list angles"]
        offset_with_180degrees = np.abs(np.array(list_angles) - 180.0)
        min_value = np.min(offset_with_180degrees)
        index_of_min_value = np.where(offset_with_180degrees == min_value)
        return int(index_of_min_value[0][0])

    def angles(self, list_files: list[str]) -> np.ndarray:
        """
        Read angles from TIFF files at ORNL.

        Parameters
        ----------
        list_files : list[str]
            List of file paths to read angles from.

        Returns
        -------
        np.ndarray
            Array of angle values extracted from the files.
        """
        ANGLE_KEY = 65039  # 65048
        x = self.retrieve_value_of_metadata_key(list_files, list_key=[ANGLE_KEY])
        angles = np.zeros(len(x))
        for idx, val in enumerate(list(x.items())):
            temp = val[1]
            angles[idx] = float(next(iter(temp.values())).split(":")[1])
        return angles

    def retrieve_value_of_metadata_key(self, list_files: list[str] = [], list_key: list[int] = []) -> OrderedDict:
        """
        Retrieve metadata values for specified keys from a list of image files.

        Parameters
        ----------
        list_files : list[str], optional
            List of file paths to extract metadata from.
        list_key : list[int], optional
            List of metadata keys to extract.

        Returns
        -------
        OrderedDict
            Dictionary mapping file paths to their metadata values.
        """
        if list_files == []:
            return {}

        _dict = OrderedDict()

        nbr_files = len(list_files)
        self.parent.eventProgress.setMaximum(nbr_files)
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)

        show_status_message(
            parent=self.parent, message="Retrieving angle values ...", status=StatusMessageStatus.working
        )

        for _index, _file in enumerate(list_files):
            _meta = Get.value_of_metadata_key(filename=_file, list_key=list_key)
            _dict[_file] = _meta
            self.parent.eventProgress.setValue(_index + 1)
            QtGui.QGuiApplication.processEvents()

        self.parent.eventProgress.setVisible(False)
        show_status_message(parent=self.parent, message="", status=StatusMessageStatus.working)
        return _dict

    @staticmethod
    def value_of_metadata_key(filename: str = "", list_key: list[int] = None) -> dict:
        """
        Extract metadata values for specified keys from an image file.

        Parameters
        ----------
        filename : str, optional
            Path to the image file to extract metadata from.
        list_key : list[int], optional
            List of metadata keys to extract. If empty, all metadata is returned.

        Returns
        -------
        dict
            Dictionary mapping metadata keys to their values.
        """
        if filename == "":
            return {}

        image = Image.open(filename)
        metadata = image.tag_v2
        result = {}
        if list_key == []:
            for _key in metadata.keys():
                result[_key] = metadata.get(_key)
            return result

        for _meta in list_key:
            result[_meta] = metadata.get(_meta)

        image.close()
        return result

    @staticmethod
    def get_number_of_cpu() -> int:
        """
        Get the number of CPU cores available on the system.

        Returns
        -------
        int
            Number of CPU cores.
        """
        return multiprocessing.cpu_count()

    @staticmethod
    def get_number_of_gpu() -> int:
        """
        Get the number of NVIDIA GPU devices available on the system.

        Returns
        -------
        int
            Number of GPU devices, or 1 if NVIDIA tools are not available.
        """
        try:
            str_list_gpu = subprocess.run(["nvidia-smi", "-L"], stdout=subprocess.PIPE)
            list_gpu = str_list_gpu.stdout.decode("utf-8").split("\n")
            nbr_gpu = 0
            for _gpu in list_gpu:
                if not (_gpu == ""):
                    nbr_gpu += 1
            return nbr_gpu

        except FileNotFoundError:
            return 1

    @staticmethod
    def full_home_file_name(base_file_name: str) -> str:
        home_folder = expanduser("~")
        full_log_file_name = os.path.join(home_folder, base_file_name)
        return full_log_file_name

    @staticmethod
    def list_of_files(folder: str = None, ext: str = "*") -> list[str]:
        list_of_files = glob.glob(os.path.join(folder, ext))
        return list_of_files
