class EventHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def radio_button_changed(self):
        list_ui_tomopy = [self.parent.ui.rotation_center_tomopy_label1,
                          self.parent.ui.rotation_center_tomopy_label2,
                          self.parent.ui.rotation_center_tomopy_value]

        list_ui_user = [self.parent.ui.rotation_center_user_label1,
                        self.parent.ui.rotation_center_user_label2,
                        self.parent.ui.rotation_center_user_value]

        is_tomopy_radio_button_checked = self.parent.ui.rotation_center_tomopy_radioButton.isChecked()

        for _ui in list_ui_tomopy:
            _ui.setEnabled(is_tomopy_radio_button_checked)
        for _ui in list_ui_user:
            _ui.setEnabled(not is_tomopy_radio_button_checked)

