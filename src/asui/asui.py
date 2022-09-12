from qtpy.QtWidgets import QMainWindow, QApplication
import sys
import os
import logging

from . import load_ui

from .log.log_launcher import LogLauncher
from .utilities.get import Get
from .utilities.config_handler import ConfigHandler
from .session.load_previous_session_launcher import LoadPreviousSessionLauncher
from .session.session_handler import SessionHandler
from .event_handler import EventHandler
from .initialization.gui_initialization import GuiInitialization

from .step1.event_handler import EventHandler as Step1EventHandler

from .step2.event_handler import EventHandler as Step2EventHandler

# warnings.filterwarnings('ignore')
DEBUG = True

if DEBUG:
    HOME_FOLDER = "/Users/j35/SNS"
else:
    HOME_FOLDER = "/SNS"


class ASUI(QMainWindow):
    log_id = None  # UI id of the logger
    config = None  # config dictionary
    homepath = HOME_FOLDER

    session_dict = {'config version'     : None,
                    'instrument'         : 'SNAP',
                    'ipts selected'      : None,
                    'ipts index selected': 0,
                    'number of obs'      : 5}

    def __init__(self, parent=None):

        super(ASUI, self).__init__(parent)

        ui_full_path = os.path.join(os.path.dirname(__file__),
                                    os.path.join('ui',
                                                 'main_application.ui'))

        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Ai Svmbir UI")

        o_gui = GuiInitialization(parent=self)
        o_gui.all()

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
        else:
            self.initialization_without_any_session_loading()

    def initialization_without_any_session_loading(self):
        self.step1_instrument_changed(None)

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
        o_event = EventHandler(parent=self)
        o_event.full_reset_clicked()

    # step 1
    def step1_instrument_changed(self, instrument):
        o_event = Step1EventHandler(parent=self)
        o_event.instrument_changed(instrument=instrument)

    def set_new_instrument(self, instrument=None):
        o_event = Step1EventHandler(parent=self)
        o_event.set_new_instrument(instrument=instrument)

    def step1_ipts_changed(self, ipts):
        o_event = Step1EventHandler(parent=self)
        o_event.step1_ipts_changed(ipts=ipts)

    def step1_start_acquisition_clicked(self):
        o_event = Step1EventHandler(parent=self)
        o_event.start_acquisition()

    def step1_check_state_of_ob_measured_clicked(self):
        o_event = Step1EventHandler(parent=self)
        o_event.check_state_of_ob_measured()

    def step1_browse_obs_clicked(self):
        o_event = Step1EventHandler(parent=self)
        o_event.browse_obs()

    # step 2
    def step2_run_title_changed(self, run_title):
        o_event = Step2EventHandler(parent=self)
        o_event.run_title_changed(run_title=run_title)

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
