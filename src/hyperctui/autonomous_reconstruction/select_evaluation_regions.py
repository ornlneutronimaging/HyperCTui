from qtpy.QtWidgets import QDialog
import os
import numpy as np
import pyqtgraph as pg

from hyperctui import load_ui
from hyperctui.utilities.table import TableHandler
from hyperctui.autonomous_reconstruction.initialization import Initialization
from hyperctui.autonomous_reconstruction import ColumnIndex


class SelectEvaluationRegions(QDialog):

    def __init__(self, parent=None):
        super(SelectEvaluationRegions, self).__init__(parent)
        self.parent = parent

        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                    os.path.join('ui',
                                                 'select_evaluation_regions.ui'))

        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Select Evaluation Regions")

        self.initialization()
        self.update_display_regions()

    def initialization(self):
        o_init = Initialization(parent=self, grand_parent=self.parent)
        o_init.all()

    def get_name_of_new_region(self):
        evaluation_regions = self.parent.evaluation_regions
        index = 1
        list_names = [evaluation_regions[key]['name'] for key in evaluation_regions.keys()]
        while True:
            region_name = self.parent.default_evaluation_region['name'] + f" {index}"
            if not (region_name in list_names):
                return region_name
            index += 1

    def clear_all_regions(self):
        # clear all region items
        for _key in self.parent.evaluation_regions.keys():
            if self.parent.evaluation_regions[_key]['id']:
                self.ui.image_view.removeItem(self.parent.evaluation_regions[_key]['id'])

    def sort(self, value1: int, value2: int):
        minimum_value = np.min([value1, value2])
        maximum_value = np.max([value1, value2])
        return minimum_value, maximum_value

    def save_table(self):
        self.clear_all_regions()

        o_table = TableHandler(table_ui=self.ui.tableWidget)
        row_count = o_table.row_count()
        evaluation_regions = {}
        for _row in np.arange(row_count):
            _state_widget = o_table.get_widget(row=_row,
                                               column=ColumnIndex.enabled_state)
            _state = _state_widget.isChecked()
            _name = o_table.get_item_str_from_cell(row=_row,
                                                  column=ColumnIndex.name)
            _from = int(o_table.get_item_str_from_cell(row=_row,
                                                  column=ColumnIndex.from_value))
            _to = int(o_table.get_item_str_from_cell(row=_row,
                                                 column=ColumnIndex.to_value))
            _from, _to = self.sort(_from, _to)

            evaluation_regions[_row] = {'state': _state,
                                        'name': _name,
                                        'from': int(_from),
                                        'to': int(_to),
                                        'id': None}
        self.parent.evaluation_regions = evaluation_regions

    def update_display_regions(self):
        # replace all the regions
        for _key in self.parent.evaluation_regions.keys():
            _entry = self.parent.evaluation_regions[_key]
            _state = _entry['state']
            if _state:
                _from = _entry['from']
                _to = _entry['to']
                _roi_id = pg.LinearRegionItem(values=(_from, _to),
                                              orientation='horizontal',
                                              movable=True,
                                              bounds=[0, self.parent.image_size['width']])
                self.ui.image_view.addItem(_roi_id)
                _roi_id.sigRegionChanged.connect(self.regions_manually_moved)
                _entry['id'] = _roi_id

    def regions_manually_moved(self):
        # replace all the regions
        o_table = TableHandler(table_ui=self.ui.tableWidget)
        o_table.block_signals()
        for _row, _key in enumerate(self.parent.evaluation_regions.keys()):
            _entry = self.parent.evaluation_regions[_key]
            _id = _entry['id']
            (_from, _to) = _id.getRegion()
            _from, _to = self.sort(_from, _to)
            o_table.set_item_with_str(row=_row,
                                      column=ColumnIndex.from_value,
                                      value=str(int(_from)))
            o_table.set_item_with_str(row=_row,
                                      column=ColumnIndex.to_value,
                                      value=str(int(_to)))
        self.check_validity_of_table()
        o_table.unblock_signals()
        self.update_evaluation_regions_dict()

    def update_evaluation_regions_dict(self):
        o_table = TableHandler(table_ui=self.ui.tableWidget)
        row_count = o_table.row_count()
        for _row in np.arange(row_count):
            _from = int(o_table.get_item_str_from_cell(row=_row,
                                                       column=ColumnIndex.from_value))
            _to = int(o_table.get_item_str_from_cell(row=_row,
                                                     column=ColumnIndex.to_value))
            self.parent.evaluation_regions[_row]['from'] = str(_from)
            self.parent.evaluation_regions[_row]['to'] = str(_to)

    def table_changed(self):
        self.save_table()
        self.check_validity_of_table()
        self.update_display_regions()

    def check_validity_of_table(self):
        """
        This is where we make sure the regions do not overlap and they are at least 1 pixel high.
        """
        return
        # o_table = TableHandler(table_ui=self.ui.tableWidget)
        # row_count = o_table.row_count()
        # list_borders = []
        # for _row in np.arange(row_count):
        #
        #     _state_widget = o_table.get_widget(row=_row,
        #                                        column=ColumnIndex.enabled_state)
        #     _state = _state_widget.isChecked()
        #     if _state:
        #         _from = int(o_table.get_item_str_from_cell(row=_row,
        #                                                    column=ColumnIndex.from_value))
        #         _to = int(o_table.get_item_str_from_cell(row=_row,
        #                                                  column=ColumnIndex.to_value))
        #         _from, _to = self.sort(_from, _to)
        #         list_borders.append(_from)
        #         list_borders.append(_to)
        #
        # unsorted_list = list_borders[:]
        # list_borders.sort()
        #
        # if unsorted_list == list_borders:
        #     self.parent.previous_evaluation_regions = self.parent.evaluation_regions
        # else:
        #     self.parent.evaluation_regions = self.parent.previous_evaluation_regions
        #
        #     # fill table with evaluation_regions content
        #     for _row, _key in enumerate(self.parent.evaluation_regions):
        #         _entry = self.parent.evaluation_regions[_key]
        #         _from = _entry['from']
        #         o_table.set_item_with_str(row=_row,
        #                                   column=ColumnIndex.from_value,
        #                                   value=str(_from))
        #         _to = _entry['to']
        #         o_table.set_item_with_str(row=_row,
        #                                   column=ColumnIndex.to_value,
        #                                   value=str(_to))
        #
        #     # now we need to replot the regions
        #     self.save_table()
        #     self.update_display_regions()

