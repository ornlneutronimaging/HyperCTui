from qtpy.QtWidgets import QMainWindow
import sys
import os
import logging
from qtpy.QtGui import QIcon

from . import load_ui
from . import refresh_large_image


class Monitor(QMainWindow):

    def __init__(self, parent=None):
        super(Monitor, self).__init__(parent)
        self.parent = parent

        ui_full_path = os.path.join(os.path.dirname(__file__),
                                    os.path.join('ui',
                                                 'monitor.ui'))

        self.ui = load_ui(ui_full_path, baseinstance=self)

        refresh_icon = QIcon(refresh_large_image)
        self.ui.refresh_pushButton.setIcon(refresh_icon)

        self.initialization()

    def initialization(self):
        """
        this is where we need to figure out the list of NeXus files already listed
        and how many we are expecting
        """
        nbr_ob_expected = self.parent.number_of_files_requested['ob']
        nbr_sample_expected = self.parent.number_of_files_requested['sample']
        homepath = self.parent.homepath
        print(f"homepath: {homepath}")

    def refresh_button_clicked(self):
        logging.info("Checking for new data reduced files!")
        print("refresh clicked")
