from qtpy.QtWidgets import QMainWindow
from qtpy.QtGui import QGuiApplication
import os
import glob
import logging
import time

from imars3d.backend.dataio.data import _load_images as imars3d_load_images
from imars3d.backend.util.functions import clamp_max_workers

from hyperctui import load_ui, EvaluationRegionKeys
from hyperctui.session import SessionKeys

from hyperctui.autonomous_reconstruction.initialization import InitializationSelectTofRegions


class SelectTofRegions(QMainWindow):

    top_roi_id = None

    def __init__(self, parent=None):
        super(SelectTofRegions, self).__init__(parent)
        self.parent = parent

        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                    os.path.join('ui',
                                                 'select_tof_regions.ui'))

        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Select TOF regions")

        self.initialization()
        self.load_images()
        self.display_tof_profile()

    def initialization(self):
        o_init = InitializationSelectTofRegions(parent=self, grand_parent=self.parent)
        o_init.all()
        self.projections_changed()

    def load_images(self):
        session_dict = self.parent.session_dict
        if self.ui.projections_0degree_radioButton.isChecked():
            if self.parent.image_data[SessionKeys.image_0_degree] is None:
                self.parent.ui.hourglass_label.setVisible(True)
                QGuiApplication.processEvents()
                time.sleep(1)
                QGuiApplication.processEvents()
                logging.info("Loading stack of images at 0degree!")
                image_0_full_path = session_dict[SessionKeys.full_path_to_projections][SessionKeys.image_0_degree]
                self.parent.image_data[SessionKeys.image_0_degree] = \
                    SelectTofRegions.load_images_from_this_folder(folder_name=image_0_full_path)
                self.parent.ui.hourglass_label.setVisible(False)
        else:
            if self.parent.image_data[SessionKeys.image_180_degree] is None:
                self.ui.hourglass_label.setVisible(True)
                time.sleep(1)
                QGuiApplication.processEvents()
                QGuiApplication.processEvents()
                logging.info("Loading stack of images at 180degrees!")
                image_180_full_path = session_dict[SessionKeys.full_path_to_projections][SessionKeys.image_180_degree]
                self.parent.image_data[SessionKeys.image_180_degree] = \
                    SelectTofRegions.load_images_from_this_folder(folder_name=image_180_full_path)
                # self.ui.hourglass_label.setVisible(False)
        QGuiApplication.processEvents()

    @staticmethod
    def load_images_from_this_folder(folder_name):
        """
        all the images are in fact inside the folder called "Run_####" within that folder
        """
        folder_inside = glob.glob(os.path.join(folder_name, 'Run_*'))
        list_tiff = glob.glob(os.path.join(folder_inside[0], "*.tif"))
        logging.info(f"-> loading {len(list_tiff)} 'tif' files!")
        # load the tiff using iMars3D
        data = imars3d_load_images(filelist=list_tiff,
                                   desc="",
                                   max_workers=clamp_max_workers(max_workers=10),
                                   tqdm_class=None)
        return data

    def display_tof_profile(self):
        pass

    def table_changed(self):
        pass

    def projections_changed(self):
        self.load_images()
        self.update_top_view()

    def instrument_settings_changed(self):
        pass

    def update_top_view(self):
        if self.ui.projections_0degree_radioButton.isChecked():
            image = self.parent.image_0_degree
        elif self.ui.projections_180degree_radioButton.isChecked():
            image = self.parent.image_180_degree
        else:
            raise NotImplementedError("image to display is not 0 or 180 degree!")
        self.ui.top_image_view.setImage(image)
        self.top_live_image = image

    def top_roi_changed(self):
        region = self.top_roi_id.getArraySlice(self.top_live_image,
                                               self.ui.top_image_view.imageItem)

        left = region[0][0].start
        right = region[0][0].stop
        top = region[0][1].start
        bottom = region[0][1].stop

        self.parent.session_dict[SessionKeys.tof_roi_region] = {'x0': left,
                                                                'y0': top,
                                                                'x1': right,
                                                                'y1': bottom}

    def accept(self):
        self.close()