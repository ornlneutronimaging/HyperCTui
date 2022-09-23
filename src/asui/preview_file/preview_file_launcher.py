from qtpy.QtWidgets import QDialog
import os

from .. import load_ui
from ..utilities.file_utilities import read_ascii


class PreviewFileLauncher(QDialog):

	def __init__(self, parent=None, file_name=None):
		self.parent = parent
		self.file_name = file_name

		QDialog.__init__(self, parent=parent)
		ui_full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
									os.path.join('ui',
												 'preview_file.ui'))

		self.ui = load_ui(ui_full_path, baseinstance=self)
		self.setWindowTitle("Preview")

		self.ui.file_name_label.setText(file_name)
		self.display_file()

	def display_file(self):
		if self.file_name is None:
			file_content = "File empty!"
		else:
			file_content = read_ascii(self.file_name)
		self.ui.file_textEdit.setText(file_content)
