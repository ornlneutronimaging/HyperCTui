import logging
from qtpy.QtCore import QRect

from .parent import Parent
from .initialization.gui_initialization import GuiInitialization
from .setup_ob.get import Get as Step1Get
from .session.new_session import NewSession
from .session import SessionKeys
from .setup_ob.event_handler import EventHandler as ObEventHandler
from . import UiSizeLarge, UiSizeSmall
from . import ObTabNames
from .setup_ob.get import Get as ObGet


class EventHandler(Parent):

    def new_session(self):
        o_new = NewSession(parent=self.parent)
        o_new.show()

    def full_reset_clicked(self):
        o_init = GuiInitialization(parent=self.parent)
        o_init.full_reset()
        logging.info("Full reset of application!")

    def ob_tab_changed(self):
        current_tab = self.parent.ui.ob_tabWidget.currentIndex()
        if current_tab == ObTabNames.selected_obs:
            o_event = ObEventHandler(parent=self.parent)
            o_event.update_list_of_obs()

    def check_start_acquisition_button(self):
        if not self.parent.ui.run_title_groupBox.isEnabled():
            button_ready_to_be_used = False
        else:
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

        if self.parent.ui.run_title_formatted_label.text() == "N/A":
            logging.info(f"Please provide a title to be able to start the acquisition!")
            return False

        if self.parent.ui.projections_output_location_label.text() == "N/A":
            logging.info(f"Make sure the output folder exists (check instrument and IPTS)!")
            return False

        if str(self.parent.ui.projections_p_charge_label.text()) == "N/A":
            logging.info(f"ASUI is unable to determine the proton charge you want to use!")
            logging.info(f"-> Possible correction: ")
            logging.info(f"     * you want to use previously measured OBs and they don't seem to have the same "
                         f"proton charge")
            return False

        return True

    def set_start_acquisition_text(self):
        button_text = "Start acquisition of "
        if self.parent.ui.ob_tabWidget.currentIndex() == 0:
            number_of_obs = self.parent.ui.number_of_ob_spinBox.value()
            button_text += f"{number_of_obs} OBs and "
        button_text += u"0\u00B0 and 180\u00B0 projections"
        self.parent.ui.start_acquisition_pushButton.setText(button_text)

    def main_tab_changed(self, new_tab_index=0):
        """
        resize the main ui according to the tab selected
        small version for the first 2 main tabs
        large version for the next 3 tabs
        """
        if new_tab_index == 1:  # initialize first projections 0 and 180 degrees
            # update p charge
            o_get = ObGet(parent=self.parent)
            proton_charge = o_get.proton_charge()
            self.parent.ui.projections_p_charge_label.setText(str(proton_charge))

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
        # if not move_to_large_ui:
        #     width = UiSizeSmall.width
        #     height = UiSizeSmall.height
        if move_to_large_ui:
            width = UiSizeLarge.width if width < UiSizeLarge.width else width
            height = UiSizeLarge.height if height < UiSizeLarge.height else height

        rect = QRect(left, top, width, height)
        self.parent.ui.setGeometry(rect)
        self.parent.current_tab_index = new_tab_index

    def start_acquisition(self):
        """
        script that will call Shimin's code to take OB and first projections
        """
        pass

    def freeze_number_ob_sample_requested(self):
        """
        this freeze the number of OB and sample measured and record the initial list of OBs and sample folders
        """
        if self.parent.ui.ob_tabWidget.currentIndex() == 0:
            number_of_obs = self.parent.ui.number_of_ob_spinBox.value()
        else:
            number_of_obs = 0

        self.parent.number_of_files_requested['ob'] = number_of_obs

        name_of_output_projection_folder = self.parent.ui.projections_output_location_label.text()
        self.parent.session_dict[SessionKeys.name_of_output_projection_folder] = name_of_output_projection_folder
        name_of_output_ob_folder = self.parent.ui.obs_output_location_label.text()
        self.parent.session_dict[SessionKeys.name_of_output_ob_folder] = name_of_output_ob_folder

        o_get = Step1Get(parent=self.parent)
        list_ob_folders = o_get.list_ob_folders_in_output_directory(output_folder=name_of_output_ob_folder)
        list_sample_folders = o_get.list_sample_folders_in_output_directory(output_folder=
                                                                            name_of_output_projection_folder)
        self.parent.session_dict[SessionKeys.list_ob_folders_initially_there] = list_ob_folders
        self.parent.session_dict[SessionKeys.list_projections_folders_initially_there] = list_sample_folders

    def save_path(self):
        pass
