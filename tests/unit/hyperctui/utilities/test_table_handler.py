"""Tests for the TableHandler methods repaired in the correctness batch.

These methods previously called np.float (removed in NumPy >= 1.24) and
QtGui.QTableWidgetItem / QtGui.QTableWidgetSelectionRange (wrong Qt module),
so they crashed on first use; exercised here against a real offscreen
QTableWidget.
"""

from qtpy.QtWidgets import QTableWidget

from hyperctui.utilities.table import TableHandler


def _table(rows: int = 3, columns: int = 2) -> QTableWidget:
    table_ui = QTableWidget()
    table_ui.setRowCount(rows)
    table_ui.setColumnCount(columns)
    return table_ui


def test_insert_item_with_float_formats_value(qapp):
    table_ui = _table()
    o_table = TableHandler(table_ui=table_ui)
    o_table.insert_item_with_float(row=0, column=0, float_value=3.14159, format_str="{:.2f}")
    assert table_ui.item(0, 0).text() == "3.14"


def test_insert_item_with_float_handles_na(qapp):
    table_ui = _table()
    o_table = TableHandler(table_ui=table_ui)
    o_table.insert_item_with_float(row=0, column=0, float_value="N/A")
    assert table_ui.item(0, 0).text() == "N/A"


def test_set_item_with_float_updates_existing_item(qapp):
    table_ui = _table()
    o_table = TableHandler(table_ui=table_ui)
    o_table.insert_item_with_float(row=1, column=1, float_value=1.0)
    o_table.set_item_with_float(row=1, column=1, float_value=2.5)
    assert table_ui.item(1, 1).text() == "2.5"


def test_select_cell_selects_exactly_that_cell(qapp):
    table_ui = _table()
    o_table = TableHandler(table_ui=table_ui)
    o_table.select_cell(row=2, column=1)
    ranges = table_ui.selectedRanges()
    assert len(ranges) == 1
    r = ranges[0]
    assert (r.topRow(), r.leftColumn(), r.bottomRow(), r.rightColumn()) == (2, 1, 2, 1)
