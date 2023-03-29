from qtpy.QtWidgets import QDialog
from qtpy.QtCore import QAbstractTableModel, Qt
import os
import pandas as pd
# import numpy as np

from hyperctui import load_ui


class TableModel(QAbstractTableModel):

    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        return 1


class HelpGoldenAngle(QDialog):

    def __init__(self, parent=None):
        super(HelpGoldenAngle, self).__init__(parent)
        self.parent = parent

        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                    os.path.join('ui',
                                                 'help_golden_angle.ui'))

        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Golden Angle")

        self.initialization()

    def initialization(self):
        golden_angle_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                                         os.path.join('static',
                                                                      'golden_angle.csv'))
        table = pd.read_csv(golden_angle_file)
        data = list(table['angles'])
        model = TableModel(data)
        self.ui.tableView.setModel(model)
