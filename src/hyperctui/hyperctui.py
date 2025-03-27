"""
The main module for HyperCTui application. This module contains the main application window class
and handles all the user interactions with the GUI. It integrates various components like data acquisition,
image processing, rotation center detection, and autonomous reconstruction.
"""

import os
import sys
from collections import OrderedDict
from typing import List, Optional, Union

from loguru import logger
from qtpy.QtGui import QCloseEvent
from qtpy.QtWidgets import QApplication, QMainWindow

from hyperctui import UI_TITLE, EvaluationRegionKeys, load_ui
from hyperctui.autonomous_reconstruction.event_handler import EventHandler as AutonomousReconstructionHandler
from hyperctui.commands_launcher import CommandLauncher
from hyperctui.crop.crop import Crop
from hyperctui.event_handler import EventHandler
from hyperctui.initialization.gui_initialization import GuiInitialization
from hyperctui.log.log_launcher import LogHandler, LogLauncher
from hyperctui.pre_processing_monitor.monitor import Monitor as PreProcessingMonitor
from hyperctui.rotation_center.event_handler import EventHandler as RotationCenterEventHandler
from hyperctui.rotation_center.rotation_center import RotationCenter
from hyperctui.session import DefaultValues, SessionKeys
from hyperctui.session.load_previous_session_launcher import LoadPreviousSessionLauncher
from hyperctui.session.session_handler import SessionHandler
from hyperctui.setup_ob.event_handler import EventHandler as Step1EventHandler
from hyperctui.setup_projections.event_handler import EventHandler as Step2EventHandler
from hyperctui.utilities.config_handler import ConfigHandler
from hyperctui.utilities.exceptions import CenterOfRotationError, CropError
from hyperctui.utilities.folder_path import FolderPath
from hyperctui.utilities.get import Get
from hyperctui.utilities.status_message_config import StatusMessageStatus, show_status_message

# warnings.filterwarnings('ignore')
DEBUG = True

if DEBUG:
    HOME_FOLDER = "/Volumes/JeanHardDrive/"  # mac at home
    if not os.path.exists(HOME_FOLDER):
        HOME_FOLDER = "/Users/j35/"  # mac at work
else:
    HOME_FOLDER = "/"


