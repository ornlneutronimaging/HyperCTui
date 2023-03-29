from qtpy.QtWidgets import QDialog
import os

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
        print(f"{evaluation_regions =}")
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
        pass

    def remove_selected_region_clicked(self):
        pass
