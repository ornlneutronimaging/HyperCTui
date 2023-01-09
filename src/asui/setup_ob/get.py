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
        return self.parent.ui.open_beam_proton_charge_doubleSpinBox.value()

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
