#!/usr/bin/env python
"""
Event handling module for pre-autonomous monitoring.

This module provides functionality to monitor and handle events related to
observation (OB) and projection data processing, including checking the status
of expected data folders, updating UI tables, and managing file movement to
final locations.
"""

import logging
import os
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from qtpy.QtWidgets import QPushButton

from hyperctui import DataType
from hyperctui.pre_autonomous_monitor import IN_PROGRESS, READY, DataStatus
from hyperctui.pre_processing_monitor.get import Get as GetMonitor
from hyperctui.session import SessionKeys
from hyperctui.utilities.file_utilities import make_folder, move_list_files_to_folder
from hyperctui.utilities.table import TableHandler


class EventHandler:
    """
    Handles events for the pre-autonomous monitoring process.

    This class provides methods to check the status of data processing,
    update UI tables, and manage data files.

    Parameters
    ----------
    parent : Any, optional
        Parent object that contains this handler
    grand_parent : Any, optional
        Grand parent object that may contain session information
    """

    def __init__(self, parent: Optional[Any] = None, grand_parent: Optional[Any] = None):
        self.parent = parent
        self.grand_parent = grand_parent

    def checking_status_of(
        self,
        data_type: DataType = DataType.ob,
        output_folder: Optional[str] = None,
        table_ui: Optional[Any] = None,
        dict_log_err_metadata: Optional[Dict] = None,
        list_folder_previously_found: Optional[List[str]] = None,
    ) -> Tuple[List[str], bool]:
        """
        Check if requested folders have been created and update the table.

        Parameters
        ----------
        data_type : DataType
            Type of data being checked (ob or projection)
        output_folder : str, optional
            Output folder to check
        table_ui : Any, optional
            Table UI widget to update
        dict_log_err_metadata : Dict, optional
            Dictionary to store log, error, and metadata information
        list_folder_previously_found : List[str], optional
            List of folders previously found

        Returns
        -------
        Tuple[List[str], bool]
            List of folders found, and whether all files were found
        """

        logging.info(f"Checking the monitor status of {data_type}")

        o_table = TableHandler(table_ui=table_ui)
        if data_type == DataType.projection:
            # only if we are looking at the projections and
            # all the obs have been found!
            if self.parent.all_obs_found:
                o_table.insert_item(row=0, column=4, value=DataStatus.in_progress)
                o_table.set_background_color(row=0, column=4, qcolor=IN_PROGRESS)

        o_table = TableHandler(table_ui=table_ui)
        nbr_row = o_table.row_count()

        list_folder_found = []

        o_get = GetMonitor(parent=self.parent, grand_parent=self.grand_parent)

        # we go row by row to see if we need to change the status of the row
        for _row in np.arange(nbr_row):
            logging.info(f"- row #{_row}")
            # if the last column says DONE, nothing to do
            row_status = o_table.get_item_str_from_cell(row=_row, column=4)
            file_name = o_table.get_item_str_from_cell(row=_row, column=0)
            logging.info(f"\t {file_name} - {row_status}")
            if row_status == READY:
                logging.info("\tfile already found!")
                list_folder_found.append(file_name)
                continue

            if os.path.exists(file_name):
                logging.info("\tfile newly found!")
                list_folder_found.append(file_name)
                # update table and add widgets + change status of file

                o_get.set_path(file_name)

                log_file = o_get.log_file()
                if log_file:
                    enable_button = True
                else:
                    enable_button = False

                log_button = QPushButton("View")
                log_button.setEnabled(enable_button)
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
                    "file_name": file_name,
                    "log_file": log_file,
                    "err_file": err_file,
                    "metadata_file": metadata_file,
                }

            else:
                logging.info("\tnot found! we can leave now")
                # no need to keep going, except that this one is in progress
                o_table.insert_item(row=_row, column=4, value=DataStatus.in_progress)
                o_table.set_background_color(row=_row, column=4, qcolor=IN_PROGRESS)
                break

        return list_folder_found, len(list_folder_found) == nbr_row

    def checking_status_of_expected_obs(self) -> None:
        """
        Look at the list of expected observations and update the OB table.

        This method checks the status of expected observation folders and
        updates the observation table with those already found.
        """
        output_folder = self.grand_parent.ui.obs_output_location_label.text()

        logging.info("Checking status of expected obs:")
        list_folder_previously_found = self.grand_parent.session_dict[SessionKeys.list_ob_folders_initially_there]
        list_folders_found, self.parent.all_obs_found = self.checking_status_of(
            data_type=DataType.ob,
            output_folder=output_folder,
            table_ui=self.parent.ui.obs_tableWidget,
            dict_log_err_metadata=self.parent.dict_ob_log_err_metadata,
            list_folder_previously_found=list_folder_previously_found,
        )
        self.grand_parent.session_dict[SessionKeys.list_ob_folders_initially_there] = list_folders_found
        logging.info(f"-> list folders found: {list_folders_found}")

    def checking_status_of_expected_projections(self) -> None:
        """
        Look at the list of projections and update the projection table.

        This method checks the status of expected projection folders and
        updates the projection table with those already found.
        """
        output_folder = self.grand_parent.ui.projections_output_location_label.text()

        logging.info("Checking status of expected projections:")
        list_folder_previously_found = self.grand_parent.session_dict[
            SessionKeys.list_projections_folders_initially_there
        ]
        list_folders_found, self.parent.all_projections_found = self.checking_status_of(
            data_type=DataType.projection,
            output_folder=output_folder,
            table_ui=self.parent.ui.projections_tableWidget,
            dict_log_err_metadata=self.parent.dict_projections_log_err_metadata,
            list_folder_previously_found=list_folder_previously_found,
        )
        self.grand_parent.session_dict[SessionKeys.list_projections_folders_initially_there] = list_folders_found

    def first_projection_in_progress(self) -> None:
        """
        Mark the first projection as in-progress.

        This method changes the status of the first row of projections from
        queue to in-progress when checking for projections for the first time.
        """
        o_table = TableHandler(table_ui=self.parent.ui.projections_tableWidget)
        o_table.insert_item(row=0, column=4, value=DataStatus.in_progress)
        o_table.set_background_color(row=0, column=4, qcolor=IN_PROGRESS)

    def obs_have_been_moved_to_final_folder(self) -> bool:
        """
        Check if observations have been moved to their final location.

        This method determines if the path of the first OB folder is the same
        as the final location.

        Returns
        -------
        bool
            True if OBs are in their final location, False otherwise
        """
        final_location = os.path.normpath(self.grand_parent.ui.final_location_of_ob_created.text())
        o_table = TableHandler(table_ui=self.parent.ui.obs_tableWidget)
        first_folder = o_table.get_item_str_from_cell(row=0, column=0)
        first_folder_path = os.path.normpath(os.path.dirname(first_folder))

        if first_folder_path == final_location:
            return True
        else:
            return False

    def move_obs_to_final_folder(self) -> None:
        """
        Move observations to their final location.

        If all OBs have been found, this method moves them to their final
        location and updates the table to point to the final locations.
        """
        logging.info("Moving obs to final folder!")
        list_ob_folders = self.grand_parent.session_dict[SessionKeys.list_ob_folders_initially_there]
        final_location = self.grand_parent.ui.final_location_of_ob_created.text()
        make_folder(final_location)
        move_list_files_to_folder(list_of_files=list_ob_folders, folder=final_location)

        logging.info("Updating table with new location of obs!")
        o_table = TableHandler(table_ui=self.parent.ui.obs_tableWidget)
        new_list_ob_folders = []
        for _row, _folder in enumerate(list_ob_folders):
            _new_final_location = os.path.join(final_location, os.path.basename(_folder))
            new_list_ob_folders.append(_new_final_location)
            o_table.set_item_with_str(row=_row, column=0, value=_new_final_location)
        self.grand_parent.session_dict[SessionKeys.list_ob_folders_initially_there] = new_list_ob_folders
        self.grand_parent.session_dict[SessionKeys.list_ob_folders_requested]
