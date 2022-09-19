import logging
from qtpy.QtCore import QRect

from .parent import Parent
from .initialization.gui_initialization import GuiInitialization
from .setup_ob.get import Get as Step1Get
from .session.new_session import NewSession
from . import UiSizeLarge, UiSizeSmall


class EventHandler(Parent):

	def new_session(self):
		o_new = NewSession(parent=self.parent)
		o_new.show()

	def full_reset_clicked(self):
		o_init = GuiInitialization(parent=self.parent)
		o_init.full_reset()
		logging.info("Full reset of application!")

	def check_start_acquisition_button(self):
		button_ready_to_be_used = self._is_start_acquisition_ready_to_be_used()
		self.parent.ui.start_acquisition_pushButton.setEnabled(button_ready_to_be_used)
		self.parent.ui.help_pushButton.setVisible(not button_ready_to_be_used)
		self.set_start_acquisition_text()

	def _is_start_acquisition_ready_to_be_used(self):

		# if selected OB tab and no OB selected -> return False
		if self.parent.ui.ob_tabWidget.currentIndex() == 1:
			o_get = Step1Get(parent=self.parent)
			list_of_selected = o_get.list_ob_folders_selected()
			if len(list_of_selected) == 0:
				logging.info(f"User selected `select obs` tab but no OBs have been selected!")
				logging.info(f"-> Possible correction: ")
				logging.info(f"     * select at least 1 OB folder")
				logging.info(f"     * select `Acquire new OBs` tab")
				return False

		if self.parent.ui.projections_output_location_label.text() == "N/A":
			logging.info(f"Please provide a title to be able to start the acquisition!")
			return False

		return True

	def set_start_acquisition_text(self):
		button_text = "Start acquisition of "
		if self.parent.ui.ob_tabWidget.currentIndex() == 0:
			number_of_obs = self.parent.ui.number_of_ob_spinBox.value()
			button_text += f"{number_of_obs} OBs and "
		number_of_projections = self.parent.ui.number_of_projections_spinBox.value()
		button_text += f"{number_of_projections} projections"
		self.parent.ui.start_acquisition_pushButton.setText(button_text)

	def main_tab_changed(self, new_tab_index=0):
		"""
		resize the main ui according to the tab selected
		small version for the first 2 main tabs
		large version for the next 3 tabs
		"""
		small_tab_index = [0, 1]

		if new_tab_index in small_tab_index:
			if self.parent.current_tab_index in small_tab_index:
				self.parent.current_tab_index = new_tab_index
				return
			else:
				move_to_large_ui = False

		else:
			if not (self.parent.current_tab_index in small_tab_index):
				self.parent.current_tab_index = new_tab_index
				return
			else:
				move_to_large_ui = True

		current_geometry = self.parent.ui.geometry()
		left = current_geometry.left()
		top = current_geometry.top()
		width = current_geometry.width()
		height = current_geometry.height()
		if not move_to_large_ui:
			width = UiSizeSmall.width
			height = UiSizeSmall.height
		else:
			width = UiSizeLarge.width if width < UiSizeLarge.width else width
			height = UiSizeLarge.height if height < UiSizeLarge.height else height

		rect = QRect(left, top, width, height)
		self.parent.ui.setGeometry(rect)
		self.parent.current_tab_index = new_tab_index
