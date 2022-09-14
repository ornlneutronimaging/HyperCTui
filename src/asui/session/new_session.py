from qtpy.QtWidgets import QDialog
import os

from .. import load_ui


class NewSession(QDialog):

	def __init__(self, parent=None, config=None):
		self.parent = parent
		QDialog.__init__(self, parent=parent)
		ui_full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
									os.path.join('ui',
												 'new_session.ui'))
		self.ui = load_ui(ui_full_path, baseinstance=self)
		self.setWindowTitle("New session")

	def accept(self):
		print("accepted")
		self.close()
