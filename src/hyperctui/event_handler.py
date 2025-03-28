#!/usr/bin/env python
"""
Event handler module for HyperCTui application.

This module provides event handling for UI interactions, including tab changes,
button clicks, and UI state management for the HyperCTui application.
"""

from loguru import logger
from qtpy.QtCore import QRect

from hyperctui import UiSizeLarge
from hyperctui.autonomous_reconstruction.event_handler import EventHandler as AutoEventHandler
from hyperctui.initialization.gui_initialization import GuiInitialization
from hyperctui.parent import Parent
from hyperctui.rotation_center.event_handler import EventHandler as RotationCenterEventHandler
from hyperctui.session import SessionKeys
from hyperctui.session.new_session import NewSession
from hyperctui.setup_ob.get import Get as ObGet
from hyperctui.setup_ob.get import Get as Step1Get


class EventHandler(Parent):
    """
    Event handler for the main UI components of the HyperCTui application.

    This class manages UI interactions, updates UI state based on application logic,
    and coordinates between different components of the application.
    """

    def new_session(self) -> None:
        """
        Display the new session dialog.

        Creates and shows a new session window to allow users to start a new session.
        """
        o_new = NewSession(parent=self.parent)
        o_new.show()

    def full_reset_clicked(self) -> None:
        """
        Reset the application to its initial state.

        Performs a complete reset of the application, clearing all settings
        and returning to the initial state.
        """
        o_init = GuiInitialization(parent=self.parent)
        o_init.full_reset()
        logger.info("Full reset of application!")

    def ob_tab_changed(self) -> None:
        """
        Handle events when the open beam tab is changed.

        Currently not implemented, will handle updates when tabs change
        in the open beam section.
        """
        pass
        # current_tab = self.parent.ui.ob_tabWidget.currentIndex()
        # if current_tab == ObTabNames.selected_obs:
        #     o_event = ObEventHandler(parent=self.parent)
        #     o_event.update_list_of_obs()

    def check_state_of_steps_menu_button(self) -> None:
        """
        Update the enabled state of step menu actions based on current UI state.

        Enables or disables menu items based on whether all tabs are visible.
        """
        if self.parent.all_tabs_visible:
            all_enable = True
        else:
            all_enable = False
        list_ui = [
            self.parent.ui.action3_Crop,
            self.parent.ui.action4_Rotation_center,
            self.parent.ui.action5_autonomous_reconstruction,
        ]
        for _ui in list_ui:
            _ui.setEnabled(all_enable)

    def check_start_acquisition_button(self) -> None:
        """
        Check if the acquisition button should be enabled based on UI state.

        Evaluates current conditions and determines if the start acquisition button
        should be enabled or disabled. Also updates the visibility of error messages.
        """
        if not self.parent.ui.run_title_groupBox.isEnabled():
            button_ready_to_be_used = False
        else:
            button_ready_to_be_used = self._is_start_acquisition_ready_to_be_used()

        if self.parent.ui.ob_tabWidget.currentIndex() == 1:
            o_get = Step1Get(parent=self.parent)
            list_of_selected = o_get.list_ob_folders_selected()
            if len(list_of_selected) == 0:
                self.parent.ui.ob_pcharge_error_label.setVisible(True)
            else:
                self.parent.ui.ob_pcharge_error_label.setVisible(False)
        else:
            self.parent.ui.ob_pcharge_error_label.setVisible(False)

        self.parent.ui.start_acquisition_pushButton.setEnabled(button_ready_to_be_used)
        self.parent.ui.help_pushButton.setVisible(not button_ready_to_be_used)
        self.set_start_acquisition_text()

    def _is_start_acquisition_ready_to_be_used(self) -> bool:
        """
        Check if all conditions are met to start acquisition.

        Returns
        -------
        bool
            True if all required conditions are met to enable the start
            acquisition button, False otherwise.
        """
        # if selected OB tab and no OB selected -> return False
        if self.parent.ui.ob_tabWidget.currentIndex() == 1:
            o_get = Step1Get(parent=self.parent)
            list_of_selected = o_get.list_ob_folders_selected()
            if len(list_of_selected) == 0:
                logger.info("User selected `select obs` tab but no OBs have been selected!")
                logger.info("-> Possible correction: ")
                logger.info("     * select at least 1 OB folder")
                logger.info("     * select `Acquire new OBs` tab")
                return False

        if self.parent.ui.run_title_formatted_label.text() == "N/A":
            logger.info("Please provide a title to be able to start the acquisition!")
            return False

        if self.parent.ui.projections_output_location_label.text() == "N/A":
            logger.info("Make sure the output folder exists (check instrument and IPTS)!")
            return False

        if str(self.parent.ui.projections_p_charge_label.text()) == "N/A":
            logger.info("ASUI is unable to determine the proton charge you want to use!")
            logger.info("-> Possible correction: ")
            logger.info(
                "     * you want to use previously measured OBs and they don't seem to have the same proton charge"
            )
            return False

        return True

    def set_start_acquisition_text(self) -> None:
        """
        Update the text displayed on the start acquisition button.

        Sets the appropriate text for the start acquisition button based on
        the current tab and acquisition settings.
        """
        button_text = "Start acquisition of "
        if self.parent.ui.ob_tabWidget.currentIndex() == 0:
            number_of_obs = self.parent.ui.number_of_ob_spinBox.value()
            button_text += f"{number_of_obs} OBs then "
        button_text += "0\u00b0 and 180\u00b0 projections"
        self.parent.ui.start_acquisition_pushButton.setText(button_text)

    def main_tab_changed(self, new_tab_index: int = 0) -> None:
        """
        Handle main tab changes and resize the UI accordingly.

        Resizes the main UI based on the selected tab. Small version for the first
        2 main tabs, large version for the next 3 tabs. Also triggers specific
        actions based on the tab selected.

        Parameters
        ----------
        new_tab_index : int, optional
            Index of the newly selected tab, by default 0
        """
        if new_tab_index == 1:  # initialize first projections 0 and 180 degrees
            self.parent.run_title_changed(self.parent.ui.run_title_lineEdit.text())
            # update p charge
            o_get = ObGet(parent=self.parent)
            proton_charge = o_get.proton_charge()
            self.parent.ui.projections_p_charge_label.setText(str(proton_charge))
            self.check_start_acquisition_button()

        elif new_tab_index == 3:  # center of rotation
            o_center_event = RotationCenterEventHandler(parent=self.parent)
            o_center_event.update_widgets()
            o_center_event.calculate_using_tomopy()

        elif new_tab_index == 4:  # autonomous reconstruction
            o_auto_event = AutoEventHandler(parent=self.parent)
            o_auto_event.update_widgets()

        small_tab_index = [0, 1]

        if new_tab_index in small_tab_index:
            if self.parent.current_tab_index in small_tab_index:
                self.parent.current_tab_index = new_tab_index
                return
            else:
                move_to_large_ui = False

        else:
            if self.parent.current_tab_index not in small_tab_index:
                self.parent.current_tab_index = new_tab_index
                return
            else:
                move_to_large_ui = True

        current_geometry = self.parent.ui.geometry()
        left = current_geometry.left()
        top = current_geometry.top()
        width = current_geometry.width()
        height = current_geometry.height()
        # if not move_to_large_ui:
        #     width = UiSizeSmall.width
        #     height = UiSizeSmall.height
        if move_to_large_ui:
            width = UiSizeLarge.width if width < UiSizeLarge.width else width
            height = UiSizeLarge.height if height < UiSizeLarge.height else height

        rect = QRect(left, top, width, height)
        self.parent.ui.setGeometry(rect)
        self.parent.current_tab_index = new_tab_index

    def freeze_number_ob_sample_requested(self) -> None:
        """
        Freeze the number of OB and sample measurements.

        Records the initial list of OBs and sample folders and stores
        the number of files requested in the session dictionary.
        """
        if self.parent.ui.ob_tabWidget.currentIndex() == 0:
            number_of_obs = self.parent.ui.number_of_ob_spinBox.value()
        else:
            number_of_obs = 0

        self.parent.number_of_files_requested["ob"] = number_of_obs

        name_of_output_projection_folder = self.parent.ui.projections_output_location_label.text()
        self.parent.session_dict[SessionKeys.name_of_output_projection_folder] = name_of_output_projection_folder

        name_of_output_ob_folder = self.parent.ui.obs_output_location_label.text()
        self.parent.session_dict[SessionKeys.name_of_output_ob_folder] = name_of_output_ob_folder

        o_get = Step1Get(parent=self.parent)
        title = self.parent.ui.run_title_lineEdit.text()
        list_ob_folders = o_get.list_ob_folders_in_output_directory(output_folder=name_of_output_ob_folder, title=title)
        list_sample_folders = o_get.list_sample_folders_in_output_directory(
            output_folder=name_of_output_projection_folder, title=title
        )

        self.parent.session_dict[SessionKeys.list_ob_folders_initially_there] = list_ob_folders
        self.parent.session_dict[SessionKeys.list_projections_folders_initially_there] = list_sample_folders

    def save_path(self) -> None:
        """
        Save path information.

        Placeholder for future implementation of path saving functionality.
        """
        pass
