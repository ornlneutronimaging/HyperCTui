import pyqtgraph as pg
from qtpy.QtWidgets import QVBoxLayout, QCheckBox

from hyperctui.utilities.table import TableHandler
from hyperctui.autonomous_reconstruction import ColumnIndex


class Initialization:

    column_sizes = [50, 200, 100, 100]

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

    def all(self):
        self.table()
        self.display()

    def table(self):
        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        o_table.set_column_sizes(self.column_sizes)
        evaluation_regions = self.grand_parent.evaluation_regions
        o_table.block_signals()
        for _row in evaluation_regions.keys():
            o_table.insert_empty_row(row=_row)

            checked_button = QCheckBox()
            checked_button.setChecked(True)
            o_table.insert_widget(row=_row,
                                  column=ColumnIndex.enabled_state,
                                  widget=checked_button)
            o_table.insert_item(row=_row,
                                column=ColumnIndex.name,
                                value=evaluation_regions[_row]['name'])
            o_table.insert_item(row=_row,
                                column=ColumnIndex.from_value,
                                value=evaluation_regions[_row]['from'])
            o_table.insert_item(row=_row,
                                column=ColumnIndex.to_value,
                                value=evaluation_regions[_row]['to'])
        o_table.unblock_signals()

    def display(self):
        self.parent.ui.image_view = pg.ImageView(view=pg.PlotItem())
        self.parent.ui.image_view.ui.roiBtn.hide()
        self.parent.ui.image_view.ui.menuBtn.hide()
        image_layout = QVBoxLayout()
        image_layout.addWidget(self.parent.ui.image_view)
        self.parent.ui.widget.setLayout(image_layout)
        image = self.grand_parent.image_0_degree
        self.parent.ui.image_view.setImage(image)
