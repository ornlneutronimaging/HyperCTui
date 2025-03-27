#!/usr/bin/env python
"""
Module for handling the cropping functionality in the HyperCTui application.

This module provides tools to load projection images, display them in the UI,
and add movable lines for cropping the images.
"""

import logging
from typing import Any, Optional

import numpy as np
import pyqtgraph as pg
from NeuNorm.normalization import Normalization
from qtpy import QtGui

from hyperctui.session import SessionKeys
from hyperctui.utilities.exceptions import CropError
from hyperctui.utilities.file_utilities import get_list_img_files_from_top_folders
from hyperctui.utilities.widgets import Widgets as UtilityWidgets


class Crop:
    """
    Class for handling the image cropping operations.

    This class is responsible for loading projection images,
    displaying them in the UI, and providing cropping functionality.

    Attributes
    ----------
    list_files : Optional[List[str]]
        List of image files, initialized to None
    parent : Any
        Parent object that holds the UI and session data
    mean_image : np.ndarray
        The mean image created from all projections
    """

    list_files = None

    def __init__(self, parent: Optional[Any] = None):
        """
        Initialize the Crop object.

        Parameters
        ----------
        parent : Any, optional
            Parent object that holds the UI and session data
        """
        self.parent = parent

    def load_projections(self) -> None:
        """
        Load the projection images.

        This method loads the projection images from the session,
        calculates the mean image, and stores the dimensions.

        Raises
        ------
        CropError
            If unable to load the projection images
        """
        logging.info("Loading projections in crop")
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

        self.mean_image = np.mean(o_loader.data["sample"]["data"][:], axis=0)
        [height, width] = np.shape(self.mean_image)
        self.parent.image_size = {"height": height, "width": width}
        self.parent.image_0_degree = o_loader.data["sample"]["data"][0]
        self.parent.image_180_degree = o_loader.data["sample"]["data"][1]
        self.parent.crop_live_image = self.mean_image

    def initialize(self) -> None:
        """
        Initialize the crop UI.

        Loads the projection images, sets up the UI components,
        and initializes the crop region.

        Raises
        ------
        CropError
            If unable to load projection images
        """
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

        default_left = 0 + width / 3
        default_right = width - width / 3

        left = self.parent.session_dict.get(SessionKeys.crop_left, default_left)
        right = self.parent.session_dict.get(SessionKeys.crop_right, default_right)

        left = int(np.min([left, right]))
        right = int(np.max([left, right]))

        self.parent.session_dict[SessionKeys.crop_left] = left
        self.parent.session_dict[SessionKeys.crop_right] = right

        self.parent.ui.crop_left_label_value.setText(str(left))
        self.parent.ui.crop_right_label_value.setText(str(right))

        self.init_roi(left, right)

    def init_roi(self, left: int, right: int) -> None:
        """
        Initialize the Region Of Interest (ROI) with movable lines.

        Sets up the vertical lines for cropping at the specified left and right positions.

        Parameters
        ----------
        left : int
            X-coordinate of the left crop line
        right : int
            X-coordinate of the right crop line
        """
        # if self.parent.crop_roi_id:
        #     self.parent.ui.crop_image_view.removeItem(self.parent.crop_roi_id)

        _color = QtGui.QColor(62, 13, 244)
        _pen = QtGui.QPen()
        _pen.setColor(_color)
        _pen.setWidthF(1)

        self.parent.crop_left_ui = pg.InfiniteLine(left, pen=_pen, angle=90, movable=True)
        self.parent.ui.crop_image_view.addItem(self.parent.crop_left_ui)
        self.parent.crop_left_ui.sigDragged.connect(self.parent.sort_the_crop_values)
        self.parent.crop_left_ui.sigPositionChangeFinished.connect(self.parent.sort_the_crop_values)

        self.parent.crop_right_ui = pg.InfiniteLine(right, pen=_pen, angle=90, movable=True)
        self.parent.ui.crop_image_view.addItem(self.parent.crop_right_ui)
        self.parent.crop_right_ui.sigDragged.connect(self.parent.sort_the_crop_values)
        self.parent.crop_right_ui.sigPositionChangeFinished.connect(self.parent.sort_the_crop_values)

    # def update_roi(self):
    #     left = self.parent.ui.crop_left_spinBox.value()
    #     right = self.parent.ui.crop_right_spinBox.value()
    #
    #     self.init_roi(left, right)

    def roi_manually_moved(self) -> None:
        """
        Handle the manual movement of the ROI.

        This method is a placeholder for future implementation to handle
        when a user manually moves the crop region.
        """
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
