#!/usr/bin/env python
"""
Event handler for autonomous reconstruction functionality.

This module provides event handling for UI interactions related to autonomous reconstruction,
including TOF region selection, projection angle handling, and reconstruction monitoring.
"""

import logging
import os
from typing import Any, List, Optional

import inflect
import numpy as np
from qtpy.QtGui import QGuiApplication
from qtpy.QtWidgets import QPushButton

from hyperctui import EvaluationRegionKeys, error_style, interact_me_style, normal_style
from hyperctui.autonomous_reconstruction import (
    KeysTofReconstructionConfig,
    ProjectionsTableColumnIndex,
    ReconstructionTableColumnIndex,
)
from hyperctui.autonomous_reconstruction.help_golden_angle import HelpGoldenAngle
from hyperctui.autonomous_reconstruction.select_evaluation_regions import SelectEvaluationRegions
from hyperctui.autonomous_reconstruction.select_tof_regions import SelectTofRegions
from hyperctui.commands_launcher import CommandLauncher
from hyperctui.pre_autonomous_monitor import DataStatus
from hyperctui.pre_processing_monitor import IN_PROGRESS, IN_QUEUE, READY
from hyperctui.pre_processing_monitor.get import Get as GetMonitor
from hyperctui.preview_file.preview_file_launcher import (
    PreviewFileLauncher,
    PreviewImageLauncher,
    PreviewMetadataFileLauncher,
)
from hyperctui.session import SessionKeys
from hyperctui.utilities.array import formatting_list_for_print
from hyperctui.utilities.config_handler import ConfigHandler
from hyperctui.utilities.get import Get
from hyperctui.utilities.status_message_config import StatusMessageStatus, show_status_message
from hyperctui.utilities.table import TableHandler


