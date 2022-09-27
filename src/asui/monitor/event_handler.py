from qtpy.QtWidgets import QPushButton
import numpy as np

from asui.utilities.file_utilities import list_tof_dirs
from asui.utilities.status_message_config import show_status_message, StatusMessageStatus
from asui.utilities.table import TableHandler
from asui.monitor.get import Get as GetMonitor

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
                           nbr_files_expected=0,
                           table_ui=None,
                           dict_log_err_metadata=None):

        list_folders = list_tof_dirs(output_folder)
        if len(list_folders) == nbr_files_expected:
            if data_type == DataType.ob:
                self.parent.all_obs_found = True

        if len(list_folders) > nbr_files_expected:
            message = f"Output {data_type} folder contains more data than requested, check the validity of the folder!"
            show_status_message(parent=self.grand_parent,
                                message=message,
                                status=StatusMessageStatus.error,
                                duration_s=10)
            return

        o_table = TableHandler(table_ui=table_ui)
        if len(list_folders) == 0:
            if data_type == DataType.ob:
                # no OB folder showed up yet
                return
            else:
                # none of the projections showed up yet,
                # we need to show that the acquisition of the first one started
                o_table.set_item_with_str(row=0, column=4, value=DataStatus.in_progress)
                o_table.set_background_color(row=0, column=4, qcolor=IN_PROGRESS)
                return

        else:

            # at least one of the projection file showed up
            o_get = GetMonitor(parent=self.parent,
                               grand_parent=self.grand_parent)
            its_first_row_with_measuring_file = True
            for _row in np.arange(nbr_files_expected):
                item = o_table.get_item_str_from_cell(row=_row,
                                                      column=0)
                if item in list_folders:
                    # we already have an entry in the table for that file
                    list_folders.remove(item)
                    if len(list_folders) == 0:
                        break
                    else:
                        continue

                elif len(list_folders) == 0:

                    # no folder so far showed up
                    if its_first_row_with_measuring_file:
                        message = DataStatus.in_progress
                        color = IN_PROGRESS
                        its_first_row_with_measuring_file = False
                    else:
                        message = DataStatus.in_queue
                        color = IN_QUEUE
                    o_table.insert_item(row=_row,
                                        column=4,
                                        value=message)
                    o_table.set_background_color(row=_row,
                                                 column=4,
                                                 qcolor=color)

                else:

                    # a new file showed up
                    o_table.remove_row(row=_row)
                    new_projection = list_folders.pop(0)
                    o_get.set_ob_folder_name(new_projection)

                    o_table.insert_empty_row(row=_row)
                    o_table.insert_item(row=_row,
                                        column=0,
                                        value=new_projection)

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

                    dict_log_err_metadata[_row] = {'file_name': new_projection,
                                                   'log_file': log_file,
                                                   'err_file': err_file,
                                                   'metadata_file': metadata_file}

    def checking_status_of_expected_obs(self):
        """look at the list of obs expected and updates the OB table
        with the one already found"""
        output_folder = self.grand_parent.ui.obs_output_location_label.text()
        nbr_obs_expected = self.grand_parent.ui.number_of_ob_spinBox.value()

        self.checking_status_of(data_type=DataType.ob,
                                output_folder=output_folder,
                                nbr_files_expected=nbr_obs_expected,
                                table_ui=self.parent.ui.obs_tableWidget,
                                dict_log_err_metadata=self.parent.dict_ob_log_err_metadata)

    def checking_status_of_expected_projections(self):
        output_folder = self.grand_parent.ui.projections_output_location_label.text()
        nbr_projections_expected = self.grand_parent.ui.number_of_projections_spinBox.value()

        self.checking_status_of(data_type=DataType.projection,
                                output_folder=output_folder,
                                nbr_files_expected=nbr_projections_expected,
                                table_ui=self.parent.ui.projections_tableWidget,
                                dict_log_err_metadata=self.parent.dict_projections_log_err_metadata)
