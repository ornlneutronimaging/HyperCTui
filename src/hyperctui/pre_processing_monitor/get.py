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

    def set_ob(self, full_ob_folder_name=None):
        self.set_path(full_ob_folder_name=full_ob_folder_name)

    def set_path(self, full_ob_folder_name=None):
        self.set_ob_folder_name(full_ob_folder_name=full_ob_folder_name)
        self.set_run_number()

    def set_run_number(self):
        """
        self.full_ob_folder_name = "/SNS/VENUS/IPTS_0445345/shared/autoreduce/OB_test_10001/run_10001
        => self.run_number = 10001
        """
        list_runs = glob.glob(self.full_ob_folder_name + "/Run_*")
        split_folder_path = list_runs[0].split("/")
        _, run_number = split_folder_path[-1].split("_")
        self.run_number = run_number

    def set_ob_folder_name(self, full_ob_folder_name=None):
        self.full_ob_folder_name = os.path.abspath(full_ob_folder_name)

    def set_run_number_full_path(self):
        full_ob_folder_name = self.full_ob_folder_name
        list_runs = glob.glob(os.path.join(full_ob_folder_name, 'Run*'))
        self.run_number_full_path = list_runs[0]

    # def set_run_number_filename(self):
    #     """
    #     will only keep the string "Run_####"
    #     """
    #     split_names = self.full_ob_folder_name.split("/")
    #     self.run_number_filename = split_names[-1]
    #
    # def get_run_number_filename(self):
    #     return self.run_number_filename

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
        run_number = self.run_number
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
        return os.path.join(self.full_ob_folder_name, "summary.json")
