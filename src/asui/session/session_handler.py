from qtpy.QtWidgets import QFileDialog, QApplication
import json
import logging
import os
import numpy as np
from qtpy.QtGui import QIcon

from . import SessionKeys, DefaultValues
from ..utilities.status_message_config import StatusMessageStatus, show_status_message
from ..utilities.get import Get
from ..utilities.table import TableHandler
from ..utilities.folder_path import FolderPath
from ..setup_ob.get import Get as Step1Get
from ..setup_ob.event_handler import EventHandler as Step1EventHandler
from ..setup_projections.event_handler import EventHandler as Step2EventHandler
from ..setup_projections.get import Get as Step2Get
from .. import TabNames, tab2_icon, tab3_icon, tab4_icon


class SessionHandler:
    config_file_name = ""
    load_successful = True

    def __init__(self, parent=None):
        self.parent = parent

    def save_from_ui(self):
        session_dict = self.parent.session_dict
        session_dict[SessionKeys.config_version] = self.parent.config[SessionKeys.config_version]

        instrument = session_dict[SessionKeys.instrument]
        ipts_selected = session_dict[SessionKeys.ipts_selected]
        ipts_index_selected = session_dict[SessionKeys.ipts_index_selected]

        # step obs
        o_get_step1 = Step1Get(parent=self.parent)
        number_of_obs = o_get_step1.number_of_obs()
        proton_charge = o_get_step1.proton_charge()
        top_obs_folder = o_get_step1.top_ob_folder()
        list_ob_folders_selected = o_get_step1.list_ob_folders_selected()
        ob_tab_selected = o_get_step1.ob_tab_selected()

        session_dict[SessionKeys.instrument] = instrument
        session_dict[SessionKeys.ipts_selected] = ipts_selected
        session_dict[SessionKeys.ipts_index_selected] = ipts_index_selected
        session_dict[SessionKeys.number_of_obs] = number_of_obs
        session_dict[SessionKeys.proton_charge] = proton_charge
        session_dict[SessionKeys.top_obs_folder] = top_obs_folder
        session_dict[SessionKeys.list_ob_folders_selected] = list_ob_folders_selected
        session_dict[SessionKeys.ob_tab_selected] = ob_tab_selected

        # step projections
        o_get_step2 = Step2Get(parent=self.parent)
        session_dict[SessionKeys.run_title] = self.parent.ui.run_title_formatted_label.text()

        # monitor
        # need to save the list of folders in output directory
        # name of each row in ob table
        # name of each row in projections table

        # all tabs
        all_tabs_visible = self.parent.all_tabs_visible
        session_dict[SessionKeys.all_tabs_visible] = all_tabs_visible

        self.parent.session_dict = session_dict

    def load_to_ui(self):

        if not self.load_successful:
            return

        session_dict = self.parent.session_dict
        self.parent.blockSignals(True)

        # setup ob
        ipts = session_dict[SessionKeys.ipts_selected]
        instrument = session_dict[SessionKeys.instrument]

        self.parent.folder_path = FolderPath(parent=self.parent)
        self.parent.folder_path.update()

        number_of_obs = session_dict.get(SessionKeys.number_of_obs, DefaultValues.number_of_obs)
        self.parent.ui.number_of_ob_spinBox.setValue(number_of_obs)

        proton_charge = session_dict.get(SessionKeys.proton_charge, DefaultValues.proton_charge)
        self.parent.ui.open_beam_proton_charge_doubleSpinBox.setValue(proton_charge)

        top_obs_folder = session_dict.get(SessionKeys.top_obs_folder, None)
        if top_obs_folder is None:
            list_top_obs_folder = ["",
                                   "SNS",
                                   instrument,
                                   ipts,
                                   "shared",
                                   "autoreduce"]
            top_obs_folder = os.sep.join(list_top_obs_folder)
        self.parent.ui.existing_ob_top_path.setText(top_obs_folder)
        o_event = Step1EventHandler(parent=self.parent)
        o_event.update_list_of_obs()

        list_ob_folders_selected = session_dict.get(SessionKeys.list_ob_folders_selected, None)
        o_table = TableHandler(table_ui=self.parent.ui.open_beam_tableWidget)
        nbr_row = o_table.row_count()
        for _row in np.arange(nbr_row):
            _folder = o_table.get_item_str_from_cell(row=_row,
                                                     column=0)
            if _folder in list_ob_folders_selected:
                o_table.select_row(row=_row)

        ob_tab_selected = session_dict.get(SessionKeys.ob_tab_selected, DefaultValues.ob_tab_selected)
        self.parent.ui.ob_tabWidget.setCurrentIndex(ob_tab_selected)

        # step projections
        run_title = session_dict.get(SessionKeys.run_title, DefaultValues.run_title)
        self.parent.ui.run_title_lineEdit.blockSignals(True)
        self.parent.ui.run_title_lineEdit.setText(run_title)
        self.parent.ui.run_title_lineEdit.blockSignals(False)
        o_projections_event = Step2EventHandler(parent=self.parent)
        o_projections_event.run_title_changed(run_title=run_title,
                                              checking_if_file_exists=False)
        self.parent.ui.projections_p_charge_label.setText(str(proton_charge))

        show_status_message(parent=self.parent,
                            message=f"Loaded {self.config_file_name}",
                            status=StatusMessageStatus.ready,
                            duration_s=10)

        all_tabs_visible = session_dict.get(SessionKeys.all_tabs_visible, False)
        if not (self.parent.all_tabs_visible == all_tabs_visible):
            if not all_tabs_visible:
                for _ in np.arange(3):
                    self.parent.ui.tabWidget.removeTab(2)
            else:
                self.parent.ui.tabWidget.insertTab(2, self.parent.tab2, QIcon(tab2_icon), TabNames.tab2)
                self.parent.ui.tabWidget.insertTab(3, self.parent.tab3, QIcon(tab3_icon), TabNames.tab3)
                self.parent.ui.tabWidget.insertTab(4, self.parent.tab4, QIcon(tab4_icon), TabNames.tab4)

            self.parent.all_tabs_visible = all_tabs_visible

        self.parent.blockSignals(False)
        self.parent.set_window_title()

    def _retrieve_general_settings(self):
        number_of_scanned_periods = self.parent.ui.number_of_scanned_periods_spinBox.value()
        full_period_true = self.parent.ui.full_period_true_radioButton.isChecked()
        rotation_of_g0rz = self.parent.ui.rotation_of_g0rz_doubleSpinBox.value()
        images_per_step = self.parent.ui.images_per_step_spinBox.value()
        general_settings = {'number of scanned periods': number_of_scanned_periods,
                            'full period'              : full_period_true,
                            'rotation of g0rz'         : rotation_of_g0rz,
                            'number of images per step': images_per_step}
        return general_settings

    def automatic_save(self):
        o_get = Get(parent=self.parent)
        full_config_file_name = o_get.get_automatic_config_file_name()
        self.save_to_file(config_file_name=full_config_file_name)

    def save_to_file(self, config_file_name=None):
        if config_file_name is None:
            config_file_name = QFileDialog.getSaveFileName(self.parent,
                                                           caption="Select session file name ...",
                                                           directory=self.parent.homepath,
                                                           filter="session (*.json)",
                                                           initialFilter="session")

            QApplication.processEvents()
            config_file_name = config_file_name[0]

        if config_file_name:
            output_file_name = config_file_name
            session_dict = self.parent.session_dict
            with open(output_file_name, 'w') as json_file:
                json.dump(session_dict, json_file)

            show_status_message(parent=self.parent,
                                message=f"Session saved in {config_file_name}",
                                status=StatusMessageStatus.ready,
                                duration_s=10)
            logging.info(f"Saving configuration into {config_file_name}")

    def load_from_file(self, config_file_name=None):
        self.parent.loading_from_config = True

        if config_file_name is None:
            config_file_name = QFileDialog.getOpenFileName(self.parent,
                                                           directory=self.parent.homepath,
                                                           caption="Select session file ...",
                                                           filter="session (*.json)",
                                                           initialFilter="session")
            QApplication.processEvents()
            config_file_name = config_file_name[0]

        if config_file_name:
            config_file_name = config_file_name
            self.config_file_name = config_file_name
            show_status_message(parent=self.parent,
                                message=f"Loading {config_file_name} ...",
                                status=StatusMessageStatus.ready)

            with open(config_file_name, "r") as read_file:
                session_to_save = json.load(read_file)
                if session_to_save.get("config version", None) is None:
                    logging.info(f"Session file is out of date!")
                    logging.info(f"-> expected version: {self.parent.config['config version']}")
                    logging.info(f"-> session version: Unknown!")
                    self.load_successful = False
                elif session_to_save["config version"] == self.parent.config["config version"]:
                    self.parent.session_dict = session_to_save
                    logging.info(f"Loaded from {config_file_name}")
                else:
                    logging.info(f"Session file is out of date!")
                    logging.info(f"-> expected version: {self.parent.config['config version']}")
                    logging.info(f"-> session version: {session_to_save['config version']}")
                    self.load_successful = False

                if self.load_successful == False:
                    show_status_message(parent=self.parent,
                                        message=f"{config_file_name} not loaded! (check log for more information)",
                                        status=StatusMessageStatus.ready,
                                        duration_s=10)

        else:
            self.load_successful = False
            show_status_message(parent=self.parent,
                                message=f"{config_file_name} not loaded! (check log for more information)",
                                status=StatusMessageStatus.ready,
                                duration_s=10)
