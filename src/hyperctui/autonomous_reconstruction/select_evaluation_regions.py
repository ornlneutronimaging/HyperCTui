from qtpy.QtWidgets import QDialog
import os
import numpy as np
import pyqtgraph as pg

from hyperctui import load_ui
from hyperctui.utilities.table import TableHandler
from hyperctui.autonomous_reconstruction.initialization import Initialization


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
        self.check_status_of_add_remove_buttons()
        self.update_display_regions()

    def initialization(self):
        o_init = Initialization(parent=self, grand_parent=self.parent)
        o_init.all()

    def add_a_region_clicked(self):
        o_table = TableHandler(table_ui=self.ui.tableWidget)
        row_count = o_table.row_count()
        o_table.block_signals()
        o_table.insert_empty_row(row=row_count)
        name_of_new_region = self.get_name_of_new_region()
        o_table.insert_item(row=row_count,
                            column=0,
                            value=name_of_new_region)
        o_table.insert_item(row=row_count,
                            column=1,
                            value=self.parent.default_evaluation_region['from'])
        o_table.insert_item(row=row_count,
                            column=2,
                            value=self.parent.default_evaluation_region['to'])
        o_table.unblock_signals()
        self.save_table()
        self.update_display_regions()
        self.check_status_of_add_remove_buttons()

    def get_name_of_new_region(self):
        evaluation_regions = self.parent.evaluation_regions
        index = 1
        list_names = [evaluation_regions[key]['name'] for key in evaluation_regions.keys()]
        while True:
            region_name = self.parent.default_evaluation_region['name'] + f" {index}"
            if not (region_name in list_names):
                return region_name
            index += 1

    def remove_selected_region_clicked(self):
        o_table = TableHandler(table_ui=self.ui.tableWidget)
        row_selected = o_table.get_row_selected()

        item_id = self.parent.evaluation_regions[row_selected][id]
        self.parent.ui.image_view.removeItem(item_id)

        o_table.remove_row(row_selected)
        self.save_table()
        self.update_display_regions()
        self.check_status_of_add_remove_buttons()

    def check_status_of_add_remove_buttons(self):
        o_table = TableHandler(table_ui=self.ui.tableWidget)
        nbr_row = o_table.row_count()
        if nbr_row > 3:
            self.ui.remove_pushButton.setEnabled(True)
        else:
            self.ui.remove_pushButton.setEnabled(False)

    def save_table(self):
        # clear all region items
        for _key in self.parent.evaluation_regions.keys():
            if self.parent.evaluation_regions[_key][id]:
                self.ui.image_view.removeItem(self.parent.evaluation_regions[_key][id])

        o_table = TableHandler(table_ui=self.ui.tableWidget)
        row_count = o_table.row_count()
        evaluation_regions = {}
        for _row in np.arange(row_count):
            _name = o_table.get_item_str_from_cell(row=_row,
                                                  column=0)
            _from = o_table.get_item_str_from_cell(row=_row,
                                                  column=1)
            _to = o_table.get_item_str_from_cell(row=_row,
                                                 column=2)
            evaluation_regions[_row] = {'name': _name,
                                        'from': _from,
                                        'to': _to,
                                        'id': None}
        self.parent.evaluation_regions = evaluation_regions

    def update_display_regions(self):
        self.parent.list_regions_id = list()
        # replace all the regions
        for _key in self.parent.evaluation_regions.keys():
            _entry = self.parent.evaluation_regions[_key]
            _from = _entry['from']
            _to = _entry['to']
            _roi_id = pg.LinearRegionItem(values=(_from, _to),
                                          orientation='horizontal',
                                          movable=True,
                                          bounds=[0, self.parent.image_size['width']])
            self.ui.image_view.addItem(_roi_id)
            _entry['id'] = _roi_id

    def table_changed(self):
        self.update_display_regions()
