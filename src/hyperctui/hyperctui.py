from qtpy.QtWidgets import QMainWindow, QApplication
import sys
import os
import logging
from collections import OrderedDict

from hyperctui import load_ui, EvaluationRegionKeys
from hyperctui import UI_TITLE

from hyperctui.autonomous_reconstruction.event_handler import EventHandler as AutonomousReconstructionHandler
from hyperctui.crop.crop import Crop
from hyperctui.event_handler import EventHandler
from hyperctui.initialization.gui_initialization import GuiInitialization
from hyperctui.log.log_launcher import LogLauncher, LogHandler
from hyperctui.pre_processing_monitor.monitor import Monitor as PreProcessingMonitor
from hyperctui.rotation_center.rotation_center import RotationCenter
from hyperctui.rotation_center.event_handler import EventHandler as RotationCenterEventHandler
from hyperctui.session.load_previous_session_launcher import LoadPreviousSessionLauncher
from hyperctui.session.session_handler import SessionHandler
from hyperctui.session import SessionKeys
from hyperctui.setup_ob.event_handler import EventHandler as Step1EventHandler
from hyperctui.setup_projections.event_handler import EventHandler as Step2EventHandler
from hyperctui.utilities.get import Get
from hyperctui.utilities.exceptions import CropError, CenterOfRotationError
from hyperctui.utilities.config_handler import ConfigHandler
from hyperctui.utilities.folder_path import FolderPath
from hyperctui.utilities.status_message_config import StatusMessageStatus, show_status_message

# warnings.filterwarnings('ignore')
DEBUG = True

if DEBUG:
    HOME_FOLDER = "/Volumes/JeanHardDrive/SNS/"  # mac at home
    if not os.path.exists(HOME_FOLDER):
        HOME_FOLDER = "/Users/j35/SNS/"              # mac at work
else:
    HOME_FOLDER = "/SNS"


