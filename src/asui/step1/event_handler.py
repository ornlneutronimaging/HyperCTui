from pathlib import Path
import logging
import glob
import os

from ..parent import Parent
from .get import Get
from ..utilities.table import TableHandler


class EventHandler(Parent):

    def instrument_changed(self):
        instrument = self.parent.ui.step1_instrument_comboBox.currentText()
        o_get = Get(parent=self.parent)
        list_ipts = o_get.list_of_ipts(instrument=instrument)
        self.parent.ui.step1_ipts_comboBox.clear()
        self.parent.ui.step1_ipts_comboBox.addItems(list_ipts)
        self.parent.session_dict['instrument'] = instrument
        self.reset_ob_search_path()

    def run_title_changed(self, run_title=None):
        run_title_listed = run_title.split(" ")
        formatted_run_title = "_".join(run_title_listed)
        self.parent.ui.run_title_formatted_label.setText(formatted_run_title)

    def check_status_of_start_acquisition_button(self):
        pass

    def start_acquisition(self):
        logging.info(f"Step1: start acquisition button clicked:")

        o_get = Get(parent=self.parent)
        instrument = o_get.instrument()
        ipts = o_get.ipts_selected()

        output_folder = Path(self.parent.homepath) / instrument / f"{ipts}" / f"raw/ob/"
        logging.info(f"-> output_folder: {output_folder}")

        # look at the OBs folder of the IPTS and retrieve list of OBs (we will use this to see if any new
        # ones show up)
        list_folder = glob.glob(f"output_folder/*")
        self.parent.nbr_of_ob_folder_before_staring_acquisition = len(list_folder)

    def step1_ipts_changed(self, ipts=None):
        logging.info(f"New IPTS selected: {ipts}")
        self.reset_ob_search_path()

    def reset_ob_search_path(self):
        logging.info(f"-> clearing the list of OBs table!")
        o_table = TableHandler(table_ui=self.parent.ui.step1_open_beam_tableWidget)
        o_table.remove_all_rows()
        ipts = self.parent.ui.step1_ipts_comboBox.currentText()
        instrument = self.parent.ui.step1_instrument_comboBox.currentText()
        full_list_path_where_to_look_for_obs = ["",
                                                "SNS",
                                                instrument,
                                                ipts,
                                                "shared",
                                                "autoreduce",
                                                "mcp",
                                                ]
        full_path_where_to_look_for_obs = os.sep.join(full_list_path_where_to_look_for_obs)
        self.parent.ui.step1_existing_ob_top_path.setText(full_path_where_to_look_for_obs)

    def check_state_of_ob_measured(self):
        logging.info(f"Checking the state of the OBs measured.")
    # look at the new list of OBs in the folder.
    # if there are as many new ones as the number of OBs requested, we are good to go.

    def browse_obs(self):
        full_path_where_to_look_for_obs = str(self.parent.ui.step1_existing_ob_top_path.text())
        logging.info(f"Looking for OBs folders/files in {full_path_where_to_look_for_obs}")
