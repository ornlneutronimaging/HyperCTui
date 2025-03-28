#!/usr/bin/env python
"""
Module for retrieving data from UI elements in the projections setup component.

This module provides functionality for getting values from UI input fields
and formatted labels related to run titles in the projection setup interface.
"""

from hyperctui.utilities.get import Get as MasterGet


class Get(MasterGet):
    """
    Specialized retrieval class for the projections setup UI elements.

    This class extends the base Get class with methods for accessing
    specific UI elements related to projection setup configuration.

    Parameters
    ----------
    parent : object
        The parent object containing the UI components.
    """

    def run_title(self) -> str:
        """
        Get the current run title from the input field.

        Returns
        -------
        str
            The text content of the run title input field.
        """
        return str(self.parent.ui.run_title_lineEdit.text())

    def formatted_run_title(self) -> str:
        """
        Get the formatted run title from the display label.

        Returns
        -------
        str
            The text content of the formatted run title label.
        """
        return str(self.parent.ui.run_title_formatted_label.text())
