#!/usr/bin/env python
"""
This module provides functionality for managing folder paths within the HyperCTui project.

It contains the FolderPath class which is responsible for creating and maintaining
paths to various directories required for data processing, reconstruction, and storage.
The module handles path construction based on session parameters such as instrument
and IPTS (Integrated Proposal Tracking System) information.
"""

import os
from typing import Optional

from hyperctui.parent import Parent
from hyperctui.session import SessionKeys
from hyperctui.setup_ob.get import Get

RECONSTRUCTION_CONFIG = "reconstruction_config.json"


class FolderPath(Parent):
    """
    This class retrieves paths to various folders of the project.

    Attributes
    ----------
    ipts_full_path : str
        Full path to the IPTS directory
    root : str
        Root path of the project
    shared : str
        Path to the shared directory
    autoreduce : str
        Path to the autoreduce directory
    mcp : str
        Path to the mcp directory
    reduction_log : str
        Path to the reduction log directory
    nexus : str
        Path to the nexus directory
    mcp_raw : str
        Path to the mcp_raw directory
    recon : str
        Path to the reconstruction directory
    reconstruction_config : str
        Path to the reconstruction configuration file
    """

    ipts_full_path: Optional[str] = None

    root: Optional[str] = None
    shared: Optional[str] = None
    autoreduce: Optional[str] = None
    mcp: Optional[str] = None
    reduction_log: Optional[str] = None
    nexus: Optional[str] = None
    mcp_raw: Optional[str] = None
    recon: Optional[str] = None
    reconstruction_config: Optional[str] = None  # json file created/updated by Shimin's code

    def update(self) -> None:
        """
        Update all folder paths based on current session parameters.

        This method uses the current session information (ipts, instrument, etc.)
        to construct all the necessary folder paths for the project.

        Returns
        -------
        None
        """
        homepath = self.parent.homepath
        self.root = homepath
        ipts = self.parent.session_dict[SessionKeys.ipts_selected]
        instrument = self.parent.session_dict[SessionKeys.instrument]

        o_get = Get(parent=self.parent)
        facility = o_get.facility(instrument=instrument)

        title = self.parent.session_dict.get(SessionKeys.run_title, "")

        if (instrument is None) | (ipts is None):
            return

        self.ipts_full_path = os.path.abspath(os.sep.join([homepath, facility, instrument, ipts]))

        self.shared()
        self.autoreduce()
        self.reduction_log()
        self.nexus()
        self.mcp()
        self.recon(title=title)
        self.create_mcp_raw()
        self.svmbir_config(title=title)

    def __repr__(self) -> str:
        """
        Return a string representation of the folder paths.

        Returns
        -------
        str
            String representation of all folder paths
        """
        return (
            "folder_path:\n" + f"- shared:  \t\t{self.shared}\n"
            f"- autoreduce:  \t{self.autoreduce}\n" + f"- mcp:  \t\t{self.mcp}\n"
            f"- reduction_log:{self.reduction_log}\n"
            f"- nexus:  \t\t{self.nexus}\n" + f"- mcp_raw:  \t{self.mcp_raw}\n"
            f"- recon:  \t\t{self.recon}\n"
            f"- reconstruction_config: {self.reconstruction_config}\n"
        )

    def shared(self) -> None:
        """
        Set the path to the shared directory.

        Returns
        -------
        None
        """
        self.shared = os.sep.join([self.ipts_full_path, "shared"])

    def autoreduce(self) -> None:
        """
        Set the path to the autoreduce directory.

        Returns
        -------
        None
        """
        self.autoreduce = os.sep.join([self.shared, "autoreduce"])

    def reduction_log(self) -> None:
        """
        Set the path to the reduction log directory.

        Returns
        -------
        None
        """
        self.reduction_log = os.sep.join([self.autoreduce, "reduction_log"])

    def nexus(self) -> None:
        """
        Set the path to the nexus directory.

        Returns
        -------
        None
        """
        self.nexus = os.sep.join([self.ipts_full_path, "nexus"])

    def mcp(self) -> None:
        """
        Set the path to the mcp directory.

        Returns
        -------
        None
        """
        self.mcp = os.sep.join([self.autoreduce, "mcp"])

    def recon(self, title: Optional[str] = None) -> None:
        """
        Set the path to the reconstruction directory.

        Parameters
        ----------
        title : str, optional
            Run title used in the path, by default None

        Returns
        -------
        None
        """
        self.recon = os.sep.join([self.shared, "insitu_recon", title, "recon"])

    def create_mcp_raw(self) -> None:
        """
        Set the path to the mcp_raw directory.

        Returns
        -------
        None
        """
        self.mcp_raw = os.sep.join([self.ipts_full_path, "images", "mcp"])

    def svmbir_config(self, title: Optional[str] = None) -> None:
        """
        Set the path to the reconstruction configuration file.

        Parameters
        ----------
        title : str, optional
            Run title used in the path, by default None

        Returns
        -------
        None
        """
        self.reconstruction_config = os.sep.join([self.shared, "insitu_recon", title, RECONSTRUCTION_CONFIG])
