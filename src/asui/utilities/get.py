from os.path import expanduser
import os
from qtpy import QtGui
import numpy as np
import multiprocessing
import subprocess
from collections import OrderedDict
from PIL import Image

from .. import TiltAlgorithm
from ..status_message_config import StatusMessageStatus, show_status_message


class Get:

    def __init__(self, parent=None):
        self.parent = parent

    def get_log_file_name(self):
        log_file_name = self.parent.config['log_file_name']
        full_log_file_name = Get.full_home_file_name(log_file_name)
        return full_log_file_name

    def get_main_tab_selected(self):
        current_tab = self.parent.ui.top_tabWidget.currentIndex()
        return current_tab

    def algorithm_selected(self):
        index_selected = self.parent.ui.pre_processing_fitting_procedure_comboBox.currentIndex()
        return self.parent.ui.pre_processing_fitting_procedure_comboBox.itemData(index_selected)

    def get_automatic_config_file_name(self):
        config_file_name = self.parent.config['session_file_name']
        full_config_file_name = Get.full_home_file_name(config_file_name)
        return full_config_file_name

    def tilt_algorithm_selected(self):
        if self.parent.ui.tilt_correction_direct_minimization_radioButton.isChecked():
            return TiltAlgorithm.direct_minimization
        elif self.parent.ui.tilt_correction_phase_correlation_radioButton.isChecked():
            return TiltAlgorithm.phase_correlation
        elif self.parent.ui.tilt_correction_use_center_radioButton.isChecked():
            return TiltAlgorithm.use_center
        elif self.parent.ui.tilt_user_defined_radioButton.isChecked():
            return TiltAlgorithm.user_defined
        else:
            NotImplementedError("Tilt algorithm not implemented!")

    def get_file_index_of_180_degree_image(self):
        # """
        # using the fact that the file name is based on the following structure, this method will return
        # the file that is as close as possible to the angle 180
        # structure_of_file:  ####_angleBeforeComma_angleAfterComma_fileIndex.ext
        # """
        # list_of_files = self.parent.input['list files'][DataType.projections]
        # list_angles = []
        # for _file in list_of_files:
        #     basename = str(PurePath(PurePath(_file).name).stem)
        #     split_basename = basename.split("_")
        #     deg_before_comma = split_basename[-3]
        #     deg_after_comma = split_basename[-2]
        #     full_deg_value = f"{deg_before_comma}.{deg_after_comma}"
        #     list_angles.append(np.float(full_deg_value))
        #
        # offset_with_180degrees = np.abs(np.array(list_angles) - 180.0)
        # min_value = np.min(offset_with_180degrees)
        # index_of_min_value = np.where(offset_with_180degrees == min_value)
        #
        # return int(index_of_min_value[0][0])

        list_angles = self.parent.input['list angles']
        offset_with_180degrees = np.abs(np.array(list_angles) - 180.0)
        min_value = np.min(offset_with_180degrees)
        index_of_min_value = np.where(offset_with_180degrees == min_value)
        return int(index_of_min_value[0][0])

    def angles(self, list_files):
        '''
        Script to read angles from tiff files at ORNL
        '''
        ANGLE_KEY = 65039  # 65048
        x = self.retrieve_value_of_metadata_key(list_files,
                                                list_key=[ANGLE_KEY])
        angles = np.zeros(len(x))
        for idx, val in enumerate(list(x.items())):
            temp = val[1]
            angles[idx] = float(next(iter(temp.values())).split(':')[1])
        return angles

    def retrieve_value_of_metadata_key(self, list_files=[], list_key=[]):
        '''
        From https://github.com/JeanBilheux/python_101/blob/master/working_with_images/images_metadata/using%20code%20from%20python%20notebooks.ipynb
        '''
        if list_files == []:
            return {}

        _dict = OrderedDict()

        nbr_files = len(list_files)
        self.parent.eventProgress.setMaximum(nbr_files)
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)

        show_status_message(parent=self.parent,
                            message="Retrieving angle values ...",
                            status=StatusMessageStatus.working)

        for _index, _file in enumerate(list_files):
            _meta = Get.value_of_metadata_key(filename=_file,
                                              list_key=list_key)
            _dict[_file] = _meta
            self.parent.eventProgress.setValue(_index+1)
            QtGui.QGuiApplication.processEvents()

        self.parent.eventProgress.setVisible(False)
        show_status_message(parent=self.parent,
                            message="",
                            status=StatusMessageStatus.working)
        return _dict

    @staticmethod
    def value_of_metadata_key(filename='', list_key=None):
        '''
        From https://github.com/JeanBilheux/python_101/blob/master/working_with_images/images_metadata/using%20code%20from%20python%20notebooks.ipynb
        '''

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
    def get_number_of_cpu():
        return multiprocessing.cpu_count()

    @staticmethod
    def get_number_of_gpu():
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
    def full_home_file_name(base_file_name):
        home_folder = expanduser("~")
        full_log_file_name = os.path.join(home_folder, base_file_name)
        return full_log_file_name
