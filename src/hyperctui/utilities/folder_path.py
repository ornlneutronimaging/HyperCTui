import os

from hyperctui.parent import Parent
from hyperctui.session import SessionKeys
from hyperctui.setup_ob.get import Get


RECONSTRUCTION_CONFIG = "reconstruction_config.json"


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
    reconstruction_config = None  # json file created/updated by Shimin's code

    def update(self):

        homepath = self.parent.homepath
        self.root = homepath
        ipts = self.parent.session_dict[SessionKeys.ipts_selected]
        instrument = self.parent.session_dict[SessionKeys.instrument]

        o_get = Get(parent=self.parent)
        facility = o_get.facility(instrument=instrument)

        title = self.parent.session_dict.get(SessionKeys.run_title, "")

        if (instrument is None) | (ipts is None):
            return

        self.ipts_full_path = os.path.abspath(os.sep.join([homepath,
                                                           facility,
                                                           instrument,
                                                           ipts]))

        self.shared()
        self.autoreduce()
        self.reduction_log()
        self.nexus()
        self.mcp()
        self.recon(title=title)
        self.create_mcp_raw()
        self.svmbir_config(title=title)

    def __repr__(self):
        return f"folder_path:\n" + \
            f"- shared:  \t\t{self.shared}\n" \
            f"- autoreduce:  \t{self.autoreduce}\n" + \
            f"- mcp:  \t\t{self.mcp}\n" \
            f"- reduction_log:{self.reduction_log}\n" \
            f"- nexus:  \t\t{self.nexus}\n" + \
            f"- mcp_raw:  \t{self.mcp_raw}\n" \
            f"- recon:  \t\t{self.recon}\n" \
            f"- reconstruction_config: {self.reconstruction_config}\n"

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
        self.recon = os.sep.join([self.shared, "insitu_recon", title, "recon"])

    def create_mcp_raw(self):
        self.mcp_raw = os.sep.join([self.ipts_full_path,
                                    'images',
                                    'mcp'])

    def svmbir_config(self, title=None):
        self.reconstruction_config = os.sep.join([self.shared, "insitu_recon", title, RECONSTRUCTION_CONFIG])
