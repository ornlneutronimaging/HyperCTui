#!/usr/bin/env python
"""
Module for handling status message configurations and display in the application.
Provides styling and display functionality for different types of status messages.
"""

from typing import Any, Optional

from qtpy.QtGui import QGuiApplication
from qtpy.QtWidgets import QApplication


class StatusMessageStatus:
    """
    Class containing stylesheet configurations for different status message types.

    Attributes:
        ready (str): Stylesheet for ready status messages (green text).
        working (str): Stylesheet for working/progress status messages (blue text).
        error (str): Stylesheet for error status messages (bold red text).
        warning (str): Stylesheet for warning status messages (red text).
    """

    ready: str = "QStatusBar{padding-left:8px;background:rgba(236,236,236,75);color:green;font-weight:normal;}"
    working: str = "QStatusBar{padding-left:8px;background:rgba(105,105,105,75);color:blue;font-weight:normal;}"
    error: str = "QStatusBar{padding-left:8px;background:rgba(236, 236, 236, 75);color:red;font-weight:bold;}"
    warning: str = "QStatusBar{padding-left:8px;background:rgba(236,236,236,75);color:red;font-weight:normal;}"


def show_status_message(
    parent: Any = None, message: str = "", status: str = StatusMessageStatus.ready, duration_s: Optional[float] = None
) -> None:
    """
    Display a message in the status bar with specified styling.

    Args:
        parent: The parent widget containing the UI with statusbar.
        message: The message to be displayed in the status bar.
        status: The style to apply to the status message (from StatusMessageStatus).
        duration_s: Duration in seconds to show the message. If None, shows until replaced.

    Returns:
        None

    Note:
        This function processes events to ensure the UI updates immediately after
        setting the status message.
    """
    parent.ui.statusbar.setStyleSheet(status)
    if duration_s:
        parent.ui.statusbar.showMessage(message, duration_s * 1000)
    else:
        parent.ui.statusbar.showMessage(message)
    QGuiApplication.processEvents()
    parent.ui.repaint()
    QApplication.processEvents()
