class Get:

	full_ob_folder_name = None

	def __init__(self, parent=None, grand_parent=None):
		self.parent = parent
		self.grand_parent = grand_parent

	def set_ob_folder_name(self, full_ob_folder_name=None):
		self.full_ob_folder_name = full_ob_folder_name

	def log_file(self):
		print(f"log file for {self.full_ob_folder_name}")
		return ""

	def err_file(self):
		return ""

	def metadata_file(self):
		return ""
