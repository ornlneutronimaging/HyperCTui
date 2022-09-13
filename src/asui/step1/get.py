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

    def instrument(self):
        return self.parent.ui.step1_instrument_comboBox.currentText()

    def ipts_selected(self):
        return self.parent.ui.step1_ipts_comboBox.currentText()

    def ipts_index_selected(self):
        return self.parent.ui.step1_ipts_comboBox.currentIndex()

    def number_of_obs(self):
        return self.parent.ui.step1_number_of_ob_spinBox.value()

    def run_title(self):
        return str(self.parent.ui.step1_run_title_lineEdit.text())

    def formatted_run_title(self):
        return str(self.parent.ui.run_title_formatted_label.text())

    def proton_charge(self):
        return self.parent.ui.open_beam_proton_charge_doubleSpinBox.value()

    def top_ob_folder(self):
        return str(self.parent.ui.step1_existing_ob_top_path.text())

    def list_ob_folders(self):
        o_table = TableHandler(table_ui=self.parent.ui.step1_open_beam_tableWidget)
        list_folders = []
        nbr_row = o_table.row_count()
        for _row in np.arange(nbr_row):
            _folder = o_table.get_item_str_from_cell(row=_row,
                                                     column=0)
            list_folders.append(_folder)
        return list_folders
