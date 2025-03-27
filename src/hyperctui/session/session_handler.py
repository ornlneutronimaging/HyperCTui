#!/usr/bin/env python
"""
Module for handling the application session state.

This module contains the SessionHandler class that manages saving and loading
application session state to/from JSON files. It handles persistence of UI state,
configuration settings, and experiment parameters.
"""

import json
import os
from collections import OrderedDict
from typing import Any, Dict, Optional, Union

import numpy as np
from loguru import logger
from qtpy.QtCore import QRect
from qtpy.QtWidgets import QApplication, QFileDialog

from hyperctui import EvaluationRegionKeys
from hyperctui.autonomous_reconstruction.event_handler import EventHandler as AutonomousReconstructionEventHandler
from hyperctui.crop.crop import Crop
from hyperctui.event_handler import EventHandler as MainEventHandler
from hyperctui.rotation_center.rotation_center import RotationCenter
from hyperctui.session import DefaultValues, SessionKeys
from hyperctui.setup_ob.event_handler import EventHandler as Step1EventHandler
from hyperctui.setup_ob.get import Get as Step1Get
from hyperctui.setup_projections.get import Get as Step2Get
from hyperctui.utilities.exceptions import CropError
from hyperctui.utilities.folder_path import FolderPath
from hyperctui.utilities.get import Get
from hyperctui.utilities.status_message_config import StatusMessageStatus, show_status_message
from hyperctui.utilities.table import TableHandler
from hyperctui.utilities.widgets import Widgets as UtilityWidgets


