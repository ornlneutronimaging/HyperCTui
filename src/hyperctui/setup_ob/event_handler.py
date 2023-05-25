from pathlib import Path
import logging
import glob
import os
import json
from qtpy.QtWidgets import QFileDialog

from ..parent import Parent
from .get import Get
from ..utilities.table import TableHandler
from ..utilities.file_utilities import list_ob_dirs
from ..utilities.check import is_float, are_equal
from ..session import SessionKeys


class EventHandler(Parent):

    # def run_title_changed(self, run_title=None):
    #     run_title_listed = run_title.split(" ")
    #     formatted_run_title = "_".join(run_title_listed)
    #     print(f"formatted run title: {formatted_run_title}")
    #     unused_formatted_run_title = self.produce_unused_formatted_run_title(formatted_run_title)
    #     print(f"unused formatted run title: {unused_formatted_run_title}")
    #     self.parent.ui.run_title_formatted_label.setText(unused_formatted_run_title)

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
        self.update_list_of_obs()

    def reset_ob_search_path(self):
        logging.info(f"-> clearing the list of OBs table!")
        o_table = TableHandler(table_ui=self.parent.ui.step1_open_beam_tableWidget)
        o_table.remove_all_rows()
        ipts = self.parent.session_dict[SessionKeys.ipts_selected]
        instrument = self.parent.session_dict[SessionKeys.instrument]
        full_list_path_where_to_look_for_obs = [self.parent.homepath,
                                                instrument,
                                                ipts,
                                                "shared",
                                                "autoreduce",
                                                "mcp",
                                                ]
        full_path_where_to_look_for_obs = os.sep.join(full_list_path_where_to_look_for_obs)
        self.parent.ui.existing_ob_top_path.setText(full_path_where_to_look_for_obs)
        self.parent.ui.location_of_ob_created.setText(full_path_where_to_look_for_obs)

    def check_state_of_ob_measured(self):
        logging.info(f"Checking the state of the OBs measured.")

    def browse_obs(self):
        full_path_where_to_look_for_obs = str(self.parent.ui.existing_ob_top_path.text())
        logging.info(f"Looking for OBs folders/files in {full_path_where_to_look_for_obs}")

        top_folder = str(QFileDialog.getExistingDirectory(self.parent,
                                                          "Select OB folder",
                                                          full_path_where_to_look_for_obs))

        if not top_folder:
            return

        if not os.path.exists(top_folder):
            logging.info(f"-> folder does not exists!")
            top_folder = os.sep.join([self.parent.homepath,
                                      self.parent.session_dict[SessionKeys.instrument]])
            logging.info(f"-> using {top_folder} instead!")

        if top_folder:
            logging.info(f"User changed top OB folder in step 1: {top_folder}")
            self.parent.ui.existing_ob_top_path.setText(top_folder)
            self.update_list_of_obs()

    def update_list_of_obs(self):
        self.clear_ob_table()
        top_folder = self.parent.ui.existing_ob_top_path.text()
        list_folders = list_ob_dirs(top_folder)
        self.load_list_of_folders(list_folders=list_folders)

    def clear_ob_table(self):
        o_table = TableHandler(table_ui=self.parent.ui.open_beam_tableWidget)
        o_table.remove_all_rows()

    def load_list_of_folders(self, list_folders):
        if list_folders is None:
            return

        proton_charge_requested_for_projections = self.parent.ui.open_beam_proton_charge_doubleSpinBox.value()

        list_proton_charge = []
        for _folder in list_folders:
            _proton_charge = EventHandler.retrieve_proton_charge_for_that_folder(_folder)
            list_proton_charge.append(_proton_charge)

        o_table = TableHandler(table_ui=self.parent.ui.open_beam_tableWidget)
        for _offset_row, _folder in enumerate(list_folders):
            o_table.insert_empty_row(row=_offset_row)
            o_table.insert_item(row=_offset_row,
                                column=0,
                                value=_folder)

            if is_float(list_proton_charge[_offset_row]):

                enabled = are_equal(proton_charge_requested_for_projections, list_proton_charge[_offset_row])

                o_table.insert_item(row=_offset_row,
                                    column=1,
                                    value=f"{list_proton_charge[_offset_row]:.2f}")

                o_table.set_item_enabled(row=_offset_row,
                                         column=1,
                                         enabled=enabled)
                o_table.set_item_enabled(row=_offset_row,
                                         column=0,
                                         enabled=enabled)

            else:
                o_table.insert_item(row=_offset_row,
                                    column=1,
                                    value=f"N/A")

                o_table.set_item_enabled(row=_offset_row,
                                         column=1,
                                         enabled=False)
                o_table.set_item_enabled(row=_offset_row,
                                         column=0,
                                         enabled=False)


    @staticmethod
    def retrieve_proton_charge_for_that_folder(folder):
        """look for the json file called summary.json
            if not there return "N/A"
            if found, look for tag proton_charge
                if found, return the value * 1e-9 (to go to C)
                if not found, return "N/A"
        """
        json_file = glob.glob(folder + os.sep + "summary.json")
        if len(json_file) == 0:
            return "N/A"

        json_file = json_file[0]
        if not os.path.exists(json_file):
            return "N/A"

        with open(json_file, 'r') as f:
            data = json.load(f)

        proton_charge = data.get('proton_charge', 'N/A')
        if proton_charge == "N/A":
            return proton_charge

        proton_charge_value = proton_charge["value"]
        proton_charge_units = proton_charge["units"]
        if proton_charge_units.lower() == "pc":
            coeff = 1e-12
        elif proton_charge_units == "nc":
            coeff = 1e-9
        else:
            raise NotImplemented("Unit of proton charge not supported yet!")

        proton_charge = float(proton_charge_value) * coeff
        return proton_charge
