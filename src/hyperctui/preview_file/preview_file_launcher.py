#!/usr/bin/env python
"""
Module for previewing different file types within the HyperCTui application.

This module provides dialog classes for previewing various file types:
- PreviewImageLauncher: For displaying FITS image files
- PreviewFileLauncher: For displaying text files
- PreviewMetadataFileLauncher: For displaying JSON metadata files
"""

import logging
import os
from pathlib import Path
from typing import Optional, Union

import pyqtgraph as pg
from astropy.io import fits
from qtpy.QtWidgets import QDialog, QVBoxLayout, QWidget

from hyperctui import load_ui
from hyperctui.utilities.file_utilities import read_ascii, read_json
from hyperctui.utilities.table import TableHandler


class PreviewImageLauncher(QDialog):
    """
    Dialog for displaying FITS image files.

    This class creates a dialog window that shows a FITS image using pyqtgraph.
    It handles both 2D and 3D FITS data.
    """

    def __init__(self, parent: Optional[QWidget] = None, file_name: Optional[Union[str, Path]] = None):
        """
        Initialize the PreviewImageLauncher dialog.

        Parameters
        ----------
        parent : QWidget, optional
            Parent widget, by default None
        file_name : str or Path, optional
            Path to the FITS file to display, by default None
        """
        QDialog.__init__(self, parent=parent)

        self.parent = parent
        self.file_name = file_name

        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), os.path.join("ui", "preview_image.ui"))

        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Preview")

        if not Path(file_name).is_file():
            logging.info(f"file name {file_name} does not exist!")
            self.ui.file_name_label.setText(f"{file_name} can not be located!")

        else:
            self.ui.file_name_label.setText(os.path.basename(file_name))
            self.display_image()

    def display_image(self) -> None:
        """
        Display the FITS image in the dialog.

        Reads the FITS file data and displays it using pyqtgraph ImageView.
        Handles 3D data by reshaping it to 2D.
        """
        image_view = pg.ImageView(view=pg.PlotItem())
        image_view.ui.roiBtn.hide()
        image_view.ui.menuBtn.hide()
        image_layout = QVBoxLayout()
        image_layout.addWidget(image_view)
        self.ui.widget.setLayout(image_layout)

        tmp = fits.open(self.file_name, ignore_missing_simple=True)[0].data
        if len(tmp.shape) == 3:
            image_data = tmp.reshape(tmp.shape[1:])
        else:
            image_data = tmp

        image_view.setImage(image_data)


class PreviewFileLauncher(QDialog):
    def __init__(self, parent=None, file_name=None):
        QDialog.__init__(self, parent=parent)

        self.parent = parent
        self.file_name = file_name

        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), os.path.join("ui", "preview_file.ui"))

        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Preview")

        if not Path(file_name).is_file():
            logging.info(f"file name {file_name} does not exist!")
            self.ui.file_name_label.setText(f"{file_name} can not be located!")

        else:
            self.ui.file_name_label.setText(file_name)
            self.display_file()

    def display_file(self):
        if self.file_name is None:
            file_content = "File empty!"
        else:
            file_content = read_ascii(self.file_name)
        self.ui.file_textEdit.setText(file_content)
        self.ui.file_textEdit.setReadOnly(True)


class PreviewMetadataFileLauncher(QDialog):
    def __init__(self, parent=None, file_name=None):
        QDialog.__init__(self, parent=parent)

        if not Path(file_name).is_file():
            logging.info(f"file name {file_name} does not exist!")
            return

        self.parent = parent
        self.file_name = file_name

        ui_full_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), os.path.join("ui", "preview_metadata_file.ui")
        )

        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Preview")

        self.ui.file_name_label.setText(file_name)
        self.initialization()
        self.display_file()

    def initialization(self):
        o_table = TableHandler(table_ui=self.ui.tableWidget)
        o_table.set_column_sizes(column_sizes=[200, 300])

    def display_file(self):
        if self.file_name is None:
            file_content = {"status": "File not found!"}
        else:
            file_content = read_json(self.file_name)

        o_table = TableHandler(table_ui=self.ui.tableWidget)
        for _row_index, _key in enumerate(file_content.keys()):
            o_table.insert_empty_row(row=_row_index)
            o_table.insert_item(row=_row_index, column=0, value=_key)
            o_table.set_item_editable(row=_row_index, column=0, editable=False)
            o_table.insert_item(row=_row_index, column=1, value=file_content[_key])
            o_table.set_item_editable(row=_row_index, column=1, editable=False)
