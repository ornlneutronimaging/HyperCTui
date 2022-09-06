import glob
import os

from ..utilities.get import Get as MasterGet


class Get(MasterGet):

	def run_title(self):
		return str(self.parent.ui.step2_run_title_lineEdit.text())

	def formatted_run_title(self):
		return str(self.parent.ui.run_title_formatted_label.text())