class EventHandler:
    """
    Handles UI events for autonomous reconstruction.

    This class manages all event handling for the autonomous reconstruction GUI,
    including user interactions with buttons, tables, and other UI elements.

    Parameters
    ----------
    parent : Any, optional
        Parent widget that owns this handler.
    """

    def __init__(self, parent: Optional[Any] = None):
        self.parent = parent

    def projections_angles_radioButton_changed(self) -> None:
        """
        Handle state changes in projections angles radio buttons.

        Updates the UI when the user toggles between fixed and automatic
        projection angle selection.
        """
        fixed_state = self.parent.ui.fixed_projections_angles_radioButton.isChecked()
        self.parent.ui.automatic_projections_angles_pushButton.setEnabled(not fixed_state)
        self.update_widgets()

    def projections_angles_automatic_button_clicked(self) -> None:
        """
        Handle click on automatic projections angles button.

        Opens the evaluation regions selection dialog.
        """
        o_ui = SelectEvaluationRegions(parent=self.parent)
        o_ui.show()

    def projections_fixed_help_clicked(self) -> None:
        """
        Handle click on fixed projections help button.

        Opens the golden angle help dialog.
        """
        o_ui = HelpGoldenAngle(parent=self.parent)
        o_ui.show()

    def evaluation_frequency_help_clicked(self) -> None:
        """
        Handle click on evaluation frequency help button.
        """
        pass

    def tof_region_selection_button_clicked(self) -> None:
        """
        Handle click on TOF region selection button.

        Opens the TOF region selection dialog and updates projections.
        """
        o_ui = SelectTofRegions(parent=self.parent)
        o_ui.show()
        QGuiApplication.processEvents()
        o_ui.projections_changed()
        QGuiApplication.processEvents()

    def update_widgets(self) -> None:
        """
        Update the widgets such as the number of TOF regions selected.
        """
        tof_regions = self.parent.tof_regions
        nbr_regions_selected = 0
        for _key in tof_regions.keys():
            if tof_regions[_key][EvaluationRegionKeys.state]:
                nbr_regions_selected += 1

        p = inflect.engine()
        self.parent.ui.tof_region_of_interest_label.setText(
            f"{nbr_regions_selected} " + p.plural("region", nbr_regions_selected) + " selected!"
        )

        if nbr_regions_selected > 0:
            self.parent.ui.tof_region_of_interest_error_label.setVisible(False)
            self.parent.ui.tof_region_of_interest_pushButton.setText("Edit TOF regions ...")
        else:
            self.parent.ui.tof_region_of_interest_error_label.setVisible(True)
            self.parent.ui.tof_region_of_interest_pushButton.setText("Select TOF regions ...")

        self.check_state_of_start_pre_acquisition_button()

    def is_start_pre_acquisition_button_ready(self) -> bool:
        """
        Check if all the conditions are met to enable the pre-acquisition button.

        Returns
        -------
        bool
            True if the button is ready, False otherwise.
        """
        tof_regions = self.parent.tof_regions
        nbr_regions_selected = 0
        for _key in tof_regions.keys():
            if tof_regions[_key][EvaluationRegionKeys.state]:
                nbr_regions_selected += 1

        if nbr_regions_selected == 0:
            self.parent.ui.tof_region_of_interest_pushButton.setStyleSheet(error_style)
            return False
        else:
            self.parent.ui.tof_region_of_interest_pushButton.setStyleSheet(normal_style)

        if self.parent.ui.automatic_projections_angles_radioButton.isChecked():
            evaluation_regions = self.parent.evaluation_regions
            nbr_regions_selected = 0
            for _key in evaluation_regions.keys():
                if evaluation_regions[_key][EvaluationRegionKeys.state]:
                    nbr_regions_selected += 1

            if nbr_regions_selected == 0:
                self.parent.ui.automatic_projections_angles_pushButton.setStyleSheet(error_style)
                return False
            else:
                self.parent.ui.automatic_projections_angles_pushButton.setStyleSheet(normal_style)

        return True

    def check_state_of_start_pre_acquisition_button(self) -> None:
        """
        Check and update the state of the start pre-acquisition button.
        """
        is_button_ready = self.is_start_pre_acquisition_button_ready()

        # no TOF selected yet
        if self.parent.tof_regions[0].get(EvaluationRegionKeys.from_index, None) is None:
            self.parent.ui.tof_region_of_interest_pushButton.setStyleSheet(interact_me_style)
            is_button_ready = False
        else:
            self.parent.ui.tof_region_of_interest_pushButton.setStyleSheet(normal_style)

        self.parent.ui.start_first_reconstruction_pushButton.setEnabled(is_button_ready)
        if is_button_ready:
            self.parent.ui.start_first_reconstruction_pushButton.setStyleSheet(interact_me_style)
        else:
            self.parent.ui.start_first_reconstruction_pushButton.setStyleSheet(normal_style)

    def evaluation_frequency_changed(self) -> None:
        """
        Handle changes in evaluation frequency.
        """
        pass

    def start_acquisition(self) -> None:
        """
        Start the acquisition process.

        Disables previous widgets and enables the refresh button.
        """
        # disable all previous widgets
        self.parent.ui.autonomous_projections_groupBox.setEnabled(False)
        self.parent.ui.autonomous_evaluation_groupBox.setEnabled(False)
        self.parent.ui.autonomous_tof_regions_groupBox.setEnabled(False)
        self.parent.ui.start_first_reconstruction_pushButton.setEnabled(False)
        self.parent.ui.start_first_reconstruction_pushButton.setStyleSheet(normal_style)

        # enable
        self.parent.ui.autonomous_refresh_pushButton.setEnabled(True)
        self.parent.ui.autonomous_reconstruction_tabWidget.setVisible(True)
        self.parent.ui.autonomous_refresh_pushButton.setStyleSheet(interact_me_style)

        number_angles = self.parent.ui.evaluation_frequency_spinBox.value()
        show_status_message(
            parent=self.parent,
            message=f"Starting acquisition of {number_angles} angles!",
            duration_s=5,
            status=StatusMessageStatus.working,
        )

        folder_path = self.parent.folder_path
        # retrieve the list of folders in the output folder (any new one will be the one we are looking for)
        self.update_list_projections_folders_initially_there(folder_path=folder_path)
        list_folders_there = self.parent.session_dict[SessionKeys.list_projections_folders_initially_there]
        list_folders_there.sort()
        formatted_list_folders_there = "\n".join(list_folders_there)
        logging.info(f"- list folders initially there:\n{formatted_list_folders_there}")

        # no projections yet as we just started
        self.parent.session_dict[SessionKeys.list_projections_folders_acquired_so_far] = None

        # retrieve list of folders in the reconstruction folder
        self.update_list_recon_folders_initially_there(folder_path=folder_path)

        self.parent.ui.autonomous_projection_location_label.setText(folder_path.mcp)

        self.init_autonomous_table()

        o_cmd = CommandLauncher(parent=self.parent)
        o_cmd.launch_preprocessing_autonomous_reconstruction()

    def stop_acquisition(self) -> None:
        """
        Stop the acquisition process.

        Enables previous widgets and shows a status message.
        """
        self.parent.ui.autonomous_projections_groupBox.setEnabled(True)
        self.parent.ui.autonomous_evaluation_groupBox.setEnabled(True)
        self.parent.ui.autonomous_tof_regions_groupBox.setEnabled(True)
        self.parent.ui.start_first_reconstruction_pushButton.setEnabled(True)

        self.parent.ui.autonomous_refresh_pushButton.setStyleSheet(normal_style)

        show_status_message(
            parent=self.parent, message="Stopped acquisition!", duration_s=5, status=StatusMessageStatus.warning
        )

    def init_autonomous_table(self) -> None:
        """
        Initialize the autonomous table with projection angles and TOF regions.
        """
        logging.info("Initialization of the autonomous table:")

        nbr_angles = self.parent.ui.evaluation_frequency_spinBox.value()
        list_golden_ratio_angles_collected = self.parent.golden_ratio_angles[0:nbr_angles]
        formatted1_list_golden_ratio_angles_collected = [
            f"{_value:.2f}" for _value in list_golden_ratio_angles_collected
        ]
        formatted2_list_golden_ratio = [
            _value.replace(".", "_") for _value in formatted1_list_golden_ratio_angles_collected
        ]

        folder_path = self.parent.folder_path
        logging.info(f"- {folder_path}")
        tof_regions = self.parent.tof_regions
        list_tof_region_collected = []
        list_tof_region_index = []
        for _index in tof_regions.keys():
            if tof_regions[_index][EvaluationRegionKeys.state]:
                _from_value = float(tof_regions[_index][EvaluationRegionKeys.from_value])
                _from_value = f"{_from_value:06.3f}"

                _from_pre, _from_post = _from_value.split(".")
                _from = f"{int(_from_pre):03d}_{int(_from_post):d}"

                _to_value = float(tof_regions[_index][EvaluationRegionKeys.to_value])
                _to_value = f"{_to_value:06.3f}"
                _to_pre, _to_post = _to_value.split(".")
                _to = f"{int(_to_pre):03d}_{int(_to_post):d}"

                _from_index = tof_regions[_index][EvaluationRegionKeys.from_index]
                _to_index = tof_regions[_index][EvaluationRegionKeys.to_index]

                list_tof_region_collected.append(f"from_{_from}Ang_to_{_to}Ang")
                list_tof_region_index.append(f"from index: {_from_index:04d} to index: {_to_index:04d}")

        logging.info(f"- {formatted2_list_golden_ratio =}")
        logging.info(f"- {list_tof_region_index =}")
        logging.info(f"- {list_tof_region_collected =}")

        o_table = TableHandler(table_ui=self.parent.ui.autonomous_projections_tableWidget)
        o_table.remove_all_rows()

        for _row in np.arange(nbr_angles):
            o_table.insert_empty_row(row=_row)

            o_table.insert_item(
                row=_row,
                column=ProjectionsTableColumnIndex.folder_name,
                value=f"projection for angle {formatted2_list_golden_ratio[_row].replace('_', '.')} degrees",
            )

            if _row == 0:
                message = DataStatus.in_progress
                background_color = IN_PROGRESS
            else:
                message = DataStatus.in_queue
                background_color = IN_QUEUE

            o_table.insert_item(row=_row, column=ProjectionsTableColumnIndex.status, value=message)
            o_table.set_background_color(row=_row, column=ProjectionsTableColumnIndex.status, qcolor=background_color)

        self.parent.ui.autonomous_reconstructed_location_label.setText(folder_path.recon)
        # self.parent.ui.autonomous_reconstructed_status_label.setStyleSheet(label_in_focus_style)
        self.parent.ui.autonomous_reconstruction_tabWidget.setTabEnabled(1, False)

    def preview_log(self, state: int = 0, row: int = -1, data_type: str = "ob") -> None:
        """
        Preview the log file for a given projection.

        Parameters
        ----------
        state : int, optional
            State of the button click, by default 0
        row : int, optional
            Row index in the table, by default -1
        data_type : str, optional
            Type of data, by default "ob"
        """
        log_file = self.parent.dict_projection_log_err_metadata[row]["log_file"]
        preview_file = PreviewFileLauncher(parent=self.parent, file_name=log_file)
        preview_file.show()

    def preview_err(self, state: int = 0, row: int = -1, data_type: str = "ob") -> None:
        """
        Preview the error file for a given projection.

        Parameters
        ----------
        state : int, optional
            State of the button click, by default 0
        row : int, optional
            Row index in the table, by default -1
        data_type : str, optional
            Type of data, by default "ob"
        """
        err_file = self.parent.dict_projection_log_err_metadata[row]["err_file"]
        preview_file = PreviewFileLauncher(parent=self.parent, file_name=err_file)
        preview_file.show()

    def preview_summary(self, state: int = 0, row: int = -1, data_type: str = "ob") -> None:
        """
        Preview the summary file for a given projection.

        Parameters
        ----------
        state : int, optional
            State of the button click, by default 0
        row : int, optional
            Row index in the table, by default -1
        data_type : str, optional
            Type of data, by default "ob"
        """
        file_name = self.parent.dict_projection_log_err_metadata[row]["metadata_file"]
        preview_file = PreviewMetadataFileLauncher(parent=self.parent, file_name=file_name)
        preview_file.show()

    def preview_data(self, row: int = -1) -> None:
        """
        Display the summed image with pyqtgraph.

        Parameters
        ----------
        row : int, optional
            Row index in the table, by default -1
        """
        file_name = self.parent.dict_projection_log_err_metadata[row]["preview_file"]
        preview_image = PreviewImageLauncher(parent=self.parent, file_name=file_name)
        preview_image.show()

    def refresh_projections_table_clicked(self) -> None:
        """
        Refresh the projections table when the refresh button is clicked.
        """
        logging.info("User refreshing the autonomous reconstruction step1 table!")

        list_projections_folders_initially_there = self.parent.session_dict[
            SessionKeys.list_projections_folders_initially_there
        ]
        list_projections_folders_acquired_so_far = self.parent.session_dict[
            SessionKeys.list_projections_folders_acquired_so_far
        ]

        logging.info(
            f"-> list_projections_folders_acquired_so_far:\n"
            f"{formatting_list_for_print(list_projections_folders_acquired_so_far)}"
        )
        logging.info(
            f"-> list_projections_folders_initially_there:\n"
            f" {formatting_list_for_print(list_projections_folders_initially_there)}"
        )

        # updating the list of projections by adding the folders already acquired
        if list_projections_folders_acquired_so_far:
            previous_list_of_folders = list_projections_folders_initially_there
            previous_list_of_folders.extend(list_projections_folders_acquired_so_far)
        else:
            previous_list_of_folders = list_projections_folders_initially_there
        logging.info(f"-> previous_list_of_folders:\n{formatting_list_for_print(previous_list_of_folders)}")

        # listing only the new folders
        list_new_folders = self.list_new_folders(
            folder_path=self.parent.folder_path, previous_list_of_folders=previous_list_of_folders
        )
        logging.info(f"-> list_new_folders: \n{formatting_list_for_print(list_new_folders)}")

        if not list_new_folders:
            # no new folders
            return

        if list_projections_folders_acquired_so_far:
            starting_row_index = len(list_projections_folders_acquired_so_far)

            # to remove duplicates
            list_projections_folders_acquired_so_far = list(set(list_projections_folders_acquired_so_far))
            list_projections_folders_acquired_so_far.extend(list_new_folders)
        else:
            starting_row_index = 0
            list_projections_folders_acquired_so_far = list_new_folders

        logging.info(
            f"Updating list of projections folders acquired so far:\n->{list_projections_folders_acquired_so_far}"
        )

        self.parent.session_dict[SessionKeys.list_projections_folders_acquired_so_far] = (
            list_projections_folders_acquired_so_far
        )

        self.fill_table_with_list_folders(list_folders=list_new_folders, starting_row_index=starting_row_index)

        self.checking_state_of_projections_table()

    def checking_state_of_projections_table(self) -> None:
        """
        Check the state of the projections table and update the UI accordingly.
        """
        list_projections_folders_acquired_so_far = self.parent.session_dict[
            SessionKeys.list_projections_folders_acquired_so_far
        ]

        if list_projections_folders_acquired_so_far is None:
            return

        number_of_projections_requested = self.parent.ui.evaluation_frequency_spinBox.value()
        if len(list_projections_folders_acquired_so_far) == number_of_projections_requested:
            # all the projections showed up, no need to click the refresh button anymore
            self.parent.ui.autonomous_refresh_pushButton.setEnabled(False)
            self.parent.ui.autonomous_refresh_pushButton.setStyleSheet(normal_style)
            self.parent.ui.autonomous_checking_reconstruction_pushButton.setEnabled(True)
            self.parent.ui.autonomous_checking_reconstruction_pushButton.setStyleSheet(interact_me_style)
            self.parent.ui.autonomous_reconstruction_tabWidget.setTabEnabled(1, True)
            self.parent.ui.autonomous_reconstruction_tabWidget.setCurrentIndex(1)

            self.initialize_reconstruction_table()
            # fill table with as many as TOF regions reconstruction requested
            # tof_regions_dict = self.parent.session_dict[SessionKeys.tof_regions]
            tof_regions_dict = self.parent.tof_regions
            o_table = TableHandler(table_ui=self.parent.ui.autonomous_reconstructions_tableWidget)

    def initialize_reconstruction_table(self) -> None:
        """
        Initialize the reconstruction table with TOF regions.
        """
        # fill table with as many as TOF regions reconstruction requested
        tof_regions_dict = self.parent.session_dict[SessionKeys.tof_regions]
        o_table = TableHandler(table_ui=self.parent.ui.autonomous_reconstructions_tableWidget)
        row_index = 0
        for _key in tof_regions_dict.keys():
            if tof_regions_dict[_key][EvaluationRegionKeys.state]:
                o_table.insert_empty_row(row=row_index)

                # temporary folder name holder
                o_table.insert_item(
                    row=row_index,
                    column=ReconstructionTableColumnIndex.folder_name,
                    value=tof_regions_dict[_key][EvaluationRegionKeys.str_from_to_value],
                )

                if row_index == 0:
                    message = DataStatus.in_progress
                    background_color = IN_PROGRESS

                else:
                    message = DataStatus.in_queue
                    background_color = IN_QUEUE

                o_table.insert_item(row=row_index, column=ReconstructionTableColumnIndex.status, value=message)
                o_table.set_background_color(
                    row=row_index, column=ReconstructionTableColumnIndex.status, qcolor=background_color
                )
                row_index += 1

    def refresh_reconstruction_table_clicked(self) -> None:
        """
        Refresh the reconstruction table when the refresh button is clicked.
        """
        logging.info("User is refreshing the autonomous reconstruction table.")

        folder_path = self.parent.folder_path
        reconstruction_config = folder_path.reconstruction_config
        if not os.path.exists(reconstruction_config):
            logging.info(f"- config file {reconstruction_config} not found!")
            return

        logging.info(f"- config file {reconstruction_config} has been located!")
        o_config = ConfigHandler(parent=self.parent)
        o_config.load_reconstruction_config(file_name=reconstruction_config)

        config = self.parent.reconstruction_config
        list_tof_reconstruction_folders = config.get(KeysTofReconstructionConfig.tof_reconstruction_folders, None)
        if not list_tof_reconstruction_folders:
            logging.info("- no TOF reconstruction folders found yet!")
            return

        logging.info(f"- list of reconstruction folders: {list_tof_reconstruction_folders}")
        if len(list_tof_reconstruction_folders) > 0:
            self.refresh_reconstruction_table()

    def refresh_reconstruction_table(self) -> None:
        """
        Refresh the reconstruction table with updated data.
        """
        pass

    def fill_table_with_list_folders(
        self, list_folders: Optional[List[str]] = None, starting_row_index: int = 0
    ) -> None:
        """
        Fill the table with a list of folders.

        Parameters
        ----------
        list_folders : list of str, optional
            List of folder names to add to the table, by default None
        starting_row_index : int, optional
            Starting row index in the table, by default 0
        """
        if list_folders is None:
            return

        o_get = GetMonitor(grand_parent=self.parent)
        o_table = TableHandler(table_ui=self.parent.ui.autonomous_projections_tableWidget)

        for _offset_row_index in np.arange(len(list_folders)):
            _row = starting_row_index + _offset_row_index
            new_file = list_folders[_offset_row_index]

            # change value of first column
            o_table.set_item_with_str(row=_row, column=ProjectionsTableColumnIndex.folder_name, value=new_file)

            # add err, log, metadata buttons
            o_get.set_path(new_file)
            log_file = o_get.log_file()
            # if log_file:
            #     enable_button = True
            # else:
            #     enable_button = False

            log_button = QPushButton("View")
            # log_button.setEnabled(enable_button)
            o_table.insert_widget(row=_row, column=ProjectionsTableColumnIndex.log, widget=log_button)

            log_button.clicked.connect(lambda state=0, row=_row: self.preview_log(row=row))

            err_file = o_get.err_file()
            if err_file:
                enable_button = True
            else:
                enable_button = False

            err_button = QPushButton("View")
            err_button.setEnabled(enable_button)
            o_table.insert_widget(row=_row, column=ProjectionsTableColumnIndex.err, widget=err_button)
            err_button.clicked.connect(lambda state=0, row=_row: self.preview_err(row=row))

            metadata_file = o_get.metadata_file()
            if metadata_file:
                enable_button = True
            else:
                enable_button = False

            summary_button = QPushButton("View")
            summary_button.setEnabled(enable_button)
            o_table.insert_widget(row=_row, column=ProjectionsTableColumnIndex.meta, widget=summary_button)
            summary_button.clicked.connect(lambda state=0, row=_row: self.preview_summary(row=row))

            # preview
            preview_file = o_get.preview_file()
            enable_button = True if preview_file else False
            preview_button = QPushButton("View")
            preview_button.setEnabled(enable_button)
            o_table.insert_widget(row=_row, column=ProjectionsTableColumnIndex.preview, widget=preview_button)
            preview_button.clicked.connect(lambda state=0, row=_row: self.preview_data(row=row))

            self.parent.dict_projection_log_err_metadata[_row] = {
                "file_name": new_file,
                "log_file": log_file,
                "err_file": err_file,
                "preview_file": preview_file,
                "metadata_file": metadata_file,
            }

            # change state of last column
            o_table.set_item_with_str(row=_row, column=ProjectionsTableColumnIndex.status, value=DataStatus.ready)

            o_table.set_background_color(row=_row, column=ProjectionsTableColumnIndex.status, qcolor=READY)

            if _row < (o_table.row_count() - 1):
                o_table.set_item_with_str(
                    row=_row + 1, column=ProjectionsTableColumnIndex.status, value=DataStatus.in_progress
                )
                o_table.set_background_color(
                    row=_row + 1, column=ProjectionsTableColumnIndex.status, qcolor=IN_PROGRESS
                )

    def checking_reconstruction_clicked(self) -> None:
        """
        Handle click on the checking reconstruction button.
        """
        logging.info("User is checking the state of the reconstruction.")

    def is_reconstruction_done(self) -> bool:
        """
        Check if the reconstruction is done.

        Returns
        -------
        bool
            True if the reconstruction is done, False otherwise.
        """
        # if folder does not even exist, it's not done
        if not os.path.exists(self.parent.folder_path.recon):
            return False

        o_get = Get(parent=self.parent)
        list_folders_initially_there = self.parent.session_dict[SessionKeys.list_recon_folders_initially_there]
        list_folders_now_there = o_get.list_folders_in_output_directory(output_folder=self.parent.folder_path.recon)
        if len(list_folders_now_there) > len(list_folders_initially_there):
            return True
        else:
            return False

    def update_list_recon_folders_initially_there(self, folder_path: Optional[Any] = None) -> None:
        """
        Update the list of reconstruction folders initially there.

        Parameters
        ----------
        folder_path : Any, optional
            Path to the folder, by default None
        """
        o_get = Get(parent=self.parent)
        list_folders = o_get.list_folders_in_output_directory(output_folder=folder_path.recon)
        self.parent.session_dict[SessionKeys.list_recon_folders_initially_there] = list(set(list_folders))

    def update_list_projections_folders_initially_there(self, folder_path: Optional[Any] = None) -> None:
        """
        Update the list of projections folders initially there.

        Parameters
        ----------
        folder_path : Any, optional
            Path to the folder, by default None
        """
        o_get = Get(parent=self.parent)
        list_folders = o_get.list_folders_in_output_directory(output_folder=folder_path.mcp)
        self.parent.session_dict[SessionKeys.list_projections_folders_initially_there] = list(set(list_folders))

    def list_new_folders(
        self, folder_path: Optional[Any] = None, previous_list_of_folders: Optional[List[str]] = None
    ) -> List[str]:
        """
        Retrieve the list of new folders in the folder_path location.

        Parameters
        ----------
        folder_path : Any, optional
            Path to the folder, by default None
        previous_list_of_folders : list of str, optional
            List of previous folders, by default None

        Returns
        -------
        list of str
            List of new folders.
        """
        o_get = Get(parent=self.parent)
        list_folders = o_get.list_folders_in_output_directory(output_folder=folder_path.mcp)
        if previous_list_of_folders is None:
            return list_folders

        list_new_folders = []
        for _folder in list_folders:
            if _folder in previous_list_of_folders:
                continue
            list_new_folders.append(_folder)
        return list_new_folders

    def update_autonomous_reconstruction_widgets(self) -> None:
        """
        Update the autonomous reconstruction widgets based on the session state.
        """
        if self.parent.session_dict[SessionKeys.list_projections_folders_acquired_so_far]:
            self.parent.ui.start_first_reconstruction_pushButton.setEnabled(False)
            self.parent.ui.start_first_reconstruction_pushButton.setStyleSheet(normal_style)
            self.parent.ui.autonomous_refresh_pushButton.setEnabled(True)

            self.parent.ui.autonomous_projection_location_label.setText(self.parent.folder_path.mcp)

            # enable table
            self.parent.ui.autonomous_reconstruction_tabWidget.setVisible(True)
            self.parent.ui.autonomous_refresh_pushButton.setStyleSheet(interact_me_style)

            # populate first projections table
            self.init_autonomous_table()
            list_folders_acquired = self.parent.session_dict[SessionKeys.list_projections_folders_acquired_so_far]
            self.fill_table_with_list_folders(list_folders=list_folders_acquired, starting_row_index=0)
            self.checking_state_of_projections_table()
