from qtpy.QtGui import QGuiApplication
import inflect

from hyperctui import EvaluationRegionKeys

from hyperctui.autonomous_reconstruction.help_golden_angle import HelpGoldenAngle
from hyperctui.autonomous_reconstruction.help_automatic_angles import HelpAutomaticAngles
from hyperctui.autonomous_reconstruction.select_evaluation_regions import SelectEvaluationRegions
from hyperctui.autonomous_reconstruction.select_tof_regions import SelectTofRegions


class EventHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def projections_angles_radioButton_changed(self):
        fixed_state = self.parent.ui.fixed_projections_angles_radioButton.isChecked()
        self.parent.ui.automatic_projections_angles_pushButton.setEnabled(not fixed_state)

    def projections_angles_automatic_button_clicked(self):
        o_ui = SelectEvaluationRegions(parent=self.parent)
        o_ui.show()

    def projections_fixed_help_clicked(self):
        o_ui = HelpGoldenAngle(parent=self.parent)
        o_ui.show()

    def projections_automatic_help_clicked(self):
        o_ui = HelpAutomaticAngles(parent=self.parent)
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
        else:
            self.parent.ui.tof_region_of_interest_error_label.setVisible(True)
