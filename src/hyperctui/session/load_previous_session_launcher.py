import os

from qtpy.QtWidgets import QDialog

from hyperctui import load_ui
from hyperctui.session.session_handler import SessionHandler
from hyperctui.utilities.folder_path import FolderPath
from hyperctui.utilities.get import Get


class LoadPreviousSessionLauncher(QDialog):
    def __init__(self, parent=None, config=None):
        self.parent = parent
        QDialog.__init__(self, parent=parent)
        ui_full_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), os.path.join("ui", "load_previous_session.ui")
        )
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Load previous session?")
        self.ui.pushButton.setFocus(True)
        # self.ui.no_pushButton.setFocus(True)

    def yes_clicked(self):
        self.close()
        o_session = SessionHandler(parent=self.parent)
        o_get = Get(parent=self.parent)
        full_config_file_name = o_get.get_automatic_config_file_name()
        o_session.load_from_file(config_file_name=full_config_file_name)
        o_session.load_to_ui()
        self.parent.loading_from_config = False
        self.parent.folder_path = FolderPath(parent=self.parent)
        self.parent.folder_path.update()
        self.parent.check_state_of_steps_menu_button()

    def no_clicked(self):
        self.parent.new_session_clicked()
        self.close()

    def reject(self):
        # self.parent.new_session_clicked()
        super(LoadPreviousSessionLauncher, self).reject()

    def close(self):
        super(LoadPreviousSessionLauncher, self).close()
