#!/usr/bin/env python
"""
Module for handling events related to rotation center calculations and visualization.

This module provides functionality to calculate and display the rotation center
of tomographic images using either TomoPy algorithms or user-defined values.
"""

from typing import Any, Optional, Union

import numpy as np
import pyqtgraph as pg
from qtpy import QtGui
from tomopy.recon import rotation

from hyperctui.utilities.status_message_config import StatusMessageStatus, show_status_message


class EventHandler:
    """
    Handler for events related to rotation center calculations and UI interactions.

    This class manages user interactions with the rotation center UI, including
    radio button changes, widget updates, and calculations using TomoPy or
    user-defined values.
    """

    def __init__(self, parent: Optional[Any] = None) -> None:
        """
        Initialize the EventHandler class.

        Parameters
        ----------
        parent : object, optional
            The parent object that contains the UI elements and image data.
        """
        self.parent = parent

    def radio_button_changed(self, is_tomopy_checked: bool = True) -> None:
        """
        Handle changes in the rotation center method radio buttons.

        Updates the UI to enable/disable appropriate fields based on the selected
        rotation center calculation method.

        Parameters
        ----------
        is_tomopy_checked : bool, default True
            Whether the TomoPy radio button is checked. If False, the user-defined
            radio button is assumed to be checked.
        """
        self.parent.ui.rotation_center_user_defined_radioButton.blockSignals(True)
        self.parent.ui.rotation_center_tomopy_radioButton.blockSignals(True)

        list_ui_tomopy = [
            self.parent.ui.rotation_center_tomopy_label1,
            self.parent.ui.rotation_center_tomopy_label2,
            self.parent.ui.rotation_center_tomopy_value,
        ]

        list_ui_user = [
            self.parent.ui.rotation_center_user_label1,
            self.parent.ui.rotation_center_user_label2,
            self.parent.ui.rotation_center_user_value,
        ]

        is_tomopy_radio_button_checked = is_tomopy_checked

        for _ui in list_ui_tomopy:
            _ui.setEnabled(is_tomopy_radio_button_checked)
        for _ui in list_ui_user:
            _ui.setEnabled(not is_tomopy_radio_button_checked)

        self.parent.ui.rotation_center_user_defined_radioButton.blockSignals(False)
        self.parent.ui.rotation_center_tomopy_radioButton.blockSignals(False)

        self.display_center_of_rotation(is_tomopy_checked)

    def update_widgets(self) -> None:
        """
        Update widget properties based on the current state.

        Adjusts the maximum value of the user-defined center of rotation
        based on the width of the cropped image.

        Notes
        -----
        The maximum value for the user center of rotation is set to width-1
        of the cropped image.
        """
        left = int(self.parent.ui.crop_left_label_value.text())
        right = int(self.parent.ui.crop_right_label_value.text())
        width = right - left
        self.parent.ui.rotation_center_user_value.setMaximum(width - 1)

    def calculate_using_tomopy(self) -> None:
        """
        Calculate the center of rotation using TomoPy's rotation algorithm.

        Uses the TomoPy `find_center_pc` algorithm to determine the center of
        rotation based on the 0-degree and 180-degree images.

        Notes
        -----
        The calculation is performed on cropped versions of the images based
        on the current crop settings in the UI.
        """
        image_0_degree = self.parent.image_0_degree
        image_180_degree = self.parent.image_180_degree

        left = int(self.parent.ui.crop_left_label_value.text())
        right = int(self.parent.ui.crop_right_label_value.text())

        if (image_0_degree is not None) and (image_180_degree is not None):
            cropped_image_0_degree = image_0_degree[:, left : right + 1].copy()
            cropped_image_180_degree = image_180_degree[:, left : right + 1].copy()

            value = rotation.find_center_pc(cropped_image_0_degree, cropped_image_180_degree)
            self.parent.ui.rotation_center_tomopy_value.setText(f"{int(value)}")

            # display vertical line showing the center of rotation found
            self.display_center_of_rotation()
            show_status_message(
                parent=self.parent,
                message="calculation of center of rotation: Done!",
                status=StatusMessageStatus.ready,
                duration_s=5,
            )

    def display_center_of_rotation(self, is_tomopy_checked: bool = True) -> None:
        """
        Display the center of rotation on the image view.

        Adds a vertical line to the image view to indicate the center of rotation.
        The line is movable if the user-defined method is selected.

        Parameters
        ----------
        is_tomopy_checked : bool, default True
            Whether the TomoPy radio button is checked. If False, the user-defined
            radio button is assumed to be checked.
        """
        if self.parent.center_of_rotation_item:
            self.parent.rotation_center_image_view.removeItem(self.parent.center_of_rotation_item)

        _pen = QtGui.QPen()
        _pen.setColor(QtGui.QColor(255, 0, 0))
        _pen.setWidth(1)

        center_of_rotation_value = self.get_center_of_rotation()
        if np.isfinite(center_of_rotation_value):
            self.parent.center_of_rotation_item = pg.InfiniteLine(
                center_of_rotation_value, pen=_pen, angle=90, movable=not is_tomopy_checked
            )
            self.parent.ui.rotation_center_image_view.addItem(self.parent.center_of_rotation_item)
            self.parent.center_of_rotation_item.sigDragged.connect(self.parent.manual_rotation_center_moved)
            self.parent.center_of_rotation_item.sigPositionChangeFinished.connect(
                self.parent.manual_rotation_center_moved
            )

    def get_center_of_rotation(self) -> Union[int, float]:
        """
        Get the current center of rotation value.

        Returns the center of rotation value based on the selected method (TomoPy or user-defined).

        Returns
        -------
        int or float
            The center of rotation value. Returns NaN if the value is invalid.
        """
        try:
            if self.parent.ui.rotation_center_tomopy_radioButton.isChecked():
                return int(str(self.parent.ui.rotation_center_tomopy_value.text()))
            else:
                return self.parent.ui.rotation_center_user_value.value()
        except ValueError:
            return np.nan
