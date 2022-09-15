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
from .session import SessionKeys
from .event_handler import EventHandler
from .initialization.gui_initialization import GuiInitialization

from .setup_ob.event_handler import EventHandler as Step1EventHandler

from .setup_projections.event_handler import EventHandler as Step2EventHandler

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

	clicked_create_ob = False

	session_dict = {SessionKeys.config_version: None,
	                SessionKeys.instrument: 'SNAP',
	                SessionKeys.ipts_selected: None,
	                SessionKeys.ipts_index_selected: 0,
	                SessionKeys.number_of_obs: 5}

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
		self.ob_tab_changed()

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

	# menu events
	def new_session_clicked(self):
		o_event = EventHandler(parent=self)
		o_event.new_session()

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

	# step - ob
	def ob_tab_changed(self):
		o_event = EventHandler(parent=self)
		o_event.check_start_acquisition_button()

	def step1_check_state_of_ob_measured_clicked(self):
		o_event = Step1EventHandler(parent=self)
		o_event.check_state_of_ob_measured()

	def step1_browse_obs_clicked(self):
		o_event = Step1EventHandler(parent=self)
		o_event.browse_obs()

	def step1_list_obs_selection_changed(self):
		o_event = EventHandler(parent=self)
		o_event.check_state_of_main_tabs()

	# step - setup projections
	def run_title_changed(self, run_title):
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
