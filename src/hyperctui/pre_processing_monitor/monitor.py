#!/usr/bin/env python
"""
Monitor module for pre-processing operations in HyperCTui.

This module provides a GUI window for monitoring the status of open beam (OB) images
and projections (0 degree and 180 degrees) during the pre-processing stage of CT
data acquisition and processing.
"""

import logging
import os
from typing import Any, Dict, List, Optional

from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QMainWindow

from hyperctui import load_ui, refresh_large_image
from hyperctui.pre_processing_monitor.event_handler import EventHandler as MonitorEventHandler
from hyperctui.pre_processing_monitor.initialization import Initialization
from hyperctui.preview_file.preview_file_launcher import PreviewFileLauncher, PreviewMetadataFileLauncher
from hyperctui.session import SessionKeys
from hyperctui.utilities.widgets import Widgets as UtilityWidgets


class Monitor(QMainWindow):
    """
    A GUI window for monitoring pre-processing operations.

    This class provides functionality to track and monitor the status of open beam (OB) images
    and projections during acquisition and processing, allowing users to view log files,
    error messages, and summary information.

    Attributes
    ----------
    initial_list_of_reduction_log_files : List[str]
        List of files in the reduction log folder used as reference
    dict_ob_log_err_metadata : Dict[int, Dict[str, str]]
        Dictionary containing OB files with their associated logs, errors, and metadata
    dict_projections_log_err_metadata : Dict[int, Dict[str, str]]
        Dictionary containing projection files with their associated logs, errors, and metadata
    all_obs_found : bool
        Flag indicating if all open beam images have been found
    all_obs_moved : bool
        Flag indicating if all open beam images have been moved to final folder
    all_projections_found : bool
        Flag indicating if all projections have been found
    """

    # list of files in the reduction log folder to use as a reference
    # any new files will be used
    initial_list_of_reduction_log_files: List[str] = []

    # dictionary that looks like
    # {0: { 'file_name': '<full path to ob>',
    #       'log_file': '<full path to log file>',
    #       'err_file': '<full path to err file>',
    #       'metadata_file': <full path to metadata file>',
    #     },
    #  1: { ... },
    #  ...
    # }
    dict_ob_log_err_metadata: Optional[Dict[int, Dict[str, str]]] = None
    dict_projections_log_err_metadata: Optional[Dict[int, Dict[str, str]]] = None

    all_obs_found: bool = False
    all_obs_moved: bool = False
    all_projections_found: bool = False

    def __init__(self, parent: Optional[Any] = None) -> None:
        """
        Initialize the Monitor window.

        Parameters
        ----------
        parent : Any, optional
            Parent widget, by default None
        """
        super(Monitor, self).__init__(parent)
        self.parent = parent

        ui_full_path = os.path.join(os.path.dirname(__file__), os.path.join("../ui", "pre_processing_monitor.ui"))

        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Monitor")

        refresh_icon = QIcon(refresh_large_image)
        self.ui.refresh_pushButton.setIcon(refresh_icon)

        o_init = Initialization(parent=self, grand_parent=self.parent)
        o_init.data()
        o_init.ui()

        self.refresh_button_clicked()

    def preview_log(self, state: int = 0, row: int = -1, data_type: str = "ob") -> None:
        """
        Preview log file for a specific row.

        Parameters
        ----------
        state : int, optional
            Button state, by default 0
        row : int, optional
            Row index in the table, by default -1
        data_type : str, optional
            Type of data ('ob' for open beam), by default "ob"
        """
        log_file = self.dict_ob_log_err_metadata[row]["log_file"]
        preview_file = PreviewFileLauncher(parent=self, file_name=log_file)
        preview_file.show()

    def preview_err(self, state: int = 0, row: int = -1, data_type: str = "ob") -> None:
        """
        Preview error file for a specific row.

        Parameters
        ----------
        state : int, optional
            Button state, by default 0
        row : int, optional
            Row index in the table, by default -1
        data_type : str, optional
            Type of data ('ob' for open beam), by default "ob"
        """
        err_file = self.dict_ob_log_err_metadata[row]["err_file"]
        preview_file = PreviewFileLauncher(parent=self, file_name=err_file)
        preview_file.show()

    def preview_summary(self, state: int = 0, row: int = -1, data_type: str = "ob") -> None:
        """
        Preview metadata summary file for a specific row.

        Parameters
        ----------
        state : int, optional
            Button state, by default 0
        row : int, optional
            Row index in the table, by default -1
        data_type : str, optional
            Type of data ('ob' for open beam), by default "ob"
        """
        file_name = self.dict_ob_log_err_metadata[row]["metadata_file"]
        preview_file = PreviewMetadataFileLauncher(parent=self, file_name=file_name)
        preview_file.show()

    def refresh_button_clicked(self) -> None:
        """
        Handle refresh button click event.

        Updates the monitor with current status of OBs and projections,
        and performs necessary actions based on status.
        """
        logging.info("Updating monitor table (OBs, 0degree and 180degrees projections)!")
        o_event = MonitorEventHandler(parent=self, grand_parent=self.parent)

        if not self.all_obs_found:
            o_event.checking_status_of_expected_obs()

        if self.all_obs_found:
            if not self.all_obs_moved:
                logging.info("-> all obs found!")
                o_event.move_obs_to_final_folder()

                # FIXME for now, hide those buttons
                self.ui.monitor_moving_obs_label.setVisible(False)
                self.ui.final_ob_folder_label.setVisible(False)
                self.ui.final_ob_folder_status.setVisible(False)

            logging.info("Checking status of 0 and 180 degrees projections")
            o_event.checking_status_of_expected_projections()
            if self.all_projections_found:
                logging.info("-> all projections found!")
                if not self.parent.session_dict[SessionKeys.all_tabs_visible]:
                    self.parent.session_dict[SessionKeys.all_tabs_visible] = True
                    o_widgets = UtilityWidgets(parent=self.parent)
                    o_widgets.make_tabs_visible(is_visible=True)
                    self.parent.initialize_crop()
                    self.parent.initialize_center_of_rotation()

    def closeEvent(self, c: Any) -> None:
        """
        Handle window close event.

        Parameters
        ----------
        c : Any
            Close event object
        """
        self.parent.monitor_ui = None
        self.parent.ui.checking_status_acquisition_pushButton.setEnabled(True)
        self.close()
