"""
Pre-autonomous monitoring module for HyperCTui.

This module provides status indicators and color representations for
monitoring operations in the HyperCTui application.
"""

from typing import Final

from qtpy import QtGui


class DataStatus:
    """
    Constants representing various statuses of data processing.

    Attributes
    ----------
    ready : str
        Indicates data is ready for processing
    in_progress : str
        Indicates data processing is ongoing
    failed : str
        Indicates data processing has failed
    in_queue : str
        Indicates data is waiting in queue
    done : str
        Indicates data processing is complete
    """

    ready: Final[str] = "Ready"
    in_progress: Final[str] = "In progress ..."
    failed: Final[str] = "Failed!"
    in_queue: Final[str] = "In queue"
    done: Final[str] = "Done"


class ColorDataStatus:
    """
    Color representations for different data statuses.

    Attributes
    ----------
    ready : str
        Color for ready status
    ready_button : str
        Color for ready button elements
    in_progress : str
        Color for in-progress status
    failed : str
        Color for failed status
    in_queue : str
        Color for queued status
    """

    ready: Final[str] = "green"
    ready_button: Final[str] = "light green"
    in_progress: Final[str] = "grey"
    failed: Final[str] = "red"
    in_queue: Final[str] = "cyan"


READY: Final[QtGui.QColor] = QtGui.QColor(0, 255, 0)
IN_PROGRESS: Final[QtGui.QColor] = QtGui.QColor(155, 155, 155)
FAILED: Final[QtGui.QColor] = QtGui.QColor(255, 0, 0)
IN_QUEUE: Final[QtGui.QColor] = QtGui.QColor(0, 255, 255)
