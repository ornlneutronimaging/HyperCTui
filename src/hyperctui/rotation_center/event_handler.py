from qtpy.QtWidgets import QApplication
from qtpy import QtCore
import numpy as np
from tomopy.recon import rotation


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

    def calculate_using_tomopy(self):
        """
        calculate the center of rotation using tomopy.recon.rotation algorithm
        """
        value = rotation.find_center_pc(self.parent.image_0_degree,
                                        self.parent.image_180_degree)
        self.parent.ui.rotation_center_tomopy_value.setText(f"{int(value)}")
