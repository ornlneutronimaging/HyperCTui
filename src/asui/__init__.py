from ._version import get_versions
from qtpy.uic import loadUi

__version__ = get_versions()['version']
del get_versions

__all__ = ['load_ui']


def load_ui(ui_filename, baseinstance):
    return loadUi(ui_filename, baseinstance=baseinstance)
