import numpy as np
from qtpy.QtGui import QIcon

from .. import TabNames, tab2_icon, tab3_icon, tab4_icon
from ..parent import Parent


class Widgets(Parent):

    def make_tabs_visible(self, is_visible=True):

        if not is_visible:
            for _ in np.arange(3):
                self.parent.ui.tabWidget.removeTab(2)
        else:
            self.parent.ui.tabWidget.insertTab(2, self.parent.tab2, QIcon(tab2_icon), TabNames.tab2)
            self.parent.ui.tabWidget.insertTab(3, self.parent.tab3, QIcon(tab3_icon), TabNames.tab3)
            self.parent.ui.tabWidget.insertTab(4, self.parent.tab4, QIcon(tab4_icon), TabNames.tab4)

        self.parent.all_tabs_visible = is_visible


def set_geometry(ui=None, width=100, height=100):
    pass
