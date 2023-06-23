import numpy as np
from qtpy import QtGui
from qtpy import QtCore
from qtpy.QtWidgets import QTableWidgetItem, QTableWidgetSelectionRange


class TableHandler:
    cell_str_format = "{:.3f}"
    cell_str_format = "{}"

    def __init__(self, table_ui=None):
        self.table_ui = table_ui

    def row_count(self):
        return self.table_ui.rowCount()

    def column_count(self):
        return self.table_ui.columnCount()

    def select_everything(self, state):
        nbr_row = self.table_ui.rowCount()
        nbr_column = self.table_ui.columnCount()
        selection_range = QTableWidgetSelectionRange(0, 0, nbr_row - 1, nbr_column - 1)
        self.table_ui.setRangeSelected(selection_range, state)

    def select_rows(self, list_of_rows=None):
        if list_of_rows is None:
            return

        self.select_everything(False)
        nbr_column = self.table_ui.columnCount()

        for _row in list_of_rows:
            selection_range = QTableWidgetSelectionRange(_row, 0, _row, nbr_column - 1)
            self.table_ui.setRangeSelected(selection_range, True)

    def remove_row(self, row=0):
        self.table_ui.removeRow(row)

    def remove_all_rows(self):
        nbr_row = self.table_ui.rowCount()
        for _ in np.arange(nbr_row):
            self.table_ui.removeRow(0)

    def remove_all_columns(self):
        nbr_column = self.table_ui.columnCount()
        for _ in np.arange(nbr_column):
            self.table_ui.removeColumn(0)

    def full_reset(self):
        self.remove_all_rows()
        self.remove_all_columns()

    def get_rows_of_table_selected(self):
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

    def get_row_selected(self):
        if self.table_ui is None:
            return -1
        list_selection = self.table_ui.selectedRanges()
        try:
            first_selection = list_selection[0]
        except IndexError:
            return -1
        return first_selection.topRow()

    def get_cell_selected(self):
        list_selection = self.table_ui.selectedRanges()
        first_selection = list_selection[0]
        row = first_selection.topRow()
        col = first_selection.leftColumn()
        return (row, col)

    def get_item_str_from_cell(self, row=-1, column=-1):
        item_selected = self.table_ui.item(row, column).text()
        return str(item_selected)

    def get_widget(self, row=-1, column=-1):
        _widget = self.table_ui.cellWidget(row, column)
        return _widget

    def get_inner_widget(self, row=-1, column=-1, position_index=0):
        """
        when the widget is inside another widget
        """
        _widget = self.get_widget(row=row, column=column)
        return _widget.children()[position_index]

    def select_cell(self, row=0, column=0):
        self.select_everything(False)
        range_selected = QtGui.QTableWidgetSelectionRange(row, column, row, column)
        self.table_ui.setRangeSelected(range_selected, True)

    def select_row(self, row=0):
        if row < 0:
            row = 0
        self.table_ui.selectRow(row)

    def set_column_names(self, column_names=None):
        self.table_ui.setHorizontalHeaderLabels(column_names)

    def set_row_names(self, row_names=None):
        self.table_ui.setVerticalHeaderLabels(row_names)

    def set_column_sizes(self, column_sizes=None):
        for _col, _size in enumerate(column_sizes):
            self.table_ui.setColumnWidth(_col, _size)

    def insert_empty_row(self, row=0):
        self.table_ui.insertRow(row)

    def insert_row(self, row=0, list_col_name=None):
        """row is the row number
        """
        self.table_ui.insertRow(row)
        for column, _text in enumerate(list_col_name):
            _item = QtGui.QTableWidgetItem(_text)
            self.table_ui.setItem(row, column, _item)

    def insert_column(self, column):
        self.table_ui.insertColumn(column)

    def insert_empty_column(self, column):
        self.table_ui.insertColumn(column)

    def set_item_with_str(self, row=0, column=0, value=""):
        self.table_ui.item(row, column).setText(value)

    def set_item_with_float(self, row=0, column=0, float_value=""):
        if (str(float_value) == 'None') or (str(float_value) == 'N/A'):
            _str_value = "N/A"
        else:
            _str_value = self.cell_str_format.format(np.float(float_value))
        self.table_ui.item(row, column).setText(_str_value)

    def insert_item_with_float(self, row=0, column=0, float_value="", format_str="{}"):
        if (str(float_value) == 'None') or (str(float_value) == 'N/A'):
            _str_value = "N/A"
        else:
            _str_value = format_str.format(np.float(float_value))
        _item = QtGui.QTableWidgetItem(_str_value)
        self.table_ui.setItem(row, column, _item)

    def set_item_state(self, row=0, column=0, editable=True):
        _item = self.table_ui.item(row, column)
        if not editable:
            # _item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            _item.setFlags(QtCore.Qt.ItemIsSelectable)
        else:
            _item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable)

    def set_item_enabled(self, row=0, column=0, enabled=True):
        _item = self.table_ui.item(row, column)
        if not enabled:
            _item.setFlags(QtCore.Qt.ItemIsSelectable)
        else:
            _item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)

    def set_row_enabled(self, row=0, enabled=True):
        nbr_column = self.column_count()
        for _col in np.arange(nbr_column):
            self.set_item_enabled(row=row,
                                  column=_col,
                                  enabled=enabled)

    def enable_all_rows(self, enabled=True):
        nbr_rows = self.row_count()
        for row in np.arange(nbr_rows):
            self.set_row_enabled(row=row,
                                 enabled=enabled)

    def insert_item(self, row=0, column=0, value="", format_str="{}"):
        _str_value = format_str.format(value)
        _item = QTableWidgetItem(_str_value)
        self.table_ui.setItem(row, column, _item)

    def set_background_color(self, row=0, column=0, qcolor=QtGui.QColor(0, 255, 255)):
        _item = self.table_ui.item(row, column)
        _item.setBackground(qcolor)

    def insert_widget(self, row=0, column=0, widget=None):
        self.table_ui.setCellWidget(row, column, widget)

    def block_signals(self):
        self.table_ui.blockSignals(True)

    def unblock_signals(self):
        self.table_ui.blockSignals(False)
