import numpy as np
import logging

from NeuNorm.normalization import Normalization

from ..session import SessionKeys
from ..utilities.file_utilities import get_list_img_files_from_top_folders

class Crop:

    list_files = None

    def __init__(self, parent=None):
        self.parent = parent

    def load_projections(self):
        logging.info(f"Loading projections in crop")
        list_projections = self.parent.session_dict[SessionKeys.list_projections_folders_initially_there]
        list_summed_img = get_list_img_files_from_top_folders(list_projections=list_projections)
        logging.info(f"-> list_projections: {list_summed_img}")

        o_loader = Normalization()
        o_loader.load(file=list_summed_img, notebook=False)

        self.mean_image = np.mean(o_loader.data['sample']['data'][:], axis=0)

    def display_data(self):
        self.parent.ui.crop_image_view.clear()
        self.parent.ui.crop_image_view.setImage(self.mean_image)

    def display_roi(self):
        left = self.parent.ui.crop_left_spinBox.value()
        right = self.parent.ui.crop_right_spinBox.value()
        top = self.parent.ui.crop_top_spinBox.value()
        bottom = self.parent.ui.crop_bottom_spinBox.value()

        #FIXME
