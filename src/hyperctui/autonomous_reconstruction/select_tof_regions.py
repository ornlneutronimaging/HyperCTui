from qtpy.QtWidgets import QDialog
import os
import numpy as np
import pyqtgraph as pg

from hyperctui import load_ui, EvaluationRegionKeys

from hyperctui.utilities.table import TableHandler
from hyperctui.autonomous_reconstruction.initialization import InitializationSelectTofRegions
from hyperctui.autonomous_reconstruction import ColumnIndex
from hyperctui.utilities.check import is_int


class SelectTofRegions(QDialog):

    def __init__(self, parent=None):
        super(SelectTofRegions, self).__init__(parent)
        self.parent = parent

        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                    os.path.join('ui',
                                                 'select_tof_regions.ui'))

        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Select TOF regions")

        self.initialization()
        # self.update_display_regions()

    def initialization(self):
        o_init = InitializationSelectTofRegions(parent=self, grand_parent=self.parent)
        o_init.all()

    def table_changed(self):
        pass

    def projections_changed(self):
        pass

    def instrument_settings_changed(self):
        pass
    