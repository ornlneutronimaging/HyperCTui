from qtpy.QtWidgets import QDialog
import os

from hyperctui import load_ui


class HelpAutomaticAngles(QDialog):

    def __init__(self, parent=None):
        super(HelpAutomaticAngles, self).__init__(parent)
        self.parent = parent

        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                    os.path.join('ui',
                                                 'help_automatic_angle.ui'))

        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Automatic Angle")

        self.initialization()

    def initialization(self):
        pass
