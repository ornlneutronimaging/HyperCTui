from qtpy.QtWidgets import QProgressBar, QVBoxLayout
import pyqtgraph as pg
from qtpy.QtGui import QIcon
import numpy as np

from ..utilities.config_handler import ConfigHandler
from ..utilities.table import TableHandler
from .. import more_infos, TabNames, tab0_icon, tab1_icon


class GuiInitialization:

    def __init__(self, parent=None):
        self.parent = parent

        # load config
        o_config = ConfigHandler(parent=self.parent)
        o_config.load()

    def all(self):
        self.statusbar()
        self.widgets()
        self.tables()
        self.tabs()
        self.pyqtgraph()

    def tabs(self):
        self.parent.ui.tabWidget.setTabText(0, TabNames.tab0)
        self.parent.ui.tabWidget.setTabIcon(0, QIcon(tab0_icon))
        self.parent.ui.tabWidget.setTabText(1, TabNames.tab1)
        self.parent.ui.tabWidget.setTabIcon(1, QIcon(tab1_icon))

        self.parent.tab2 = self.parent.ui.tabWidget.widget(2)
        self.parent.tab3 = self.parent.ui.tabWidget.widget(3)
        self.parent.tab4 = self.parent.ui.tabWidget.widget(4)
        for _ in np.arange(3):
            self.parent.ui.tabWidget.removeTab(2)
        self.parent.all_tabs_visible = False

    def tables(self):
        o_table = TableHandler(table_ui=self.parent.ui.open_beam_tableWidget)
        column_sizes = [600, 50]
        o_table.set_column_sizes(column_sizes=column_sizes)

    def full_reset(self):
        pass

    def widgets(self):
        more_infos_icon = QIcon(more_infos)
        self.parent.ui.help_pushButton.setIcon(more_infos_icon)

        # message telling that the projections title has been modified because it's already there
        self.parent.ui.projections_title_message.setVisible(False)
        self.parent.ui.top_crop_widget.setEnabled(False)

    def statusbar(self):
        self.parent.eventProgress = QProgressBar(self.parent.ui.statusbar)
        self.parent.eventProgress.setMinimumSize(20, 14)
        self.parent.eventProgress.setMaximumSize(540, 100)
        self.parent.eventProgress.setVisible(False)
        self.parent.ui.statusbar.addPermanentWidget(self.parent.eventProgress)

    def pyqtgraph(self):
        self.parent.ui.crop_image_view = pg.ImageView(view=pg.PlotItem())
        self.parent.ui.crop_image_view.ui.roiBtn.hide()
        self.parent.ui.crop_image_view.ui.menuBtn.hide()
        image_layout = QVBoxLayout()
        image_layout.addWidget(self.parent.ui.crop_image_view)
        self.parent.ui.crop_widget.setLayout(image_layout)
