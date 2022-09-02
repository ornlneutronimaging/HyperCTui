from qtpy.QtWidgets import QMainWindow, QApplication
import sys
import os
import logging
import versioneer

from . import load_ui

from .log.log_launcher import LogLauncher
from .utilities.get import Get
from .utilities.config_handler import ConfigHandler
from .session.load_previous_session_launcher import LoadPreviousSessionLauncher
from .session.session_handler import SessionHandler

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

        self._loading_config()
        self._loading_previous_session_automatically()

    def _loading_config(self):
        o_config = ConfigHandler(parent=self)
        o_config.load()

    def _loading_previous_session_automatically(self):
        o_get = Get(parent=self)
        full_config_file_name = o_get.get_automatic_config_file_name()
        if os.path.exists(full_config_file_name):
            load_session_ui = LoadPreviousSessionLauncher(parent=self)
            load_session_ui.show()

    # menu events
    def menu_log_clicked(self):
        LogLauncher(parent=self)

    def load_session_clicked(self):
        o_session = SessionHandler(parent=self)
        o_session.load_from_file()
        o_session.load_to_ui()

    def save_session_clicked(self):
        o_session = SessionHandler(parent=self)
        o_session.save_from_ui()
        o_session.save_to_file()

    def full_reset_clicked(self):
        pass
        # o_event = EventHandler(parent=self)
        # o_event.full_reset_clicked()

    # widgets events

    # leaving ui
    def closeEvent(self, c):
        o_session = SessionHandler(parent=self)
        o_session.save_from_ui()
        o_session.automatic_save()
        logging.info(" #### Leaving ASUI ####")
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
