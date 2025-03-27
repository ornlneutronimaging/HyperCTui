#!/usr/bin/env python
"""
Event handler module for the Open Beam setup interface.

This module contains event handling logic for the Open Beam (OB) setup interface
in the HyperCTui application. It manages user interactions such as IPTS selection,
OB folder browsing, acquisition start, and selecting OB files for processing.
"""

import glob
import json
import os
from pathlib import Path
from typing import List, Optional, Union

import numpy as np
from loguru import logger
from qtpy.QtWidgets import QFileDialog

from hyperctui.parent import Parent
from hyperctui.session import SessionKeys
from hyperctui.setup_ob.get import Get
from hyperctui.utilities.check import is_float
from hyperctui.utilities.file_utilities import list_ob_dirs
from hyperctui.utilities.table import TableHandler


class EventHandler(Parent):
    """
    Handle events for the Open Beam setup interface.

    This class manages event handling for the Open Beam setup interface, including
    IPTS changes, OB selection, acquisition start, and OB browsing.

    Parameters
    ----------
    parent : Parent
        The parent object containing UI and session information.
    """

    # def run_title_changed(self, run_title=None):
    #     run_title_listed = run_title.split(" ")
    #     formatted_run_title = "_".join(run_title_listed)
    #     print(f"formatted run title: {formatted_run_title}")
    #     unused_formatted_run_title = self.produce_unused_formatted_run_title(formatted_run_title)
    #     print(f"unused formatted run title: {unused_formatted_run_title}")
    #     self.parent.ui.run_title_formatted_label.setText(unused_formatted_run_title)

    def start_acquisition(self) -> None:
        """
        Start the acquisition process for open beam measurements.

        This method is called when the start acquisition button is clicked.
        It retrieves the instrument and IPTS information, sets up the output folder,
        and checks the current number of OB folders for later comparison.
        """
        logger.info("Step1: start acquisition button clicked:")

        o_get = Get(parent=self.parent)
        instrument = o_get.instrument()
        ipts = o_get.ipts_selected()

        output_folder = Path(self.parent.homepath) / instrument / f"{ipts}" / "raw/ob/"
        logger.info(f"-> output_folder: {output_folder}")

        # look at the OBs folder of the IPTS and retrieve list of OBs (we will use this to see if any new
        # ones show up)
        list_folder = glob.glob("output_folder/*")
        self.parent.nbr_of_ob_folder_before_staring_acquisition = len(list_folder)

    def step1_ipts_changed(self, ipts: Optional[str] = None) -> None:
        """
        Handle change in IPTS selection.

        Parameters
        ----------
        ipts : str, optional
            The selected IPTS number.
        """
        logger.info(f"New IPTS selected: {ipts}")
        self.reset_ob_search_path()
        self.update_list_of_obs()

    def update_state_of_rows(self) -> None:
        """
        Update the state of rows in the open beam table based on selection.

        This method handles the logic for enabling/disabling rows based on
        consistent proton charge values across selected rows.
        """
        o_table = TableHandler(table_ui=self.parent.ui.open_beam_tableWidget)
        o_table.block_signals()

        rows_selected = o_table.get_rows_of_table_selected()

        clean_list_of_rows_selected = []
        list_obs_selected = []

        if rows_selected:
            if len(rows_selected) == 1:
                first_proton_charge = o_table.get_item_str_from_cell(row=rows_selected[0], column=1)

                # only enabled all the rows with the same proton charge
                nbr_row = o_table.row_count()
                for _row in np.arange(nbr_row):
                    if _row == rows_selected[0]:
                        pass
                    else:
                        _pc = o_table.get_item_str_from_cell(row=_row, column=1)
                        if _pc != first_proton_charge:
                            o_table.set_row_enabled(row=_row, enabled=False)

            first_previous_row_selected = rows_selected[0]
            proton_charge = o_table.get_item_str_from_cell(row=first_previous_row_selected, column=1)

            clean_list_of_rows_selected.append(rows_selected[0])
            for _row in rows_selected[1:]:
                if o_table.get_item_str_from_cell(row=_row, column=1) == proton_charge:
                    clean_list_of_rows_selected.append(_row)

            for _row in rows_selected:
                _file_name = o_table.get_item_str_from_cell(row=_row, column=0)
                list_obs_selected.append(_file_name)

        else:
            o_table.enable_all_rows(enabled=True)

        self.parent.list_obs_selected = list_obs_selected
        o_table.unblock_signals()

    def reset_ob_search_path(self) -> None:
        """
        Reset the search path for OB files based on the selected IPTS.

        This method clears the OB table and sets the search path for OB files
        based on the selected IPTS and instrument.
        """
        logger.info("-> clearing the list of OBs table!")
        o_table = TableHandler(table_ui=self.parent.ui.step1_open_beam_tableWidget)
        o_table.remove_all_rows()
        ipts = self.parent.session_dict[SessionKeys.ipts_selected]
        instrument = self.parent.session_dict[SessionKeys.instrument]
        full_list_path_where_to_look_for_obs = [
            self.parent.homepath,
            instrument,
            ipts,
            "shared",
            "autoreduce",
            "mcp",
        ]
        full_path_where_to_look_for_obs = os.sep.join(full_list_path_where_to_look_for_obs)
        self.parent.ui.existing_ob_top_path.setText(full_path_where_to_look_for_obs)
        self.parent.ui.location_of_ob_created.setText(full_path_where_to_look_for_obs)

    def check_state_of_ob_measured(self) -> None:
        """
        Check the state of the measured OB files.

        This method performs checks on the state of the OB files measured.
        """
        logger.info("Checking the state of the OBs measured.")

    def browse_obs(self) -> None:
        """
        Browse for OB folders/files.

        This method opens a file dialog for the user to select the top folder
        containing OB files and updates the list of OBs based on the selected folder.
        """
        full_path_where_to_look_for_obs = str(self.parent.ui.existing_ob_top_path.text())
        logger.info(f"Looking for OBs folders/files in {full_path_where_to_look_for_obs}")

        top_folder = str(
            QFileDialog.getExistingDirectory(self.parent, "Select OB folder", full_path_where_to_look_for_obs)
        )

        if not top_folder:
            return

        if not os.path.exists(top_folder):
            logger.info("-> folder does not exists!")
            top_folder = os.sep.join([self.parent.homepath, self.parent.session_dict[SessionKeys.instrument]])
            logger.info(f"-> using {top_folder} instead!")

        if top_folder:
            logger.info(f"User changed top OB folder in step 1: {top_folder}")
            self.parent.ui.existing_ob_top_path.setText(top_folder)
            self.update_list_of_obs()

    def update_list_of_obs(self) -> None:
        """
        Update the list of OB folders/files.

        This method clears the OB table and loads the list of OB folders/files
        based on the current top folder path.
        """
        self.clear_ob_table()
        top_folder = self.parent.ui.existing_ob_top_path.text()
        list_folders = list_ob_dirs(top_folder)
        self.load_list_of_folders(list_folders=list_folders)

    def save_list_of_obs_selected(self) -> None:
        """
        Save the list of selected OB files.

        This method retrieves the list of selected OB files from the table
        and saves it to the parent object.
        """
        o_table = TableHandler(table_ui=self.parent.ui.open_beam_tableWidget)
        list_row_selected = o_table.get_rows_of_table_selected()
        _cache_list_obs_selected = self.parent.list_obs_selected
        if list_row_selected:
            list_obs_selected = [o_table.get_item_str_from_cell(row=_row, column=0) for _row in list_row_selected]
            self.parent.list_obs_selected = list_obs_selected
        else:
            logger.warning("Empty list_obs_selected, reverting to previous selection.")
            self.parent.list_obs_selected = _cache_list_obs_selected

    def reselect_the_obs_previously_selected(self) -> None:
        """
        Reselect the previously selected OB files.

        This method reselects the OB files in the table based on the previously
        saved list of selected OB files.
        """
        o_table = TableHandler(table_ui=self.parent.ui.open_beam_tableWidget)
        list_obs_selected = self.parent.list_obs_selected
        nbr_row = o_table.row_count()
        list_row_to_select = []
        for _row in np.arange(nbr_row):
            _file_name = o_table.get_item_str_from_cell(row=_row, column=0)
            if _file_name in list_obs_selected:
                list_row_to_select.append(_row)

        if list_row_to_select:
            o_table.select_rows(list_of_rows=list_row_to_select)

    def clear_ob_table(self) -> None:
        """
        Clear the OB table.

        This method clears all rows in the OB table.
        """
        o_table = TableHandler(table_ui=self.parent.ui.open_beam_tableWidget)
        o_table.block_signals()
        o_table.remove_all_rows()
        o_table.unblock_signals()

    def load_list_of_folders(self, list_folders: Optional[List[str]]) -> None:
        """
        Load the list of OB folders into the table.

        Parameters
        ----------
        list_folders : list of str, optional
            The list of OB folder paths to load into the table.
        """
        if list_folders is None:
            return

        # proton_charge_requested_for_projections = self.parent.ui.open_beam_proton_charge_doubleSpinBox.value()

        list_proton_charge = []
        for _folder in list_folders:
            _proton_charge = EventHandler.retrieve_proton_charge_for_that_folder(_folder)
            list_proton_charge.append(_proton_charge)

        o_table = TableHandler(table_ui=self.parent.ui.open_beam_tableWidget)
        for _offset_row, _folder in enumerate(list_folders):
            o_table.insert_empty_row(row=_offset_row)
            o_table.insert_item(row=_offset_row, column=0, value=_folder)

            if is_float(list_proton_charge[_offset_row]):
                enabled = True

                o_table.insert_item(row=_offset_row, column=1, value=f"{list_proton_charge[_offset_row]:.2f}")

                o_table.set_item_enabled(row=_offset_row, column=1, enabled=enabled)
                o_table.set_item_enabled(row=_offset_row, column=0, enabled=enabled)

            else:
                o_table.insert_item(row=_offset_row, column=1, value="N/A")

                o_table.set_item_enabled(row=_offset_row, column=1, enabled=False)
                o_table.set_item_enabled(row=_offset_row, column=0, enabled=False)

    @staticmethod
    def retrieve_proton_charge_for_that_folder(folder: str) -> Union[str, float]:
        """
        Retrieve the proton charge for a given folder.

        This method looks for a summary.json file in the given folder and retrieves
        the proton charge value if available. If not found, it returns "N/A".

        Parameters
        ----------
        folder : str
            The folder path to look for the summary.json file.

        Returns
        -------
        str or float
            The proton charge value in Coulombs, or "N/A" if not found.
        """
        json_file = glob.glob(folder + os.sep + "summary.json")
        if len(json_file) == 0:
            return "N/A"

        json_file = json_file[0]
        if not os.path.exists(json_file):
            return "N/A"

        with open(json_file, "r") as f:
            data = json.load(f)

        proton_charge = data.get("proton_charge", "N/A")
        if proton_charge == "N/A":
            return proton_charge

        proton_charge_value = proton_charge["value"]
        proton_charge_units = proton_charge["units"]
        if proton_charge_units.lower() == "pc":
            coeff = 1e-12
        elif proton_charge_units == "nc":
            coeff = 1e-9
        else:
            raise NotImplementedError("Unit of proton charge not supported yet!")

        proton_charge = float(proton_charge_value) * coeff
        return proton_charge
