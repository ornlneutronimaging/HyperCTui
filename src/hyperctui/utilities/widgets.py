#!/usr/bin/env python
"""
Utility widgets module for HyperCTui.

This module provides utilities for managing UI widgets and their properties,
including tab visibility control and geometry settings.
"""

from typing import Any, Optional

import numpy as np
from qtpy.QtGui import QIcon

from hyperctui import TabNames, tab2_icon, tab3_icon, tab4_icon
from hyperctui.parent import Parent


class Widgets(Parent):
    """
    Widget management class that extends the Parent class.

    Provides functionality for UI widget manipulation, primarily for tab
    visibility control.
    """

    def make_tabs_visible(self, is_visible: bool = True) -> None:
        """
        Show or hide tabs 2, 3, and 4 in the UI.

        Parameters
        ----------
        is_visible : bool, optional
            Whether to make tabs visible (True) or hidden (False).
            Default is True.

        Returns
        -------
        None
        """
        if not is_visible:
            for _ in np.arange(3):
                self.parent.ui.tabWidget.removeTab(2)
        else:
            self.parent.ui.tabWidget.insertTab(2, self.parent.tab2, QIcon(tab2_icon), TabNames.tab2)
            self.parent.ui.tabWidget.insertTab(3, self.parent.tab3, QIcon(tab3_icon), TabNames.tab3)
            self.parent.ui.tabWidget.insertTab(4, self.parent.tab4, QIcon(tab4_icon), TabNames.tab4)

        self.parent.all_tabs_visible = is_visible


def set_geometry(ui: Optional[Any] = None, width: int = 100, height: int = 100) -> None:
    """
    Set the geometry (size) of a UI component.

    Parameters
    ----------
    ui : Any, optional
        The UI component whose geometry will be modified. Default is None.
    width : int, optional
        The desired width in pixels. Default is 100.
    height : int, optional
        The desired height in pixels. Default is 100.

    Returns
    -------
    None
    """
    pass
