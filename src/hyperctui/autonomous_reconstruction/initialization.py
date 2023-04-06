import pyqtgraph as pg
from qtpy.QtWidgets import QVBoxLayout, QCheckBox, QHBoxLayout, QSpacerItem, \
    QSizePolicy, QWidget, QProgressBar
from qtpy import QtGui

from hyperctui import EvaluationRegionKeys
from hyperctui import DETECTOR_OFFSET, SOURCE_DETECTOR_DISTANCE
from hyperctui.session import SessionKeys

from hyperctui.utilities.table import TableHandler
from hyperctui.autonomous_reconstruction import ColumnIndex

LABEL_YOFFSET = 0


class InitializationSelectEvaluationRegions:

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
            checked_button.setChecked(evaluation_regions[_row][EvaluationRegionKeys.state])
            checked_button.clicked.connect(self.parent.checkButton_clicked)
            horizontal_layout = QHBoxLayout()
            spacer1 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
            horizontal_layout.addItem(spacer1)
            horizontal_layout.addWidget(checked_button)
            spacer2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
            horizontal_layout.addItem(spacer2)
            checked_button_widget = QWidget()
            checked_button_widget.setLayout(horizontal_layout)
            o_table.insert_widget(row=_row,
                                  column=ColumnIndex.enabled_state,
                                  widget=checked_button_widget)

            o_table.insert_item(row=_row,
                                column=ColumnIndex.name,
                                value=evaluation_regions[_row][EvaluationRegionKeys.name])

            o_table.insert_item(row=_row,
                                column=ColumnIndex.from_value,
                                value=evaluation_regions[_row][EvaluationRegionKeys.from_value])

            o_table.insert_item(row=_row,
                                column=ColumnIndex.to_value,
                                value=evaluation_regions[_row][EvaluationRegionKeys.to_value])
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


