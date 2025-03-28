"""
Pre-processing monitor module.

This module provides status tracking and color coding for monitoring
pre-processing tasks in the HyperCTui application.
"""

from typing import Final

from qtpy import QtGui


class DataStatus:
    """
    Data processing status constants.

    This class defines string constants representing various states
    of data processing tasks.

    Attributes
    ----------
    ready : str
        Status indicating data is ready for processing.
    in_progress : str
        Status indicating processing is currently underway.
    failed : str
        Status indicating processing has failed.
    in_queue : str
        Status indicating task is waiting in queue.
    done : str
        Status indicating processing is complete.
    """

    ready: Final[str] = "Ready"
    in_progress: Final[str] = "In progress ..."
    failed: Final[str] = "Failed!"
    in_queue: Final[str] = "In queue"
    done: Final[str] = "Done"


class ColorDataStatus:
    """
    Color coding constants for data processing status.

    This class defines string constants representing colors that correspond
    to various data processing states for UI elements.

    Attributes
    ----------
    ready : str
        Color for ready status.
    ready_button : str
        Color for ready button state.
    in_progress : str
        Color for in-progress status.
    failed : str
        Color for failed status.
    in_queue : str
        Color for queued status.
    """

    ready: Final[str] = "green"
    ready_button: Final[str] = "light green"
    in_progress: Final[str] = "grey"
    failed: Final[str] = "red"
    in_queue: Final[str] = "cyan"


# QColor constants for status representation in the UI
READY: Final[QtGui.QColor] = QtGui.QColor(0, 255, 0)  # Green
IN_PROGRESS: Final[QtGui.QColor] = QtGui.QColor(155, 155, 155)  # Grey
FAILED: Final[QtGui.QColor] = QtGui.QColor(255, 0, 0)  # Red
IN_QUEUE: Final[QtGui.QColor] = QtGui.QColor(0, 255, 255)  # Cyan
