#!/usr/bin/env python
"""
Module for selecting evaluation regions in autonomous reconstruction.

This module provides a dialog interface for users to select, modify, and visualize
evaluation regions for autonomous CT reconstruction tasks. It allows users to define
regions of interest with customizable parameters.
"""

import os
from typing import Tuple

import numpy as np
import pyqtgraph as pg
from qtpy import QtGui
from qtpy.QtWidgets import QDialog

from hyperctui import EvaluationRegionKeys, load_ui
from hyperctui.autonomous_reconstruction import ColumnIndex
from hyperctui.autonomous_reconstruction.initialization import InitializationSelectEvaluationRegions
from hyperctui.utilities.check import is_int
from hyperctui.utilities.table import TableHandler

LABEL_XOFFSET = -50


class SelectEvaluationRegions(QDialog):
    """Dialog for selecting evaluation regions for autonomous reconstruction.

    This dialog allows users to define, modify, and visualize evaluation regions
    that will be used in the reconstruction process. Users can enable/disable regions,
    set their positions, and name them.

    Attributes
    ----------
    ok_clicked : bool
        Flag indicating whether the OK button was clicked
    parent : QWidget
        Parent widget reference
    ui : Any
        The loaded UI from the .ui file
    """

    ok_clicked = False

    def __init__(self, parent=None):
        """Initialize the dialog.

        Parameters
        ----------
        parent : QWidget, optional
            Parent widget, by default None
        """
        super(SelectEvaluationRegions, self).__init__(parent)
        self.parent = parent

        ui_full_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), os.path.join("ui", "select_evaluation_regions.ui")
        )

        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Select Evaluation Regions")

        self.parent.backup_evaluation_regions = self.parent.evaluation_regions
        self.initialization()
        self.update_display_regions()
        self.check_state_ok_button()

    def initialization(self) -> None:
        """Initialize the dialog components and handlers."""
        o_init = InitializationSelectEvaluationRegions(parent=self, grand_parent=self.parent)
        o_init.all()

    def get_name_of_new_region(self) -> str:
        """Generate a unique name for a new evaluation region.

        Returns
        -------
        str
            Unique name for the new region
        """
        evaluation_regions = self.parent.evaluation_regions
        index = 1
        list_names = [evaluation_regions[key][EvaluationRegionKeys.name] for key in evaluation_regions.keys()]
        while True:
            region_name = self.parent.default_evaluation_region[EvaluationRegionKeys.name] + f" {index}"
            if region_name not in list_names:
                return region_name
            index += 1

    def clear_all_regions(self) -> None:
        """Remove all region items and labels from the view."""
        # clear all region items and labels
        for _key in self.parent.evaluation_regions.keys():
            if self.parent.evaluation_regions[_key][EvaluationRegionKeys.id]:
                self.ui.image_view.removeItem(self.parent.evaluation_regions[_key][EvaluationRegionKeys.id])
                self.ui.image_view.removeItem(self.parent.evaluation_regions[_key][EvaluationRegionKeys.label_id])

    def sort(self, value1: int, value2: int) -> Tuple[int, int]:
        """Sort two values in ascending order.

        Parameters
        ----------
        value1 : int
            First value
        value2 : int
            Second value

        Returns
        -------
        Tuple[int, int]
            Sorted values (min, max)
        """
        minimum_value = np.min([value1, value2])
        maximum_value = np.max([value1, value2])
        return minimum_value, maximum_value

    def save_table(self) -> None:
        """Save the table data to the evaluation regions dictionary."""
        o_table = TableHandler(table_ui=self.ui.tableWidget)
        row_count = o_table.row_count()
        evaluation_regions = {}
        for _row in np.arange(row_count):
            _state_widget = o_table.get_inner_widget(row=_row, column=ColumnIndex.enabled_state, position_index=1)
            _state = _state_widget.isChecked()
            _name = o_table.get_item_str_from_cell(row=_row, column=ColumnIndex.name)
            _from = int(o_table.get_item_str_from_cell(row=_row, column=ColumnIndex.from_value))
            _to = int(o_table.get_item_str_from_cell(row=_row, column=ColumnIndex.to_value))
            _from, _to = self.sort(_from, _to)

            evaluation_regions[_row] = {
                EvaluationRegionKeys.state: _state,
                EvaluationRegionKeys.name: _name,
                EvaluationRegionKeys.from_value: int(_from),
                EvaluationRegionKeys.to_value: int(_to),
                EvaluationRegionKeys.id: None,
            }
        self.parent.evaluation_regions = evaluation_regions

    def update_display_regions(self) -> None:
        """Update the display by creating region visualizations for enabled regions."""
        # replace all the regions
        for _key in self.parent.evaluation_regions.keys():
            _entry = self.parent.evaluation_regions[_key]
            _state = _entry[EvaluationRegionKeys.state]
            if _state:
                _from = int(_entry[EvaluationRegionKeys.from_value])
                _to = int(_entry[EvaluationRegionKeys.to_value])
                _roi_id = pg.LinearRegionItem(
                    values=(_from, _to),
                    orientation="horizontal",
                    movable=True,
                    bounds=[0, self.parent.image_size["width"]],
                )
                self.ui.image_view.addItem(_roi_id)
                _roi_id.sigRegionChanged.connect(self.regions_manually_moved)
                _entry[EvaluationRegionKeys.id] = _roi_id

                # label of region
                _name_of_region = _entry[EvaluationRegionKeys.name]
                _label_id = pg.TextItem(
                    html='<div style="text-align: center">' + _name_of_region + "</div>",
                    fill=QtGui.QColor(255, 255, 255),
                    anchor=(0, 1),
                )
                _label_id.setPos(LABEL_XOFFSET, _from)
                self.ui.image_view.addItem(_label_id)
                _entry[EvaluationRegionKeys.label_id] = _label_id

    def regions_manually_moved(self) -> None:
        """Handle region position updates when regions are manually moved."""
        # replace all the regions
        o_table = TableHandler(table_ui=self.ui.tableWidget)
        o_table.block_signals()
        for _row, _key in enumerate(self.parent.evaluation_regions.keys()):
            _entry = self.parent.evaluation_regions[_key]
            _state = _entry[EvaluationRegionKeys.state]
            if _state:
                _id = _entry[EvaluationRegionKeys.id]
                (_from, _to) = _id.getRegion()
                _from, _to = self.sort(_from, _to)
                o_table.set_item_with_str(row=_row, column=ColumnIndex.from_value, value=str(int(_from)))
                o_table.set_item_with_str(row=_row, column=ColumnIndex.to_value, value=str(int(_to)))

                # move label as well
                _label_id = _entry[EvaluationRegionKeys.label_id]
                _label_id.setPos(LABEL_XOFFSET, _from)

        o_table.unblock_signals()
        self.update_evaluation_regions_dict()

    def update_evaluation_regions_dict(self) -> None:
        """Update the evaluation regions dictionary from the table data."""
        o_table = TableHandler(table_ui=self.ui.tableWidget)
        row_count = o_table.row_count()
        for _row in np.arange(row_count):
            _from = int(o_table.get_item_str_from_cell(row=_row, column=ColumnIndex.from_value))
            _to = int(o_table.get_item_str_from_cell(row=_row, column=ColumnIndex.to_value))
            self.parent.evaluation_regions[_row][EvaluationRegionKeys.from_value] = str(_from)
            self.parent.evaluation_regions[_row][EvaluationRegionKeys.to_value] = str(_to)

    def table_changed(self) -> None:
        """Handle changes to the table by updating regions and validation."""
        self.check_table_content()
        self.clear_all_regions()
        self.save_table()
        self.check_table_state()
        self.update_display_regions()

    def checkButton_clicked(self) -> None:
        """Handle click on check button by updating regions and validation."""
        self.clear_all_regions()
        self.save_table()
        self.update_display_regions()
        self.check_table_state()
        self.check_state_ok_button()

    def check_table_content(self) -> None:
        """
        Validate table content.

        Makes sure 'from' and 'to' values are integers,
        'from' value is smaller than 'to' value (otherwise reverses them),
        and checks that at least 3 regions have been selected.
        """
        o_table = TableHandler(table_ui=self.ui.tableWidget)
        o_table.block_signals()
        nbr_row = o_table.row_count()
        nbr_row_selected = 0
        for _row in np.arange(nbr_row):
            from_value = o_table.get_item_str_from_cell(row=_row, column=ColumnIndex.from_value)
            to_value = o_table.get_item_str_from_cell(row=_row, column=ColumnIndex.to_value)
            if not is_int(from_value):
                from_value = 0
            else:
                from_value = int(from_value)

            if not is_int(to_value):
                to_value = 10
            else:
                to_value = int(to_value)

            minimum_value = np.min([from_value, to_value])
            maximum_value = np.max([from_value, to_value])

            from_value = str(minimum_value)
            to_value = str(maximum_value)

            o_table.set_item_with_str(row=_row, column=ColumnIndex.from_value, value=from_value)
            o_table.set_item_with_str(row=_row, column=ColumnIndex.to_value, value=to_value)

    def check_table_state(self) -> None:
        """
        Check and update table state.

        If a state is disabled, the other widgets/columns for that row will be disabled and
        cannot be edited.
        """
        o_table = TableHandler(table_ui=self.ui.tableWidget)
        o_table.block_signals()
        nbr_row = o_table.row_count()
        nbr_row_selected = 0
        for _row in np.arange(nbr_row):
            _state_widget = o_table.get_inner_widget(row=_row, column=ColumnIndex.enabled_state, position_index=1)
            _state = _state_widget.isChecked()

            # disabled or not editing
            o_table.set_item_state(row=_row, column=ColumnIndex.name, editable=_state)
            o_table.set_item_state(row=_row, column=ColumnIndex.from_value, editable=_state)
            o_table.set_item_state(row=_row, column=ColumnIndex.to_value, editable=_state)

        o_table.unblock_signals()

    def is_ok_button_ready(self) -> bool:
        """
        Check if the OK button should be enabled.

        Returns
        -------
        bool
            True if at least 3 regions are enabled, False otherwise
        """
        evaluation_regions = self.parent.evaluation_regions
        nbr_region_enabled = 0
        for _key in evaluation_regions.keys():
            if evaluation_regions[_key][EvaluationRegionKeys.state]:
                nbr_region_enabled += 1

        if nbr_region_enabled > 2:
            return True

        return False

    def check_state_ok_button(self) -> None:
        """Update the enabled state of the OK button based on validation."""
        if self.is_ok_button_ready():
            self.ui.pushButton.setEnabled(True)
        else:
            self.ui.pushButton.setEnabled(False)

    def accept(self) -> None:
        """Handle dialog acceptance by saving data and closing."""
        self.ok_clicked = True
        self.save_table()
        self.parent.update_autonomous_widgets()
        self.close()

    def cancel(self) -> None:
        """Handle dialog cancellation."""
        self.close()

    def closeEvent(self, a0) -> None:
        """
        Handle close event.

        If OK was not clicked, restore the backup evaluation regions.

        Parameters
        ----------
        a0 : QtGui.QCloseEvent
            The close event
        """
        if self.ok_clicked:
            pass
        else:
            self.parent.evaluation_regions = self.parent.backup_evaluation_regions
