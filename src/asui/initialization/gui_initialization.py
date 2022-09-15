from qtpy.QtWidgets import QProgressBar, QVBoxLayout
import pyqtgraph as pg

from ..utilities.config_handler import ConfigHandler
from ..utilities.table import TableHandler
# from . import interact_me_style


class GuiInitialization:

    def __init__(self, parent=None):
        self.parent = parent

        # load config
        o_config = ConfigHandler(parent=self.parent)
        o_config.load()

    def all(self):
        pass
        # self.main_tab()
        # self.tables()

    def main_tab(self):
        self.parent.ui.tabWidget.setTabEnabled(1, False)

    def tables(self):
        o_table = TableHandler(table_ui=self.parent.ui.step1_open_beam_tableWidget)
        column_sizes = [650, 50]
        o_table.set_column_sizes(column_sizes=column_sizes)

    def full_reset(self):
        pass

    #     self.widgets()
    #
    #     self.parent.ui.crop_image_view.clear()
    #     self.parent.ui.center_of_rotation_image_view.clear()
    #     self.parent.ui.tilt_correction_image_view.clear()
    #     self.parent.ui.projections_lineEdit.setText("")
    #
    #     self.parent.ui.ob_lineEdit.setText("")
    #     self.parent.ui.ob_lineEdit.setEnabled(False)
    #     self.parent.ui.select_ob_pushButton.setEnabled(False)
    #
    #     self.parent.ui.df_lineEdit.setText("")
    #     self.parent.ui.df_lineEdit.setEnabled(False)
    #     self.parent.ui.select_df_pushButton.setEnabled(False)
    #
    #     self.parent.ui.preview_pushButton.setEnabled(False)
    #
    #     self.parent.ui.output_folder_lineEdit.setText("")
    #     self.parent.ui.output_folder_lineEdit.setEnabled(False)
    #     self.parent.ui.select_output_folder_pushButton.setEnabled(False)
    #
    #     self.parent.preview_histogram = None
    #
    # def widgets(self):
    #     self.parent.ui.select_projections_pushButton.setStyleSheet(interact_me_style)
    #     self.parent.ui.tabWidget.setTabEnabled(1, False)
    #     self.parent.ui.tabWidget.setTabEnabled(2, False)
    #     self.parent.ui.tabWidget.setTabEnabled(3, False)
    #
    #     self.parent.ui.tabWidget_2.setTabEnabled(1, False)
    #     self.parent.ui.tabWidget_2.setCurrentIndex(0)
    #     self.parent.ui.tabWidget_3.setCurrentIndex(0)
    #
    # def statusbar(self):
    #     self.parent.eventProgress = QProgressBar(self.parent.ui.statusbar)
    #     self.parent.eventProgress.setMinimumSize(20, 14)
    #     self.parent.eventProgress.setMaximumSize(540, 100)
    #     self.parent.eventProgress.setVisible(False)
    #     self.parent.ui.statusbar.addPermanentWidget(self.parent.eventProgress)
    #
    # def pyqtgraph(self):
    #
    #     # crop
    #     self.parent.ui.crop_image_view = pg.ImageView(view=pg.PlotItem())
    #     self.parent.ui.crop_image_view.ui.roiBtn.hide()
    #     self.parent.ui.crop_image_view.ui.menuBtn.hide()
    #     image_layout = QVBoxLayout()
    #     image_layout.addWidget(self.parent.ui.crop_image_view)
    #     self.parent.ui.crop_widget.setLayout(image_layout)
    #
    #     # center of rotation
    #     self.parent.ui.center_of_rotation_image_view = pg.ImageView(view=pg.PlotItem())
    #     self.parent.ui.center_of_rotation_image_view.ui.roiBtn.hide()
    #     self.parent.ui.center_of_rotation_image_view.ui.menuBtn.hide()
    #     image_layout = QVBoxLayout()
    #     image_layout.addWidget(self.parent.ui.center_of_rotation_image_view)
    #     self.parent.ui.center_of_rotation_widget.setLayout(image_layout)
    #
    #     # tilt correction
    #     self.parent.ui.tilt_correction_image_view = pg.ImageView(view=pg.PlotItem())
    #     self.parent.ui.tilt_correction_image_view.ui.roiBtn.hide()
    #     self.parent.ui.tilt_correction_image_view.ui.menuBtn.hide()
    #     image_layout = QVBoxLayout()
    #     image_layout.addWidget(self.parent.ui.tilt_correction_image_view)
    #     self.parent.ui.tilt_correction_widget.setLayout(image_layout)
    #
    #     # output tab
    #     self.parent.ui.output_image_view = pg.ImageView(view=pg.PlotItem())
    #     self.parent.ui.output_image_view.ui.roiBtn.hide()
    #     self.parent.ui.output_image_view.ui.menuBtn.hide()
    #     image_layout = QVBoxLayout()
    #     image_layout.addWidget(self.parent.ui.output_image_view)
    #     self.parent.ui.output_widget.setLayout(image_layout)
    #
    #     self.parent.ui.reconstructed_image_view = pg.ImageView(view=pg.PlotItem())
    #     self.parent.ui.reconstructed_image_view.ui.roiBtn.hide()
    #     self.parent.ui.reconstructed_image_view.ui.menuBtn.hide()
    #     image_layout = QVBoxLayout()
    #     image_layout.addWidget(self.parent.ui.reconstructed_image_view)
    #     self.parent.ui.final_reconstructed_widget.setLayout(image_layout)
