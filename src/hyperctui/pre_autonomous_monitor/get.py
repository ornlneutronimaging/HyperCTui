#!/usr/bin/env python
"""
File path handling utilities for pre-autonomous monitoring.

This module provides functionality to resolve paths to log files, error files, and metadata
based on the observation folder structure for instrument data processing.
"""

import glob
import os
from typing import Any, List, Optional

from hyperctui.session import SessionKeys


class Get:
    """
    Utility class for retrieving file paths related to data processing.

    This class handles path resolution for log files, error files, and metadata files
    based on the observation folder structure.

    Attributes
    ----------
    full_ob_folder_name : str
        Path to the observation folder, typically following the pattern:
        /SNS/VENUS/IPTS-30023/shared/autoreduce/mcp/scan17/Run_57100
    run_number_full_path : str
        Full path to the run directory
    parent : Any
        Reference to the parent object
    grand_parent : Any
        Reference to the grand parent object
    folder_path : Any
        Reference to the folder path from the grand parent
    """

    # will look like /SNS/VENUS/IPTS-30023/shared/autoreduce/mcp/scan17/Run_57100
    full_ob_folder_name: Optional[str] = None
    run_number_full_path: Optional[str] = None

    def __init__(self, parent: Optional[Any] = None, grand_parent: Optional[Any] = None):
        """
        Initialize the Get class.

        Parameters
        ----------
        parent : Any, optional
            Reference to the parent object
        grand_parent : Any, optional
            Reference to the grand parent object which contains folder_path
        """
        self.parent = parent
        self.grand_parent = grand_parent
        self.folder_path = grand_parent.folder_path

    def set_path(self, full_ob_folder_name: Optional[str] = None) -> None:
        """
        Set the observation folder path and resolve the run number path.

        Parameters
        ----------
        full_ob_folder_name : str, optional
            Path to the observation folder
        """
        self.set_ob_folder_name(full_ob_folder_name=full_ob_folder_name)
        self.set_run_number_full_path()

    def set_ob_folder_name(self, full_ob_folder_name: Optional[str] = None) -> None:
        """
        Set the observation folder name using the absolute path.

        Parameters
        ----------
        full_ob_folder_name : str, optional
            Path to the observation folder
        """
        self.full_ob_folder_name = os.path.abspath(full_ob_folder_name)

    def set_run_number_full_path(self) -> None:
        """
        Set the run number full path based on the observation folder.

        Finds the first directory matching "Run*" pattern in the observation folder.
        """
        full_ob_folder_name = self.full_ob_folder_name
        list_runs: List[str] = glob.glob(os.path.join(full_ob_folder_name, "Run*"))
        self.run_number_full_path = list_runs[0]

    def log_file(self) -> str:
        """
        Get the path to the log file.

        Returns
        -------
        str
            Path to the log file

        Examples
        --------
        If full_ob_folder_name is:
            /SNS/VENUS/IPTS-30023/shared/autoreduce/mcp/scan17/Run_57100
        It will return:
            /SNS/VENUS/IPTS-30023/shared/autoreduce/reduction_log/VENUS_57100.nxs.h5.log
        """
        prefix = self.log_err_prefix()
        return prefix + ".log"

    def log_err_prefix(self) -> str:
        """
        Get the common prefix for log and error files.

        Returns
        -------
        str
            Common prefix path for log and error files

        Examples
        --------
        If full_ob_folder_name is:
            /SNS/VENUS/IPTS-30023/shared/autoreduce/mcp/scan17/Run_57100
        It will return:
            /SNS/VENUS/IPTS-30023/shared/autoreduce/reduction_log/VENUS_57100.nxs.h5
        """
        folder = self.folder_path.reduction_log
        base_file_name = os.path.basename(self.run_number_full_path)
        _, run_number = base_file_name.split("_")
        instrument = self.grand_parent.session_dict[SessionKeys.instrument]
        return os.path.join(folder, f"{instrument}_{run_number}.nxs.h5")

    def err_file(self) -> str:
        """
        Get the path to the error file.

        Returns
        -------
        str
            Path to the error file

        Examples
        --------
        If full_ob_folder_name is:
            /SNS/VENUS/IPTS-30023/shared/autoreduce/mcp/scan17/Run_57100
        It will return:
            /SNS/VENUS/IPTS-30023/shared/autoreduce/reduction_log/VENUS_57100.nxs.h5.err
        """
        prefix = self.log_err_prefix()
        return prefix + ".err"

    def metadata_file(self) -> str:
        """
        Get the path to the metadata file.

        Returns
        -------
        str
            Path to the summary.json metadata file

        Examples
        --------
        If full_ob_folder_name is:
            /SNS/VENUS/IPTS-30023/shared/autoreduce/mcp/scan17/Run_57100
        It will return:
            /SNS/VENUS/IPTS-30023/shared/autoreduce/mcp/scan17/Run_57100/summary.json
        """
        return os.path.join(self.run_number_full_path, "summary.json")