class SessionHandler:
    """
    Handles saving and loading of application session state.

    This class provides methods to save the current state of the UI to a session dictionary
    and to load a previously saved state back into the UI.

    Attributes
    ----------
    config_file_name : str
        The file name of the currently loaded configuration.
    load_successful : bool
        Flag indicating if the last load operation was successful.
    parent : Any
        The parent widget that contains the UI elements.
    """

    config_file_name = ""
    load_successful = True

    def __init__(self, parent: Optional[Any] = None) -> None:
        """
        Initialize the SessionHandler.

        Parameters
        ----------
        parent : Any, optional
            The parent widget that contains the UI elements, by default None
        """
        self.parent = parent

    def save_from_ui(self) -> None:
        """
        Save the current state of the UI to the session dictionary.

        This method extracts values from various UI elements and stores them
        in the session dictionary for later retrieval.

        Returns
        -------
        None
        """
        session_dict = self.parent.session_dict
        session_dict[SessionKeys.config_version] = self.parent.config[SessionKeys.config_version]

        current_geometry = self.parent.ui.geometry()
        width = current_geometry.width()
        height = current_geometry.height()

        session_dict[SessionKeys.window_width] = width
        session_dict[SessionKeys.window_height] = height

        instrument = session_dict[SessionKeys.instrument]
        facility = session_dict.get(SessionKeys.facility, "SNS")
        ipts_selected = session_dict[SessionKeys.ipts_selected]
        ipts_index_selected = session_dict[SessionKeys.ipts_index_selected]

        # step obs
        o_get_step1 = Step1Get(parent=self.parent)
        number_of_obs = o_get_step1.number_of_obs()
        proton_charge = o_get_step1.proton_charge()
        top_obs_folder = o_get_step1.top_ob_folder()
        list_ob_folders_selected = o_get_step1.list_ob_folders_selected()
        ob_tab_selected = o_get_step1.ob_tab_selected()
        ob_will_be_moved_to = o_get_step1.ob_will_be_moved_to()
        ob_will_be_saved_as = o_get_step1.ob_will_be_saved_as()
        output_projection_folder = o_get_step1.projection_folder()
        output_ob_folder = o_get_step1.ob_folder()

        session_dict[SessionKeys.facility] = facility
        session_dict[SessionKeys.instrument] = instrument
        session_dict[SessionKeys.ipts_selected] = ipts_selected
        session_dict[SessionKeys.ipts_index_selected] = ipts_index_selected
        session_dict[SessionKeys.number_of_obs] = number_of_obs
        session_dict[SessionKeys.proton_charge] = proton_charge
        session_dict[SessionKeys.top_obs_folder] = top_obs_folder
        session_dict[SessionKeys.list_ob_folders_selected] = list_ob_folders_selected
        session_dict[SessionKeys.ob_tab_selected] = ob_tab_selected
        session_dict[SessionKeys.ob_will_be_saved_as] = ob_will_be_saved_as
        session_dict[SessionKeys.ob_will_be_moved_to] = ob_will_be_moved_to
        session_dict[SessionKeys.name_of_output_projection_folder] = output_projection_folder
        session_dict[SessionKeys.name_of_output_ob_folder] = output_ob_folder

        # step projections
        o_get_step2 = Step2Get(parent=self.parent)
        session_dict[SessionKeys.run_title] = self.parent.ui.run_title_formatted_label.text()

        # monitor
        # need to save the list of folders in output directory
        # name of each row in ob table
        # name of each row in projections table

        # all tabs
        all_tabs_visible = self.parent.all_tabs_visible
        main_tab_selected = self.parent.ui.tabWidget.currentIndex()

        session_dict[SessionKeys.all_tabs_visible] = all_tabs_visible
        session_dict[SessionKeys.main_tab_selected] = main_tab_selected

        # crop
        try:
            left = int(self.parent.ui.crop_left_label_value.text())
        except ValueError:
            left = 0

        try:
            right = int(self.parent.ui.crop_right_label_value.text())
        except ValueError:
            right = width - 1

        session_dict[SessionKeys.crop_left] = left
        session_dict[SessionKeys.crop_right] = right

        ## evaluation regions

        # reset ids
        evaluation_regions = self.parent.evaluation_regions
        for _key in evaluation_regions.keys():
            evaluation_regions[_key][EvaluationRegionKeys.id] = None
            evaluation_regions[_key][EvaluationRegionKeys.label_id] = None

        # make sure key is a string
        new_evaluation_regions = OrderedDict()
        for _key in evaluation_regions.keys():
            new_evaluation_regions[str(_key)] = evaluation_regions[_key]
        session_dict[SessionKeys.evaluation_regions] = new_evaluation_regions

        ## tof regions

        # reset ids
        tof_regions = self.parent.tof_regions
        for _key in tof_regions.keys():
            tof_regions[_key][EvaluationRegionKeys.id] = None
            tof_regions[_key][EvaluationRegionKeys.label_id] = None

        # make sure key is a string
        new_tof_regions = OrderedDict()
        for _key in tof_regions.keys():
            new_tof_regions[str(_key)] = tof_regions[_key]
        session_dict[SessionKeys.tof_regions] = new_tof_regions

        # evaluation frequency
        session_dict[SessionKeys.evaluation_frequency] = self.parent.ui.evaluation_frequency_spinBox.value()

        self.parent.session_dict = session_dict

    def load_to_ui(self) -> None:
        """
        Load the saved session state into the UI.

        This method applies the values stored in the session dictionary to
        the appropriate UI elements. If loading was not successful, it returns
        without making any changes.

        Returns
        -------
        None
        """
        if not self.load_successful:
            return

        session_dict = self.parent.session_dict
        self.parent.blockSignals(True)

        # size of main application
        width = session_dict.get(SessionKeys.window_width, DefaultValues.window_width)
        height = session_dict.get(SessionKeys.window_height, DefaultValues.window_height)
        current_geometry = self.parent.ui.geometry()
        left = current_geometry.left()
        top = current_geometry.top()
        rect = QRect(left, top, width, height)
        self.parent.ui.setGeometry(rect)

        # setup ob
        ipts = session_dict[SessionKeys.ipts_selected]
        instrument = session_dict[SessionKeys.instrument]

        self.parent.folder_path = FolderPath(parent=self.parent)
        self.parent.folder_path.update()

        number_of_obs = session_dict.get(SessionKeys.number_of_obs, DefaultValues.number_of_obs)
        self.parent.ui.number_of_ob_spinBox.setValue(number_of_obs)

        proton_charge = session_dict.get(SessionKeys.proton_charge, DefaultValues.proton_charge)
        # check if proton_charge is a digital value
        try:
            proton_charge = int(proton_charge)
        except ValueError:
            logger.warning(
                f"Proton charge value '{proton_charge}' is not a number."
                f"Using default value {DefaultValues.proton_charge}"
            )
            proton_charge = DefaultValues.proton_charge

        self.parent.ui.open_beam_proton_charge_doubleSpinBox.setValue(proton_charge)

        ob_will_be_saved_as = session_dict.get(SessionKeys.ob_will_be_saved_as, None)
        if ob_will_be_saved_as:
            self.parent.ui.location_of_ob_created.setText(ob_will_be_saved_as)

        ob_will_be_moved_to = session_dict.get(SessionKeys.ob_will_be_moved_to, None)
        if ob_will_be_moved_to:
            self.parent.ui.final_location_of_ob_created.setText(ob_will_be_moved_to)

        top_obs_folder = session_dict.get(SessionKeys.top_obs_folder, None)
        if top_obs_folder is None:
            list_top_obs_folder = ["", "SNS", instrument, ipts, "shared", "autoreduce"]
            top_obs_folder = os.sep.join(list_top_obs_folder)
        self.parent.ui.existing_ob_top_path.setText(top_obs_folder)
        o_ob_event = Step1EventHandler(parent=self.parent)
        o_ob_event.update_list_of_obs()

        list_ob_folders_selected = session_dict.get(SessionKeys.list_ob_folders_selected, None)
        o_table = TableHandler(table_ui=self.parent.ui.open_beam_tableWidget)
        nbr_row = o_table.row_count()
        for _row in np.arange(nbr_row):
            _folder = o_table.get_item_str_from_cell(row=_row, column=0)
            if _folder in list_ob_folders_selected:
                o_table.select_row(row=_row)

        ob_tab_selected = session_dict.get(SessionKeys.ob_tab_selected, DefaultValues.ob_tab_selected)
        self.parent.ui.ob_tabWidget.setCurrentIndex(ob_tab_selected)

        # step projections
        run_title = session_dict.get(SessionKeys.run_title, DefaultValues.run_title)
        self.parent.ui.run_title_lineEdit.blockSignals(True)
        self.parent.ui.run_title_lineEdit.setText(run_title)
        self.parent.ui.run_title_lineEdit.blockSignals(False)
        name_of_output_projection_folder = session_dict[SessionKeys.name_of_output_projection_folder]
        self.parent.ui.run_title_formatted_label.setText(run_title)
        self.parent.ui.projections_output_location_label.setText(name_of_output_projection_folder)

        name_of_output_ob_folder = session_dict[SessionKeys.name_of_output_ob_folder]
        self.parent.ui.obs_output_location_label.setText(name_of_output_ob_folder)

        self.parent.ui.projections_p_charge_label.setText(str(proton_charge))

        show_status_message(
            parent=self.parent,
            message=f"Loaded {self.config_file_name}",
            status=StatusMessageStatus.ready,
            duration_s=10,
        )

        self.parent.blockSignals(False)
        self.parent.set_window_title()

        o_main_event = MainEventHandler(parent=self.parent)
        o_main_event.check_start_acquisition_button()

        # hide start acquisition if already ran for that config
        if session_dict.get(SessionKeys.started_acquisition, False):
            self.parent.ui.start_acquisition_pushButton.setVisible(False)
            self.parent.ui.checking_status_acquisition_pushButton.setEnabled(True)

        if session_dict.get(SessionKeys.all_tabs_visible, False):
            try:
                # crop
                o_crop = Crop(parent=self.parent)
                o_crop.initialize()
            except CropError:
                return

            # rotation center
            o_rotation = RotationCenter(parent=self.parent)
            o_rotation.initialize()

            # autonomous reconstruction
            ## evaluation regions
            if session_dict.get(SessionKeys.evaluation_regions, None):
                self.parent.evaluation_regions = session_dict[SessionKeys.evaluation_regions]

            # key must be int because key=row in the table
            new_evaluation_regions = OrderedDict()
            for _key in self.parent.evaluation_regions.keys():
                new_evaluation_regions[int(_key)] = self.parent.evaluation_regions[_key]
            self.parent.evaluation_regions = new_evaluation_regions

            evaluation_frequency = session_dict.get(SessionKeys.evaluation_frequency, 3)
            self.parent.ui.evaluation_frequency_spinBox.setValue(evaluation_frequency)

            ## tof top ROI regions
            if not session_dict.get(SessionKeys.tof_roi_region, None):
                session_dict[SessionKeys.tof_roi_region] = {"x0": 5, "y0": 5, "x1": 200, "y1": 200}

            ## tof_regions
            if session_dict.get(SessionKeys.tof_regions, None):
                self.parent.tof_regions = session_dict[SessionKeys.tof_regions]

            # key must be int because key=row in the table
            new_tof_regions = OrderedDict()
            for _key in self.parent.tof_regions.keys():
                new_tof_regions[int(_key)] = self.parent.tof_regions[_key]
            self.parent.tof_regions = new_tof_regions

        all_tabs_visible = session_dict.get(SessionKeys.all_tabs_visible, False)
        # if not (self.parent.all_tabs_visible == all_tabs_visible):
        o_main_widgets = UtilityWidgets(parent=self.parent)
        o_main_widgets.make_tabs_visible(is_visible=all_tabs_visible)

        main_tab_selected = session_dict.get(SessionKeys.main_tab_selected, DefaultValues.main_tab_selected)
        self.parent.ui.tabWidget.setCurrentIndex(main_tab_selected)
        if main_tab_selected == 4:
            o_event = AutonomousReconstructionEventHandler(parent=self.parent)
            o_event.update_autonomous_reconstruction_widgets()

    def _retrieve_general_settings(self) -> Dict[str, Union[int, float, bool]]:
        """
        Retrieve general settings from the UI.

        This internal method collects general configuration settings
        from various UI controls.

        Returns
        -------
        Dict[str, Union[int, float, bool]]
            Dictionary containing general configuration settings
        """
        number_of_scanned_periods = self.parent.ui.number_of_scanned_periods_spinBox.value()
        full_period_true = self.parent.ui.full_period_true_radioButton.isChecked()
        rotation_of_g0rz = self.parent.ui.rotation_of_g0rz_doubleSpinBox.value()
        images_per_step = self.parent.ui.images_per_step_spinBox.value()
        general_settings = {
            "number of scanned periods": number_of_scanned_periods,
            "full period": full_period_true,
            "rotation of g0rz": rotation_of_g0rz,
            "number of images per step": images_per_step,
        }
        return general_settings

    def automatic_save(self) -> None:
        """
        Automatically save the session to a predetermined file.

        This method saves the current session to a file name that is
        automatically generated based on the current configuration.

        Returns
        -------
        None
        """
        o_get = Get(parent=self.parent)
        full_config_file_name = o_get.get_automatic_config_file_name()
        self.save_to_file(config_file_name=full_config_file_name)

    def save_to_file(self, config_file_name: Optional[str] = None) -> None:
        """
        Save the session to a file.

        If no file name is provided, a file dialog will be shown for the user
        to select a file location.

        Parameters
        ----------
        config_file_name : str, optional
            The file name to save the session to, by default None

        Returns
        -------
        None
        """
        if config_file_name is None:
            config_file_name = QFileDialog.getSaveFileName(
                self.parent,
                caption="Select session file name ...",
                directory=self.parent.homepath,
                filter="session (*.json)",
                initialFilter="session",
            )

            QApplication.processEvents()
            config_file_name = config_file_name[0]

        if config_file_name:
            output_file_name = config_file_name
            session_dict = self.parent.session_dict

            with open(output_file_name, "w") as json_file:
                json.dump(session_dict, json_file)

            show_status_message(
                parent=self.parent,
                message=f"Session saved in {config_file_name}",
                status=StatusMessageStatus.ready,
                duration_s=10,
            )
            logger.info(f"Saving configuration into {config_file_name}")

    def load_from_file(self, config_file_name: Optional[str] = None) -> None:
        """
        Load a session from a file.

        If no file name is provided, a file dialog will be shown for the user
        to select a file to load.

        Parameters
        ----------
        config_file_name : str, optional
            The file name to load the session from, by default None

        Returns
        -------
        None
        """
        self.parent.loading_from_config = True

        if config_file_name is None:
            config_file_name = QFileDialog.getOpenFileName(
                self.parent,
                directory=self.parent.homepath,
                caption="Select session file ...",
                filter="session (*.json)",
                initialFilter="session",
            )
            QApplication.processEvents()
            config_file_name = config_file_name[0]

        if config_file_name:
            config_file_name = config_file_name
            self.config_file_name = config_file_name
            show_status_message(
                parent=self.parent, message=f"Loading {config_file_name} ...", status=StatusMessageStatus.ready
            )

            with open(config_file_name, "r") as read_file:
                session_to_save = json.load(read_file)
                if session_to_save.get("config version", None) is None:
                    logger.info("Session file is out of date!")
                    logger.info(f"-> expected version: {self.parent.config['config version']}")
                    logger.info("-> session version: Unknown!")
                    self.load_successful = False
                elif session_to_save["config version"] == self.parent.config["config version"]:
                    self.parent.session_dict = session_to_save
                    logger.info(f"Loaded from {config_file_name}")
                else:
                    logger.info("Session file is out of date!")
                    logger.info(f"-> expected version: {self.parent.config['config version']}")
                    logger.info(f"-> session version: {session_to_save['config version']}")
                    self.load_successful = False

                if not self.load_successful:
                    show_status_message(
                        parent=self.parent,
                        message=f"{config_file_name} not loaded! (check log for more information)",
                        status=StatusMessageStatus.ready,
                        duration_s=10,
                    )

        else:
            self.load_successful = False
            show_status_message(
                parent=self.parent,
                message=f"{config_file_name} not loaded! (check log for more information)",
                status=StatusMessageStatus.ready,
                duration_s=10,
            )
