import glob
import os
import numpy as np
import logging

from ..utilities.get import Get as MasterGet
from ..utilities.table import TableHandler


class Get(MasterGet):

    def list_of_ipts(self, instrument):
        """
        return the list of IPTS for the specified instrument
        ex: ['IPTS-0001', 'IPTS-0002']
        """
        logging.info(f"list of IPTS:")
        home_folder = self.parent.homepath
        logging.info(f"-> home_folder: {home_folder}")
        full_path_list_ipts = glob.glob(os.path.join(home_folder, instrument + '/IPTS-*'))
        logging.info(f"-> full_path_list_ipts: {full_path_list_ipts}")
        list_ipts = [os.path.basename(_folder) for _folder in full_path_list_ipts]
        list_ipts.sort()
        return list_ipts

    def number_of_obs(self):
        return self.parent.ui.number_of_ob_spinBox.value()

    def proton_charge(self):
        if self.ob_tab_selected() == 0:
            return self.parent.ui.open_beam_proton_charge_doubleSpinBox.value()

        else:
            o_table = TableHandler(table_ui=self.parent.ui.open_beam_tableWidget)
            nbr_row = o_table.row_count()
            if nbr_row == 0:

                logging.info(f"Unable to retrieve OB proton charge from empty table "
                             f"(1- Setup the open beams / Select OBs)")
                return "N/A"

            list_proton_charge = []
            for _row in np.arange(nbr_row):
                _pc = o_table.get_item_str_from_cell(row=_row, column=1)
                list_proton_charge.append(_pc)

            set_proton_charge = set(list_proton_charge)
            if len(set_proton_charge) > 1:

                logging.info(f"The OBs selected don't have the same proton charge!")
                return "N/A"

            return list_proton_charge[0]

    def top_ob_folder(self):
        return str(self.parent.ui.existing_ob_top_path.text())

    def list_folders_in_output_directory(self, output_folder=None):
        list_raw = glob.glob(output_folder + os.sep + "*")
        list_folders = []
        for _entry in list_raw:
            if os.path.isdir(_entry):
                list_folders.append(_entry)
        return list_folders

    def list_ob_folders_in_output_directory(self, output_folder=None):
        list_folders = self.list_folders_in_output_directory(output_folder=output_folder)
        list_ob_folders = []
        for _folder in list_folders:
            if os.path.basename(_folder).startswith("ob_"):
                list_ob_folders.append(_folder)
        return list_ob_folders

    def list_sample_folders_in_output_directory(self, output_folder=None):
        list_folders = self.list_folders_in_output_directory(output_folder=output_folder)
        list_sample_folders = []
        for _folder in list_folders:
            if not (os.path.basename(_folder).startswith("ob_")):
                list_sample_folders.append(_folder)
        return list_sample_folders

    def list_ob_folders_selected(self, output_folder=None):
        o_table = TableHandler(table_ui=self.parent.ui.open_beam_tableWidget)
        list_row_selected = o_table.get_rows_of_table_selected()
        if not list_row_selected:
            return []

        list_folders = []
        for _row in list_row_selected:
            _folder = o_table.get_item_str_from_cell(row=_row,
                                                     column=0)
            list_folders.append(_folder)
        return list_folders

    def ob_tab_selected(self):
        return self.parent.ui.ob_tabWidget.currentIndex()

    def ob_will_be_moved_to(self):
        return str(self.parent.ui.final_location_of_ob_created.text())

    def ob_will_be_saved_as(self):
        return str(self.parent.ui.location_of_ob_created.text())

    def projection_folder(self):
        """return the location where the projections will be saved"""
        folder = str(self.parent.ui.projections_output_location_label.text())
        return os.path.dirname(folder)

    def ob_folder(self):
        return str(self.parent.ui.location_of_ob_created.text())
    