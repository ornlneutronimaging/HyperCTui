from qtpy.QtWidgets import QMainWindow
from qtpy.QtGui import QGuiApplication
from qtpy import QtGui
import os
import glob
import logging
import numpy as np
import tifffile
import pyqtgraph as pg

from neutronbraggedge.experiment_handler.tof import TOF
from neutronbraggedge.experiment_handler.experiment import Experiment

from hyperctui.utilities.table import TableHandler
from hyperctui import load_ui, EvaluationRegionKeys
from hyperctui.session import SessionKeys
from hyperctui.utilities.check import is_float, is_int

from hyperctui.autonomous_reconstruction.initialization import InitializationSelectTofRegions
from hyperctui.autonomous_reconstruction import ColumnIndex

LABEL_YOFFSET = 0


class SelectTofRegions(QMainWindow):

    top_roi_id = None

    ok_clicked = False

    # used in case the value entered by the user are not valid
    previous_distance_source_detector = None
    previous_detector_offset = None

    # tof array from spectra file (using the 0degree angle to retrieve it)
    tof_array = None

    # lambda array to use for x-axis of Bragg edge
    lambda_array = None

    def __init__(self, parent=None):
        super(SelectTofRegions, self).__init__(parent)
        self.parent = parent

        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                    os.path.join('ui',
                                                 'select_tof_regions.ui'))

        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Select TOF regions")

        self.parent.backup_tof_regions = self.parent.tof_regions
        self.initialization()
        self.load_time_spectra()
        self.calculate_lambda_axis()
        self.check_table_state()
        self.check_state_ok_button()

    def initialization(self):
        o_init = InitializationSelectTofRegions(parent=self, grand_parent=self.parent)
        o_init.all()

    def init_bragg_regions(self):
        o_init = InitializationSelectTofRegions(parent=self, grand_parent=self.parent)
        # o_init.bragg_regions()

    def load_time_spectra(self):
        session_dict = self.parent.session_dict
        image_0_full_path = session_dict[SessionKeys.full_path_to_projections][SessionKeys.image_0_degree]
        folder_inside = glob.glob(os.path.join(image_0_full_path, 'Run_*'))
        spectra_filename = glob.glob(os.path.join(folder_inside[0], "*_Spectra.txt"))
        tof_handler = TOF(filename=spectra_filename[0])
        self.tof_array = tof_handler.tof_array

    def load_images(self):
        session_dict = self.parent.session_dict
        if self.ui.projections_0degree_radioButton.isChecked():
            if self.parent.image_data[SessionKeys.image_0_degree] is None:
                logging.info("Loading stack of images at 0degree!")
                image_0_full_path = session_dict[SessionKeys.full_path_to_projections][SessionKeys.image_0_degree]
                self.parent.image_data[SessionKeys.image_0_degree] = \
                    self.load_images_from_this_folder(folder_name=image_0_full_path)
        else:
            if self.parent.image_data[SessionKeys.image_180_degree] is None:
                logging.info("Loading stack of images at 180degrees!")
                image_180_full_path = session_dict[SessionKeys.full_path_to_projections][SessionKeys.image_180_degree]
                self.parent.image_data[SessionKeys.image_180_degree] = \
                    self.load_images_from_this_folder(folder_name=image_180_full_path)

    def load_images_from_this_folder(self, folder_name):
        """
        all the images are in fact inside the folder called "Run_####" within that folder
        """
        folder_inside = glob.glob(os.path.join(folder_name, 'Run_*'))
        list_tiff = glob.glob(os.path.join(folder_inside[0], "*.tif"))
        list_tiff.sort()
        logging.info(f"-> loading {len(list_tiff)} 'tif' files!")
        # load the tiff using iMars3D

        self.eventProgress.setValue(0)
        self.eventProgress.setMaximum(len(list_tiff))
        self.eventProgress.setVisible(True)
        QGuiApplication.processEvents()

        data = []

        for _index, _file in enumerate(list_tiff):
            # _data = dxchange.read_tiff(_file)
            _data = tifffile.imread(_file)
            self.eventProgress.setValue(_index+1)
            QGuiApplication.processEvents()
            data.append(_data)

        self.eventProgress.setVisible(False)
        QGuiApplication.processEvents()

        return data

    def display_tof_profile(self):
        tof_roi_region = self.parent.session_dict[SessionKeys.tof_roi_region]
        x0 = tof_roi_region['x0']
        y0 = tof_roi_region['y0']
        x1 = tof_roi_region['x1']
        y1 = tof_roi_region['y1']
        if self.ui.projections_0degree_radioButton.isChecked():
            full_data = self.parent.image_data[SessionKeys.image_0_degree]
        else:
            full_data = self.parent.image_data[SessionKeys.image_180_degree]

        tof_profile = []
        for _index, _data in enumerate(full_data):
            _counts_of_roi = _data[y0:y1+1, x0:x1+1]
            _mean_counts = np.mean(_counts_of_roi)
            tof_profile.append(_mean_counts)

        self.ui.bragg_edge_plot.clear()
        self.ui.bragg_edge_plot.plot(self.lambda_array, tof_profile)
        self.ui.bragg_edge_plot.setLabel("bottom", u"\u03BB (\u212B)")
        self.ui.bragg_edge_plot.setLabel("left", "Average Counts")

    def table_changed(self):
        # self.check_table_content()
        self.clear_all_regions()
        self.save_table()
        self.check_table_state()
        self.update_display_regions()

    def clear_all_regions(self):
        # clear all region items and labels
        for _key in self.parent.tof_regions.keys():
            if self.parent.tof_regions[_key][EvaluationRegionKeys.id]:
                self.ui.bragg_edge_plot.removeItem(self.parent.tof_regions[_key][EvaluationRegionKeys.id])
                self.ui.bragg_edge_plot.removeItem(self.parent.tof_regions[_key][EvaluationRegionKeys.label_id])

    def update_display_regions(self):
        # replace all the regions
        for _key in self.parent.tof_regions.keys():
            _entry = self.parent.tof_regions[_key]
            _state = _entry[EvaluationRegionKeys.state]
            if _state:
                _from = float(_entry[EvaluationRegionKeys.from_value])
                _to = float(_entry[EvaluationRegionKeys.to_value])
                _roi_id = pg.LinearRegionItem(values=(_from, _to),
                                              orientation='vertical',
                                              movable=True,
                                              bounds=[0, self.parent.image_size['height']])
                self.ui.bragg_edge_plot.addItem(_roi_id)
                _roi_id.sigRegionChanged.connect(self.regions_manually_moved)
                _roi_id.sigRegionChangeFinished.connect(self.regions_done_manually_moved)
                _entry[EvaluationRegionKeys.id] = _roi_id

                # label of region
                _name_of_region = _entry[EvaluationRegionKeys.name]
                _label_id = pg.TextItem(html='<div style="text-align: center">' + _name_of_region + '</div>',
                                        fill=QtGui.QColor(255, 255, 255),
                                        anchor=(0, 1))
                _label_id.setPos(_from, LABEL_YOFFSET)
                self.ui.bragg_edge_plot.addItem(_label_id)
                _entry[EvaluationRegionKeys.label_id] = _label_id

    def save_table(self):
        o_table = TableHandler(table_ui=self.ui.tableWidget)
        row_count = o_table.row_count()
        tof_regions = {}
        for _row in np.arange(row_count):
            _state_widget = o_table.get_inner_widget(row=_row,
                                                     column=ColumnIndex.enabled_state,
                                                     position_index=1)
            _state = _state_widget.isChecked()
            _name = o_table.get_item_str_from_cell(row=_row,
                                                   column=ColumnIndex.name)
            _from = float(o_table.get_item_str_from_cell(row=_row,
                                                       column=ColumnIndex.from_value))
            _to = float(o_table.get_item_str_from_cell(row=_row,
                                                     column=ColumnIndex.to_value))
            _from, _to = self.sort(_from, _to)

            tof_regions[_row] = {EvaluationRegionKeys.state: _state,
                                 EvaluationRegionKeys.name: _name,
                                 EvaluationRegionKeys.from_value: float(_from),
                                 EvaluationRegionKeys.to_value: float(_to),
                                 EvaluationRegionKeys.id: None}
        self.parent.tof_regions = tof_regions

    def check_table_content(self):
        """
        make sure 'from' and 'to' values are int
        make sure 'from' value is smaller than 'to' value, otherwise reverse them
        """
        o_table = TableHandler(table_ui=self.ui.tableWidget)
        o_table.block_signals()
        nbr_row = o_table.row_count()
        for _row in np.arange(nbr_row):
            from_value = o_table.get_item_str_from_cell(row=_row,
                                                        column=ColumnIndex.from_value)
            to_value = o_table.get_item_str_from_cell(row=_row,
                                                      column=ColumnIndex.to_value)
            if not is_float(from_value):
                from_value = 0
            else:
                from_value = float(from_value)

            if not is_float(to_value):
                to_value = 10
            else:
                to_value = float(to_value)

            minimum_value = np.min([from_value, to_value])
            maximum_value = np.max([from_value, to_value])

            from_value = str(minimum_value)
            to_value = str(maximum_value)

            o_table.set_item_with_str(row=_row,
                                      column=ColumnIndex.from_value,
                                      value=from_value)
            o_table.set_item_with_str(row=_row,
                                      column=ColumnIndex.to_value,
                                      value=to_value)

    def check_table_state(self):
        """
        for example, if a state is disabled, the other widgets/columns for that row will be disabled and
        can not be edited
        """
        o_table = TableHandler(table_ui=self.ui.tableWidget)
        o_table.block_signals()
        nbr_row = o_table.row_count()
        for _row in np.arange(nbr_row):
            _state_widget = o_table.get_inner_widget(row=_row,
                                                     column=ColumnIndex.enabled_state,
                                                     position_index=1)
            _state = _state_widget.isChecked()

            # disabled or not editing
            o_table.set_item_state(row=_row, column=ColumnIndex.name, editable=_state)
            o_table.set_item_state(row=_row, column=ColumnIndex.from_value, editable=_state)
            o_table.set_item_state(row=_row, column=ColumnIndex.to_value, editable=_state)
        o_table.unblock_signals()

    def projections_changed(self):
        self.ui.setEnabled(False)
        self.load_images()
        self.update_top_view()
        self.display_tof_profile()
        self.update_display_regions()
        self.ui.setEnabled(True)

    def instrument_settings_changed(self):
        distance_source_detector = str(self.ui.distance_source_detector_value.text())
        if not is_float(distance_source_detector):
            distance_source_detector = self.previous_distance_source_detector
        else:
            self.previous_distance_source_detector = distance_source_detector

        self.ui.distance_source_detector_value.blockSignals(True)
        self.ui.distance_source_detector_value.setText(f"{float(distance_source_detector):.3f}")
        self.ui.distance_source_detector_value.blockSignals(False)

        detector_offset = str(self.ui.detector_offset_value.text())
        if not is_int(detector_offset):
            detector_offset = self.previous_detector_offset
        else:
            self.previous_detector_offset = detector_offset
        self.ui.detector_offset_value.blockSignals(True)
        self.ui.detector_offset_value.setText(f"{int(detector_offset)}")
        self.ui.detector_offset_value.blockSignals(False)

        self.calculate_lambda_axis()
        self.display_tof_profile()
        self.update_display_regions()

    def calculate_lambda_axis(self):
        distance_source_detector = float(str(self.ui.distance_source_detector_value.text()))
        detector_offset = float(str(self.ui.detector_offset_value.text()))

        tof_array = self.tof_array
        exp = Experiment(tof=tof_array,
                         distance_source_detector_m=distance_source_detector,
                         detector_offset_micros=detector_offset)
        self.lambda_array = exp.lambda_array * 1e10  # to be in Angstroms

    def update_top_view(self):
        if self.ui.projections_0degree_radioButton.isChecked():
            image = self.parent.image_0_degree
        elif self.ui.projections_180degree_radioButton.isChecked():
            image = self.parent.image_180_degree
        else:
            raise NotImplementedError("image to display is not 0 or 180 degree!")
        self.ui.top_image_view.setImage(image)
        self.top_live_image = image

    def top_roi_changed(self):
        region = self.top_roi_id.getArraySlice(self.top_live_image,
                                               self.ui.top_image_view.imageItem)

        left = region[0][0].start
        right = region[0][0].stop
        top = region[0][1].start
        bottom = region[0][1].stop

        self.parent.session_dict[SessionKeys.tof_roi_region] = {'x0': left,
                                                                'y0': top,
                                                                'x1': right,
                                                                'y1': bottom}
        self.display_tof_profile()
        self.replot_bragg_regions()

    def checkButton_clicked(self):
        self.table_changed()
        self.check_state_ok_button()

    def replot_bragg_regions(self):
        """replot the Bragg regions"""
        for _key in self.parent.tof_regions.keys():
            _entry = self.parent.tof_regions[_key]
            _state = _entry[EvaluationRegionKeys.state]
            if _state:
                _roi_id = _entry[EvaluationRegionKeys.id]
                self.ui.bragg_edge_plot.addItem(_roi_id)

                # label of region
                _label_id = _entry[EvaluationRegionKeys.label_id]
                self.ui.bragg_edge_plot.addItem(_label_id)

    def regions_done_manually_moved(self):
        self.table_changed()

    def regions_manually_moved(self):
        """
        user moved one of the region using mouse click
        so the program needs to record the new position of the regions and fill the
        table with this value
        """
        o_table = TableHandler(table_ui=self.ui.tableWidget)
        o_table.block_signals()
        for _row, _key in enumerate(self.parent.tof_regions.keys()):

            _entry = self.parent.tof_regions[_key]
            _state = _entry[EvaluationRegionKeys.state]
            if _state:
                _id = _entry[EvaluationRegionKeys.id]
                (_from, _to) = _id.getRegion()
                _from, _to = SelectTofRegions.sort(_from, _to)
                o_table.set_item_with_str(row=_row,
                                          column=ColumnIndex.from_value,
                                          value=f"{float(_from):.2f}")
                o_table.set_item_with_str(row=_row,
                                          column=ColumnIndex.to_value,
                                          value=f"{float(_to):.2f}")

                # move label as well
                _label_id = _entry[EvaluationRegionKeys.label_id]
                _label_id.setPos(_from, LABEL_YOFFSET)

        # self.check_validity_of_table()
        o_table.unblock_signals()
        # self.update_evaluation_regions_dict()

    def is_ok_button_ready(self):
        tof_regions = self.parent.tof_regions
        nbr_region_enabled = 0
        for _key in tof_regions.keys():
            if tof_regions[_key][EvaluationRegionKeys.state]:
                nbr_region_enabled += 1

        if nbr_region_enabled > 0:
            return True

        return False

    def check_state_ok_button(self):
        if self.is_ok_button_ready():
            self.ui.pushButton.setEnabled(True)
        else:
            self.ui.pushButton.setEnabled(False)


    def accept(self):
        self.ok_clicked = True
        self.save_table()
        self.parent.update_autonomous_widgets()
        self.close()

    def cancel(self):
        self.close()

    def closeEvent(self, a0):
        if self.ok_clicked:
            pass
        else:
            self.parent.tof_regions = self.parent.backup_tof_regions

    @staticmethod
    def sort(value1: float, value2: float):
        minimum_value = np.min([value1, value2])
        maximum_value = np.max([value1, value2])
        return minimum_value, maximum_value

