from pathlib import Path
import logging

from ..parent import Parent
from .get import Get


class EventHandler(Parent):

	def instrument_changed(self):
		instrument = self.parent.ui.step1_instrument_comboBox.currentText()
		o_get = Get(parent=self.parent)
		list_ipts = o_get.list_of_ipts(instrument=instrument)
		self.parent.ui.step1_ipts_comboBox.clear()
		self.parent.ui.step1_ipts_comboBox.addItems(list_ipts)
		self.parent.session_dict['instrument'] = instrument

	def run_title_changed(self, run_title=None):
		run_title_listed = run_title.split(" ")
		formatted_run_title = "_".join(run_title_listed)
		self.parent.ui.run_title_formatted_label.setText(formatted_run_title)

	def check_status_of_start_acquisition_button(self):
		pass
		# formatted_run_title = self.parent.ui.run_title_formatted_label.text()
		# if formatted_run_title == "":
		# 	status = False
		# else:
		# 	status = True
		#
		# self.parent.ui.run_title_missing_label.setVisible(not status)
		# self.parent.ui.step1_start_acquisition_pushButton.setEnabled(status)

	def start_acquisition(self):
		logging.info(f"Step1: start acquisition button clicked:")
		o_get = Get(parent=self.parent)
		instrument = o_get.instrument()
		ipts = o_get.ipts_selected()
		formatted_run_title = o_get.formatted_run_title()

		output_folder = Path(self.parent.homepath) / instrument / f"{ipts}" / f"raw/ob/{formatted_run_title}"
		logging.info(f"-> output_folder: {output_folder}")
