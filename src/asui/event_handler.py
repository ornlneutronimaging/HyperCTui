import logging

from .parent import Parent
from .initialization.gui_initialization import GuiInitialization
from .utilities.table import TableHandler


class EventHandler(Parent):

	def full_reset_clicked(self):
		o_init = GuiInitialization(parent=self.parent)
		o_init.full_reset()

		logging.info("Full reset of application!")

	def check_state_of_main_tabs(self):
		"""
		if working on step 1:
			validate tab2 if "select ob" tab visible and at least 1 OB selected
			otherwise validate tab2 if "create ob" button has been clicked at least once
		"""
		if self.parent.ui.tabWidget.currentIndex() == 0:  # OB acquisition
			if self.parent.ui.ob_tabWidget.currentIndex() == 1:  # select OBs
				o_table = TableHandler(table_ui=self.parent.ui.step1_open_beam_tableWidget)
				row_selected = o_table.get_rows_of_table_selected()
				if row_selected:
					self.parent.ui.tabWidget.setTabEnabled(1, True)
				else:
					self.parent.ui.tabWidget.setTabEnabled(1, False)
			else:  # create OB
				if self.parent.clicked_create_ob:
					self.parent.ui.tabWidget.setTabEnabled(1, True)
				else:
					self.parent.ui.tabWidget.setTabEnabled(1, False)
