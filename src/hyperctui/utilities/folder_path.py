import os

from hyperctui.parent import Parent
from hyperctui.session import SessionKeys


class FolderPath(Parent):
    """
    This class will retrieve the path to the various folders of the
    project
    """
    ipts_full_path = None

    root = None
    shared = None
    autoreduce = None
    mcp = None
    reduction_log = None
    nexus = None
    mcp_raw = None
    recon = None

    def update(self):

        homepath = self.parent.homepath
        self.root = homepath
        ipts = self.parent.session_dict[SessionKeys.ipts_selected]
        instrument = self.parent.session_dict[SessionKeys.instrument]
        title = self.parent.ui.run_title_formatted_label.text()

        if (instrument is None) | (ipts is None):
            return

        self.ipts_full_path = os.path.abspath(os.sep.join([homepath,
                                              instrument,
                                              ipts]))

        self.shared()
        self.autoreduce()
        self.reduction_log()
        self.nexus()
        self.mcp()
        self.recon(title=title)
        self.create_mcp_raw()

    def __repr__(self):
        return f"folder_path:\n" + \
            f"- shared: \t\t{self.shared}\n-autoreduce: \t\t{self.autoreduce}" + \
            f"\n-mcp: \t\t\t{self.mcp}\n-reduction_log: \t{self.reduction_log}\n-nexus: \t\t{self.nexus}" + \
            f"\n-mcp_raw: \t\t{self.mcp_raw}"

    def shared(self):
        self.shared = os.sep.join([self.ipts_full_path, "shared"])

    def autoreduce(self):
        self.autoreduce = os.sep.join([self.shared,
                                       "autoreduce"])

    def reduction_log(self):
        self.reduction_log = os.sep.join([self.autoreduce,
                                          "reduction_log"])

    def nexus(self):
        self.nexus = os.sep.join([self.ipts_full_path,
                                  "nexus"])

    def mcp(self):
        self.mcp = os.sep.join([self.autoreduce, "mcp"])

    def recon(self, title=None):
        self.recon = os.sep.join([self.shared], "insitu_recon", "recon", title)

    def create_mcp_raw(self):
        self.mcp_raw = os.sep.join([self.ipts_full_path,
                                    'images',
                                    'mcp'])
