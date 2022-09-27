from qtpy.QtWidgets import QPushButton
import numpy as np

from asui.utilities.file_utilities import list_ob_dirs
from asui.utilities.status_message_config import show_status_message, StatusMessageStatus
from asui.utilities.table import TableHandler
from asui.monitor.get import Get as GetMonitor

from . import READY, IN_PROGRESS, IN_QUEUE, FAILED
from . import DataStatus


class EventHandler:

	def __init__(self, parent=None, grand_parent=None):
		self.parent = parent
		self.grand_parent = grand_parent

	def checking_status_of_expected_obs(self):
		"""look at the list of obs expected and updates the OB table
		with the one already found"""
		output_folder = self.grand_parent.ui.obs_output_location_label.text()
		nbr_obs_expected = self.grand_parent.ui.number_of_ob_spinBox.value()
		list_folders = list_ob_dirs(output_folder)

		if len(list_folders) > nbr_obs_expected:
			message = "Output OB folder contains more data than requested, check the validity of the folder!"
			show_status_message(parent=self.grand_parent,
								message=message,
								status=StatusMessageStatus.error,
								duration_s=10)
			return

		if len(list_folders) == 0:
			# no OB folder showed up yet
			return

		else:
			# at least one OB folder showed up
			o_table = TableHandler(table_ui=self.parent.ui.obs_tableWidget)
			o_get = GetMonitor(parent=self.parent,
							   grand_parent=self.grand_parent)
			its_first_row_with_measuring_ob = True
			for _row in np.arange(nbr_obs_expected):
				item = o_table.get_item_str_from_cell(row=_row,
													  column=0)
				if item in list_folders:
					list_folders.remove(item)
					if len(list_folders) == 0:
						break
					else:
						continue

				elif len(list_folders) == 0:

					if its_first_row_with_measuring_ob:
						message = DataStatus.in_progress
						color = IN_PROGRESS
						its_first_row_with_measuring_ob = False
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
					new_ob = list_folders.pop(0)
					o_get.set_ob_folder_name(new_ob)

					o_table.insert_empty_row(row=_row)
					o_table.insert_item(row=_row,
										column=0,
										value=new_ob)

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

					self.parent.dict_ob_log_err_metadata[_row] = {'ob': new_ob,
																  'log_file': log_file,
																  'err_file': err_file,
																  'metadata_file': metadata_file}