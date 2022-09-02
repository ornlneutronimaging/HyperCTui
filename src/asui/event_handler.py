import logging

from .parent import Parent
from .initialization.gui_initialization import GuiInitialization


class EventHandler(Parent):

	def full_reset_clicked(self):
		o_init = GuiInitialization(parent=self.parent)
		o_init.full_reset()

		logging.info("Full reset of application!")
