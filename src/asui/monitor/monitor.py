from qtpy.QtWidgets import QMainWindow
import os
import logging
from qtpy.QtGui import QIcon

from asui import load_ui
from asui import refresh_large_image

from .initialization import Initialization


class Monitor(QMainWindow):

    # list of files in the reduction log folder to use as a reference
    # any new files will be used
    initial_list_of_reduction_log_files = []

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

    def preview_err(self, state=0, row=-1, data_type='ob'):
        print(f"log row:{row}")

    def preview_summary(self, state=0, row=-1, data_type='ob'):
        print(f"preview summary json file from row:{row}")

    def refresh_button_clicked(self):
        logging.info("Checking for new data reduced files!")
        print("refresh clicked")

    def closeEvent(self, c):
        self.parent.monitor_ui = None
        self.close()