class HyperCTui(QMainWindow):
    log_id = None  # UI id of the logger
    config = None  # config dictionary

    log_buffer_size = 500  #  500 lines

    # path
    homepath = HOME_FOLDER

    # instance of FolderPath class that keep record of all the folders
    # path such as full path to the reduction log for example.
    folder_path = None

    # ui id
    monitor_ui = None

    clicked_create_ob = False

    session_dict = {SessionKeys.config_version     : None,
                    SessionKeys.instrument         : 'SNAP',
                    SessionKeys.ipts_selected      : None,
                    SessionKeys.ipts_index_selected: 0,
                    SessionKeys.number_of_obs      : 5,
                    SessionKeys.list_ob_folders_requested: None,   # ob acquired so far in this experiment
                    SessionKeys.list_ob_folders_acquired_so_far: None,
                    SessionKeys.list_ob_folders_initially_there: None,
                    SessionKeys.list_projections: None,
                    SessionKeys.list_projections_folders_initially_there: None,
                    SessionKeys.list_projections_folders_acquired_so_far: None,
                    SessionKeys.list_recon_folders_initially_there: None,
                    SessionKeys.started_acquisition: False,
                    SessionKeys.obs_have_been_moved_already: False,
                    SessionKeys.tof_roi_region: {'x0': 5,
                                                 'y0': 5,
                                                 'x1': 200,
                                                 'y1': 200},
                    SessionKeys.all_tabs_visible: False,
                    SessionKeys.full_path_to_projections: {SessionKeys.image_0_degree: None,
                                                           SessionKeys.image_180_degree: None}
                    }

    tab2 = None  # handle to tab #2 - cropping
    tab3 = None  # handle to tab #3 - rotation center
    tab4 = None  # handle to tab #4 - options (with advanced)
    all_tabs_visible = True
    current_tab_index = 0

    number_of_files_requested = {'ob': None,
                                 'sample': None}

    # step1 - setup ob tab
    list_obs_selected = None

    # crop
    crop_live_image = None
    crop_roi_id = None

    # rotation center
    rotation_center_live_image = None
    rotation_center_id = None
    center_of_rotation_item = None
    rotation_center_image_view = None
    image_0_degree = None
    image_180_degree = None
    image_size = {'height': None,
                  'width': None}

    # autonomous reconstruction

    # angles
    golden_ratio_angles = None

    # evaluation regions
    evaluation_regions = OrderedDict()
    evaluation_regions[0] = {EvaluationRegionKeys.state: True,
                             EvaluationRegionKeys.name: 'Region 1',
                             EvaluationRegionKeys.from_value: 20,
                             EvaluationRegionKeys.to_value: 30,
                             EvaluationRegionKeys.id: None,
                             EvaluationRegionKeys.label_id: None,
                             }
    evaluation_regions[1] = {EvaluationRegionKeys.state: True,
                             EvaluationRegionKeys.name: 'Region 2',
                             EvaluationRegionKeys.from_value: 50,
                             EvaluationRegionKeys.to_value: 60,
                             EvaluationRegionKeys.id: None,
                             EvaluationRegionKeys.label_id: None,
                             }
    evaluation_regions[2] = {EvaluationRegionKeys.state: True,
                             EvaluationRegionKeys.name: 'Region 3',
                             EvaluationRegionKeys.from_value: 200,
                             EvaluationRegionKeys.to_value: 230,
                             EvaluationRegionKeys.id: None,
                             EvaluationRegionKeys.label_id: None,
                             }
    evaluation_regions[3] = {EvaluationRegionKeys.state: True,
                             EvaluationRegionKeys.name: 'Region 4',
                             EvaluationRegionKeys.from_value: 240,
                             EvaluationRegionKeys.to_value: 300,
                             EvaluationRegionKeys.id: None,
                             EvaluationRegionKeys.label_id: None,
                             }
    evaluation_regions[4] = {EvaluationRegionKeys.state: True,
                             EvaluationRegionKeys.name: 'Region 5',
                             EvaluationRegionKeys.from_value: 350,
                             EvaluationRegionKeys.to_value: 400,
                             EvaluationRegionKeys.id: None,
                             EvaluationRegionKeys.label_id: None,
                             }
    # this will be a copy of evaluation regions used when user exit the view without using OK button
    backup_evaluation_regions = None

    # tof selection regions
    tof_regions = OrderedDict()
    tof_regions[0] = {EvaluationRegionKeys.state: True,
                      EvaluationRegionKeys.name: 'TOF 1',
                      EvaluationRegionKeys.from_value: 0.9,
                      EvaluationRegionKeys.to_value: 1.1,
                      EvaluationRegionKeys.id: None,
                      EvaluationRegionKeys.label_id: None,
                      EvaluationRegionKeys.from_index: None,
                      EvaluationRegionKeys.to_index: None,
                      }
    tof_regions[1] = {EvaluationRegionKeys.state: True,
                      EvaluationRegionKeys.name: 'TOF 2',
                      EvaluationRegionKeys.from_value: 1.9,
                      EvaluationRegionKeys.to_value: 2.1,
                      EvaluationRegionKeys.id: None,
                      EvaluationRegionKeys.label_id: None,
                      EvaluationRegionKeys.from_index: None,
                      EvaluationRegionKeys.to_index: None,
                      }
    tof_regions[2] = {EvaluationRegionKeys.state: False,
                      EvaluationRegionKeys.name: 'TOF 3',
                      EvaluationRegionKeys.from_value: 2.9,
                      EvaluationRegionKeys.to_value: 3.1,
                      EvaluationRegionKeys.id: None,
                      EvaluationRegionKeys.label_id: None,
                      EvaluationRegionKeys.from_index: None,
                      EvaluationRegionKeys.to_index: None,
                      }

    # this will be a copy of evaluation regions used when user exit the view without using OK button
    backup_tof_regions = None

    # dictionary that will store the 3D images (used in the TOF region selection)
    image_data = {SessionKeys.image_0_degree: None,
                  SessionKeys.image_180_degree: None}

    # list of files (err, status, metadata) associated to each row of projections
    dict_projection_log_err_metadata = {}

    def __init__(self, parent=None):

        super(HyperCTui, self).__init__(parent)

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
        self.check_log_file_size()

    def _loading_config(self):
        o_config = ConfigHandler(parent=self)
        o_config.load()

    def check_log_file_size(self):
        o_get = Get(parent=self)
        log_file_name = o_get.get_log_file_name()
        o_handler = LogHandler(parent=self,
                               log_file_name=log_file_name)
        o_handler.cut_log_size_if_bigger_than_buffer()

    def _loading_previous_session_automatically(self):
        o_get = Get(parent=self)
        full_config_file_name = o_get.get_automatic_config_file_name()
        if os.path.exists(full_config_file_name):
            load_session_ui = LoadPreviousSessionLauncher(parent=self)
            load_session_ui.show()
        else:
            self.new_session_clicked()

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
        self.folder_path = FolderPath(parent=self)
        self.folder_path.update()

    def save_session_clicked(self):
        o_session = SessionHandler(parent=self)
        o_session.save_from_ui()
        o_session.save_to_file()

    def full_reset_clicked(self):
        o_event = EventHandler(parent=self)
        o_event.full_reset_clicked()

    def launch_pre_processing_monitor_view(self):
        if self.session_dict[SessionKeys.process_in_progress]:
            if self.monitor_ui:
                self.monitor_ui.showMinimized()
                self.monitor_ui.showNormal()

            else:
                o_monitor = PreProcessingMonitor(parent=self)
                o_monitor.show()
                self.monitor_ui = o_monitor
            self.ui.checking_status_acquisition_pushButton.setEnabled(False)

    def action_step1_clicked(self):
        self.ui.tabWidget.setCurrentIndex(0)

    def action_step2_clicked(self):
        self.ui.tabWidget.setCurrentIndex(1)

    def action_step3_clicked(self):
        self.ui.tabWidget.setCurrentIndex(2)

    def action_step4_clicked(self):
        self.ui.tabWidget.setCurrentIndex(3)

    def action_step5_clicked(self):
        self.ui.tabWidget.setCurrentIndex(4)

    def action_settings_clicked(self):
        if self.ui.tabWidget.count() > 3:
            self.ui.tabWidget.setCurrentIndex(5)
        else:
            self.ui.tabWidget.setCurrentIndex(2)

    def check_state_of_steps_menu_button(self):
        o_event = EventHandler(parent=self)
        o_event.check_state_of_steps_menu_button()

    # main tab
    def main_tab_changed(self, new_tab_index):
        o_event = EventHandler(parent=self)
        o_event.main_tab_changed(new_tab_index=new_tab_index)

    # step - ob
    def ob_tab_changed(self):
        o_event = EventHandler(parent=self)
        o_event.ob_tab_changed()
        o_event.check_start_acquisition_button()

    def step1_check_state_of_ob_measured_clicked(self):
        o_event = Step1EventHandler(parent=self)
        o_event.check_state_of_ob_measured()

    def step1_browse_obs_clicked(self):
        o_event = Step1EventHandler(parent=self)
        o_event.browse_obs()

    def list_obs_selection_changed(self):
        o_event = Step1EventHandler(parent=self)
        o_event.update_state_of_rows()

        o_event = EventHandler(parent=self)
        o_event.check_start_acquisition_button()

    def refresh_list_of_obs_button_clicked(self):
        o_event = Step1EventHandler(parent=self)
        o_event.save_list_of_obs_selected()
        o_event.update_list_of_obs()
        o_event.reselect_the_obs_previously_selected()

    def ob_proton_charge_changed(self, proton_charge):
        self.ui.projections_p_charge_label.setText(str(proton_charge))

    def number_of_obs_changed(self, value):
        o_event = EventHandler(parent=self)
        o_event.check_start_acquisition_button()

    # step - setup projections
    def run_title_changed(self, run_title):
        if run_title == "":
            self.ui.run_title_groupBox.setEnabled(False)
        else:
            self.ui.run_title_groupBox.setEnabled(True)
        o_event = Step2EventHandler(parent=self)
        o_event.run_title_changed(run_title=run_title, checking_if_file_exists=True)
        self.inform_of_output_location()
        o_event = EventHandler(parent=self)
        o_event.check_start_acquisition_button()

    def number_of_projections_changed(self, value):
        o_event = EventHandler(parent=self)
        o_event.check_start_acquisition_button()

    def start_acquisition_clicked(self):
        self.session_dict[SessionKeys.process_in_progress] = True
        self.session_dict[SessionKeys.started_acquisition] = True
        o_event = EventHandler(parent=self)
        o_event.start_acquisition()
        o_event.freeze_number_ob_sample_requested()
        self.launch_pre_processing_monitor_view()
        self.ui.start_acquisition_pushButton.setEnabled(False)

    def checking_status_acquisition_button_clicked(self):
        self.launch_pre_processing_monitor_view()

    # step crop
    def initialize_crop(self):
        try:
            o_crop = Crop(parent=self)
            o_crop.initialize()
        except CropError:
            show_status_message(parent=self,
                                message="Initialization of crop failed! check log!",
                                duration_s=10,
                                status=StatusMessageStatus.error)

    def crop_top_changed(self, value):
        self.crop_changed()

    def crop_top_edit_finished(self):
        self.crop_changed()

    def crop_bottom_changed(self, value):
        self.crop_changed()

    def crop_bottom_edit_finished(self):
        self.crop_changed()

    def crop_left_changed(self, value):
        self.crop_changed()

    def crop_left_edit_finished(self):
        self.crop_changed()

    def crop_right_changed(self, value):
        self.crop_changed()

    def crop_right_edit_finished(self):
        self.crop_changed()

    def crop_changed(self):
        o_crop = Crop(parent=self)
        o_crop.update_roi()

    def crop_roi_manually_moved(self):
        o_crop = Crop(parent=self)
        o_crop.roi_manually_moved()

    # center of rotation
    def initialize_center_of_rotation(self):
        try:
            o_rot = RotationCenter(parent=self)
            o_rot.initialize()
        except CenterOfRotationError:
            show_status_message(parent=self,
                                message="Initialization of center of rotation failed! check log!",
                                duration_s=10,
                                status=StatusMessageStatus.error)

    def rotation_center_tomopy_clicked(self, button_state):
        self.ui.rotation_center_user_defined_radioButton.blockSignals(True)
        self.ui.rotation_center_user_defined_radioButton.setChecked(not button_state)
        o_event = RotationCenterEventHandler(parent=self)
        o_event.radio_button_changed(is_tomopy_checked=button_state)
        self.ui.rotation_center_user_defined_radioButton.blockSignals(False)

    def rotation_center_user_clicked(self, button_state):
        self.ui.rotation_center_tomopy_radioButton.blockSignals(True)
        self.ui.rotation_center_tomopy_radioButton.setChecked(not button_state)
        o_event = RotationCenterEventHandler(parent=self)
        o_event.radio_button_changed(is_tomopy_checked=not button_state)
        self.ui.rotation_center_tomopy_radioButton.blockSignals(False)

    def rotation_center_tomopy_calculate_clicked(self):
        o_event = RotationCenterEventHandler(parent=self)
        o_event.calculate_using_tomopy()

    def rotation_center_user_value_changed(self, value):
        o_event = RotationCenterEventHandler(parent=self)
        o_event.radio_button_changed(is_tomopy_checked=False)

    # autonomous reconstruction

    def update_autonomous_widgets(self):
        o_event = AutonomousReconstructionHandler(parent=self)
        o_event.update_widgets()

    def projections_angles_clicked(self):
        o_event = AutonomousReconstructionHandler(parent=self)
        o_event.projections_angles_radioButton_changed()

    def projections_fixed_help_clicked(self):
        o_event = AutonomousReconstructionHandler(parent=self)
        o_event.projections_fixed_help_clicked()

    def projections_angles_automatic_button_clicked(self):
        o_event = AutonomousReconstructionHandler(parent=self)
        o_event.projections_angles_automatic_button_clicked()

    def evaluation_frequency_help_clicked(self):
        o_event = AutonomousReconstructionHandler(parent=self)
        o_event.evaluation_frequency_help_clicked()

    def tof_region_selection_button_clicked(self):
        o_event = AutonomousReconstructionHandler(parent=self)
        o_event.tof_region_selection_button_clicked()

    def autonomous_evaluation_frequency_changed(self, new_value):
        o_event = AutonomousReconstructionHandler(parent=self)
        o_event.evaluation_frequency_changed()

    def autonomous_start_acquisition_clicked(self):
        o_event = AutonomousReconstructionHandler(parent=self)
        o_event.start_acquisition()

    def autonomous_reconstruction_stop_process_button_clicked(self):
        o_event = AutonomousReconstructionHandler(parent=self)
        o_event.stop_acquisition()

    def autonomous_refresh_table_clicked(self):
        o_event = AutonomousReconstructionHandler(parent=self)
        o_event.refresh_table_clicked()

    def autonomous_checking_reconstruction_clicked(self):
        o_event = AutonomousReconstructionHandler(parent=self)
        o_event.checking_reconstruction_clicked()

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

        if (ipts is None) or (ipts == ""):
            output_location = "N/A"
            ob_output_location = "N/A"
            final_ob_output_location = "N/A"

        elif title == "":
            output_location = "'title'"
            ob_output_location = "'title'"
            final_ob_output_location = "'title'"

        else:
            if title == "N/A":
                title = "'title'"

            output_location = os.sep.join([self.homepath,
                                           instrument,
                                           ipts,
                                           "shared",
                                           "autoreduce",
                                           "mcp",
                                           ])
            ob_output_location = os.sep.join([self.homepath,
                                              instrument,
                                              ipts,
                                              "shared",
                                              "autoreduce",
                                              "mcp",
                                              ])
            final_ob_output_location = os.sep.join([self.homepath,
                                              instrument,
                                              ipts,
                                              "shared",
                                              "autoreduce",
                                              "mcp",
                                              f"OBs_{title}" + os.path.sep])

        self.ui.projections_output_location_label.setText(os.path.abspath(output_location))
        self.ui.obs_output_location_label.setText(os.path.abspath(ob_output_location))
        self.ui.location_of_ob_created.setText(os.path.abspath(ob_output_location))
        self.ui.final_location_of_ob_created.setText(os.path.abspath(final_ob_output_location))


def main(args):
    app = QApplication(args)
    app.setStyle('Fusion')
    app.aboutToQuit.connect(clean_up)
    app.setApplicationDisplayName("Ai Svmbir UI")
    window = HyperCTui()
    window.show()
    sys.exit(app.exec_())


def clean_up():
    app = QApplication.instance()
    app.closeAllWindows()
