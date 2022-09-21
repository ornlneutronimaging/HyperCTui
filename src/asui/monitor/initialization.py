from qtpy.QtWidgets import QPushButton

from asui.setup_ob.get import Get as GetOB
from asui.utilities.get import Get
from asui.utilities.table import TableHandler


class Initialization:

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

    def data(self):
        """
               this is where we need to figure out the list of NeXus files already listed
               and how many we are expecting
               """
        nbr_ob_expected = self.grand_parent.number_of_files_requested['ob']
        if not nbr_ob_expected:
            # retrieve list of ob selected
            o_get_ob = GetOB(parent=self.grand_parent)
            list_ob = o_get_ob.list_ob_folders_selected()
            self.populate_ob_table(list_ob=list_ob)

        nbr_sample_expected = self.grand_parent.number_of_files_requested['sample']
        folder_path = self.grand_parent.folder_path

        initial_list_of_reduction_log_files = \
            Get.list_of_files(folder=folder_path.reduction_log,
                              ext="*")
        self.parent.initial_list_of_reduction_log_files = \
            initial_list_of_reduction_log_files

    def ui(self):
        table_columns = [600, 50, 50, 50]
        o_ob_table = TableHandler(table_ui=self.parent.ui.obs_tableWidget)
        o_ob_table.set_column_sizes(column_sizes=table_columns)
        o_pro_table = TableHandler(table_ui=self.parent.ui.projections_tableWidget)
        o_pro_table.set_column_sizes(column_sizes=table_columns)

    def populate_ob_table(self, list_ob=None):
        if list_ob is None:
            return

        o_table = TableHandler(table_ui=self.parent.ui.obs_tableWidget)
        for _row_index, _ob in enumerate(list_ob):
            o_table.insert_empty_row(row=_row_index)
            o_table.insert_item(row=_row_index,
                                column=0,
                                value=_ob)

            log_button = QPushButton("View")
            o_table.insert_widget(row=_row_index,
                                  column=1,
                                  widget=log_button)
            log_button.clicked.connect(lambda state=0, row=_row_index:
                                              self.parent.preview_log(row=row,
                                                                      data_type='ob'))
