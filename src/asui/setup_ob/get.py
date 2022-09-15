import glob
import os
import numpy as np

from ..utilities.get import Get as MasterGet
from ..utilities.table import TableHandler


class Get(MasterGet):

    def list_of_ipts(self, instrument):
        """
		    return the list of IPTS for the specified instrument
		    ex: ['IPTS-0001', 'IPTS-0002']
		"""
        home_folder = self.parent.homepath
        full_path_list_ipts = glob.glob(os.path.join(home_folder, instrument + '/IPTS-*'))
        list_ipts = [os.path.basename(_folder) for _folder in full_path_list_ipts]
        return list_ipts

    def number_of_obs(self):
        return self.parent.ui.number_of_ob_spinBox.value()

    def proton_charge(self):
        return self.parent.ui.open_beam_proton_charge_doubleSpinBox.value()

    def top_ob_folder(self):
        return str(self.parent.ui.existing_ob_top_path.text())

    def list_ob_folders_selected(self):
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
