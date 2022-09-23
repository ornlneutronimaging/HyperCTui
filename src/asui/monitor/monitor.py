from qtpy.QtWidgets import QMainWindow
import os
import logging
from qtpy.QtGui import QIcon

from asui import load_ui
from asui import refresh_large_image

from .initialization import Initialization
from ..preview_file.preview_file_launcher import PreviewFileLauncher, PreviewMetadataFileLauncher


class Monitor(QMainWindow):

    # list of files in the reduction log folder to use as a reference
    # any new files will be used
    initial_list_of_reduction_log_files = []

    # dictionary that looks like
    # {0: { 'ob': '<full path to ob>',
    #       'log_file': '<full path to log file>',
    #       'err_file': '<full path to err file>',
    #       'metadata_file': <full path to metadata file>',
    #     },
    #  1: { ... },
    #  ...
    # }
    dict_ob_log_err_metadata = None

    def __init__(self, parent=None):
        super(Monitor, self).__init__(parent)
        self.parent = parent

        ui_full_path = os.path.join(os.path.dirname(__file__),
                                    os.path.join('../ui',
                                                 'monitor.ui'))

        self.ui = load_ui(ui_full_path, baseinstance=self)

        refresh_icon = QIcon(refresh_large_image)
        self.ui.refresh_pushButton.setIcon(refresh_icon)

        o_init = Initialization(parent=self,
                                grand_parent=self.parent)
        o_init.data()
        o_init.ui()

    def preview_log(self, state=0, row=-1, data_type='ob'):
        print(f"preview row:{row}")
        preview_file = PreviewFileLauncher(parent=self,
                                           file_name=None)
        preview_file.show()

    def preview_err(self, state=0, row=-1, data_type='ob'):
        print(f"log row:{row}")

    def preview_summary(self, state=0, row=-1, data_type='ob'):
        file_name = self.dict_ob_log_err_metadata[row]['metadata_file']
        preview_file = PreviewMetadataFileLauncher(parent=self,
                                                   file_name=file_name)
        preview_file.show()

    def refresh_button_clicked(self):
        logging.info("Checking for new data reduced files!")
        print("refresh clicked")

    def closeEvent(self, c):
        self.parent.monitor_ui = None
        self.close()
