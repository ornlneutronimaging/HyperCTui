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

