#!/usr/bin/env python
"""
This module provides event handling for the setup projections part of the HyperCTui application.
It manages run title changes and ensures unique filenames in the MCP folders.
"""

import logging
import os
from typing import Optional, Tuple

from hyperctui.parent import Parent
from hyperctui.utilities.time import get_current_time_in_special_file_name_format


class EventHandler(Parent):
    """
    Event handler for setup projections.

    This class handles events related to the setup projections UI, particularly
    for managing run titles and ensuring filenames are unique.

    Parameters
    ----------
    parent : Parent
        The parent object that contains UI components and other necessary attributes.
    """

    def run_title_changed(self, run_title: Optional[str] = None, checking_if_file_exists: bool = True) -> None:
        """
        Handle changes to the run title in the UI.

        This method formats the run title and checks if the formatted name already
        exists in the filesystem if checking_if_file_exists is True.

        Parameters
        ----------
        run_title : str, optional
            The title of the run to be formatted
        checking_if_file_exists : bool, default=True
            Whether to check if a file with the formatted title already exists

        Returns
        -------
        None
        """
        if (run_title == "") or (run_title == "None"):
            # self.parent.ui.projections_title_message.setVisible(True)
            logging.info("Please provide a valid title string!")
            self.parent.ui.run_title_formatted_label.setText("None")
            return

        run_title_listed = run_title.split(" ")
        formatted_run_title = "_".join(run_title_listed)

        if checking_if_file_exists:
            formatted_run_title, show_label_ui = self.produce_unused_formatted_run_title(formatted_run_title)
        else:
            show_label_ui = False

        self.parent.ui.run_title_formatted_label.setText(formatted_run_title)
        self.parent.ui.projections_title_message.setVisible(show_label_ui)

    def produce_unused_formatted_run_title(self, run_title: str) -> Tuple[str, bool]:
        """
        Generate a unique formatted run title.

        This will retrieve the mcp_raw location and look if the run_title exists there.
        If it doesn't, it will return the run_title.
        If it does, it will add a date/time stamp.

        Parameters
        ----------
        run_title : str
            The formatted run title to check for uniqueness

        Returns
        -------
        tuple[str, bool]
            A tuple containing:
            - The new file name (original or with timestamp)
            - A boolean indicating if the file name has been changed (True) or not (False)
        """
        o_path = self.parent.folder_path
        mcp_raw = o_path.mcp_raw
        mcp = o_path.mcp

        full_file_name = os.path.join(mcp_raw, run_title)

        if not os.path.exists(full_file_name):
            return run_title, False

        mcp_raw_full_file_name = os.path.join(mcp_raw, run_title)
        autoreduce_full_file_name = os.path.join(mcp, run_title)
        if (not os.path.exists(mcp_raw_full_file_name)) and (not os.path.exists(autoreduce_full_file_name)):
            return run_title, False

        time_suffix = get_current_time_in_special_file_name_format()
        return f"{run_title}_{time_suffix}", True
