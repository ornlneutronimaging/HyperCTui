#!/usr/bin/env python
"""
Module for displaying golden angle information in a table view.

This module provides a dialog that shows the golden angle values
loaded from a CSV file.
"""

import os
from typing import Any, List, Optional

import pandas as pd
from qtpy.QtCore import QAbstractTableModel, QModelIndex, Qt
from qtpy.QtWidgets import QDialog

# import numpy as np
from hyperctui import load_ui


class TableModel(QAbstractTableModel):
    """
    Table model for displaying golden angle data.

    Parameters
    ----------
    data : List[Any]
        The data to be displayed in the table.
    """

    def __init__(self, data: List[Any]):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index: QModelIndex, role: int) -> Optional[Any]:
        """
        Return data for the specified index and role.

        Parameters
        ----------
        index : QModelIndex
            Index of the cell.
        role : int
            Role for which to return data.

        Returns
        -------
        Optional[Any]
            Cell data if role is DisplayRole, None otherwise.
        """
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()]

    def rowCount(self, index: QModelIndex) -> int:
        """
        Return the number of rows.

        Parameters
        ----------
        index : QModelIndex
            Parent index, unused.

        Returns
        -------
        int
            Number of rows in the table.
        """
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index: QModelIndex) -> int:
        """
        Return the number of columns.

        Parameters
        ----------
        index : QModelIndex
            Parent index, unused.

        Returns
        -------
        int
            Number of columns in the table (1).
        """
        return 1


class HelpGoldenAngle(QDialog):
    """
    Dialog for displaying golden angle information.

    Parameters
    ----------
    parent : Optional[QDialog]
        Parent widget.
    """

    def __init__(self, parent: Optional[QDialog] = None):
        super(HelpGoldenAngle, self).__init__(parent)
        self.parent = parent

        ui_full_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), os.path.join("ui", "help_golden_angle.ui")
        )

        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Golden Angle")

        self.initialization()

    def initialization(self) -> None:
        """
        Initialize the table view with golden angle data.

        Loads golden angle values from a CSV file and sets up the table model.
        """
        golden_angle_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), os.path.join("static", "golden_angle.csv")
        )
        table = pd.read_csv(golden_angle_file)
        data = list(table["angles"])
        model = TableModel(data)
        self.ui.tableView.setModel(model)
