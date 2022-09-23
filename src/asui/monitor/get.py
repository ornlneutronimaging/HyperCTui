import os


class Get:

	# will look like /SNS/VENUS/IPTS-30023/shared/autoreduce/mcp/scan17/Run_57100
	full_ob_folder_name = None

	def __init__(self, parent=None, grand_parent=None):
		self.parent = parent
		self.grand_parent = grand_parent
		self.folder_path = grand_parent.folder_path

	def set_ob_folder_name(self, full_ob_folder_name=None):
		self.full_ob_folder_name = os.path.abspath(full_ob_folder_name)

	def log_file(self):
		"""
		if full_ob_folder_name is
			/SNS/VENUS/IPTS-30023/shared/autoreduce/mcp/scan17/Run_57100
		it needs to return
			/SNS/VENUS/IPTS-30023/shared/autoreduce/reduction_log/VENUS_57100.nxs.h5.log
		"""
		print(f"log file for {self.full_ob_folder_name}")
		print(self.folder_path.reduction_log)
		return ""

	def err_file(self):
		"""
		if full_ob_folder_name is
			/SNS/VENUS/IPTS-30023/shared/autoreduce/mcp/scan17/Run_57100
		it needs to return
			/SNS/VENUS/IPTS-30023/shared/autoreduce/reduction_log/VENUS_57100.nxs.h5.err
		"""
		return ""

	def metadata_file(self):
		"""
		if full_ob_folder_name is
			/SNS/VENUS/IPTS-30023/shared/autoreduce/mcp/scan17/Run_57100
		it needs to return
			/SNS/VENUS/IPTS-30023/shared/autoreduce/mcp/scan17/Run_57100/summary.json
		"""
		return os.path.join(self.full_ob_folder_name, "summary.json")
