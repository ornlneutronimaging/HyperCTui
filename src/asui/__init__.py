from ._version import get_versions
from qtpy.uic import loadUi
import os

__version__ = get_versions()['version']
del get_versions

__all__ = ['load_ui']

root = os.path.dirname(os.path.realpath(__file__))
refresh_image = os.path.join(root, "static/refresh.png")
more_infos = os.path.join(root, "static/more_infos.png")
tab0_icon = os.path.join(root, "static/tab0.png")
tab1_icon = os.path.join(root, "static/tab1.png")
tab2_icon = os.path.join(root, "static/tab2.png")
tab3_icon = os.path.join(root, "static/tab3.png")
tab4_icon = os.path.join(root, "static/tab4.png")

UI_TITLE = "Ai Svmbir UI"


# main window dimensions
class UiSizeSmall:
    width = 800
    height = 300


class UiSizeLarge:
    width = 800
    height = 800


class TabNames:
    tab0 = " - Setup the open beams"
    tab1 = " - Setup the first projections"
    tab2 = " - Crop"
    tab3 = " - Rotation center"
    tab4 = " - Settings"


def load_ui(ui_filename, baseinstance):
    return loadUi(ui_filename, baseinstance=baseinstance)
