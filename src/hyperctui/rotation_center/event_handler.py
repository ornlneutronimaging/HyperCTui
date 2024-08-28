from qtpy import QtGui
import pyqtgraph as pg
import numpy as np
from tomopy.recon import rotation

from hyperctui.utilities.status_message_config import StatusMessageStatus, show_status_message


class EventHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def radio_button_changed(self, is_tomopy_checked=True):

        self.parent.ui.rotation_center_user_defined_radioButton.blockSignals(True)
        self.parent.ui.rotation_center_tomopy_radioButton.blockSignals(True)

        list_ui_tomopy = [self.parent.ui.rotation_center_tomopy_label1,
                          self.parent.ui.rotation_center_tomopy_label2,
                          self.parent.ui.rotation_center_tomopy_value]

        list_ui_user = [self.parent.ui.rotation_center_user_label1,
                        self.parent.ui.rotation_center_user_label2,
                        self.parent.ui.rotation_center_user_value]

        is_tomopy_radio_button_checked = is_tomopy_checked

        for _ui in list_ui_tomopy:
            _ui.setEnabled(is_tomopy_radio_button_checked)
        for _ui in list_ui_user:
            _ui.setEnabled(not is_tomopy_radio_button_checked)

        self.parent.ui.rotation_center_user_defined_radioButton.blockSignals(False)
        self.parent.ui.rotation_center_tomopy_radioButton.blockSignals(False)

        self.display_center_of_rotation()

    def update_widgets(self):
        """
        1. max value of user center of rotation value is width-1 of cropped image
        """
        left = int(self.parent.ui.crop_left_label_value.text())
        right = int(self.parent.ui.crop_right_label_value.text())
        width = right - left
        self.parent.ui.rotation_center_user_value.setMaximum(width-1)

    def calculate_using_tomopy(self):
        """
        calculate the center of rotation using tomopy.recon.rotation algorithm
        """

        image_0_degree = self.parent.image_0_degree
        image_180_degree = self.parent.image_180_degree

        left = int(self.parent.ui.crop_left_label_value.text())
        right = int(self.parent.ui.crop_right_label_value.text())

        if (not (image_0_degree is None)) and (not (image_180_degree is None)):
            cropped_image_0_degree = image_0_degree[:, left:right+1].copy()
            cropped_image_180_degree = image_180_degree[:, left:right+1].copy()

            value = rotation.find_center_pc(cropped_image_0_degree,
                                            cropped_image_180_degree)
            self.parent.ui.rotation_center_tomopy_value.setText(f"{int(value)}")

            # display vertical line showing the center of rotation found
            self.display_center_of_rotation()
            show_status_message(parent=self.parent,
                                message="calculation of center of rotation: Done!",
                                status=StatusMessageStatus.ready,
                                duration_s=5)

    def display_center_of_rotation(self):

        if self.parent.center_of_rotation_item:
            self.parent.rotation_center_image_view.removeItem(self.parent.center_of_rotation_item)

        _pen = QtGui.QPen()
        _pen.setColor(QtGui.QColor(255, 0, 0))
        _pen.setWidth(1)

        center_of_rotation_value = self.get_center_of_rotation()
        if np.isfinite(center_of_rotation_value):
            self.parent.center_of_rotation_item = pg.InfiniteLine(center_of_rotation_value,
                                                                  pen=_pen,
                                                                  angle=90,
                                                                  movable=False)
            self.parent.ui.rotation_center_image_view.addItem(self.parent.center_of_rotation_item)
            self.parent.center_of_rotation_item.sigDragged.connect(self.parent.manual_rotation_center_moved)
            self.parent.center_of_rotation_item.sigPositionChangeFinished.connect(self.parent.manual_rotation_center_moved)

    def get_center_of_rotation(self):
        try:
            if self.parent.ui.rotation_center_tomopy_radioButton.isChecked():
                return int(str(self.parent.ui.rotation_center_tomopy_value.text()))
            else:
                return self.parent.ui.rotation_center_user_value.value()
        except ValueError:
            return np.nan
