#!/usr/bin/env python0
"""
Module for handling events related to pre-processing monitoring of OB and projection data.

This module contains functionality to track and update the status of OB (Open Beam)
and projection data processing, including monitoring new folders, updating tables,
and moving processed data to final locations.
"""

import logging
import os
from typing import Any, Dict, List, Optional

import numpy as np
from qtpy.QtWidgets import QPushButton

from hyperctui import DataType
from hyperctui.pre_processing_monitor import IN_PROGRESS, READY, DataStatus
from hyperctui.pre_processing_monitor.get import Get as GetMonitor
from hyperctui.session import SessionKeys
from hyperctui.setup_ob.get import Get as Step1Get
from hyperctui.utilities.file_utilities import make_folder, move_list_files_to_folder
from hyperctui.utilities.table import TableHandler


class EventHandler:
    """
    Handles events related to pre-processing monitoring of data.

    This class provides methods to update tables, check data status, and move
    processed data to final locations.

    Parameters
    ----------
    parent : Any, optional
        The parent object that contains this event handler
    grand_parent : Any, optional
        The grand parent object that contains the parent
    """

    def __init__(self, parent: Optional[Any] = None, grand_parent: Optional[Any] = None):
        self.parent = parent
        self.grand_parent = grand_parent

    def update_ob_monitor_table(
        self,
        output_folder: Optional[str] = None,
        dict_log_err_metadata: Optional[Dict[int, Dict[str, str]]] = None,
        list_folder_previously_found: Optional[List[str]] = None,
    ) -> None:
        """
        Check for new OB folders and update the monitoring table.

        Parameters
        ----------
        output_folder : str, optional
            Path to the output folder containing OB data
        dict_log_err_metadata : dict, optional
            Dictionary to store log, error, and metadata information
        list_folder_previously_found : list, optional
            List of folders that were previously found

        Returns
        -------
        None

        Notes
        -----
        This method checks for new OB folders that have appeared and updates
        the monitoring table with their status.
        """
        logging.info(f"-- checking if new {DataType.ob} showed up and updating the monitor table.")

        table_ui = self.parent.ui.obs_tableWidget

        o_get = Step1Get(parent=self.grand_parent)
        title = self.grand_parent.ui.run_title_lineEdit.text()
        name_of_output_ob_folder = self.grand_parent.ui.obs_output_location_label.text()
        list_ob_folders = o_get.list_ob_folders_in_output_directory(output_folder=name_of_output_ob_folder, title=title)
        logging.info(f"-- list_ob_folders: {list_ob_folders}")
        list_folder_previously_found = self.grand_parent.session_dict[SessionKeys.list_ob_folders_initially_there]
        logging.info(f"-- list_folder_previously_found: {list_folder_previously_found}")

        if len(list_ob_folders) == len(list_folder_previously_found):
            logging.info("No new OBs have been found! nothing to update.")
            return

        # just keeping the new folders located
        list_new_ob_folders = []
        for _folder in list_ob_folders:
            if _folder in list_folder_previously_found:
                continue
            list_new_ob_folders.append(_folder)

        list_ob_folders_acquired_so_far = self.grand_parent.session_dict[SessionKeys.list_ob_folders_acquired_so_far]
        if list_ob_folders_acquired_so_far is None:
            starting_working_row = 0
        else:
            starting_working_row = len(list_ob_folders_acquired_so_far)

        o_table = TableHandler(table_ui=table_ui)
        nbr_total_row = o_table.row_count()

        o_get = GetMonitor(parent=self.parent, grand_parent=self.grand_parent)

        # we go row by row to see if we need to change the status of the row
        range_row_to_update = np.arange(starting_working_row, starting_working_row + len(list_new_ob_folders))
        list_new_ob_folders.sort()

        for _new_file_index, _row in enumerate(range_row_to_update):
            new_file = list_new_ob_folders[_new_file_index]
            o_table.set_item_with_str(row=_row, column=0, value=new_file)

            o_get.set_path(new_file)
            log_file = o_get.log_file()
            # if log_file:
            #     enable_button = True
            # else:
            #     enable_button = False

            log_button = QPushButton("View")
            # log_button.setEnabled(enable_button)
            o_table.insert_widget(row=_row, column=1, widget=log_button)

            log_button.clicked.connect(lambda state=0, row=_row: self.parent.preview_log(row=row, data_type="ob"))

            err_file = o_get.err_file()
            if err_file:
                enable_button = True
            else:
                enable_button = False

            err_button = QPushButton("View")
            err_button.setEnabled(enable_button)
            o_table.insert_widget(row=_row, column=2, widget=err_button)
            err_button.clicked.connect(lambda state=0, row=_row: self.parent.preview_err(row=row, data_type="ob"))

            metadata_file = o_get.metadata_file()
            if metadata_file:
                enable_button = True
            else:
                enable_button = False

            summary_button = QPushButton("View")
            summary_button.setEnabled(enable_button)
            o_table.insert_widget(row=_row, column=3, widget=summary_button)
            summary_button.clicked.connect(
                lambda state=0, row=_row: self.parent.preview_summary(row=row, data_type="ob")
            )

            o_table.insert_item(row=_row, column=4, value=DataStatus.ready)
            o_table.set_background_color(row=_row, column=4, qcolor=READY)

            dict_log_err_metadata[_row] = {
                "file_name": new_file,
                "log_file": log_file,
                "err_file": err_file,
                "metadata_file": metadata_file,
            }

            if _row < (nbr_total_row - 1):
                o_table.insert_item(row=_row + 1, column=4, value=DataStatus.in_progress)
                o_table.set_background_color(row=_row + 1, column=4, qcolor=IN_PROGRESS)

            elif _row == (nbr_total_row - 1):
                # last row of the ob has been found!
                o_table = TableHandler(table_ui=self.parent.ui.projections_tableWidget)
                o_table.insert_item(row=0, column=4, value=DataStatus.in_progress)
                o_table.set_background_color(row=0, column=4, qcolor=IN_PROGRESS)

                self.parent.all_obs_found = True

    def update_projections_monitor_table(
        self,
        output_folder: Optional[str] = None,
        dict_log_err_metadata: Optional[Dict[int, Dict[str, str]]] = None,
        list_folder_previously_found: Optional[List[str]] = None,
    ) -> None:
        """
        Check for new projection folders and update the monitoring table.

        Parameters
        ----------
        output_folder : str, optional
            Path to the output folder containing projection data
        dict_log_err_metadata : dict, optional
            Dictionary to store log, error, and metadata information
        list_folder_previously_found : list, optional
            List of folders that were previously found

        Returns
        -------
        None

        Notes
        -----
        This method checks for new projection folders that have appeared and
        updates the monitoring table with their status.
        """
        logging.info(f"updating the monitor table of {DataType.projection}")

        table_ui = self.parent.ui.projections_tableWidget

        o_get = Step1Get(parent=self.grand_parent)
        title = self.grand_parent.ui.run_title_lineEdit.text()
        # name_of_output_ob_folder = self.grand_parent.ui.obs_output_location_label.text()
        # list_ob_folders = o_get.list_ob_folders_in_output_directory(output_folder=name_of_output_ob_folder,
        #                                                             title=title)
        list_folder_previously_found = self.grand_parent.session_dict[
            SessionKeys.list_projections_folders_initially_there
        ]
        output_folder = self.grand_parent.ui.projections_output_location_label.text()
        list_projections_folders = o_get.list_sample_folders_in_output_directory(
            output_folder=output_folder, title=title
        )

        # just keeping the new folders located
        list_new_projections_folders = []
        for _folder in list_projections_folders:
            if _folder in list_folder_previously_found:
                continue
            list_new_projections_folders.append(_folder)

        list_projections_folders_acquired_so_far = self.grand_parent.session_dict[
            SessionKeys.list_projections_folders_acquired_so_far
        ]
        if list_projections_folders_acquired_so_far is None:
            starting_working_row = 0
        else:
            starting_working_row = len(list_projections_folders_acquired_so_far)

        o_table = TableHandler(table_ui=table_ui)
        nbr_total_row = o_table.row_count()

        o_get = GetMonitor(parent=self.parent, grand_parent=self.grand_parent)

        # we go row by row to see if we need to change the status of the row
        range_row_to_update = np.arange(starting_working_row, starting_working_row + len(list_new_projections_folders))

        for _new_file_index, _row in enumerate(range_row_to_update):
            new_file = list_new_projections_folders[_new_file_index]
            o_table.set_item_with_str(row=_row, column=0, value=new_file)

            o_get.set_path(new_file)
            log_file = o_get.log_file()
            log_button = QPushButton("View")
            o_table.insert_widget(row=_row, column=1, widget=log_button)

            log_button.clicked.connect(
                lambda state=0, row=_row: self.parent.preview_log(row=row, data_type=DataType.projection)
            )

            err_file = o_get.err_file()
            err_button = QPushButton("View")
            o_table.insert_widget(row=_row, column=2, widget=err_button)
            err_button.clicked.connect(
                lambda state=0, row=_row: self.parent.preview_err(row=row, data_type=DataType.projection)
            )

            metadata_file = o_get.metadata_file()
            summary_button = QPushButton("View")
            o_table.insert_widget(row=_row, column=3, widget=summary_button)
            summary_button.clicked.connect(
                lambda state=0, row=_row: self.parent.preview_summary(row=row, data_type=DataType.projection)
            )

            o_table.insert_item(row=_row, column=4, value=DataStatus.ready)
            o_table.set_background_color(row=_row, column=4, qcolor=READY)

            dict_log_err_metadata[_row] = {
                "file_name": new_file,
                "log_file": log_file,
                "err_file": err_file,
                "metadata_file": metadata_file,
            }

            if _row < (nbr_total_row - 1):
                o_table.insert_item(row=_row + 1, column=4, value=DataStatus.in_progress)
                o_table.set_background_color(row=_row + 1, column=4, qcolor=IN_PROGRESS)

            elif _row == (nbr_total_row - 1):
                self.parent.all_projections_found = True

            if self.grand_parent.session_dict[SessionKeys.list_projections] is None:
                self.grand_parent.session_dict[SessionKeys.list_projections] = [new_file]
            else:
                self.grand_parent.session_dict[SessionKeys.list_projections].append(new_file)

            if _row == 0:
                self.grand_parent.session_dict[SessionKeys.full_path_to_projections][SessionKeys.image_0_degree] = (
                    new_file
                )
            else:
                self.grand_parent.session_dict[SessionKeys.full_path_to_projections][SessionKeys.image_180_degree] = (
                    new_file
                )

    def checking_status_of_expected_obs(self) -> None:
        """
        Look at the list of expected OBs and update the OB table.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        This method retrieves the list of expected OB folders and updates
        the OB monitoring table with those that have been found.
        """
        output_folder = self.grand_parent.ui.obs_output_location_label.text()

        logging.info("Checking status of expected obs:")
        list_folder_previously_found = self.grand_parent.session_dict[SessionKeys.list_ob_folders_initially_there]
        self.update_ob_monitor_table(
            output_folder=output_folder,
            dict_log_err_metadata=self.parent.dict_ob_log_err_metadata,
            list_folder_previously_found=list_folder_previously_found,
        )

    def checking_status_of_expected_projections(self) -> None:
        """
        Look at the list of projections and update the projection table.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        This method retrieves the list of expected projection folders and updates
        the projection monitoring table with those that have been found.
        """
        output_folder = self.grand_parent.ui.projections_output_location_label.text()

        logging.info("Checking status of expected projections:")
        list_folder_previously_found = self.grand_parent.session_dict[
            SessionKeys.list_projections_folders_initially_there
        ]
        self.update_projections_monitor_table(
            output_folder=output_folder,
            dict_log_err_metadata=self.parent.dict_projections_log_err_metadata,
            list_folder_previously_found=list_folder_previously_found,
        )
        # self.grand_parent.session_dict[SessionKeys.list_projections_folders_initially_there] = list_folders_found

    def first_projection_in_progress(self) -> None:
        """
        Set the status of the first projection row to "in progress".

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        This method changes the status of the first row in the projections table
        from "queue" to "in progress" when checking for projections for the first time.
        """
        o_table = TableHandler(table_ui=self.parent.ui.projections_tableWidget)
        o_table.insert_item(row=0, column=4, value=DataStatus.in_progress)
        o_table.set_background_color(row=0, column=4, qcolor=IN_PROGRESS)

    def obs_have_been_moved_to_final_folder(self) -> bool:
        """
        Check if OB folders have been moved to their final location.

        Parameters
        ----------
        None

        Returns
        -------
        bool
            True if OB folders have been moved to final location, False otherwise

        Notes
        -----
        This method compares the path of the first OB folder with the final location
        to determine if OBs have already been moved.
        """
        final_location = os.path.normpath(self.grand_parent.ui.final_location_of_ob_created.text())
        o_table = TableHandler(table_ui=self.parent.ui.obs_tableWidget)
        first_folder = o_table.get_item_str_from_cell(row=0, column=0)
        first_folder_path = os.path.normpath(os.path.dirname(first_folder))

        if first_folder_path == final_location:
            return True
        else:
            return False

        # list_ob_folders = self.grand_parent.session_dict[SessionKeys.list_ob_folders_initially_there]
        # final_location = self.grand_parent.ui.final_location_of_ob_created.text()
        # for _folder in list_ob_folders:
        #     base_name = os.path.basename(_folder)
        #     full_name_in_final_location = os.path.join(final_location, base_name)
        #     if not os.path.exists(full_name_in_final_location):
        #         return False
        # return True

    def move_obs_to_final_folder(self) -> None:
        """
        Move all OB folders to their final location.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        If all OBs have been found, this method moves them to their final location
        and updates the table to point to the new locations.
        """
        logging.info("Moving obs to final folder!")
        o_table = TableHandler(table_ui=self.parent.ui.obs_tableWidget)
        list_obs_folders = o_table.get_elements_from_column()
        # list_ob_folders = self.grand_parent.session_dict[SessionKeys.list_ob_folders_initially_there]

        final_location = self.grand_parent.ui.final_location_of_ob_created.text()

        make_folder(final_location)
        move_list_files_to_folder(list_of_files=list_obs_folders, folder=final_location)

        logging.info("Updating table with new location of obs!")
        o_table = TableHandler(table_ui=self.parent.ui.obs_tableWidget)
        new_list_ob_folders = []
        for _row, _folder in enumerate(list_obs_folders):
            _new_final_location = os.path.join(final_location, os.path.basename(_folder))
            new_list_ob_folders.append(_new_final_location)
            o_table.set_item_with_str(row=_row, column=0, value=_new_final_location)
        self.grand_parent.session_dict[SessionKeys.list_ob_folders_initially_there] = new_list_ob_folders
        # self.grand_parent.session_dict[SessionKeys.list_ob_folders_requested]
        self.parent.all_obs_moved = True