class InitializationSelectTofRegions:

    column_sizes = [60, 150, 90, 90]

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

    def all(self):
        self.pyqtgraph()
        self.widgets()
        self.roi()
        self.table()
        self.statusbar()
        self.splitter()

    def splitter(self):
        self.parent.ui.splitter.setSizes([70, 50])

    def statusbar(self):
        self.parent.eventProgress = QProgressBar(self.parent.ui.statusbar)
        self.parent.eventProgress.setMinimumSize(20, 14)
        self.parent.eventProgress.setMaximumSize(540, 100)
        self.parent.eventProgress.setVisible(False)
        self.parent.ui.statusbar.addPermanentWidget(self.parent.eventProgress)

    def pyqtgraph(self):
        self.parent.ui.top_image_view = pg.ImageView(view=pg.PlotItem())
        self.parent.ui.top_image_view.ui.roiBtn.hide()
        self.parent.ui.top_image_view.ui.menuBtn.hide()
        top_image_layout = QVBoxLayout()
        top_image_layout.addWidget(self.parent.ui.top_image_view)
        self.parent.ui.top_widget.setLayout(top_image_layout)

        self.parent.ui.bragg_edge_plot = pg.PlotWidget(title='TOF spectrum')
        self.parent.ui.bragg_edge_plot.plot()
        bottom_image_layout = QVBoxLayout()
        bottom_image_layout.addWidget(self.parent.ui.bragg_edge_plot)
        self.parent.ui.bottom_widget.setLayout(bottom_image_layout)

    def widgets(self):
        self.parent.ui.detector_offset_label.setText(u"Detector offset (\u00B5s)")
        self.parent.ui.distance_source_detector_value.setText(f"{SOURCE_DETECTOR_DISTANCE: .3f}")
        self.parent.ui.detector_offset_value.setText(f"{DETECTOR_OFFSET: .2f}")
        self.parent.previous_distance_source_detector = SOURCE_DETECTOR_DISTANCE
        self.parent.previous_detector_offset = DETECTOR_OFFSET

        self.parent.ui.projections_0degree_radioButton.setText(u"0\u00B0")
        self.parent.ui.projections_180degree_radioButton.setText(u"180\u00B0")

    def roi(self):
        roi = self.grand_parent.session_dict[SessionKeys.tof_roi_region]
        x0 = roi['x0']
        y0 = roi['y0']
        x1 = roi['x1']
        y1 = roi['y1']

        width = x1 - x0 + 1
        height = y1 - y0 + 1

        _color = QtGui.QColor(62, 13, 244)
        _pen = QtGui.QPen()
        _pen.setColor(_color)
        _pen.setWidthF(0.01)

        _roi_id = pg.ROI([x0, y0],
                         [width, height],
                         pen=_pen,
                         scaleSnap=True)
        _roi_id.addScaleHandle([1, 1], [0, 0])
        _roi_id.addScaleHandle([0, 0], [1, 1])

        self.parent.ui.top_image_view.addItem(_roi_id)
        _roi_id.sigRegionChanged.connect(self.parent.top_roi_changed)
        self.parent.top_roi_id = _roi_id

    def table(self):
        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        o_table.set_column_sizes(self.column_sizes)
        tof_regions = self.grand_parent.tof_regions
        o_table.block_signals()
        for _row in tof_regions.keys():
            o_table.insert_empty_row(row=_row)

            checked_button = QCheckBox()
            checked_button.setChecked(tof_regions[_row][EvaluationRegionKeys.state])
            checked_button.clicked.connect(self.parent.checkButton_clicked)
            horizontal_layout = QHBoxLayout()
            spacer1 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
            horizontal_layout.addItem(spacer1)
            horizontal_layout.addWidget(checked_button)
            spacer2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
            horizontal_layout.addItem(spacer2)
            checked_button_widget = QWidget()
            checked_button_widget.setLayout(horizontal_layout)
            o_table.insert_widget(row=_row,
                                  column=ColumnIndex.enabled_state,
                                  widget=checked_button_widget)

            o_table.insert_item(row=_row,
                                column=ColumnIndex.name,
                                value=f"{tof_regions[_row][EvaluationRegionKeys.name]}")

            o_table.insert_item(row=_row,
                                column=ColumnIndex.from_value,
                                value=f"{float(tof_regions[_row][EvaluationRegionKeys.from_value]):.2f}")

            o_table.insert_item(row=_row,
                                column=ColumnIndex.to_value,
                                value=f"{float(tof_regions[_row][EvaluationRegionKeys.to_value]):.2f}")
        o_table.unblock_signals()

    def bragg_regions(self):
        self.parent.ui.tableWidget.blockSignals(True)
        for _key in self.grand_parent.tof_regions.keys():
            _entry = self.grand_parent.tof_regions[_key]
            _state = _entry[EvaluationRegionKeys.state]
            _from = float(_entry[EvaluationRegionKeys.from_value])
            _to = float(_entry[EvaluationRegionKeys.to_value])
            _roi_id = pg.LinearRegionItem(values=(_from, _to),
                                          orientation='vertical',
                                          movable=True,
                                          bounds=[0, self.grand_parent.image_size['height']])

            _roi_id.sigRegionChanged.connect(self.parent.regions_manually_moved)
            _entry[EvaluationRegionKeys.id] = _roi_id

            # label of region
            _name_of_region = _entry[EvaluationRegionKeys.name]
            _label_id = pg.TextItem(html='<div style="text-align:center">' + _name_of_region + '</div>',
                                    fill=QtGui.QColor(255, 255, 255),
                                    anchor=(0, 1))
            _label_id.setPos(_from, LABEL_YOFFSET)
            _entry[EvaluationRegionKeys.label_id] = _label_id

            if _state:
                self.parent.ui.bragg_edge_plot.addItem(_roi_id)
                self.parent.ui.bragg_edge_plot.addItem(_label_id)

        self.parent.ui.tableWidget.blockSignals(False)
