from qtpy.QtWidgets import QDialog
import os

from .. import load_ui
from ..setup_ob.get import Get
from . import SessionKeys


class NewSession(QDialog):

	def __init__(self, parent=None):
		session_dict = parent.session_dict
		self.parent = parent
		QDialog.__init__(self, parent=parent)
		ui_full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
									os.path.join('ui',
												 'new_session.ui'))
		self.ui = load_ui(ui_full_path, baseinstance=self)
		self.setWindowTitle("New session")

		instrument = session_dict['instrument']
		index_instrument = self.ui.instrument_comboBox.findText(instrument)
		self.ui.instrument_comboBox.setCurrentIndex(index_instrument)
		self.instrument_changed(instrument)

	def instrument_changed(self, new_instrument):
		o_get = Get(parent=self.parent)
		list_ipts = o_get.list_of_ipts(instrument=new_instrument)
		self.ui.ipts_comboBox.clear()
		self.ui.ipts_comboBox.blockSignals(True)
		self.ui.ipts_comboBox.addItems(list_ipts)

	def accept(self):
		instrument = self.ui.instrument_comboBox.currentText()
		ipts = self.ui.ipts_comboBox.currentText()
		ipts_index = self.ui.ipts_comboBox.selectedIndex()

		self.parent.session_dict[SessionKeys.instrument] = instrument
		self.parent.session_dict[SessionKeys.ipts_selected] = ipts
		self.parent.session_dict[SessionKeys.ipts_index_selected] = ipts_index

		self.close()
