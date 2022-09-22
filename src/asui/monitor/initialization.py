from qtpy.QtWidgets import QPushButton
import numpy as np

from asui.setup_ob.get import Get as GetOB
from asui.utilities.get import Get
from asui.utilities.table import TableHandler
from asui.monitor.get import Get as GetMonitor

from . import READY, IN_PROGRESS, IN_QUEUE, FAILED


class Initialization:

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

    def data(self):
        """
               this is where we need to figure out the list of NeXus files already listed
               and how many we are expecting
               """
        nbr_obs_expected = self.grand_parent.number_of_files_requested['ob']
        if not nbr_obs_expected:
            # retrieve list of ob selected
            o_get_ob = GetOB(parent=self.grand_parent)
            list_ob = o_get_ob.list_ob_folders_selected()
            self.populate_table_with_existing_obs(list_ob=list_ob)

        else:
            self.populate_table_with_expected_obs(nbr_obs_expected=nbr_obs_expected)

        nbr_sample_expected = self.grand_parent.number_of_files_requested['sample']
        folder_path = self.grand_parent.folder_path

        initial_list_of_reduction_log_files = \
            Get.list_of_files(folder=folder_path.reduction_log,
                              ext="*")
        self.parent.initial_list_of_reduction_log_files = \
            initial_list_of_reduction_log_files

    def ui(self):
        table_columns = [540, 50, 50, 50, 45]
        o_ob_table = TableHandler(table_ui=self.parent.ui.obs_tableWidget)
        o_ob_table.set_column_sizes(column_sizes=table_columns)
        o_pro_table = TableHandler(table_ui=self.parent.ui.projections_tableWidget)
        o_pro_table.set_column_sizes(column_sizes=table_columns)

    def populate_table_with_expected_obs(self, nbr_obs_expected=0):
        o_table = TableHandler(table_ui=self.parent.ui.obs_tableWidget)
        for _row_index in np.arange(nbr_obs_expected):
            o_table.insert_empty_row(row=_row_index)
            o_table.insert_item(row=_row_index,
                                column=0,
                                value="N/A")
            o_table.insert_item(row=_row_index,
                                column=3,
                                value="Measuring")
            o_table.set_background_color(row=_row_index,
                                         column=3,
                                         qcolor=IN_PROGRESS)

    def populate_table_with_existing_obs(self, list_ob=None):
        if list_ob is None:
            return

        o_table = TableHandler(table_ui=self.parent.ui.obs_tableWidget)
        o_get = GetMonitor(parent=self.parent,
                           grand_parent=self.grand_parent)
        dict_ob_log_err_metadata = {}
        for _row_index, _ob in enumerate(list_ob):
            o_table.insert_empty_row(row=_row_index)
            o_table.insert_item(row=_row_index,
                                column=0,
                                value=_ob)


            log_file = o_get.log_file(_ob)
            if log_file:
                log_button = QPushButton("View")
                o_table.insert_widget(row=_row_index,
                                      column=1,
                                      widget=log_button)
                log_button.clicked.connect(lambda state=0, row=_row_index:
                                           self.parent.preview_log(row=row,
                                                                   data_type='ob'))
            else:
                o_table.insert_item(row=_row_index,
                                    column=1,
                                    value="N/A")

            err_file = o_get.err_file(_ob)
            if err_file:
                err_button = QPushButton("View")
                o_table.insert_widget(row=_row_index,
                                      column=2,
                                      widget=err_button)
                err_button.clicked.connect(lambda state=0, row=_row_index:
                                           self.parent.preview_err(row=row,
                                                                   data_type='ob'))
            else:
                o_table.insert_item(row=_row_index,
                                    column=2,
                                    value="N/A")

            metadata_file = o_get.metadata_file(_ob)
            if metadata_file:
                summary_button = QPushButton("View")
                o_table.insert_widget(row=_row_index,
                                      column=3,
                                      widget=summary_button)
                summary_button.clicked.connect(lambda state=0, row=_row_index:
                                               self.parent.preview_summary(row=row,
                                                                           data_type='ob'))
            else:
                o_table.insert_item(row=_row_index,
                                    column=3,
                                    value="N/A")

            o_table.insert_item(row=_row_index,
                                column=4,
                                value="Ready")
            o_table.set_background_color(row=_row_index,
                                         column=4,
                                         qcolor=READY)

            dict_ob_log_err_metadata[_row_index] = {'ob': _ob,
                                                'log_file': log_file,
                                                'err_file': err_file,
                                                'metadata_file': metadata_file}

        self.parent.dict_ob_log_err_metadata = dict_ob_log_err_metadata