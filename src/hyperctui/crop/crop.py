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
from astropy.io import fits
from qtpy import QtGui

from hyperctui.session import SessionKeys
from hyperctui.utilities.exceptions import CropError
from hyperctui.utilities.file_utilities import get_list_img_files_from_top_folders
from hyperctui.utilities.widgets import Widgets as UtilityWidgets


def _auto_gamma_filter(image: np.ndarray, raw_dtype) -> np.ndarray:
    """Replicate NeuNorm 1.x's automatic gamma filtering for behavior parity.

    For integer raw data, pixels strictly above ``iinfo(raw_dtype).max - 5``
    are treated as gamma hits and replaced by the mean of their 8 neighbors
    (zero-padded at the borders), computed on the unfiltered image — the
    exact semantics of NeuNorm 1.x's ``_auto_gamma_filtering`` (3x3 ones
    kernel with zero center, ``convolve(..., mode="constant")``). Float raw
    data is returned unchanged, as in 1.x. Same implementation as
    NeutronImagingScripts' ``detector_correction._auto_gamma_filter``.

    ``image`` must already be the float32 working copy.
    """
    if not np.issubdtype(np.dtype(raw_dtype), np.integer):
        return image
    threshold = np.iinfo(raw_dtype).max - 5
    gamma = image > threshold
    if not gamma.any():
        return image

    padded = np.pad(image, 1, mode="constant", constant_values=0.0)
    neighbor_mean = (
        padded[:-2, :-2]
        + padded[:-2, 1:-1]
        + padded[:-2, 2:]
        + padded[1:-1, :-2]
        + padded[1:-1, 2:]
        + padded[2:, :-2]
        + padded[2:, 1:-1]
        + padded[2:, 2:]
    ) / 8.0
    filtered = image.copy()
    filtered[gamma] = neighbor_mean[gamma]
    return filtered


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
        # direct astropy I/O (NeuNorm removed, issue #175). Contract pinned
        # by tests/unit/hyperctui/crop/test_load_projections.py: iterate the
        # list exactly as given (0/180 identity is positional), squeeze
        # singleton-3D HDUs, replicate the 1.x auto gamma filter, and
        # normalize to native float32 (1.x passed float FITS through as
        # big-endian — a deliberate, value-preserving change)
        images = []
        for _file in list_summed_img:
            with fits.open(_file, ignore_missing_end=True) as hdulist:
                raw = hdulist[0].data
                _image = np.squeeze(np.asarray(raw, dtype=np.float32))
                raw_dtype = raw.dtype
            _image = _auto_gamma_filter(_image, raw_dtype)
            if images and _image.shape != images[0].shape:
                # 1.x raised from inside NeuNorm on shape mismatch; surface
                # it through the documented CropError channel instead
                raise CropError(f"ERROR! shape of {_file} does not match the other projections")
            images.append(_image)

        # the 0/180-degree assignment below is positional, so anything other
        # than exactly two loaded projections means the session list is
        # incomplete or corrupted (e.g. a projection folder without Run_* is
        # silently skipped upstream) — fail loudly instead of mis-assigning
        if len(images) != 2:
            raise CropError(
                f"ERROR! expected exactly 2 projections (0 and 180 degrees) "
                f"but loaded {len(images)} *_SummedImg.fits from {list_projections}"
            )

        self.mean_image = np.mean(images, axis=0)
        [height, width] = np.shape(self.mean_image)
        self.parent.image_size = {"height": height, "width": width}
        self.parent.image_0_degree = images[0]
        self.parent.image_180_degree = images[1]
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

        # tuple assignment: the previous sequential min/max overwrote left
        # before computing right, collapsing inverted inputs to zero width
        left, right = int(min(left, right)), int(max(left, right))
        left = max(0, left)
        right = min(width - 1, right)

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
