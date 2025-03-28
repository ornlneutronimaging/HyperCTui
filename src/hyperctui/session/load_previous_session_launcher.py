#!/usr/bin/env python
"""
Module for launching a dialog that prompts users to load a previous session.

This module contains the LoadPreviousSessionLauncher class which handles the UI
and logic for allowing users to decide whether to load a previous session or
start a new one.
"""

import os
from typing import Any, Optional

from qtpy.QtWidgets import QDialog

from hyperctui import load_ui
from hyperctui.session.session_handler import SessionHandler
from hyperctui.utilities.folder_path import FolderPath
from hyperctui.utilities.get import Get


class LoadPreviousSessionLauncher(QDialog):
    """
    Dialog to prompt users to load a previous session.

    This dialog presents users with the option to either load a previous session
    or start a new one. It handles the initialization of a session based on the
    user's choice.

    Parameters
    ----------
    parent : Any, optional
        The parent widget. Default is None.
    config : Any, optional
        Configuration settings. Default is None.
    """

    def __init__(self, parent: Optional[Any] = None, config: Optional[Any] = None) -> None:
        self.parent = parent
        QDialog.__init__(self, parent=parent)
        ui_full_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), os.path.join("ui", "load_previous_session.ui")
        )
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Load previous session?")
        self.ui.pushButton.setFocus(True)
        # self.ui.no_pushButton.setFocus(True)

    def yes_clicked(self) -> None:
        """
        Handle the 'Yes' button click event.

        Closes the dialog, loads the previous session from the automatic config file,
        updates the UI with the loaded session data, and refreshes folder paths.
        """
        self.close()
        o_session = SessionHandler(parent=self.parent)
        o_get = Get(parent=self.parent)
        full_config_file_name = o_get.get_automatic_config_file_name()
        o_session.load_from_file(config_file_name=full_config_file_name)
        o_session.load_to_ui()
        self.parent.loading_from_config = False
        self.parent.folder_path = FolderPath(parent=self.parent)
        self.parent.folder_path.update()
        self.parent.check_state_of_steps_menu_button()

    def no_clicked(self) -> None:
        """
        Handle the 'No' button click event.

        Creates a new session and closes the dialog.
        """
        self.parent.new_session_clicked()
        self.close()

    def reject(self) -> None:
        """
        Handle the dialog rejection event (e.g., when Escape key is pressed).

        Calls the parent class's reject method.
        """
        # self.parent.new_session_clicked()
        super(LoadPreviousSessionLauncher, self).reject()

    def close(self) -> None:
        """
        Handle the dialog close event.

        Calls the parent class's close method.
        """
        super(LoadPreviousSessionLauncher, self).close()
