import numpy as np
import logging
from qtpy import QtGui
import pyqtgraph as pg

from NeuNorm.normalization import Normalization

from hyperctui.session import SessionKeys
from hyperctui.utilities.file_utilities import get_list_img_files_from_top_folders
from hyperctui.utilities.widgets import Widgets as UtilityWidgets
from hyperctui.utilities.exceptions import CropError


class Crop:

    list_files = None

    def __init__(self, parent=None):
        self.parent = parent

    def load_projections(self):
        logging.info(f"Loading projections in crop")
        list_projections = self.parent.session_dict[SessionKeys.list_projections]
        logging.info(f"-> list_projections: {list_projections}")

        try:
            list_summed_img = get_list_img_files_from_top_folders(list_projections=list_projections)
        except IndexError as error:
            logging.info(f"ERROR! unable to locate the _SummedImg.fits file in {error}")
            raise CropError(f"ERROR! unable to locate the _SummedImg.fits file in {error}")

        logging.info(f"-> list_projections: {list_summed_img}")
        o_loader = Normalization()
        o_loader.load(file=list_summed_img, notebook=False)

        self.mean_image = np.mean(o_loader.data['sample']['data'][:], axis=0)
        [height, width] = np.shape(self.mean_image)
        self.parent.image_size = {'height': height, 'width': width}
        self.parent.image_0_degree = o_loader.data['sample']['data'][0]
        self.parent.image_180_degree = o_loader.data['sample']['data'][1]
        self.parent.crop_live_image = self.mean_image

    def initialize(self):
        try:
            self.load_projections()
        except CropError:
            o_widgets = UtilityWidgets(parent=self.parent)
            o_widgets.make_tabs_visible(is_visible=False)
            raise CropError

        self.parent.ui.crop_image_view.clear()
        self.parent.ui.crop_image_view.setImage(np.transpose(self.mean_image))
        self.parent.ui.top_crop_widget.setEnabled(True)

        [_, width] = np.shape(self.parent.crop_live_image)

        default_left = 0 + width/3
        default_right = width - width/3

        left = self.parent.session_dict.get(SessionKeys.crop_left, default_left)
        right = self.parent.session_dict.get(SessionKeys.crop_right, default_right)

        left = int(np.min([left, right]))
        right = int(np.max([left, right]))

        self.parent.session_dict[SessionKeys.crop_left] = left
        self.parent.session_dict[SessionKeys.crop_right] = right

        self.parent.ui.crop_left_label_value.setText(str(left))
        self.parent.ui.crop_right_label_value.setText(str(right))

        self.init_roi(left, right)

    def init_roi(self, left, right):

        # if self.parent.crop_roi_id:
        #     self.parent.ui.crop_image_view.removeItem(self.parent.crop_roi_id)

        _color = QtGui.QColor(62, 13, 244)
        _pen = QtGui.QPen()
        _pen.setColor(_color)
        _pen.setWidthF(1)

        self.parent.crop_left_ui = pg.InfiniteLine(left,
                                           pen=_pen,
                                           angle=90,
                                           movable=True)
        self.parent.ui.crop_image_view.addItem(self.parent.crop_left_ui)
        self.parent.crop_left_ui.sigDragged.connect(self.parent.sort_the_crop_values)
        self.parent.crop_left_ui.sigPositionChangeFinished.connect(self.parent.sort_the_crop_values)

        self.parent.crop_right_ui = pg.InfiniteLine(right,
                                                    pen=_pen,
                                                    angle=90,
                                                    movable=True)
        self.parent.ui.crop_image_view.addItem(self.parent.crop_right_ui)
        self.parent.crop_right_ui.sigDragged.connect(self.parent.sort_the_crop_values)
        self.parent.crop_right_ui.sigPositionChangeFinished.connect(self.parent.sort_the_crop_values)

    # def update_roi(self):
    #     left = self.parent.ui.crop_left_spinBox.value()
    #     right = self.parent.ui.crop_right_spinBox.value()
    #
    #     self.init_roi(left, right)

    def roi_manually_moved(self):
        pass
        # region = self.parent.crop_roi_id.getArraySlice(self.parent.crop_live_image,
        #                                                self.parent.ui.crop_image_view.imageItem)
        #
        # left = region[0][0].start
        # right = region[0][0].stop
        # top = region[0][1].start
        # bottom = region[0][1].stop
        #
        # self.parent.ui.crop_left_spinBox.blockSignals(True)
        # self.parent.ui.crop_right_spinBox.blockSignals(True)
        # self.parent.ui.crop_top_spinBox.blockSignals(True)
        # self.parent.ui.crop_bottom_spinBox.blockSignals(True)
        #
        # self.parent.ui.crop_left_spinBox.setValue(left)
        # self.parent.ui.crop_right_spinBox.setValue(right)
        # self.parent.ui.crop_top_spinBox.setValue(top)
        # self.parent.ui.crop_bottom_spinBox.setValue(bottom)
        #
        # self.parent.ui.crop_left_spinBox.blockSignals(False)
        # self.parent.ui.crop_right_spinBox.blockSignals(False)
        # self.parent.ui.crop_top_spinBox.blockSignals(False)
        # self.parent.ui.crop_bottom_spinBox.blockSignals(False)
