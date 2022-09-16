from qtpy.QtWidgets import QMainWindow, QApplication
import sys
import os
import logging
from qtpy.QtGui import QIcon

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

from . import UI_TITLE, TabNames, tab2_icon, tab3_icon, tab4_icon

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

	tab2 = None  # handle to tab #2 - cropoing
	tab3 = None  # handle to tab #3 - rotation center
	tab4 = None  # handle to tab #4 - options (with advanced)
	all_tabs_visible = True

	def __init__(self, parent=None):

		super(ASUI, self).__init__(parent)

		ui_full_path = os.path.join(os.path.dirname(__file__),
		                            os.path.join('ui',
		                                         'main_application.ui'))

		self.ui = load_ui(ui_full_path, baseinstance=self)

		o_gui = GuiInitialization(parent=self)
		o_gui.all()

		self._loading_config()
		self._loading_previous_session_automatically()
		self.ob_tab_changed()

		self.set_window_title()
		self.inform_of_output_location()

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

	def list_obs_selection_changed(self):
		o_event = EventHandler(parent=self)
		o_event.check_start_acquisition_button()

	def ob_proton_charge_changed(self, proton_charge):
		self.ui.projections_p_charge_label.setText(str(proton_charge))

	# step - setup projections
	def run_title_changed(self, run_title):
		o_event = Step2EventHandler(parent=self)
		o_event.run_title_changed(run_title=run_title)
		self.inform_of_output_location()
		o_event = EventHandler(parent=self)
		o_event.check_start_acquisition_button()

	def start_acquisition_clicked(self):
		self.ui.tabWidget.insertTab(2, self.tab2, QIcon(tab2_icon), TabNames.tab2)
		self.ui.tabWidget.insertTab(3, self.tab3, QIcon(tab3_icon), TabNames.tab3)
		self.ui.tabWidget.insertTab(4, self.tab4, QIcon(tab4_icon), TabNames.tab4)
		self.all_tabs_visible = True

	# leaving ui
	def closeEvent(self, c):
		o_session = SessionHandler(parent=self)
		o_session.save_from_ui()
		o_session.automatic_save()
		logging.info(" #### Leaving ASUI ####")
		self.close()

	def set_window_title(self):
		instrument = self.session_dict[SessionKeys.instrument]
		ipts = self.session_dict[SessionKeys.ipts_selected]
		title = f"{UI_TITLE} - instrument:{instrument} - IPTS:{ipts}"
		self.ui.setWindowTitle(title)

	def inform_of_output_location(self):
		instrument = self.session_dict[SessionKeys.instrument]
		ipts = self.session_dict[SessionKeys.ipts_selected]
		title = self.ui.run_title_formatted_label.text()

		if ipts is None:
			output_location = "N/A"
		elif title == "":
			output_location = "N/A"
		else:
			output_location = os.sep.join([self.homepath,
										   instrument,
										   ipts,
										   "shared",
										   "autoreduce",
										   "mcp",
										   title])
		self.ui.projections_output_location_label.setText(output_location)


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
