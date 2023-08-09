from qtpy.QtGui import QGuiApplication
import inflect
import numpy as np

from hyperctui import EvaluationRegionKeys
from hyperctui import interact_me_style, normal_style, error_style, label_in_focus_style

from hyperctui.utilities.status_message_config import StatusMessageStatus, show_status_message
from hyperctui.utilities.table import TableHandler

from hyperctui.autonomous_reconstruction.help_golden_angle import HelpGoldenAngle
from hyperctui.autonomous_reconstruction.select_evaluation_regions import SelectEvaluationRegions
from hyperctui.autonomous_reconstruction.select_tof_regions import SelectTofRegions
from hyperctui.pre_autonomous_monitor import DataStatus, ColorDataStatus


class EventHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def projections_angles_radioButton_changed(self):
        fixed_state = self.parent.ui.fixed_projections_angles_radioButton.isChecked()
        self.parent.ui.automatic_projections_angles_pushButton.setEnabled(not fixed_state)
        self.update_widgets()

    def projections_angles_automatic_button_clicked(self):
        o_ui = SelectEvaluationRegions(parent=self.parent)
        o_ui.show()

    def projections_fixed_help_clicked(self):
        o_ui = HelpGoldenAngle(parent=self.parent)
        o_ui.show()

    def evaluation_frequency_help_clicked(self):
        pass

    def tof_region_selection_button_clicked(self):
        o_ui = SelectTofRegions(parent=self.parent)
        o_ui.show()
        QGuiApplication.processEvents()
        o_ui.projections_changed()
        QGuiApplication.processEvents()

    def update_widgets(self):
        """ update the widgets such as the number of TOF regions selected"""
        tof_regions = self.parent.tof_regions
        nbr_regions_selected = 0
        for _key in tof_regions.keys():
            if tof_regions[_key][EvaluationRegionKeys.state]:
                nbr_regions_selected += 1

        p = inflect.engine()
        self.parent.ui.tof_region_of_interest_label.setText(f"{nbr_regions_selected} " +
                                                            p.plural("region", nbr_regions_selected) + " selected!")

        if nbr_regions_selected > 0:
            self.parent.ui.tof_region_of_interest_error_label.setVisible(False)
            self.parent.ui.tof_region_of_interest_pushButton.setText("Edit TOF regions ...")
        else:
            self.parent.ui.tof_region_of_interest_error_label.setVisible(True)
            self.parent.ui.tof_region_of_interest_pushButton.setText("Select TOF regions ...")

        self.check_state_of_start_pre_acquisition_button()

    def is_start_pre_acquisition_button_ready(self):
        """
        return True if all the conditions are met to enable the pre-acquisition button
        """
        tof_regions = self.parent.tof_regions
        nbr_regions_selected = 0
        for _key in tof_regions.keys():
            if tof_regions[_key][EvaluationRegionKeys.state]:
                nbr_regions_selected += 1

        if nbr_regions_selected == 0:
            self.parent.ui.tof_region_of_interest_pushButton.setStyleSheet(error_style)
            return False
        else:
            self.parent.ui.tof_region_of_interest_pushButton.setStyleSheet(normal_style)

        if self.parent.ui.automatic_projections_angles_radioButton.isChecked():
            evaluation_regions = self.parent.evaluation_regions
            nbr_regions_selected = 0
            for _key in evaluation_regions.keys():
                if evaluation_regions[_key][EvaluationRegionKeys.state]:
                    nbr_regions_selected += 1

            if nbr_regions_selected == 0:
                self.parent.ui.automatic_projections_angles_pushButton.setStyleSheet(error_style)
                return False
            else:
                self.parent.ui.automatic_projections_angles_pushButton.setStyleSheet(normal_style)

        return True

    def check_state_of_start_pre_acquisition_button(self):
        is_button_ready = self.is_start_pre_acquisition_button_ready()

        # no TOF selected yet
        if self.parent.tof_regions[0].get(EvaluationRegionKeys.from_index, None) is None:
            self.parent.ui.tof_region_of_interest_pushButton.setStyleSheet(interact_me_style)
            is_button_ready = False
        else:
            self.parent.ui.tof_region_of_interest_pushButton.setStyleSheet(normal_style)

        self.parent.ui.start_first_reconstruction_pushButton.setEnabled(is_button_ready)
        if is_button_ready:
            self.parent.ui.start_first_reconstruction_pushButton.setStyleSheet(interact_me_style)
        else:
            self.parent.ui.start_first_reconstruction_pushButton.setStyleSheet(normal_style)

    def evaluation_frequency_changed(self):
        pass

    def start_acquisition(self):
        # disable all previous widgets
        self.parent.ui.autonomous_projections_groupBox.setEnabled(False)
        self.parent.ui.autonomous_evaluation_groupBox.setEnabled(False)
        self.parent.ui.autonomous_tof_regions_groupBox.setEnabled(False)
        self.parent.ui.start_first_reconstruction_pushButton.setEnabled(False)
        self.parent.ui.start_first_reconstruction_pushButton.setStyleSheet(normal_style)
        self.parent.ui.autonomous_refresh_pushButton.setEnabled(True)

        # enable table
        self.parent.ui.autonomous_monitor_groupBox.setVisible(True)
        self.parent.ui.autonomous_refresh_pushButton.setStyleSheet(interact_me_style)

        number_angles = self.parent.ui.evaluation_frequency_spinBox.value()
        show_status_message(parent=self.parent,
                            message=f"Starting acquisition of {number_angles} angles!",
                            duration_s=5,
                            status=StatusMessageStatus.working)

        self.init_autonomous_table()

    def stop_acquisition(self):
        self.parent.ui.autonomous_projections_groupBox.setEnabled(True)
        self.parent.ui.autonomous_evaluation_groupBox.setEnabled(True)
        self.parent.ui.autonomous_tof_regions_groupBox.setEnabled(True)
        self.parent.ui.start_first_reconstruction_pushButton.setEnabled(True)

        self.parent.ui.autonomous_refresh_pushButton.setStyleSheet(normal_style)

        show_status_message(parent=self.parent,
                            message=f"Stopped acquisition!",
                            duration_s=5,
                            status=StatusMessageStatus.warning)

    def init_autonomous_table(self):
        # output_table =
        nbr_angles = self.parent.ui.evaluation_frequency_spinBox.value()
        list_golden_ratio_angles_collected = self.parent.golden_ratio_angles[0:nbr_angles]
        formatted1_list_golden_ratio_angles_collected = [f"{_value:.2f}" for _value in
                                                         list_golden_ratio_angles_collected]
        formatted2_list_golden_ratio = [_value.replace(".", "_") for _value in
                                        formatted1_list_golden_ratio_angles_collected]

        folder_path = self.parent.folder_path
        print(f"{folder_path =}")

        tof_regions = self.parent.tof_regions
        list_tof_region_collected = []
        list_tof_region_index = []
        for _index in tof_regions.keys():
            if tof_regions[_index][EvaluationRegionKeys.state]:
                _from_value = float(tof_regions[_index][EvaluationRegionKeys.from_value])
                _from_value = f"{_from_value:06.3f}"

                _from_pre, _from_post = _from_value.split(".")
                _from = "{:03d}_{:d}".format(int(_from_pre), int(_from_post))

                _to_value = float(tof_regions[_index][EvaluationRegionKeys.to_value])
                _to_value = f"{_to_value:06.3f}"
                _to_pre, _to_post = _to_value.split(".")
                _to = "{:03d}_{:d}".format(int(_to_pre), int(_to_post))

                _from_index = tof_regions[_index][EvaluationRegionKeys.from_index]
                _to_index = tof_regions[_index][EvaluationRegionKeys.to_index]

                list_tof_region_collected.append(f"from_{_from}Ang_to_{_to}Ang")
                list_tof_region_index.append(f"from index: {_from_index:04d} to index: {_to_index:04d}")

        print(f"{formatted2_list_golden_ratio =}")
        print(f"{ list_tof_region_collected =}")
        print(f"{list_tof_region_index =}")

        o_table = TableHandler(table_ui=self.parent.ui.autonomous_reconstruction_tableWidget)
        o_table.remove_all_rows()

        for _row in np.arange(nbr_angles):
            o_table.insert_empty_row(row=_row)







        self.parent.ui.autonomous_reconstructed_location_label.setText(folder_path.recon)
        self.parent.ui.autonomous_reconstructed_status_label.setText(DataStatus.in_progress)
        self.parent.ui.autonomous_reconstructed_status_label.setStyleSheet(label_in_focus_style)

    def refresh_table_clicked(self):
        """refresh button next to the table has been clicked"""
        pass
