import copy
import os

from qtpy.QtWidgets import QPushButton
import numpy as np
import logging

from asui.utilities.file_utilities import list_tof_dirs, make_folder, move_list_files_to_folder
from asui.utilities.status_message_config import show_status_message, StatusMessageStatus
from asui.utilities.table import TableHandler
from asui.pre_processing_monitor.get import Get as GetMonitor
from ..session import SessionKeys

from . import READY, IN_PROGRESS, IN_QUEUE, FAILED
from . import DataStatus
from .. import DataType


class EventHandler:

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

    def checking_status_of(self,
                           data_type=DataType.ob,
                           output_folder=None,
                           table_ui=None,
                           dict_log_err_metadata=None,
                           list_folder_previously_found=None):
        """
        this method should check if the folder requested has been found (already created)
        and will update the table

        Return: list of folders found, are all files found
        """

        logging.info(f"Checking the monitor status of {data_type}")

        o_table = TableHandler(table_ui=table_ui)
        if data_type == DataType.projection:
            # only if we are looking at the projections and
            # all the obs have been found!
            if self.parent.all_obs_found:

                o_table.insert_item(row=0,
                                    column=4,
                                    value=DataStatus.in_progress)
                o_table.set_background_color(row=0,
                                             column=4,
                                             qcolor=IN_PROGRESS)

        o_table = TableHandler(table_ui=table_ui)
        nbr_row = o_table.row_count()

        list_folder_found = []

        o_get = GetMonitor(parent=self.parent,
                           grand_parent=self.grand_parent)

        # we go row by row to see if we need to change the status of the row
        for _row in np.arange(nbr_row):

            logging.info(f"- row #{_row}")
            # if the last column says DONE, nothing to do
            row_status = o_table.get_item_str_from_cell(row=_row, column=4)
            file_name = o_table.get_item_str_from_cell(row=_row, column=0)
            logging.info(f"\t {file_name} - {row_status}")
            if row_status == READY:
                logging.info(f"\tfile already found!")
                list_folder_found.append(file_name)
                continue

            if os.path.exists(file_name):
                logging.info(f"\tfile newly found!")
                list_folder_found.append(file_name)
                # update table and add widgets + change status of file

                o_get.set_path(file_name)

                log_file = o_get.log_file()
                if log_file:
                    enable_button = True
                else:
                    enable_button = False

                log_button = QPushButton("View")
                log_button.setEnabled(enable_button)
                o_table.insert_widget(row=_row,
                                      column=1,
                                      widget=log_button)

                log_button.clicked.connect(lambda state=0, row=_row:
                                           self.parent.preview_log(row=row,
                                                                   data_type='ob'))
                err_file = o_get.err_file()
                if err_file:
                    enable_button = True
                else:
                    enable_button = False

                err_button = QPushButton("View")
                err_button.setEnabled(enable_button)
                o_table.insert_widget(row=_row,
                                      column=2,
                                      widget=err_button)
                err_button.clicked.connect(lambda state=0, row=_row:
                                           self.parent.preview_err(row=row,
                                                                   data_type='ob'))

                metadata_file = o_get.metadata_file()
                if metadata_file:
                    enable_button = True
                else:
                    enable_button = False

                summary_button = QPushButton("View")
                summary_button.setEnabled(enable_button)
                o_table.insert_widget(row=_row,
                                      column=3,
                                      widget=summary_button)
                summary_button.clicked.connect(lambda state=0, row=_row:
                                               self.parent.preview_summary(row=row,
                                                                           data_type='ob'))

                o_table.insert_item(row=_row,
                                    column=4,
                                    value=DataStatus.ready)
                o_table.set_background_color(row=_row,
                                             column=4,
                                             qcolor=READY)

                dict_log_err_metadata[_row] = {'file_name': file_name,
                                               'log_file': log_file,
                                               'err_file': err_file,
                                               'metadata_file': metadata_file}

            else:
                logging.info(f"\tnot found! we can leave now")
                # no need to keep going, except that this one is in progress
                o_table.insert_item(row=_row,
                                    column=4,
                                    value=DataStatus.in_progress)
                o_table.set_background_color(row=_row,
                                             column=4,
                                             qcolor=IN_PROGRESS)
                break

        return list_folder_found, len(list_folder_found) == nbr_row

    def checking_status_of_expected_obs(self):
        """look at the list of obs expected and updates the OB table
        with the ones already found"""
        output_folder = self.grand_parent.ui.obs_output_location_label.text()
        # nbr_obs_expected = self.grand_parent.ui.number_of_ob_spinBox.value()

        logging.info(f"Checking status of expected obs:")
        list_folders_found, self.parent.all_obs_found = self.checking_status_of(
                                                         data_type=DataType.ob,
                                                         output_folder=output_folder,
                                                         table_ui=self.parent.ui.obs_tableWidget,
                                                         dict_log_err_metadata=self.parent.dict_ob_log_err_metadata,
                                                         list_folder_previously_found=
                                                         self.grand_parent.session_dict[SessionKeys.list_ob_folders_initially_there])
        self.grand_parent.session_dict[SessionKeys.list_ob_folders_initially_there] = list_folders_found
        logging.info(f"-> list folders found: {list_folders_found}")

    def checking_status_of_expected_projections(self):
        """look at the list of projections and updates the projection table
        with the ones already found!"""
        output_folder = self.grand_parent.ui.projections_output_location_label.text()
        nbr_projections_expected = self.grand_parent.ui.number_of_projections_spinBox.value()

        list_folders_found, self.parent.all_projections_found = self.checking_status_of(
                                                                 data_type=DataType.projection,
                                                                 output_folder=output_folder,
                                                                 nbr_files_expected=nbr_projections_expected,
                                                                 table_ui=self.parent.ui.projections_tableWidget,
                                                                 dict_log_err_metadata=self.parent.dict_projections_log_err_metadata)
        self.grand_parent.session_dict[SessionKeys.list_projections_folders_initially_there] = list_folders_found

    def obs_have_been_moved_to_final_folder(self):
        list_ob_folders = self.grand_parent.session_dict[SessionKeys.list_ob_folders_initially_there]
        final_location = self.grand_parent.ui.final_location_of_ob_created.text()
        for _folder in list_ob_folders:
            base_name = os.path.basename(_folder)
            full_name_in_final_location = os.path.join(final_location, base_name)
            if not os.path.exists(full_name_in_final_location):
                return False
        return True

    def move_obs_to_final_folder(self):
        """
        If all the OBs have been found, it will move them to their final location and will update the table at the
        same time to make sure we are now pointing to the final location.
        """
        logging.info(f"Moving obs to final folder!")
        list_ob_folders = self.grand_parent.session_dict[SessionKeys.list_ob_folders_initially_there]
        final_location = self.grand_parent.ui.final_location_of_ob_created.text()
        make_folder(final_location)
        move_list_files_to_folder(list_of_files=list_ob_folders,
                                  folder=final_location)

        logging.info(f"Updating table with new location of obs!")
        o_table = TableHandler(table_ui=self.parent.ui.obs_tableWidget)
        for _row, _folder in enumerate(list_ob_folders):
            _new_final_location = os.path.join(final_location, os.path.basename(_folder))
            o_table.set_item_with_str(row=_row,
                                      column=0,
                                      value=_new_final_location)
