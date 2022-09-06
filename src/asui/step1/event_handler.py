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
		formated_run_title = "_".join(run_title_listed)
		self.parent.ui.run_title_formated_label.setText(formated_run_title)

	def check_status_of_start_acquisition_button(self):
		formated_run_title = self.parent.ui.run_title_formated_label.text()
		if formated_run_title == "":
			status = False
		else:
			status = True

		self.parent.ui.run_title_missing_label.setVisible(not status)
		self.parent.ui.step1_start_acquisition_pushButton.setEnabled(status)
		