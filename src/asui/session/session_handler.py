from qtpy.QtWidgets import QFileDialog, QApplication
import json
import logging
import os

from . import SessionKeys, DefaultValues
from ..utilities.status_message_config import StatusMessageStatus, show_status_message
from ..utilities.get import Get
from ..step1.get import Get as Step1Get
from ..step2.get import Get as Step2Get


class SessionHandler:

    config_file_name = ""
    load_successful = True

    def __init__(self, parent=None):
        self.parent = parent

    def save_from_ui(self):
        session_dict = {SessionKeys.config_version: self.parent.config[SessionKeys.config_version]}

        # step 1
        o_get_step1 = Step1Get(parent=self.parent)
        instrument = o_get_step1.instrument()
        ipts_selected = o_get_step1.ipts_selected()
        ipts_index_selected = o_get_step1.ipts_index_selected()
        number_of_obs = o_get_step1.number_of_obs()
        proton_charge = o_get_step1.proton_charge()
        top_obs_folder = o_get_step1.top_ob_folder()

        session_dict[SessionKeys.instrument] = instrument
        session_dict[SessionKeys.ipts_selected] = ipts_selected
        session_dict[SessionKeys.ipts_index_selected] = ipts_index_selected
        session_dict[SessionKeys.number_of_obs] = number_of_obs
        session_dict[SessionKeys.proton_charge] = proton_charge
        session_dict[SessionKeys.top_obs_folder] = top_obs_folder

        # step 2
        o_get_step2 = Step2Get(parent=self.parent)
        run_title = o_get_step2.run_title()
        session_dict[SessionKeys.run_title] = run_title

        self.parent.session_dict = session_dict

    def load_to_ui(self):

        if not self.load_successful:
            return

        session_dict = self.parent.session_dict

        # step1
        instrument = session_dict.get(SessionKeys.instrument, DefaultValues.instrument)
        self.parent.set_new_instrument(instrument=instrument)
        self.parent.step1_instrument_changed(instrument=instrument)
        ipts_index_selected = session_dict.get(SessionKeys.ipts_index_selected, DefaultValues.ipts_index_selected)
        self.parent.ui.step1_ipts_comboBox.setCurrentIndex(ipts_index_selected)
        ipts = session_dict.get(SessionKeys.ipts_selected)
        number_of_obs = session_dict.get(SessionKeys.number_of_obs, DefaultValues.number_of_obs)
        self.parent.ui.step1_number_of_ob_spinBox.setValue(number_of_obs)
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
        self.parent.ui.step1_existing_ob_top_path.setText(top_obs_folder)

        # step 2
        run_title = session_dict.get(SessionKeys.run_title, DefaultValues.run_title)
        self.parent.ui.step2_run_title_lineEdit.setText(run_title)
        self.parent.step2_run_title_changed(run_title=run_title)

        show_status_message(parent=self.parent,
                            message=f"Loaded {self.config_file_name}",
                            status=StatusMessageStatus.ready,
                            duration_s=10)

    def _retrieve_general_settings(self):
        number_of_scanned_periods = self.parent.ui.number_of_scanned_periods_spinBox.value()
        full_period_true = self.parent.ui.full_period_true_radioButton.isChecked()
        rotation_of_g0rz = self.parent.ui.rotation_of_g0rz_doubleSpinBox.value()
        images_per_step = self.parent.ui.images_per_step_spinBox.value()
        general_settings = {'number of scanned periods': number_of_scanned_periods,
                            'full period': full_period_true,
                            'rotation of g0rz': rotation_of_g0rz,
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
