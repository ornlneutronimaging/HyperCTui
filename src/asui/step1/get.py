import glob
import os

from ..utilities.get import Get as MasterGet


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
