from hyperctui.autonomous_reconstruction.help_golden_angle import HelpGoldenAngle
from hyperctui.autonomous_reconstruction.help_automatic_angles import HelpAutomaticAngles
from hyperctui.autonomous_reconstruction.select_evaluation_regions import SelectEvaluationRegions


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
        pass
