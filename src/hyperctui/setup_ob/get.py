"""
Module for retrieving and managing Open Beam (OB) related data in HyperCT.

This module provides functionalities to list and access IPTS (Instrument Proposal Tracking System),
open beam configurations, and various folders related to the data acquisition and processing.
"""

import glob
import logging
import os
from typing import List, Optional, Union

from hyperctui.utilities.get import Get as MasterGet
from hyperctui.utilities.table import TableHandler


class Get(MasterGet):
    """
    Class for retrieving Open Beam (OB) configuration data and paths.

    Extends the MasterGet class with specific functionalities for handling
    open beam configurations, IPTSs, and related file paths.
    """

    def list_of_ipts(self, instrument: str, facility: str) -> List[str]:
        """
        Return the list of IPTS for the specified instrument.

        Parameters
        ----------
        instrument : str
            Name of the instrument
        facility : str
            Name of the facility (SNS or HFIR)

        Returns
        -------
        List[str]
            List of IPTS names (e.g., ['IPTS-0001', 'IPTS-0002'])
        """
        logging.info("list of IPTS:")
        home_folder = self.parent.homepath
        logging.info(f"-> home_folder: {home_folder}")
        logging.info(f"-> looking ipts in {os.path.join(home_folder + '/' + facility, instrument + '/IPTS-*') =}")
        full_path_list_ipts = glob.glob(os.path.join(home_folder + "/" + facility, instrument + "/IPTS-*"))
        logging.info(f"-> full_path_list_ipts: {full_path_list_ipts}")
        list_ipts = [os.path.basename(_folder) for _folder in full_path_list_ipts]
        list_ipts.sort()
        return list_ipts

    @staticmethod
    def facility(instrument: str) -> str:
        """
        Determine the facility based on instrument name.

        Parameters
        ----------
        instrument : str
            Name of the instrument

        Returns
        -------
        str
            Facility name ("HFIR" or "SNS")
        """
        if instrument == "MARS":
            return "HFIR"
        else:
            return "SNS"

    def number_of_obs(self) -> int:
        """
        Get the number of open beams specified in the UI.

        Returns
        -------
        int
            Number of open beams
        """
        return self.parent.ui.number_of_ob_spinBox.value()

    def proton_charge(self) -> Union[float, str]:
        """
        Get the proton charge value based on the selected OB tab.

        If the first OB tab is selected, returns the value of the proton charge requested.
        If the second OB tab is selected, uses the first row selected (if any) and returns
        the value of the proton charge.

        Returns
        -------
        Union[float, str]
            Proton charge value or "N/A" if not available
        """

        if self.ob_tab_selected() == 0:
            return self.parent.ui.open_beam_proton_charge_doubleSpinBox.value()

        else:
            o_table = TableHandler(table_ui=self.parent.ui.open_beam_tableWidget)
            nbr_row = o_table.row_count()
            if nbr_row == 0:
                logging.info(
                    "Unable to retrieve OB proton charge from empty table (1- Setup the open beams / Select OBs)"
                )
                return "N/A"

            selected_rows = o_table.get_rows_of_table_selected()
            if selected_rows is None:
                return "N/A"

            proton_charge = o_table.get_item_str_from_cell(row=selected_rows[0], column=1)
            return proton_charge

    def top_ob_folder(self) -> str:
        """
        Get the top-level open beam folder path.

        Returns
        -------
        str
            Path to the top-level open beam folder
        """
        return str(self.parent.ui.existing_ob_top_path.text())

    def list_folders_in_output_directory(self, output_folder: Optional[str] = None) -> List[str]:
        """
        List all folders in the specified output directory.

        Parameters
        ----------
        output_folder : str, optional
            Path to the output directory

        Returns
        -------
        List[str]
            List of folder paths in the output directory
        """
        list_raw = glob.glob(output_folder + os.sep + "*")
        list_folders = []
        for _entry in list_raw:
            if os.path.isdir(_entry):
                list_folders.append(_entry)
        return list_folders

    def list_ob_folders_in_output_directory(self, output_folder: Optional[str] = None, title: str = "") -> List[str]:
        """
        List all open beam folders in the specified output directory.

        Parameters
        ----------
        output_folder : str, optional
            Path to the output directory
        title : str, optional
            Title filter for folder names

        Returns
        -------
        List[str]
            List of open beam folder paths
        """
        list_folders = self.list_folders_in_output_directory(output_folder=output_folder)
        list_ob_folders = []
        for _folder in list_folders:
            base_folder = os.path.basename(_folder)
            if ("ob" in base_folder.lower()) and (title in base_folder):
                list_ob_folders.append(_folder)
        return list_ob_folders

    def list_sample_folders_in_output_directory(
        self, output_folder: Optional[str] = None, title: str = ""
    ) -> List[str]:
        """
        List all sample folders in the specified output directory.

        Parameters
        ----------
        output_folder : str, optional
            Path to the output directory
        title : str, optional
            Title filter for folder names

        Returns
        -------
        List[str]
            List of sample folder paths
        """
        list_folders = self.list_folders_in_output_directory(output_folder=output_folder)
        list_sample_folders = []
        for _folder in list_folders:
            base_folder = os.path.basename(_folder)
            if ("ob" not in base_folder.lower()) and (title in base_folder):
                list_sample_folders.append(_folder)
        return list_sample_folders

    def list_ob_folders_selected(self, output_folder: Optional[str] = None) -> List[str]:
        """
        Get the list of selected open beam folders.

        Parameters
        ----------
        output_folder : str, optional
            Path to the output directory (not used, kept for API consistency)

        Returns
        -------
        List[str]
            List of selected open beam folder paths
        """
        o_table = TableHandler(table_ui=self.parent.ui.open_beam_tableWidget)
        list_row_selected = o_table.get_rows_of_table_selected()
        if not list_row_selected:
            return []

        list_folders = []
        for _row in list_row_selected:
            _folder = o_table.get_item_str_from_cell(row=_row, column=0)
            list_folders.append(_folder)
        return list_folders

    def ob_tab_selected(self) -> int:
        """
        Get the index of the currently selected open beam tab.

        Returns
        -------
        int
            Index of the selected open beam tab
        """
        return self.parent.ui.ob_tabWidget.currentIndex()

    def ob_will_be_moved_to(self) -> str:
        """
        Get the destination path where open beam files will be moved.

        Returns
        -------
        str
            Path where open beam files will be moved
        """
        return str(self.parent.ui.final_location_of_ob_created.text())

    def ob_will_be_saved_as(self) -> str:
        """
        Get the path where open beam files will be initially saved.

        Returns
        -------
        str
            Path where open beam files will be initially saved
        """
        return str(self.parent.ui.location_of_ob_created.text())

    def projection_folder(self) -> str:
        """
        Get the location where projections will be saved.

        Returns
        -------
        str
            Path to the projections folder
        """
        folder = str(self.parent.ui.projections_output_location_label.text())
        return folder

    def ob_folder(self) -> str:
        """
        Get the location of the open beam folder.

        Returns
        -------
        str
            Path to the open beam folder
        """
        return str(self.parent.ui.location_of_ob_created.text())
