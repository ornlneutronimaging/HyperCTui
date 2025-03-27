#!/usr/bin/env python
"""
Initialization module for pre-processing monitor.

This module handles the setup and initialization of the monitoring interface
for open beam (OB) acquisition and projection data preprocessing.
It populates tables with status information and configures the UI components.
"""

import os
from typing import List, Optional

import numpy as np
from qtpy.QtWidgets import QProgressBar, QPushButton

from hyperctui.pre_processing_monitor import IN_PROGRESS, IN_QUEUE, READY, ColorDataStatus, DataStatus
from hyperctui.pre_processing_monitor.event_handler import EventHandler
from hyperctui.pre_processing_monitor.get import Get as GetMonitor
from hyperctui.session import SessionKeys
from hyperctui.setup_ob.get import Get as GetOB
from hyperctui.utilities.get import Get
from hyperctui.utilities.table import TableHandler


class Initialization:
    """
    Class for initializing the pre-processing monitoring interface.

    Handles the setup of UI components and data for monitoring the
    pre-processing of open beam images and projections.

    Attributes
    ----------
    first_in_queue_is_projections : bool
        Flag indicating if projections are first in the processing queue
    parent : object
        The parent widget that contains this initialization
    grand_parent : object
        The top-level parent widget
    """

    first_in_queue_is_projections = True

    def __init__(self, parent: Optional[object] = None, grand_parent: Optional[object] = None) -> None:
        """
        Initialize the class with parent references.

        Parameters
        ----------
        parent : object, optional
            The parent widget
        grand_parent : object, optional
            The top-level parent widget
        """
        self.parent = parent
        self.grand_parent = grand_parent

    def data(self) -> None:
        """
        Initialize the data for monitoring pre-processing.

        This method determines the list of NeXus files already available
        and how many are expected. It populates the tables with open beam
        and projection data based on the current application state.
        """
        if self.grand_parent.ui.ob_tabWidget.currentIndex() == 0:
            # we want to take new obs
            nbr_obs_expected = self.grand_parent.ui.number_of_ob_spinBox.value()
            self.first_in_queue_is_projections = False
            self.populate_table_with_expected_obs(nbr_obs_expected=nbr_obs_expected)
        else:
            # we will use the one we selected
            # retrieve list of ob selected
            o_get_ob = GetOB(parent=self.grand_parent)
            list_ob = o_get_ob.list_ob_folders_selected()
            # remove the Run_* part
            list_ob = [os.path.dirname(_folder) for _folder in list_ob]
            self.populate_table_with_existing_obs(list_ob=list_ob)
            o_event = EventHandler(parent=self.parent, grand_parent=self.grand_parent)
            o_event.checking_status_of_expected_projections()

        folder_path = self.grand_parent.folder_path
        self.populate_table_with_expected_projections()

        initial_list_of_reduction_log_files = Get.list_of_files(folder=folder_path.reduction_log, ext="*")
        self.parent.initial_list_of_reduction_log_files = initial_list_of_reduction_log_files

        self.parent.ui.final_ob_folder_label.setText(self.grand_parent.ui.final_location_of_ob_created.text())
        self.parent.ui.final_ob_folder_status.setText(DataStatus.in_queue)
        self.parent.ui.final_ob_folder_status.setStyleSheet(f"background-color: {ColorDataStatus.in_queue}")

    def ui(self) -> None:
        """
        Configure the user interface components.

        Sets up table columns and progress bar for monitoring status.
        """
        table_columns = [540, 80, 80, 80, 100]
        o_ob_table = TableHandler(table_ui=self.parent.ui.obs_tableWidget)
        o_ob_table.set_column_sizes(column_sizes=table_columns)
        o_pro_table = TableHandler(table_ui=self.parent.ui.projections_tableWidget)
        o_pro_table.set_column_sizes(column_sizes=table_columns)

        self.parent.eventProgress = QProgressBar(self.parent.ui.statusbar)
        self.parent.eventProgress.setMinimumSize(20, 14)
        self.parent.eventProgress.setMaximumSize(540, 100)
        self.parent.eventProgress.setVisible(False)
        self.parent.ui.statusbar.addPermanentWidget(self.parent.eventProgress)

    def populate_table_with_expected_obs(self, nbr_obs_expected: int = 2) -> None:
        """
        Populate the table with expected open beam files.

        Initializes the table with placeholder OB file names while waiting
        for actual files to appear.

        Parameters
        ----------
        nbr_obs_expected : int, optional
            Number of expected open beam files, default is 2
        """
        o_table = TableHandler(table_ui=self.parent.ui.obs_tableWidget)
        dict_ob_log_err_metadata = {}

        if self.grand_parent.session_dict[SessionKeys.obs_have_been_moved_already]:
            list_ob_expected = self.grand_parent.session_dict[SessionKeys.list_ob_folders_requested]
            new_location = os.path.abspath(self.grand_parent.ui.final_location_of_ob_created.text())
            new_list_ob_expected = []
            for _folder in list_ob_expected:
                folder_name = os.path.basename(_folder)
                new_folder_name = os.path.join(new_location, folder_name)
                new_list_ob_expected.append(new_folder_name)

            # hide the widgets relative to moving the obs
            self.parent.ui.monitor_moving_obs_label.setVisible(False)
            self.parent.ui.final_ob_folder_label.setVisible(False)
            self.parent.ui.final_ob_folder_status.setVisible(False)

            list_ob_expected = new_list_ob_expected

        else:
            ob_base_name = self.grand_parent.ui.location_of_ob_created.text() + os.path.sep
            list_ob_expected = self.grand_parent.session_dict[SessionKeys.list_ob_folders_requested]

        if not self.grand_parent.session_dict[SessionKeys.list_ob_folders_requested]:
            # first time figuring out the name of the files
            list_ob_expected = []
            for _row_index in np.arange(nbr_obs_expected):
                # _ob_name = f"{ob_base_name}{_row_index:03d}"
                _ob_name = f"{ob_base_name}<OB file #{_row_index}>"
                list_ob_expected.append(_ob_name)

            # self.grand_parent.session_dict[SessionKeys.list_ob_folders_requested] = list_ob_expected

        # populating the table
        for _row_index, _ob_name in enumerate(list_ob_expected):
            o_table.insert_empty_row(row=_row_index)
            o_table.insert_item(row=_row_index, column=0, value=_ob_name)
            if _row_index == 0:
                message = DataStatus.in_progress
                color = IN_PROGRESS
            else:
                message = DataStatus.in_queue
                color = IN_QUEUE
            o_table.insert_item(row=_row_index, column=4, value=message)
            o_table.set_background_color(row=_row_index, column=4, qcolor=color)
            dict_ob_log_err_metadata[_row_index] = {
                "file_name": _ob_name,
                "log_file": "",
                "err_file": "",
                "metadata_file": "",
            }
        self.parent.dict_ob_log_err_metadata = dict_ob_log_err_metadata

    def populate_table_with_existing_obs(self, list_ob: Optional[List[str]] = None) -> None:
        """
        Populate the table with existing open beam folders.

        Sets up the table with information about existing OB files
        including references to log files, error files, and metadata.

        Parameters
        ----------
        list_ob : list of str, optional
            List of paths to existing open beam folders
        """
        if list_ob is None:
            return

        o_table = TableHandler(table_ui=self.parent.ui.obs_tableWidget)
        o_get = GetMonitor(parent=self.parent, grand_parent=self.grand_parent)
        dict_ob_log_err_metadata = {}

        for _row_index, _ob in enumerate(list_ob):
            o_get.set_ob(full_ob_folder_name=_ob)

            o_table.insert_empty_row(row=_row_index)
            o_table.insert_item(row=_row_index, column=0, value=_ob)

            log_file = o_get.log_file()
            if log_file:
                enable_button = True
            else:
                enable_button = False

            log_button = QPushButton("View")
            log_button.setEnabled(enable_button)
            o_table.insert_widget(row=_row_index, column=1, widget=log_button)

            log_button.clicked.connect(lambda state=0, row=_row_index: self.parent.preview_log(row=row, data_type="ob"))
            err_file = o_get.err_file()
            if err_file:
                enable_button = True
            else:
                enable_button = False

            err_button = QPushButton("View")
            err_button.setEnabled(enable_button)
            o_table.insert_widget(row=_row_index, column=2, widget=err_button)
            err_button.clicked.connect(lambda state=0, row=_row_index: self.parent.preview_err(row=row, data_type="ob"))

            metadata_file = o_get.metadata_file()
            if metadata_file:
                enable_button = True
            else:
                enable_button = False

            summary_button = QPushButton("View")
            summary_button.setEnabled(enable_button)
            o_table.insert_widget(row=_row_index, column=3, widget=summary_button)
            summary_button.clicked.connect(
                lambda state=0, row=_row_index: self.parent.preview_summary(row=row, data_type="ob")
            )

            o_table.insert_item(row=_row_index, column=4, value=DataStatus.ready)
            o_table.set_background_color(row=_row_index, column=4, qcolor=READY)

            dict_ob_log_err_metadata[_row_index] = {
                "file_name": _ob,
                "log_file": log_file,
                "err_file": err_file,
                "metadata_file": metadata_file,
            }

        # hide the widgets relative to moving the obs
        self.parent.ui.monitor_moving_obs_label.setVisible(False)
        self.parent.ui.final_ob_folder_label.setVisible(False)
        self.parent.ui.final_ob_folder_status.setVisible(False)

        self.parent.dict_ob_log_err_metadata = dict_ob_log_err_metadata

    def populate_table_with_expected_projections(self) -> None:
        """
        Populate the table with expected projection files.

        Creates placeholder entries for projections and sets their
        initial status in the monitoring UI. Typically includes
        projections at 0 and 180 degrees.
        """
        o_table = TableHandler(table_ui=self.parent.ui.projections_tableWidget)

        dict_projections_log_err_metadata = {}

        title = self.grand_parent.ui.run_title_formatted_label.text()

        output_folder = os.path.dirname(str(self.grand_parent.ui.projections_output_location_label.text()))
        first_projection_name = os.path.join(output_folder, "<projection angle 0 degree>")
        last_projection_name = os.path.join(output_folder, "<projection angle 180 degree>")

        for _row_index, file_name in enumerate([first_projection_name, last_projection_name]):
            if _row_index == 0:
                if self.first_in_queue_is_projections:
                    message = DataStatus.in_progress
                    color = IN_PROGRESS
                else:
                    message = DataStatus.in_queue
                    color = IN_QUEUE
            else:
                message = DataStatus.in_queue
                color = IN_QUEUE

            o_table.insert_empty_row(row=_row_index)
            o_table.insert_item(row=_row_index, column=0, value=file_name)

            o_table.insert_item(row=_row_index, column=4, value=message)
            o_table.set_background_color(row=_row_index, column=4, qcolor=color)

            dict_projections_log_err_metadata[_row_index] = {
                "file_name": file_name,
                "log_file": "",
                "err_file": "",
                "metadata_file": "",
            }
        self.parent.dict_projections_log_err_metadata = dict_projections_log_err_metadata
