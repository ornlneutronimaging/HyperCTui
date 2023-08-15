from qtpy.QtWidgets import QMainWindow
import os
from qtpy.QtGui import QIcon
from qtpy import QtGui
import logging

from hyperctui import load_ui
from hyperctui import refresh_image
from hyperctui.utilities.get import Get
from hyperctui.utilities.file_utilities import read_ascii, write_ascii


class LogLauncher:

    def __init__(self, parent=None):
        self.parent = parent

        if self.parent.log_id is None:
            log_id = Log(parent=self.parent)
            log_id.show()
            self.parent.log_id = log_id
        else:
            self.parent.log_id.activateWindow()
            self.parent.log_id.setFocus()


class Log(QMainWindow):

    def __init__(self, parent=None):
        self.parent = parent
        QMainWindow.__init__(self, parent=parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                    os.path.join('ui',
                                                 'log.ui'))
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

    def closeEvent(self, c):
        self.parent.log_id = None

    def loading_logging_file(self):
        try:
            log_text = read_ascii(self.log_file_name)
            self.ui.log_text.setPlainText(log_text)
            self.ui.log_text.moveCursor(QtGui.QTextCursor.End)
        except FileNotFoundError:
            self.ui.log_text.setPlainText("")

    def clear_clicked(self):
        if os.path.exists(self.log_file_name):
            write_ascii(text="", filename=self.log_file_name)
            logging.info("log file has been cleared by user")
        self.loading_logging_file()


class LogHandler:

    def __init__(self, parent=None, log_file_name=""):
        self.parent = parent
        self.log_file_name = log_file_name

    def cut_log_size_if_bigger_than_buffer(self):
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
            logging.info("log file has been truncated to fit buffer size limit")
