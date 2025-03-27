#!/usr/bin/env python
"""
Custom exceptions for the HyperCTui package.

This module contains exception classes that are used throughout the HyperCTui
application to handle specific error cases related to CT image processing
operations such as cropping and center of rotation calculations.
"""


class CropError(Exception):
    """
    Raised when something went wrong with the crop process.

    Parameters
    ----------
    message : str, optional
        Explanation of the error, by default "Something went wrong during crop"
    """

    def __init__(self, message: str = "Something went wrong during crop") -> None:
        self.message = message
        super().__init__(self.message)


class CenterOfRotationError(Exception):
    """
    Raised when the center of rotation initialization goes wrong.

    Parameters
    ----------
    message : str, optional
        Explanation of the error, by default "Something went wrong during initialization of center of rotation"
    """

    def __init__(self, message: str = "Something went wrong during initialization of center of rotation") -> None:
        self.message = message
        super().__init__(self.message)
