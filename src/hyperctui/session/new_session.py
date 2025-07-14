from qtpy.QtWidgets import QDialog
import os
import numpy as np

from hyperctui import load_ui
from hyperctui.setup_ob.get import Get
from hyperctui.utilities.folder_path import FolderPath
from hyperctui.utilities.table import TableHandler
from hyperctui.setup_ob.event_handler import EventHandler as ObEventHandler
from hyperctui.session import SessionKeys


class NewSession(QDialog):

    def __init__(self, parent=None):
        session_dict = parent.session_dict
        self.parent = parent
        QDialog.__init__(self, parent=parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                    os.path.join('ui',
                                                 'new_session.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)

        instrument = session_dict[SessionKeys.instrument]
        index_instrument = self.ui.instrument_comboBox.findText(instrument)
        self.ui.instrument_comboBox.setCurrentIndex(index_instrument)
        self.instrument_changed(instrument)
        ipts = session_dict[SessionKeys.ipts_selected]
        if ipts in self.new_list_ipts:
            index = self.ui.ipts_comboBox.findText(ipts)
            self.ui.ipts_comboBox.setCurrentIndex(index)
        self.ui.ok_pushButton.setFocus(True)
        self.setWindowTitle("New session")

    def instrument_changed(self, new_instrument):
        o_get = Get(parent=self.parent)
        facility = Get.facility(instrument=new_instrument)
        list_ipts = o_get.list_of_ipts(instrument=new_instrument,
                                       facility=facility)
        self.new_list_ipts = list_ipts
        self.ui.ipts_comboBox.clear()
        self.ui.ipts_comboBox.blockSignals(True)
        self.ui.ipts_comboBox.addItems(list_ipts)

    def accept(self):
        instrument = self.ui.instrument_comboBox.currentText()
        ipts = self.ui.ipts_comboBox.currentText()
        ipts_index = self.ui.ipts_comboBox.currentIndex()

        self.parent.session_dict[SessionKeys.facility] = 'SNS' if instrument in ['SNAP', 'VENUS'] else 'HFIR'
        self.parent.session_dict[SessionKeys.instrument] = instrument
        self.parent.session_dict[SessionKeys.ipts_selected] = ipts
        self.parent.session_dict[SessionKeys.ipts_index_selected] = ipts_index
        self.parent.set_window_title()
        self.parent.inform_of_output_location()

        # make sure start acquisition button is visible
        self.parent.ui.start_acquisition_pushButton.setVisible(True)
        self.parent.ui.checking_status_acquisition_pushButton.setEnabled(False)
        self.parent.session_dict[SessionKeys.started_acquisition] = False

        self.parent.ui.tabWidget.setCurrentIndex(0)
        self.parent.ui.ob_tabWidget.setCurrentIndex(0)
        self.parent.all_tabs_visible = False

        self.parent.ui.tabWidget.setCurrentIndex(0)
        self.parent.ui.run_title_lineEdit.setText("")

        self.parent.folder_path = FolderPath(parent=self.parent)
        self.parent.folder_path.update()

        # clear OB
        mcp_folder = self.parent.folder_path.mcp
        self.parent.ui.existing_ob_top_path.setText(mcp_folder)
        o_table = TableHandler(table_ui=self.parent.ui.open_beam_tableWidget)
        o_table.remove_all_rows()
        o_ob_event = ObEventHandler(parent=self.parent)
        o_ob_event.update_list_of_obs()

        if self.parent.session_dict.get(SessionKeys.all_tabs_visible, False):
            self.parent.session_dict[SessionKeys.all_tabs_visible] = False
            self.parent.tab2 = self.parent.ui.tabWidget.widget(2)
            self.parent.tab3 = self.parent.ui.tabWidget.widget(3)
            self.parent.tab4 = self.parent.ui.tabWidget.widget(4)
            for _ in np.arange(3):
                self.parent.ui.tabWidget.removeTab(2)

        # bring back to life the move_obs_to_folder widgets
        self.parent.session_dict[SessionKeys.obs_have_been_moved_already] = False

        self.parent.check_state_of_steps_menu_button()

        self.close()
