import os
import glob

from hyperctui.session import SessionKeys


class Get:

	# will look like /SNS/VENUS/IPTS-30023/shared/autoreduce/mcp/scan17/Run_57100
	full_ob_folder_name = None
	run_number_full_path = None

	def __init__(self, parent=None, grand_parent=None):
		self.parent = parent
		self.grand_parent = grand_parent
		self.folder_path = grand_parent.folder_path

	def set_path(self, full_ob_folder_name=None):
		self.set_ob_folder_name(full_ob_folder_name=full_ob_folder_name)
		self.set_run_number_full_path()

	def set_ob_folder_name(self, full_ob_folder_name=None):
		self.full_ob_folder_name = os.path.abspath(full_ob_folder_name)

	def set_run_number_full_path(self):
		full_ob_folder_name = self.full_ob_folder_name
		list_runs = glob.glob(os.path.join(full_ob_folder_name, 'Run*'))
		self.run_number_full_path = list_runs[0]

	def log_file(self):
		"""
		if full_ob_folder_name is
			/SNS/VENUS/IPTS-30023/shared/autoreduce/mcp/scan17/Run_57100
		it needs to return
			/SNS/VENUS/IPTS-30023/shared/autoreduce/reduction_log/VENUS_57100.nxs.h5.log
		"""
		prefix = self.log_err_prefix()
		return prefix + ".log"

	def log_err_prefix(self):
		"""
		if full_ob_folder_name is
			/SNS/VENUS/IPTS-30023/shared/autoreduce/mcp/scan17/Run_57100
		it will return
			/SNS/VENUS/IPTS-30023/shared/autoreduce/reduction_log/VENUS_57100.nxs.h5
		"""
		folder = self.folder_path.reduction_log
		base_file_name = os.path.basename(self.run_number_full_path)
		_, run_number = base_file_name.split("_")
		instrument = self.grand_parent.session_dict[SessionKeys.instrument]
		return os.path.join(folder, f"{instrument}_{run_number}.nxs.h5")

	def err_file(self):
		"""
		if full_ob_folder_name is
			/SNS/VENUS/IPTS-30023/shared/autoreduce/mcp/scan17/Run_57100
		it needs to return
			/SNS/VENUS/IPTS-30023/shared/autoreduce/reduction_log/VENUS_57100.nxs.h5.err
		"""
		prefix = self.log_err_prefix()
		return prefix + ".err"

	def metadata_file(self):
		"""
		if full_ob_folder_name is
			/SNS/VENUS/IPTS-30023/shared/autoreduce/mcp/scan17/Run_57100
		it needs to return
			/SNS/VENUS/IPTS-30023/shared/autoreduce/mcp/scan17/Run_57100/summary.json
		"""
		return os.path.join(self.run_number_full_path, "summary.json")
