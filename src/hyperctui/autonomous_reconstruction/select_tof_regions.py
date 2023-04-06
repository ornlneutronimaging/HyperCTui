from qtpy.QtWidgets import QMainWindow
from qtpy.QtGui import QGuiApplication
import os
import glob
import logging
import dxchange
import numpy as np

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

    def initialization(self):
        o_init = InitializationSelectTofRegions(parent=self, grand_parent=self.parent)
        o_init.all()

    def load_images(self):
        session_dict = self.parent.session_dict
        if self.ui.projections_0degree_radioButton.isChecked():
            if self.parent.image_data[SessionKeys.image_0_degree] is None:
                logging.info("Loading stack of images at 0degree!")
                image_0_full_path = session_dict[SessionKeys.full_path_to_projections][SessionKeys.image_0_degree]
                self.parent.image_data[SessionKeys.image_0_degree] = \
                    self.load_images_from_this_folder(folder_name=image_0_full_path)
        else:
            if self.parent.image_data[SessionKeys.image_180_degree] is None:
                logging.info("Loading stack of images at 180degrees!")
                image_180_full_path = session_dict[SessionKeys.full_path_to_projections][SessionKeys.image_180_degree]
                self.parent.image_data[SessionKeys.image_180_degree] = \
                    self.load_images_from_this_folder(folder_name=image_180_full_path)

    def load_images_from_this_folder(self, folder_name):
        """
        all the images are in fact inside the folder called "Run_####" within that folder
        """
        folder_inside = glob.glob(os.path.join(folder_name, 'Run_*'))
        list_tiff = glob.glob(os.path.join(folder_inside[0], "*.tif"))
        list_tiff.sort()
        logging.info(f"-> loading {len(list_tiff)} 'tif' files!")
        # load the tiff using iMars3D

        self.eventProgress.setValue(0)
        self.eventProgress.setMaximum(len(list_tiff))
        self.eventProgress.setVisible(True)
        QGuiApplication.processEvents()

        data = []

        import tifffile
        for _index, _file in enumerate(list_tiff):
            # _data = dxchange.read_tiff(_file)
            _data = tifffile.imread(_file)
            self.eventProgress.setValue(_index+1)
            QGuiApplication.processEvents()
            data.append(_data)

        self.eventProgress.setVisible(False)
        QGuiApplication.processEvents()

        return data

    def display_tof_profile(self):
        tof_roi_region = self.parent.session_dict[SessionKeys.tof_roi_region]
        x0 = tof_roi_region['x0']
        y0 = tof_roi_region['y0']
        x1 = tof_roi_region['x1']
        y1 = tof_roi_region['y1']
        if self.ui.projections_0degree_radioButton.isChecked():
            full_data = self.parent.image_data[SessionKeys.image_0_degree]
        else:
            full_data = self.parent.image_data[SessionKeys.image_180_degree]

        tof_profile = []
        for _index, _data in enumerate(full_data):
            # print(f"{x0 =}, {y0 =}, {x1 =}, {y1 =} -> {_index =}: {np.shape(_data) =}")
            _counts_of_roi = _data[y0:y1+1, x0:x1+1]
            _mean_counts = np.mean(_counts_of_roi)
            tof_profile.append(_mean_counts)

        self.ui.bragg_edge_plot.plot(tof_profile)

    def table_changed(self):
        pass

    def projections_changed(self):
        self.load_images()
        self.update_top_view()
        self.display_tof_profile()

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