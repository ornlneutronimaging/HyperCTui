from qtpy.QtWidgets import QDialog
import os
import numpy as np

from hyperctui import load_ui
from hyperctui import DEFAULT_EVALUATION_REGIONS
from hyperctui.utilities.table import TableHandler


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

    def initialization(self):
        o_table = TableHandler(table_ui=self.ui.tableWidget)
        evaluation_regions = self.parent.evaluation_regions
        for _row in evaluation_regions.keys():
            o_table.insert_empty_row(row=_row)
            o_table.insert_item(row=_row,
                                column=0,
                                value=evaluation_regions[_row]['name'])
            o_table.insert_item(row=_row,
                                column=1,
                                value=evaluation_regions[_row]['from'])
            o_table.insert_item(row=_row,
                                column=2,
                                value=evaluation_regions[_row]['to'])

    def add_a_region_clicked(self):
        o_table = TableHandler(table_ui=self.ui.tableWidget)
        row_count = o_table.row_count()
        o_table.insert_empty_row(row=row_count)
        o_table.insert_item(row=row_count,
                            column=0,
                            value=self.parent.default_evaluation_region['name'])
        o_table.insert_item(row=row_count,
                            column=1,
                            value=self.parent.default_evaluation_region['from'])
        o_table.insert_item(row=row_count,
                            column=2,
                            value=self.parent.default_evaluation_region['to'])
        self.save_table()
        self.update_display()
        self.check_status_of_add_remove_buttons()

    def remove_selected_region_clicked(self):
        o_table = TableHandler(table_ui=self.ui.tableWidget)
        row_selected = o_table.get_row_selected()
        o_table.remove_row(row_selected)
        self.save_table()
        self.update_display()
        self.check_status_of_add_remove_buttons()

    def check_status_of_add_remove_buttons(self):
        o_table = TableHandler(table_ui=self.ui.tableWidget)
        nbr_row = o_table.row_count()
        if nbr_row > 3:
            self.ui.remove_pushButton.setEnabled(False)
        else:
            self.ui.remove_pushButton.setEnabled(True)

    def save_table(self):
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
                                        'to': _to}
        self.parent.evaluation_regions = evaluation_regions

    def update_display(self):
        #FIXME
        pass
