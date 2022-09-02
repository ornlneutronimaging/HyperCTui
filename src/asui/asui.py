from qtpy.QtWidgets import QMainWindow, QApplication
import sys
import os
from . import load_ui

#warnings.filterwarnings('ignore')


class AiSvmbirUi(QMainWindow):


    def __init__(self, parent=None):

        super(AiSvmbirUi, self).__init__(parent)

        ui_full_path = os.path.join(os.path.dirname(__file__),
                                    os.path.join('ui',
                                                 'main_application.ui'))

        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("aiSVMBIRui")

    # leaving ui
    def closeEvent(self, c):
        self.close()


def main(args):
    app = QApplication(args)
    app.setStyle('Fusion')
    app.aboutToQuit.connect(clean_up)
    app.setApplicationDisplayName("aiSVMBIRui")
    window = AiSvmbirUi()
    window.show()
    sys.exit(app.exec_())


def clean_up():
    app = QApplication.instance()
    app.closeAllWindows()
