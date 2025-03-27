#!/usr/bin/env python
"""
Utility module for handling table operations in the HyperCTui application.
Provides a TableHandler class that wraps QT table widget functionality with simpler interface.
"""

from typing import Any, List, Optional, Tuple, Union

import numpy as np
from qtpy import QtCore, QtGui
from qtpy.QtWidgets import QTableWidget, QTableWidgetItem, QTableWidgetSelectionRange, QWidget


class TableHandler:
    """
    Handler for QTableWidget operations providing simplified interface for common table operations.

    This class encapsulates methods for manipulating table data, selection, and appearance.
    """

    cell_str_format = "{:.3f}"
    cell_str_format = "{}"

    def __init__(self, table_ui: Optional[QTableWidget] = None) -> None:
        """
        Initialize the TableHandler with a QTableWidget.

        Args:
            table_ui: The QTableWidget instance to handle
        """
        self.table_ui = table_ui

    def row_count(self) -> int:
        """
        Get the number of rows in the table.

        Returns:
            Number of rows
        """
        return self.table_ui.rowCount()

    def column_count(self) -> int:
        """
        Get the number of columns in the table.

        Returns:
            Number of columns
        """
        return self.table_ui.columnCount()

    def select_everything(self, state: bool) -> None:
        """
        Select or deselect all cells in the table.

        Args:
            state: True to select, False to deselect
        """
        nbr_row = self.table_ui.rowCount()
        nbr_column = self.table_ui.columnCount()
        selection_range = QTableWidgetSelectionRange(0, 0, nbr_row - 1, nbr_column - 1)
        self.table_ui.setRangeSelected(selection_range, state)

    def select_rows(self, list_of_rows: Optional[List[int]] = None) -> None:
        """
        Select specific rows in the table.

        Args:
            list_of_rows: List of row indices to select
        """
        if list_of_rows is None:
            return

        self.select_everything(False)
        nbr_column = self.table_ui.columnCount()

        for _row in list_of_rows:
            selection_range = QTableWidgetSelectionRange(_row, 0, _row, nbr_column - 1)
            self.table_ui.setRangeSelected(selection_range, True)

    def remove_row(self, row: int = 0) -> None:
        """
        Remove a specific row from the table.

        Args:
            row: Index of the row to remove
        """
        self.table_ui.removeRow(row)

    def remove_all_rows(self) -> None:
        """
        Remove all rows from the table.
        """
        nbr_row = self.table_ui.rowCount()
        for _ in np.arange(nbr_row):
            self.table_ui.removeRow(0)

    def remove_all_columns(self) -> None:
        """
        Remove all columns from the table.
        """
        nbr_column = self.table_ui.columnCount()
        for _ in np.arange(nbr_column):
            self.table_ui.removeColumn(0)

    def full_reset(self) -> None:
        """
        Reset the table by removing all rows and columns.
        """
        self.remove_all_rows()
        self.remove_all_columns()

    def select_cell(self, row: int = 0, column: int = 0) -> None:
        """
        Select a specific cell in the table.

        Args:
            row: Row index of the cell to select
            column: Column index of the cell to select
        """
        self.select_everything(False)
        range_selected = QtGui.QTableWidgetSelectionRange(row, column, row, column)
        self.table_ui.setRangeSelected(range_selected, True)

    def select_row(self, row: int = 0) -> None:
        """
        Select a specific row in the table.

        Args:
            row: Index of the row to select
        """
        if row < 0:
            row = 0
        self.table_ui.selectRow(row)

    def set_column_names(self, column_names: Optional[List[str]] = None) -> None:
        """
        Set the column headers for the table.

        Args:
            column_names: List of column names
        """
        self.table_ui.setHorizontalHeaderLabels(column_names)

    def set_row_names(self, row_names: Optional[List[str]] = None) -> None:
        """
        Set the row headers for the table.

        Args:
            row_names: List of row names
        """
        self.table_ui.setVerticalHeaderLabels(row_names)

    def set_column_sizes(self, column_sizes: Optional[List[int]] = None) -> None:
        """
        Set the width of each column.

        Args:
            column_sizes: List of column widths in pixels
        """
        for _col, _size in enumerate(column_sizes):
            self.table_ui.setColumnWidth(_col, _size)

    def insert_empty_row(self, row: int = 0) -> None:
        """
        Insert an empty row at the specified position.

        Args:
            row: Index where to insert the new row
        """
        self.table_ui.insertRow(row)

    def insert_row(self, row: int = 0, list_col_name: Optional[List[str]] = None) -> None:
        """
        Insert a new row and populate it with provided data.

        Args:
            row: Index where to insert the new row
            list_col_name: List of values to populate the row
        """
        self.table_ui.insertRow(row)
        for column, _text in enumerate(list_col_name):
            _item = QtGui.QTableWidgetItem(_text)
            self.table_ui.setItem(row, column, _item)

    def insert_column(self, column: int) -> None:
        """
        Insert a new column at the specified position.

        Args:
            column: Index where to insert the new column
        """
        self.table_ui.insertColumn(column)

    def insert_empty_column(self, column: int) -> None:
        """
        Insert an empty column at the specified position.

        Args:
            column: Index where to insert the new column
        """
        self.table_ui.insertColumn(column)

    def set_item_with_str(self, row: int = 0, column: int = 0, value: str = "") -> None:
        """
        Set the text of a specific cell.

        Args:
            row: Row index of the cell
            column: Column index of the cell
            value: Text to set in the cell
        """
        self.table_ui.item(row, column).setText(value)

    def set_item_with_float(self, row: int = 0, column: int = 0, float_value: Union[float, str] = "") -> None:
        """
        Set the text of a specific cell with a float value.

        Args:
            row: Row index of the cell
            column: Column index of the cell
            float_value: Float value to set in the cell
        """
        if (str(float_value) == "None") or (str(float_value) == "N/A"):
            _str_value = "N/A"
        else:
            _str_value = self.cell_str_format.format(np.float(float_value))
        self.table_ui.item(row, column).setText(_str_value)

    def insert_item_with_float(
        self, row: int = 0, column: int = 0, float_value: Union[float, str] = "", format_str: str = "{}"
    ) -> None:
        """
        Insert a new item with a float value at the specified position.

        Args:
            row: Row index of the cell
            column: Column index of the cell
            float_value: Float value to set in the cell
            format_str: Format string for the float value
        """
        if (str(float_value) == "None") or (str(float_value) == "N/A"):
            _str_value = "N/A"
        else:
            _str_value = format_str.format(np.float(float_value))
        _item = QtGui.QTableWidgetItem(_str_value)
        self.table_ui.setItem(row, column, _item)

    def set_item_state(self, row: int = 0, column: int = 0, editable: bool = True) -> None:
        """
        Set the state of a specific cell.

        Args:
            row: Row index of the cell
            column: Column index of the cell
            editable: True to make the cell editable, False to make it read-only
        """
        _item = self.table_ui.item(row, column)
        if not editable:
            _item.setFlags(QtCore.Qt.ItemIsSelectable)
        else:
            _item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable)

    def set_item_editable(self, row: int = 0, column: int = 0, editable: bool = True) -> None:
        """
        Set the editable state of a specific cell.

        Args:
            row: Row index of the cell
            column: Column index of the cell
            editable: True to make the cell editable, False to make it read-only
        """
        _item = self.table_ui.item(row, column)
        if not editable:
            _item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        else:
            _item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable)

    def set_item_enabled(self, row: int = 0, column: int = 0, enabled: bool = True) -> None:
        """
        Set the enabled state of a specific cell.

        Args:
            row: Row index of the cell
            column: Column index of the cell
            enabled: True to enable the cell, False to disable it
        """
        _item = self.table_ui.item(row, column)
        if not enabled:
            _item.setFlags(QtCore.Qt.ItemIsSelectable)
        else:
            _item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)

    def set_row_enabled(self, row: int = 0, enabled: bool = True) -> None:
        """
        Set the enabled state of a specific row.

        Args:
            row: Index of the row
            enabled: True to enable the row, False to disable it
        """
        nbr_column = self.column_count()
        for _col in np.arange(nbr_column):
            self.set_item_enabled(row=row, column=_col, enabled=enabled)

    def enable_all_rows(self, enabled: bool = True) -> None:
        """
        Enable or disable all rows in the table.

        Args:
            enabled: True to enable all rows, False to disable all rows
        """
        nbr_rows = self.row_count()
        for row in np.arange(nbr_rows):
            self.set_row_enabled(row=row, enabled=enabled)

    def insert_item(self, row: int = 0, column: int = 0, value: Any = "", format_str: str = "{}") -> None:
        """
        Insert a new item at the specified position.

        Args:
            row: Row index of the cell
            column: Column index of the cell
            value: Value to set in the cell
            format_str: Format string for the value
        """
        _str_value = format_str.format(value)
        _item = QTableWidgetItem(_str_value)
        self.table_ui.setItem(row, column, _item)

    def set_background_color(
        self, row: int = 0, column: int = 0, qcolor: QtGui.QColor = QtGui.QColor(0, 255, 255)
    ) -> None:
        """
        Set the background color of a specific cell.

        Args:
            row: Row index of the cell
            column: Column index of the cell
            qcolor: QColor instance representing the background color
        """
        _item = self.table_ui.item(row, column)
        _item.setBackground(qcolor)

    def insert_widget(self, row: int = 0, column: int = 0, widget: Optional[QWidget] = None) -> None:
        """
        Insert a widget at the specified position.

        Args:
            row: Row index of the cell
            column: Column index of the cell
            widget: QWidget instance to insert
        """
        self.table_ui.setCellWidget(row, column, widget)

    def block_signals(self) -> None:
        """
        Block signals from the table.
        """
        self.table_ui.blockSignals(True)

    def unblock_signals(self) -> None:
        """
        Unblock signals from the table.
        """
        self.table_ui.blockSignals(False)

    ## GETTER

    def get_rows_of_table_selected(self) -> Optional[List[int]]:
        """
        Get the indices of the selected rows in the table.

        Returns:
            List of selected row indices, or None if no rows are selected
        """
        if self.table_ui is None:
            return None

        selected_ranges = self.table_ui.selectedRanges()
        if selected_ranges == []:
            return None

        list_row_selected = []
        for _selection in selected_ranges:
            top_row = _selection.topRow()
            bottom_row = _selection.bottomRow()
            if top_row == bottom_row:
                list_row_selected.append(top_row)
            else:
                _range = np.arange(top_row, bottom_row + 1)
                for _row in _range:
                    list_row_selected.append(_row)

        return list_row_selected

    def get_row_selected(self) -> int:
        """
        Get the index of the first selected row in the table.

        Returns:
            Index of the first selected row, or -1 if no rows are selected
        """
        if self.table_ui is None:
            return -1
        list_selection = self.table_ui.selectedRanges()
        try:
            first_selection = list_selection[0]
        except IndexError:
            return -1
        return first_selection.topRow()

    def get_cell_selected(self) -> Tuple[int, int]:
        """
        Get the indices of the first selected cell in the table.

        Returns:
            Tuple containing the row and column indices of the first selected cell
        """
        list_selection = self.table_ui.selectedRanges()
        first_selection = list_selection[0]
        row = first_selection.topRow()
        col = first_selection.leftColumn()
        return (row, col)

    def get_item_str_from_cell(self, row: int = -1, column: int = -1) -> str:
        """
        Get the text of a specific cell.

        Args:
            row: Row index of the cell
            column: Column index of the cell

        Returns:
            Text of the cell
        """
        item_selected = self.table_ui.item(row, column).text()
        return str(item_selected)

    def get_widget(self, row: int = -1, column: int = -1) -> Optional[QWidget]:
        """
        Get the widget at a specific cell.

        Args:
            row: Row index of the cell
            column: Column index of the cell

        Returns:
            QWidget instance at the cell, or None if no widget is present
        """
        _widget = self.table_ui.cellWidget(row, column)
        return _widget

    def get_inner_widget(self, row: int = -1, column: int = -1, position_index: int = 0) -> Optional[QWidget]:
        """
        Get the inner widget at a specific cell.

        Args:
            row: Row index of the cell
            column: Column index of the cell
            position_index: Index of the inner widget

        Returns:
            QWidget instance of the inner widget, or None if no widget is present
        """
        _widget = self.get_widget(row=row, column=column)
        return _widget.children()[position_index]

    def get_elements_from_column(self, column: int = 0) -> List[str]:
        """
        Get all values from a specific column.

        Args:
            column: Index of the column to retrieve

        Returns:
            List of string values from the column
        """
        list_element = []
        row_count = self.row_count()
        for _row in np.arange(row_count):
            list_element.append(self.get_item_str_from_cell(row=_row, column=column))
        return list_element
