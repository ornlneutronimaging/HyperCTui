#!/usr/bin/env python
"""
Module for handling rotation center operations in HyperCTui.

This module provides functionality for manipulating and displaying
rotation center images for CT reconstruction.
"""

from typing import Any, Optional

import numpy as np


class RotationCenter:
    """
    Class for managing rotation center operations.

    This class handles the initialization and processing of
    rotation center images based on cropped input data.

    Parameters
    ----------
    parent : Any, optional
        Parent object that contains UI elements and image data.
    """

    def __init__(self, parent: Optional[Any] = None) -> None:
        self.parent = parent

    def initialize(self) -> None:
        """
        Initialize rotation center image view.

        Clears the current view, extracts crop dimensions from UI elements,
        creates a cropped copy of the live image, and displays it in the
        rotation center image view with the appropriate orientation.

        Returns
        -------
        None
        """
        self.parent.rotation_center_image_view.clear()

        left = int(self.parent.ui.crop_left_label_value.text())
        right = int(self.parent.ui.crop_right_label_value.text())

        self.parent.rotation_center_live_image = self.parent.crop_live_image[:, left : right + 1].copy()
        self.parent.rotation_center_image_view.setImage(np.transpose(self.parent.rotation_center_live_image))
