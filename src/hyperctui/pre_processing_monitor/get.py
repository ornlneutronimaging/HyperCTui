#!/usr/bin/env python
"""
Provides utilities for retrieving and manipulating file paths for preprocessing monitoring.

This module contains the Get class that handles setting and retrieving paths for
open beam folders, run numbers, log files, error files, metadata files, and preview files.
"""

import glob
import os
from typing import Optional

from hyperctui.session import SessionKeys


class Get:
    """
    A class to handle retrieval of various file paths for preprocessing monitoring.

    Attributes
    ----------
    full_ob_folder_name : str or None
        Full path to the open beam folder, typically follows the pattern
        /SNS/VENUS/IPTS-XXX/shared/autoreduce/mcp/scanYY/Run_ZZZZZ
    run_number_full_path : str or None
        Full path to the run number directory
    run_number : str or None
        The run number extracted from the folder path
    """

    # will look like /SNS/VENUS/IPTS-30023/shared/autoreduce/mcp/scan17/Run_57100
    full_ob_folder_name: Optional[str] = None
    run_number_full_path: Optional[str] = None

    def __init__(self, parent=None, grand_parent=None):
        """
        Initialize the Get class.

        Parameters
        ----------
        parent : object, optional
            Reference to the parent object
        grand_parent : object, optional
            Reference to the grand parent object
        """
        self.parent = parent
        self.grand_parent = grand_parent
        self.folder_path = grand_parent.folder_path

    def set_ob(self, full_ob_folder_name: Optional[str] = None) -> None:
        """
        Set the open beam folder and derive related paths.

        Parameters
        ----------
        full_ob_folder_name : str, optional
            Full path to the open beam folder
        """
        self.set_path(full_ob_folder_name=full_ob_folder_name)

    def set_path(self, full_ob_folder_name: Optional[str] = None) -> None:
        """
        Set the path for open beam folder and run number.

        Parameters
        ----------
        full_ob_folder_name : str, optional
            Full path to the open beam folder
        """
        self.set_ob_folder_name(full_ob_folder_name=full_ob_folder_name)
        self.set_run_number()

    def set_run_number(self) -> None:
        """
        Extract and set the run number from the folder path.

        The method extracts run number from a path like:
        "/SNS/VENUS/IPTS_0445345/shared/autoreduce/OB_test_10001/run_10001"
        and sets self.run_number to "10001"
        """
        list_runs = glob.glob(self.full_ob_folder_name + "/Run_*")
        self.run_number_full_path = list_runs[0]
        split_folder_path = list_runs[0].split("/")
        _, run_number = split_folder_path[-1].split("_")
        self.run_number = run_number

    def set_ob_folder_name(self, full_ob_folder_name: Optional[str] = None) -> None:
        """
        Set the full open beam folder name.

        Parameters
        ----------
        full_ob_folder_name : str, optional
            Full path to the open beam folder
        """
        self.full_ob_folder_name = os.path.abspath(full_ob_folder_name)

    def set_run_number_full_path(self) -> None:
        """
        Set the full path to the run number directory.

        Searches for directories that match 'Run*' pattern in the open beam folder
        and sets the first match as the run number full path.
        """
        full_ob_folder_name = self.full_ob_folder_name
        list_runs = glob.glob(os.path.join(full_ob_folder_name, "Run*"))
        self.run_number_full_path = list_runs[0]

    def log_file(self) -> str:
        """
        Get the log file path.

        For a path like /SNS/VENUS/IPTS-30023/shared/autoreduce/mcp/scan17/Run_57100
        it needs to return
        /SNS/VENUS/IPTS-30023/shared/autoreduce/reduction_log/VENUS_57100.nxs.h5.log

        Returns
        -------
        str
            Path to the log file
        """
        prefix = self.log_err_prefix()
        return prefix + ".log"

    def log_err_prefix(self) -> str:
        """
        Get the common prefix for log and err files.

        For a path like /SNS/VENUS/IPTS-30023/shared/autoreduce/mcp/scan17/Run_57100
        it will return
        /SNS/VENUS/IPTS-30023/shared/autoreduce/reduction_log/VENUS_57100.nxs.h5

        Returns
        -------
        str
            Common prefix for log and error files
        """
        folder = self.folder_path.reduction_log
        run_number = self.run_number
        instrument = self.grand_parent.session_dict[SessionKeys.instrument]
        return os.path.join(folder, f"{instrument}_{run_number}.nxs.h5")

    def err_file(self) -> str:
        """
        Get the error file path.

        For a path like /SNS/VENUS/IPTS-30023/shared/autoreduce/mcp/scan17/Run_57100
        it needs to return
        /SNS/VENUS/IPTS-30023/shared/autoreduce/reduction_log/VENUS_57100.nxs.h5.err

        Returns
        -------
        str
            Path to the error file
        """
        prefix = self.log_err_prefix()
        return prefix + ".err"

    def metadata_file(self) -> str:
        """
        Get the metadata file path.

        For a path like /SNS/VENUS/IPTS-30023/shared/autoreduce/mcp/scan17/Run_57100
        it needs to return
        /SNS/VENUS/IPTS-30023/shared/autoreduce/mcp/scan17/Run_57100/summary.json

        Returns
        -------
        str
            Path to the metadata file (summary.json)
        """
        return os.path.join(self.run_number_full_path, "summary.json")

    def preview_file(self) -> Optional[str]:
        """
        Get the preview image file path.

        For a path like /SNS/VENUS/IPTS-30023/shared/autoreduce/mcp/scan17/Run_57100
        it needs to return
        /SNS/VENUS/IPTS-30023/shared/autoreduce/mcp/scan17/Run_57100/*_SummedImg.fits

        Returns
        -------
        str or None
            Path to the preview image file if found, None otherwise
        """
        list_summed_files = glob.glob(os.path.join(self.run_number_full_path, "*_SummedImg.fits"))
        if list_summed_files:
            return list_summed_files[0]
        else:
            return None
