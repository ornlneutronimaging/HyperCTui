from qtpy.QtWidgets import QMainWindow, QApplication
import sys
import os
import logging
import versioneer

from . import load_ui

from .log.log_launcher import LogLauncher
from .utilities.get import Get
from .utilities.config_handler import ConfigHandler

#warnings.filterwarnings('ignore')


class ASUI(QMainWindow):

    log_id = None  # UI id of the logger
    config = None  # config dictionary
    homepath = "./"

    def __init__(self, parent=None):

        super(ASUI, self).__init__(parent)

        ui_full_path = os.path.join(os.path.dirname(__file__),
                                    os.path.join('ui',
                                                 'main_application.ui'))

        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Ai Svmbir UI")

        o_config = ConfigHandler(parent=self)
        o_config.load()

        o_get = Get(parent=self)
        log_file_name = o_get.get_log_file_name()
        logging.basicConfig(filename=log_file_name,
                            filemode='a',
                            format='[%(levelname)s] - %(asctime)s - %(message)s',
                            level=logging.INFO)
        logging.info("*** Starting a new session ***")
        logging.info(f" Version: {versioneer.get_version()}")


    # menu events
    def menu_log_clicked(self):
        LogLauncher(parent=self)
        print('here')

    # widgets events

    # leaving ui
    def closeEvent(self, c):
        self.close()


def main(args):
    app = QApplication(args)
    app.setStyle('Fusion')
    app.aboutToQuit.connect(clean_up)
    app.setApplicationDisplayName("Ai Svmbir UI")
    window = ASUI()
    window.show()
    sys.exit(app.exec_())


def clean_up():
    app = QApplication.instance()
    app.closeAllWindows()
