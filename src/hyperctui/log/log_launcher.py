#!/usr/bin/env python
"""
Log management module for HyperCTui application.

This module provides log viewing, management, and handling capabilities
through the LogLauncher, Log and LogHandler classes.
"""

import os
from typing import Any, Optional

from loguru import logger
from qtpy import QtGui
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QMainWindow

from hyperctui import load_ui, refresh_image
from hyperctui.utilities.file_utilities import read_ascii, write_ascii
from hyperctui.utilities.get import Get


class LogLauncher:
    """
    Launcher for the Log window.

    This class manages the creation or activation of the log window.

    Parameters
    ----------
    parent : Any, optional
        Parent object that owns the log launcher.
    """

    def __init__(self, parent: Optional[Any] = None) -> None:
        """
        Initialize the LogLauncher.

        Parameters
        ----------
        parent : Any, optional
            Parent object that owns the log launcher.
        """
        self.parent = parent

        if self.parent.log_id is None:
            log_id = Log(parent=self.parent)
            log_id.show()
            self.parent.log_id = log_id
        else:
            self.parent.log_id.activateWindow()
            self.parent.log_id.setFocus()


class Log(QMainWindow):
    """
    Log window that displays log file contents.

    This class provides a UI window for viewing and managing log files.

    Parameters
    ----------
    parent : Any, optional
        Parent object that owns the log window.
    """

    def __init__(self, parent: Optional[Any] = None) -> None:
        """
        Initialize the Log window.

        Parameters
        ----------
        parent : Any, optional
            Parent object that owns the log window.
        """
        self.parent = parent
        QMainWindow.__init__(self, parent=parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), os.path.join("ui", "log.ui"))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Log")
        self.ui.log_text.setReadOnly(True)

        refresh_icon = QIcon(refresh_image)
        self.ui.refresh_pushButton.setIcon(refresh_icon)

        o_get = Get(parent=self.parent)
        self.log_file_name = o_get.get_log_file_name()
        self.loading_logging_file()

        # jump to end of file
        self.ui.log_text.moveCursor(QtGui.QTextCursor.End)

    def closeEvent(self, c: QtGui.QCloseEvent) -> None:
        """
        Handle the window close event.

        Parameters
        ----------
        c : QtGui.QCloseEvent
            Close event object.
        """
        self.parent.log_id = None

    def loading_logging_file(self) -> None:
        """
        Load and display the content of the log file.

        Reads the log file content and displays it in the text area.
        If the file is not found, displays an empty text area.
        """
        try:
            log_text = read_ascii(self.log_file_name)
            self.ui.log_text.setPlainText(log_text)
            self.ui.log_text.moveCursor(QtGui.QTextCursor.End)
        except FileNotFoundError:
            self.ui.log_text.setPlainText("")

    def clear_clicked(self) -> None:
        """
        Clear the log file content.

        Clears the content of the log file and updates the display.
        Logs an information message about the clearing action.
        """
        if os.path.exists(self.log_file_name):
            write_ascii(text="", filename=self.log_file_name)
            logger.info("log file has been cleared by user")
        self.loading_logging_file()


class LogHandler:
    """
    Handler for log file operations.

    This class provides methods to manage log file size and content.

    Parameters
    ----------
    parent : Any, optional
        Parent object that owns the log handler.
    log_file_name : str, optional
        Path to the log file to be handled.
    """

    def __init__(self, parent: Optional[Any] = None, log_file_name: str = "") -> None:
        """
        Initialize the LogHandler.

        Parameters
        ----------
        parent : Any, optional
            Parent object that owns the log handler.
        log_file_name : str, optional
            Path to the log file to be handled.
        """
        self.parent = parent
        self.log_file_name = log_file_name

    def cut_log_size_if_bigger_than_buffer(self) -> None:
        """
        Truncate the log file if it exceeds the buffer size.

        Checks the current size of the log file and truncates it to match
        the buffer size limit if it exceeds that limit. Keeps the most
        recent log entries.

        Note: This method is deprecated with loguru as it handles rotation automatically.
        """
        # This functionality is now handled by loguru's rotation capabilities
        # The method is kept for backward compatibility
        logger.debug("Log rotation is now handled automatically by loguru")

        # Legacy fallback in case the method is still called:
        log_buffer_size = self.parent.log_buffer_size
        # check current size of log file
        log_text = read_ascii(self.log_file_name)
        log_text_split_by_cr = log_text.split("\n")
        log_file_size = len(log_text_split_by_cr)
        if log_file_size <= log_buffer_size:
            return
        else:
            new_log_text = log_text_split_by_cr[-log_buffer_size:]
            new_log_text = "\n".join(new_log_text)
            write_ascii(text=new_log_text, filename=self.log_file_name)
            logger.info("log file has been truncated to fit buffer size limit")
