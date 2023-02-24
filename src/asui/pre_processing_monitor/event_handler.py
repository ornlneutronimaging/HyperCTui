import copy
import os

from qtpy.QtWidgets import QPushButton
import numpy as np
import logging

from asui.utilities.file_utilities import list_tof_dirs
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
        """

        logging.info(f"Checking the monitor status of {data_type}")
        logging.info(f"- here is the list of folder previously found:")
        for _folder in list_folder_previously_found:
            logging.info(f"\t - {_folder}")

        # get list of folders requested
        o_table = TableHandler(table_ui=table_ui)
        nbr_row = o_table.row_count()
        list_folder_requested = []
        logging.info(f"- list folder requested:")
        for _row in np.arange(nbr_row):
            _folder = o_table.get_item_str_from_cell(row=_row, column=0)
            list_folder_requested.append(_folder)
            logging.info(f"\t- {_folder}")

        # checking the folders that do exists
        logging.info(f"- Checking list of folders that exists:")
        list_folders_requested_and_found = []
        for _folder in list_folder_requested:
            if os.path.exists(_folder):
                list_folders_requested_and_found.append(_folder)
                logging.info(f"\t {_folder}")

        # let's remove from that list the folder that was previously found
        # to only work with the one not been found yet
        logging.info(f"- keeping only the new file created:")
        list_folder_requested_and_newly_found = []
        if list_folders_requested_and_found:
            if list_folder_previously_found:
                for _folder in list_folders_requested_and_found:
                    if not (_folder in list_folder_previously_found):
                        list_folder_requested_and_newly_found.append(_folder)
                        logging.info(f"\t - {_folder}")
        if len(list_folder_requested_and_newly_found) == 0:
            logging.info(f"\t - None!")


        # no new folder found so we can just return the same list of folder previously found
        if len(list_folder_requested_and_newly_found) == 0:
            return list_folder_previously_found

        # with the remaining folder, go one by one to find if they have been found now





        # logging.info(f"List of folders requested and found:")
        # if len(list_folders_requested_and_found) > 0:
        #     for _folder in list_folders_requested_and_found:
        #         logging.info(f"\t- {_folder}")
        # else:
        #     logging.info(f"\n- None!")
        #
        # if len(list_folders_requested_and_found) == len(list_folder_requested):
        #     if data_type == DataType.ob:
        #         self.parent.all_obs_found = True
        #     else:
        #         self.parent.all_projections_found = True
        #
        # untouched_list_folders = copy.deepcopy(list_folders_requested_and_found)
        #
        # o_table = TableHandler(table_ui=table_ui)
        # if len(list_folders_requested_and_found) == 0:
        #     if data_type == DataType.ob:
        #         # no OB folder showed up yet
        #         return []
        #     else:
        #         # none of the projections showed up yet,
        #         # we need to show that the acquisition of the first one started
        #         o_table.set_item_with_str(row=0, column=4, value=DataStatus.in_progress)
        #         o_table.set_background_color(row=0, column=4, qcolor=IN_PROGRESS)
        #         return []
        #
        # else:
        #
        #     # at least one of the projection file showed up
        #     o_get = GetMonitor(parent=self.parent,
        #                        grand_parent=self.grand_parent)
        #     its_first_row_with_measuring_file = True
        #     for _row in np.arange(o_table.row_count()):
        #         _file_name_in_table = o_table.get_item_str_from_cell(row=_row,
        #                                                              column=0)
        #         if _file_name_in_table in list_folders_requested_and_found:
        #             # we already have an entry in the table for that file
        #
        #             # a new file showed up
        #             o_table.remove_row(row=_row)
        #             new_projection = list_folders.pop(0)
        #             o_get.set_ob_folder_name(new_projection)
        #
        #             # o_table.insert_empty_row(row=_row)
        #             # o_table.insert_item(row=_row,
        #             #                     column=0,
        #             #                     value=new_projection)
        #
        #             log_file = o_get.log_file()
        #             if log_file:
        #                 enable_button = True
        #             else:
        #                 enable_button = False
        #
        #             log_button = QPushButton("View")
        #             log_button.setEnabled(enable_button)
        #             o_table.insert_widget(row=_row,
        #                                   column=1,
        #                                   widget=log_button)
        #
        #             log_button.clicked.connect(lambda state=0, row=_row:
        #                                        self.parent.preview_log(row=row,
        #                                                                data_type='ob'))
        #             err_file = o_get.err_file()
        #             if err_file:
        #                 enable_button = True
        #             else:
        #                 enable_button = False
        #
        #             err_button = QPushButton("View")
        #             err_button.setEnabled(enable_button)
        #             o_table.insert_widget(row=_row,
        #                                   column=2,
        #                                   widget=err_button)
        #             err_button.clicked.connect(lambda state=0, row=_row:
        #                                        self.parent.preview_err(row=row,
        #                                                                data_type='ob'))
        #
        #             metadata_file = o_get.metadata_file()
        #             if metadata_file:
        #                 enable_button = True
        #             else:
        #                 enable_button = False
        #
        #             summary_button = QPushButton("View")
        #             summary_button.setEnabled(enable_button)
        #             o_table.insert_widget(row=_row,
        #                                   column=3,
        #                                   widget=summary_button)
        #             summary_button.clicked.connect(lambda state=0, row=_row:
        #                                            self.parent.preview_summary(row=row,
        #                                                                        data_type='ob'))
        #
        #             o_table.insert_item(row=_row,
        #                                 column=4,
        #                                 value=DataStatus.ready)
        #             o_table.set_background_color(row=_row,
        #                                          column=4,
        #                                          qcolor=READY)
        #
        #             dict_log_err_metadata[_row] = {'file_name': new_projection,
        #                                            'log_file': log_file,
        #                                            'err_file': err_file,
        #                                            'metadata_file': metadata_file}
        #
        #
        #
        #
        #
        #



                #     list_folders.remove(item)
                #     if len(list_folders) == 0:
                #         break
                #     else:
                #         continue
                #
                # elif len(list_folders) == 0:
                #
                #     # no folder so far showed up
                #     if its_first_row_with_measuring_file:
                #         message = DataStatus.in_progress
                #         color = IN_PROGRESS
                #         its_first_row_with_measuring_file = False
                #     else:
                #         message = DataStatus.in_queue
                #         color = IN_QUEUE
                #     o_table.insert_item(row=_row,
                #                         column=4,
                #                         value=message)
                #     o_table.set_background_color(row=_row,
                #                                  column=4,
                #                                  qcolor=color)
                #
                # else:

                    # # a new file showed up
                    # o_table.remove_row(row=_row)
                    # new_projection = list_folders.pop(0)
                    # o_get.set_ob_folder_name(new_projection)
                    #
                    # o_table.insert_empty_row(row=_row)
                    # o_table.insert_item(row=_row,
                    #                     column=0,
                    #                     value=new_projection)
                    #
                    # log_file = o_get.log_file()
                    # if log_file:
                    #     enable_button = True
                    # else:
                    #     enable_button = False
                    #
                    # log_button = QPushButton("View")
                    # log_button.setEnabled(enable_button)
                    # o_table.insert_widget(row=_row,
                    #                       column=1,
                    #                       widget=log_button)
                    #
                    # log_button.clicked.connect(lambda state=0, row=_row:
                    #                            self.parent.preview_log(row=row,
                    #                                                    data_type='ob'))
                    # err_file = o_get.err_file()
                    # if err_file:
                    #     enable_button = True
                    # else:
                    #     enable_button = False
                    #
                    # err_button = QPushButton("View")
                    # err_button.setEnabled(enable_button)
                    # o_table.insert_widget(row=_row,
                    #                       column=2,
                    #                       widget=err_button)
                    # err_button.clicked.connect(lambda state=0, row=_row:
                    #                            self.parent.preview_err(row=row,
                    #                                                    data_type='ob'))
                    #
                    # metadata_file = o_get.metadata_file()
                    # if metadata_file:
                    #     enable_button = True
                    # else:
                    #     enable_button = False
                    #
                    # summary_button = QPushButton("View")
                    # summary_button.setEnabled(enable_button)
                    # o_table.insert_widget(row=_row,
                    #                       column=3,
                    #                       widget=summary_button)
                    # summary_button.clicked.connect(lambda state=0, row=_row:
                    #                                self.parent.preview_summary(row=row,
                    #                                                            data_type='ob'))
                    #
                    # o_table.insert_item(row=_row,
                    #                     column=4,
                    #                     value=DataStatus.ready)
                    # o_table.set_background_color(row=_row,
                    #                              column=4,
                    #                              qcolor=READY)
                    #
                    # dict_log_err_metadata[_row] = {'file_name': new_projection,
                    #                                'log_file': log_file,
                    #                                'err_file': err_file,
                    #                                'metadata_file': metadata_file}

        return untouched_list_folders

    def checking_status_of_expected_obs(self):
        """look at the list of obs expected and updates the OB table
        with the ones already found"""
        output_folder = self.grand_parent.ui.obs_output_location_label.text()
        # nbr_obs_expected = self.grand_parent.ui.number_of_ob_spinBox.value()

        logging.info(f"Checking status of expected obs:")
        list_folders_found = self.checking_status_of(
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

        list_folders_found = self.checking_status_of(
                                                     data_type=DataType.projection,
                                                     output_folder=output_folder,
                                                     nbr_files_expected=nbr_projections_expected,
                                                     table_ui=self.parent.ui.projections_tableWidget,
                                                     dict_log_err_metadata=self.parent.dict_projections_log_err_metadata)
        self.grand_parent.session_dict[SessionKeys.list_projections_folders_initially_there] = list_folders_found

    def obs_have_been_moved_to_final_folder(self):
        # FIXME
        pass

    def move_obs_to_final_folder(self):
        # FIXME
        pass