class HyperCTui(QMainWindow):
    """
    Main application window for HyperCTui.

    This class orchestrates all the components of the HyperCTui application, including setup of open
    beam measurements, projections, crop settings, rotation center detection, and autonomous reconstruction.
    It handles user interactions, session management, and coordinates between different modules.

    Attributes
    ----------
    log_id : Optional[int]
        UI id of the logger
    config : Optional[Dict]
        Config dictionary containing application settings
    reconstruction_config : Optional[Dict]
        Configuration for the reconstruction process
    log_buffer_size : int
        Number of lines to keep in the log buffer
    homepath : str
        Home directory path
    folder_path : Optional[FolderPath]
        Instance to manage folder paths
    monitor_ui : Optional[Any]
        Reference to the pre-processing monitor UI
    clicked_create_ob : bool
        Flag indicating if create OB button was clicked
    session_dict : Dict
        Dictionary storing all session related information
    tab2, tab3, tab4 : Optional[Any]
        Handles to various tabs
    all_tabs_visible : bool
        Flag indicating if all tabs are visible
    current_tab_index : int
        Index of the currently selected tab
    number_of_files_requested : Dict
        Number of requested files for OB and sample
    list_obs_selected : Optional[List]
        List of selected OB files
    evaluation_regions : OrderedDict
        Dictionary of evaluation regions for reconstruction
    tof_regions : OrderedDict
        Dictionary of TOF regions
    image_data : Dict
        Dictionary storing 3D image data
    """

    log_id = None  # UI id of the logger
    config = None  # config dictionary
    reconstruction_config = None  # config of the

    log_buffer_size = 500  #  500 lines

    # path
    homepath = HOME_FOLDER

    # instance of FolderPath class that keep record of all the folders
    # path such as full path to the reduction log for example.
    folder_path = None

    # ui id
    monitor_ui = None

    clicked_create_ob = False

    session_dict = {
        SessionKeys.config_version: None,
        SessionKeys.instrument: DefaultValues.instrument,
        SessionKeys.ipts_selected: None,
        SessionKeys.ipts_index_selected: DefaultValues.ipts_index_selected,
        SessionKeys.number_of_obs: DefaultValues.number_of_obs,
        SessionKeys.list_ob_folders_requested: None,  # ob acquired so far in this experiment
        SessionKeys.list_ob_folders_acquired_so_far: None,
        SessionKeys.list_ob_folders_initially_there: None,
        SessionKeys.list_projections: None,
        SessionKeys.list_projections_folders_initially_there: None,
        SessionKeys.list_projections_folders_acquired_so_far: None,
        SessionKeys.list_recon_folders_initially_there: None,
        SessionKeys.started_acquisition: False,
        SessionKeys.obs_have_been_moved_already: False,
        SessionKeys.tof_roi_region: {"x0": 5, "y0": 5, "x1": 200, "y1": 200},
        SessionKeys.all_tabs_visible: False,
        SessionKeys.full_path_to_projections: {SessionKeys.image_0_degree: None, SessionKeys.image_180_degree: None},
    }

    tab2 = None  # handle to tab #2 - cropping
    tab3 = None  # handle to tab #3 - rotation center
    tab4 = None  # handle to tab #4 - options (with advanced)
    all_tabs_visible = True
    current_tab_index = 0

    number_of_files_requested = {"ob": None, "sample": None}

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
    image_size = {"height": None, "width": None}

    # autonomous reconstruction

    # angles
    golden_ratio_angles = None

    # evaluation regions
    evaluation_regions = OrderedDict()
    evaluation_regions[0] = {
        EvaluationRegionKeys.state: True,
        EvaluationRegionKeys.name: "Region 1",
        EvaluationRegionKeys.from_value: 20,
        EvaluationRegionKeys.to_value: 30,
        EvaluationRegionKeys.id: None,
        EvaluationRegionKeys.label_id: None,
    }
    evaluation_regions[1] = {
        EvaluationRegionKeys.state: True,
        EvaluationRegionKeys.name: "Region 2",
        EvaluationRegionKeys.from_value: 50,
        EvaluationRegionKeys.to_value: 60,
        EvaluationRegionKeys.id: None,
        EvaluationRegionKeys.label_id: None,
    }
    evaluation_regions[2] = {
        EvaluationRegionKeys.state: True,
        EvaluationRegionKeys.name: "Region 3",
        EvaluationRegionKeys.from_value: 200,
        EvaluationRegionKeys.to_value: 230,
        EvaluationRegionKeys.id: None,
        EvaluationRegionKeys.label_id: None,
    }
    evaluation_regions[3] = {
        EvaluationRegionKeys.state: True,
        EvaluationRegionKeys.name: "Region 4",
        EvaluationRegionKeys.from_value: 240,
        EvaluationRegionKeys.to_value: 300,
        EvaluationRegionKeys.id: None,
        EvaluationRegionKeys.label_id: None,
    }
    evaluation_regions[4] = {
        EvaluationRegionKeys.state: True,
        EvaluationRegionKeys.name: "Region 5",
        EvaluationRegionKeys.from_value: 350,
        EvaluationRegionKeys.to_value: 400,
        EvaluationRegionKeys.id: None,
        EvaluationRegionKeys.label_id: None,
    }
    # this will be a copy of evaluation regions used when user exit the view without using OK button
    backup_evaluation_regions = None

    # tof selection regions
    tof_regions = OrderedDict()
    tof_regions[0] = {
        EvaluationRegionKeys.state: True,
        EvaluationRegionKeys.name: "TOF 1",
        EvaluationRegionKeys.from_value: 0.9,
        EvaluationRegionKeys.to_value: 1.1,
        EvaluationRegionKeys.id: None,
        EvaluationRegionKeys.label_id: None,
        EvaluationRegionKeys.from_index: None,
        EvaluationRegionKeys.to_index: None,
    }
    tof_regions[1] = {
        EvaluationRegionKeys.state: True,
        EvaluationRegionKeys.name: "TOF 2",
        EvaluationRegionKeys.from_value: 1.9,
        EvaluationRegionKeys.to_value: 2.1,
        EvaluationRegionKeys.id: None,
        EvaluationRegionKeys.label_id: None,
        EvaluationRegionKeys.from_index: None,
        EvaluationRegionKeys.to_index: None,
    }
    tof_regions[2] = {
        EvaluationRegionKeys.state: False,
        EvaluationRegionKeys.name: "TOF 3",
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
    image_data = {SessionKeys.image_0_degree: None, SessionKeys.image_180_degree: None}

    # list of files (err, status, metadata) associated to each row of projections
    dict_projection_log_err_metadata = {}

    def __init__(self, parent: Optional[QMainWindow] = None) -> None:
        """
        Initialize the HyperCTui application.

        Parameters
        ----------
        parent : Optional[QMainWindow]
            Parent widget, by default None
        """
        super(HyperCTui, self).__init__(parent)

        ui_full_path = os.path.join(os.path.dirname(__file__), os.path.join("ui", "main_application.ui"))

        self.ui = load_ui(ui_full_path, baseinstance=self)

        o_gui = GuiInitialization(parent=self)
        o_gui.all()

        self._loading_config()
        self._loading_previous_session_automatically()
        self.ob_tab_changed()

        self.set_window_title()
        self.inform_of_output_location()
        self.check_log_file_size()

    def _loading_config(self) -> None:
        """
        Load the configuration settings.
        """
        o_config = ConfigHandler(parent=self)
        o_config.load()

    def check_log_file_size(self) -> None:
        """
        Check if the log file is larger than the buffer size and truncate if necessary.
        """
        o_get = Get(parent=self)
        log_file_name = o_get.get_log_file_name()
        o_handler = LogHandler(parent=self, log_file_name=log_file_name)
        o_handler.cut_log_size_if_bigger_than_buffer()

    def _loading_previous_session_automatically(self) -> None:
        """
        Attempt to load previous session if available, otherwise start a new session.
        """
        o_get = Get(parent=self)
        full_config_file_name = o_get.get_automatic_config_file_name()
        if os.path.exists(full_config_file_name):
            load_session_ui = LoadPreviousSessionLauncher(parent=self)
            load_session_ui.show()
        else:
            self.new_session_clicked()

    # menu events
    def new_session_clicked(self) -> None:
        """
        Handle the new session menu action.
        """
        o_event = EventHandler(parent=self)
        o_event.new_session()

    def menu_log_clicked(self) -> None:
        """
        Handle the log menu action.
        """
        LogLauncher(parent=self)

    def load_session_clicked(self) -> None:
        """
        Handle the load session menu action.

        Loads session from file and updates the UI accordingly.
        """
        o_session = SessionHandler(parent=self)
        o_session.load_from_file()
        o_session.load_to_ui()
        self.folder_path = FolderPath(parent=self)
        self.folder_path.update()

    def save_session_clicked(self) -> None:
        """
        Handle the save session menu action.

        Saves current session configuration to file.
        """
        o_session = SessionHandler(parent=self)
        o_session.save_from_ui()
        o_session.save_to_file()

    def full_reset_clicked(self) -> None:
        """
        Handle the full reset menu action.

        Resets the application to its initial state.
        """
        o_event = EventHandler(parent=self)
        o_event.full_reset_clicked()

    def launch_pre_processing_monitor_view(self) -> None:
        """
        Launch or bring to front the pre-processing monitor view.

        If monitor is already open, it will be minimized and then restored.
        Otherwise, a new monitor window will be created.
        """
        if self.session_dict[SessionKeys.process_in_progress]:
            if self.monitor_ui:
                self.monitor_ui.showMinimized()
                self.monitor_ui.showNormal()

            else:
                o_monitor = PreProcessingMonitor(parent=self)
                o_monitor.show()
                self.monitor_ui = o_monitor
            self.ui.checking_status_acquisition_pushButton.setEnabled(False)

    def action_step1_clicked(self) -> None:
        """Set current tab to Step 1 (Setup OBs)."""
        self.ui.tabWidget.setCurrentIndex(0)

    def action_step2_clicked(self) -> None:
        """Set current tab to Step 2 (Setup Projections)."""
        self.ui.tabWidget.setCurrentIndex(1)

    def action_step3_clicked(self) -> None:
        """Set current tab to Step 3 (Crop)."""
        self.ui.tabWidget.setCurrentIndex(2)

    def action_step4_clicked(self) -> None:
        """Set current tab to Step 4 (Rotation Center)."""
        self.ui.tabWidget.setCurrentIndex(3)

    def action_step5_clicked(self) -> None:
        """Set current tab to Step 5 (Autonomous Reconstruction)."""
        self.ui.tabWidget.setCurrentIndex(4)

    def action_settings_clicked(self) -> None:
        """Set current tab to Settings."""
        if self.ui.tabWidget.count() > 3:
            self.ui.tabWidget.setCurrentIndex(5)
        else:
            self.ui.tabWidget.setCurrentIndex(2)

    def check_state_of_steps_menu_button(self) -> None:
        """
        Update the state of steps menu button based on current application state.
        """
        o_event = EventHandler(parent=self)
        o_event.check_state_of_steps_menu_button()

    # main tab
    def main_tab_changed(self, new_tab_index: int) -> None:
        """
        Handle tab change events in the main tab widget.

        Parameters
        ----------
        new_tab_index : int
            Index of the newly selected tab
        """
        o_event = EventHandler(parent=self)
        o_event.main_tab_changed(new_tab_index=new_tab_index)

    # step - ob
    def ob_tab_changed(self) -> None:
        """
        Update UI in response to OB tab changes.
        """
        o_event = EventHandler(parent=self)
        o_event.ob_tab_changed()
        o_event.check_start_acquisition_button()

    def step1_check_state_of_ob_measured_clicked(self) -> None:
        """
        Handle the check state of OB measured button click.
        """
        o_event = Step1EventHandler(parent=self)
        o_event.check_state_of_ob_measured()

    def step1_browse_obs_clicked(self) -> None:
        """
        Handle the browse OBs button click.
        """
        o_event = Step1EventHandler(parent=self)
        o_event.browse_obs()

    def list_obs_selection_changed(self) -> None:
        """
        Update UI in response to OB selection changes.
        """
        o_event = Step1EventHandler(parent=self)
        o_event.update_state_of_rows()

        o_event = EventHandler(parent=self)
        o_event.check_start_acquisition_button()

    def refresh_list_of_obs_button_clicked(self) -> None:
        """
        Handle the refresh list of OBs button click.

        Saves current selections, refreshes the list, and reselects previously selected items.
        """
        o_event = Step1EventHandler(parent=self)
        o_event.save_list_of_obs_selected()
        o_event.update_list_of_obs()
        o_event.reselect_the_obs_previously_selected()

    def ob_proton_charge_changed(self, proton_charge: Union[float, str]) -> None:
        """
        Update the proton charge label.

        Parameters
        ----------
        proton_charge : Union[float, str]
            New proton charge value
        """
        self.ui.projections_p_charge_label.setText(str(proton_charge))

    def number_of_obs_changed(self, value: int) -> None:
        """
        Handle changes to the number of OBs.

        Parameters
        ----------
        value : int
            New number of OBs
        """
        o_event = EventHandler(parent=self)
        o_event.check_start_acquisition_button()

    # step - setup projections
    def run_title_changed(self, run_title: str) -> None:
        """
        Handle changes to the run title.

        Parameters
        ----------
        run_title : str
            New run title
        """
        if run_title == "":
            self.ui.run_title_groupBox.setEnabled(False)
        else:
            self.ui.run_title_groupBox.setEnabled(True)
        o_event = Step2EventHandler(parent=self)
        o_event.run_title_changed(run_title=run_title, checking_if_file_exists=True)
        self.inform_of_output_location()
        o_event = EventHandler(parent=self)
        o_event.check_start_acquisition_button()

    def number_of_projections_changed(self, value: int) -> None:
        """
        Handle changes to the number of projections.

        Parameters
        ----------
        value : int
            New number of projections
        """
        o_event = EventHandler(parent=self)
        o_event.check_start_acquisition_button()

    def start_acquisition_clicked(self) -> None:
        """
        Handle the start acquisition button click.

        Launches the OB and first projections acquisition process.
        """
        self.session_dict[SessionKeys.process_in_progress] = True
        self.session_dict[SessionKeys.started_acquisition] = True

        o_cmd = CommandLauncher(parent=self)
        o_cmd.launch_ob_first_projections_acquisition()

        o_event = EventHandler(parent=self)
        o_event.freeze_number_ob_sample_requested()
        self.launch_pre_processing_monitor_view()
        self.ui.start_acquisition_pushButton.setEnabled(False)

        print("start acquisition clicked!")

    def checking_status_acquisition_button_clicked(self) -> None:
        """
        Handle the checking status acquisition button click.

        Launches the pre-processing monitor view.
        """
        self.launch_pre_processing_monitor_view()

    # step crop
    def initialize_crop(self) -> None:
        """
        Initialize the crop settings.

        Raises
        ------
        CropError
            If initialization of crop settings fails
        """
        try:
            o_crop = Crop(parent=self)
            o_crop.initialize()
        except CropError:
            show_status_message(
                parent=self,
                message="Initialization of crop failed! check log!",
                duration_s=10,
                status=StatusMessageStatus.error,
            )

    def crop_top_changed(self, value: int) -> None:
        """
        Handle changes to the top crop value.

        Parameters
        ----------
        value : int
            New top crop value
        """
        self.crop_changed()

    def crop_top_edit_finished(self) -> None:
        """
        Handle the event when top crop value editing is finished.
        """
        self.crop_changed()

    def crop_bottom_changed(self, value: int) -> None:
        """
        Handle changes to the bottom crop value.

        Parameters
        ----------
        value : int
            New bottom crop value
        """
        self.crop_changed()

    def crop_bottom_edit_finished(self) -> None:
        """
        Handle the event when bottom crop value editing is finished.
        """
        self.crop_changed()

    def crop_left_changed(self, value: int) -> None:
        """
        Handle changes to the left crop value.

        Parameters
        ----------
        value : int
            New left crop value
        """
        self.crop_changed()

    def crop_left_edit_finished(self) -> None:
        """
        Handle the event when left crop value editing is finished.
        """
        self.crop_changed()

    def crop_right_changed(self, value: int) -> None:
        """
        Handle changes to the right crop value.

        Parameters
        ----------
        value : int
            New right crop value
        """
        self.crop_changed()

    def crop_right_edit_finished(self) -> None:
        """
        Handle the event when right crop value editing is finished.
        """
        self.crop_changed()

    def crop_changed(self) -> None:
        """
        Update the crop ROI based on the current crop values.
        """
        o_crop = Crop(parent=self)
        o_crop.update_roi()

    def crop_roi_manually_moved(self) -> None:
        """
        Handle the event when crop ROI is manually moved.
        """
        o_crop = Crop(parent=self)
        o_crop.roi_manually_moved()

    def sort_the_crop_values(self) -> None:
        """
        Sort the left and right crop values and update the UI accordingly.
        """
        left_crop_value = int(self.crop_left_ui.value())
        right_crop_value = int(self.crop_right_ui.value())
        left_right = [left_crop_value, right_crop_value]
        left_right.sort()
        self.ui.crop_left_label_value.setText(str(left_right[0]))
        self.ui.crop_right_label_value.setText(str(left_right[1]))

    # center of rotation
    def initialize_center_of_rotation(self) -> None:
        """
        Initialize the center of rotation settings.

        Raises
        ------
        CenterOfRotationError
            If initialization of center of rotation settings fails
        """
        try:
            o_rot = RotationCenter(parent=self)
            o_rot.initialize()
        except CenterOfRotationError:
            show_status_message(
                parent=self,
                message="Initialization of center of rotation failed! check log!",
                duration_s=10,
                status=StatusMessageStatus.error,
            )

    def rotation_center_tomopy_clicked(self, button_state: bool) -> None:
        """
        Handle the event when Tomopy rotation center radio button is clicked.

        Parameters
        ----------
        button_state : bool
            State of the Tomopy rotation center radio button
        """
        self.center_of_rotation_item.setMovable(False)
        self.ui.rotation_center_user_defined_radioButton.blockSignals(True)
        self.ui.rotation_center_user_defined_radioButton.setChecked(not button_state)
        o_event = RotationCenterEventHandler(parent=self)
        o_event.radio_button_changed(is_tomopy_checked=button_state)
        self.ui.rotation_center_user_defined_radioButton.blockSignals(False)

    def rotation_center_user_clicked(self, button_state: bool) -> None:
        """
        Handle the event when user-defined rotation center radio button is clicked.

        Parameters
        ----------
        button_state : bool
            State of the user-defined rotation center radio button
        """
        self.center_of_rotation_item.setMovable(True)
        self.ui.rotation_center_tomopy_radioButton.blockSignals(True)
        self.ui.rotation_center_tomopy_radioButton.setChecked(not button_state)
        o_event = RotationCenterEventHandler(parent=self)
        o_event.radio_button_changed(is_tomopy_checked=not button_state)
        self.ui.rotation_center_tomopy_radioButton.blockSignals(False)

    def manual_rotation_center_moved(self) -> None:
        """
        Handle the event when manual rotation center is moved.
        """
        center_value = int(self.center_of_rotation_item.value())
        self.ui.rotation_center_user_value.blockSignals(True)
        self.ui.rotation_center_user_value.setValue(center_value)
        self.ui.rotation_center_user_value.blockSignals(False)

    def rotation_center_tomopy_calculate_clicked(self) -> None:
        """
        Handle the event when Tomopy calculate button is clicked.
        """
        o_event = RotationCenterEventHandler(parent=self)
        o_event.calculate_using_tomopy()

    def rotation_center_user_value_changed(self, value: int) -> None:
        """
        Handle changes to the user-defined rotation center value.

        Parameters
        ----------
        value : int
            New user-defined rotation center value
        """
        o_event = RotationCenterEventHandler(parent=self)
        o_event.radio_button_changed(is_tomopy_checked=False)

    # autonomous reconstruction

    def update_autonomous_widgets(self) -> None:
        """
        Update the autonomous reconstruction widgets.
        """
        o_event = AutonomousReconstructionHandler(parent=self)
        o_event.update_widgets()

    def projections_angles_clicked(self) -> None:
        """
        Handle the event when projections angles radio button is clicked.
        """
        o_event = AutonomousReconstructionHandler(parent=self)
        o_event.projections_angles_radioButton_changed()

    def projections_fixed_help_clicked(self) -> None:
        """
        Handle the event when projections fixed help button is clicked.
        """
        o_event = AutonomousReconstructionHandler(parent=self)
        o_event.projections_fixed_help_clicked()

    def projections_angles_automatic_button_clicked(self) -> None:
        """
        Handle the event when projections angles automatic button is clicked.
        """
        o_event = AutonomousReconstructionHandler(parent=self)
        o_event.projections_angles_automatic_button_clicked()

    def evaluation_frequency_help_clicked(self) -> None:
        """
        Handle the event when evaluation frequency help button is clicked.
        """
        o_event = AutonomousReconstructionHandler(parent=self)
        o_event.evaluation_frequency_help_clicked()

    def tof_region_selection_button_clicked(self) -> None:
        """
        Handle the event when TOF region selection button is clicked.
        """
        o_event = AutonomousReconstructionHandler(parent=self)
        o_event.tof_region_selection_button_clicked()

    def autonomous_evaluation_frequency_changed(self, new_value: int) -> None:
        """
        Handle changes to the autonomous evaluation frequency.

        Parameters
        ----------
        new_value : int
            New evaluation frequency value
        """
        o_event = AutonomousReconstructionHandler(parent=self)
        o_event.evaluation_frequency_changed()

    def autonomous_start_acquisition_clicked(self) -> None:
        """
        Handle the event when autonomous start acquisition button is clicked.
        """
        o_event = AutonomousReconstructionHandler(parent=self)
        o_event.start_acquisition()

    def autonomous_reconstruction_stop_process_button_clicked(self) -> None:
        """
        Handle the event when autonomous reconstruction stop process button is clicked.
        """
        o_event = AutonomousReconstructionHandler(parent=self)
        o_event.stop_acquisition()

    def autonomous_refresh_table_clicked(self) -> None:
        """
        Handle the event when autonomous refresh table button is clicked.
        """
        o_event = AutonomousReconstructionHandler(parent=self)
        o_event.refresh_projections_table_clicked()

    def autonomous_checking_reconstruction_clicked(self) -> None:
        """
        Handle the event when autonomous checking reconstruction button is clicked.
        """
        o_event = AutonomousReconstructionHandler(parent=self)
        o_event.refresh_reconstruction_table_clicked()

    # leaving ui
    def closeEvent(self, c: QCloseEvent) -> None:
        """
        Handle the window close event.

        Saves the session automatically before closing the application.

        Parameters
        ----------
        c : QCloseEvent
            Close event object
        """
        o_session = SessionHandler(parent=self)
        o_session.save_from_ui()
        o_session.automatic_save()
        logger.info(" #### Leaving ASUI ####")
        self.close()

    def set_window_title(self) -> None:
        """
        Set the window title based on the current instrument and IPTS.
        """
        instrument = self.session_dict[SessionKeys.instrument]
        ipts = self.session_dict[SessionKeys.ipts_selected]
        title = f"{UI_TITLE} - instrument:{instrument} - IPTS:{ipts}"
        self.ui.setWindowTitle(title)

    def inform_of_output_location(self) -> None:
        """
        Update the UI with information about the output location.
        """
        facility = self.session_dict.get(SessionKeys.facility, "SNS")
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

            output_location = os.sep.join(
                [
                    facility,
                    instrument,
                    ipts,
                    "shared",
                    "autoreduce",
                    "mcp",
                ]
            )
            output_location = os.path.join(HOME_FOLDER, output_location)

            ob_output_location = os.sep.join(
                [
                    facility,
                    instrument,
                    ipts,
                    "shared",
                    "autoreduce",
                    "mcp",
                ]
            )
            ob_output_location = os.path.join(HOME_FOLDER, ob_output_location)

            final_ob_output_location = os.sep.join(
                [facility, instrument, ipts, "shared", "autoreduce", "mcp", f"OBs_{title}" + os.path.sep]
            )
            final_ob_output_location = os.path.join(HOME_FOLDER, final_ob_output_location)

        self.ui.projections_output_location_label.setText(output_location)
        self.ui.obs_output_location_label.setText(os.path.abspath(ob_output_location))
        self.ui.location_of_ob_created.setText(os.path.abspath(ob_output_location))
        self.ui.final_location_of_ob_created.setText(os.path.abspath(final_ob_output_location))


def main(args: List[str]) -> None:
    """
    Main function to start the application.

    Parameters
    ----------
    args : List[str]
        Command line arguments
    """
    app = QApplication(args)
    app.setStyle("Fusion")
    app.aboutToQuit.connect(clean_up)
    app.setApplicationDisplayName("Ai Svmbir UI")
    window = HyperCTui()
    window.show()
    sys.exit(app.exec_())


def clean_up() -> None:
    """
    Clean up resources before application exit.
    """
    app = QApplication.instance()
    app.closeAllWindows()
