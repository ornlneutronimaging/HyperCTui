#!/usr/bin/env python
"""
Module for initializing the HyperCTui graphical user interface.

This module provides functionality for setting up the GUI components including
status bars, widgets, tables, tabs, and PyQtGraph visualization elements.
"""

import os

import numpy as np
import pandas as pd
import pyqtgraph as pg
from qtpy.QtGui import QIcon, QPixmap
from qtpy.QtWidgets import QProgressBar, QVBoxLayout

from hyperctui import TabNames, golden_ratio_file, more_infos, tab0_icon, tab1_icon
from hyperctui.utilities.config_handler import ConfigHandler
from hyperctui.utilities.table import TableHandler


class GuiInitialization:
    """
    Class responsible for initializing all GUI components of HyperCTui application.

    This class sets up the status bar, widgets, tables, tabs, PyQtGraph elements,
    and loads necessary data for autonomous reconstruction.

    Parameters
    ----------
    parent : object, optional
        The parent object to which this initialization is attached
    """

    def __init__(self, parent=None) -> None:
        self.parent = parent

        # load config
        o_config = ConfigHandler(parent=self.parent)
        o_config.load()

    def all(self) -> None:
        """
        Initialize all GUI components.

        This method calls all individual initialization methods in sequence.
        """
        self.statusbar()
        self.widgets()
        self.tables()
        self.tabs()
        self.pyqtgraph()
        self.autonomous_reconstruction_data()

    def autonomous_reconstruction_data(self) -> None:
        """
        Load golden ratio angles for autonomous reconstruction.

        Reads angle data from CSV file and stores it in the parent object.
        """
        table = pd.read_csv(golden_ratio_file)
        self.parent.golden_ratio_angles = list(table["angles"])

    def tabs(self) -> None:
        """
        Initialize tab settings and visibility.

        Sets tab text, icons, and manages tab visibility. Removes tabs that should
        not be shown initially and disables certain UI components.
        """
        self.parent.ui.tabWidget.setTabText(0, TabNames.tab0)
        self.parent.ui.tabWidget.setTabIcon(0, QIcon(tab0_icon))
        self.parent.ui.tabWidget.setTabText(1, TabNames.tab1)
        self.parent.ui.tabWidget.setTabIcon(1, QIcon(tab1_icon))

        self.parent.tab2 = self.parent.ui.tabWidget.widget(2)
        self.parent.tab3 = self.parent.ui.tabWidget.widget(3)
        self.parent.tab4 = self.parent.ui.tabWidget.widget(4)
        for _ in np.arange(3):
            self.parent.ui.tabWidget.removeTab(2)
        self.parent.all_tabs_visible = False

        # disable the second part of the Autonomous reconstruction
        self.parent.ui.autonomous_reconstruction_toolBox.setItemEnabled(1, False)

    def tables(self) -> None:
        """
        Configure table layouts and column sizes.

        Sets the column sizes for various tables in the UI.
        """
        o_table = TableHandler(table_ui=self.parent.ui.open_beam_tableWidget)
        column_sizes = [600, 50]
        o_table.set_column_sizes(column_sizes=column_sizes)

        table_columns = [540, 80, 80, 80, 80, 100]
        o_table = TableHandler(table_ui=self.parent.ui.autonomous_projections_tableWidget)
        o_table.set_column_sizes(column_sizes=table_columns)

        recon_table_columns = [740, 80, 100]
        o_table = TableHandler(table_ui=self.parent.ui.autonomous_reconstructions_tableWidget)
        o_table.set_column_sizes(column_sizes=table_columns)

    def full_reset(self) -> None:
        """
        Reset the GUI to its initial state.

        Currently a placeholder method for future implementation.
        """
        pass

    def widgets(self) -> None:
        """
        Initialize and configure various widgets in the UI.

        Sets up icons, visibility states, and text for UI elements.
        """
        more_infos_icon = QIcon(more_infos)
        self.parent.ui.help_pushButton.setIcon(more_infos_icon)

        # message telling that the projections title has been modified because it's already there
        self.parent.ui.projections_title_message.setVisible(False)
        self.parent.ui.top_crop_widget.setEnabled(False)

        # 0 and 180 degrees label
        self.parent.ui.setup_0_180_label.setText("0\u00b0 and 180\u00b0 projections will be acquired automatically!")

        # add logo to background of tabs
        _file_path = os.path.dirname(__file__)
        background_file = os.path.abspath(os.path.join(_file_path, "../static/hyperctui_logo.png"))
        logo_icon = QPixmap(background_file)
        self.parent.ui.logo.setPixmap(logo_icon)

        self.parent.ui.autonomous_reconstruction_tabWidget.setVisible(False)

    def statusbar(self) -> None:
        """
        Initialize and configure the status bar.

        Sets up the progress bar in the status bar with appropriate sizing.
        """
        self.parent.eventProgress = QProgressBar(self.parent.ui.statusbar)
        self.parent.eventProgress.setMinimumSize(20, 14)
        self.parent.eventProgress.setMaximumSize(540, 100)
        self.parent.eventProgress.setVisible(False)
        self.parent.ui.statusbar.addPermanentWidget(self.parent.eventProgress)

    def pyqtgraph(self) -> None:
        """
        Initialize PyQtGraph visualization components.

        Sets up image viewers for crop tab and rotation center tab.
        """
        # crop tab
        self.parent.ui.crop_image_view = pg.ImageView(view=pg.PlotItem())
        self.parent.ui.crop_image_view.ui.roiBtn.hide()
        self.parent.ui.crop_image_view.ui.menuBtn.hide()
        image_layout = QVBoxLayout()
        image_layout.addWidget(self.parent.ui.crop_image_view)
        self.parent.ui.crop_widget.setLayout(image_layout)

        # # rotation center tab
        self.parent.rotation_center_image_view = pg.ImageView(view=pg.PlotItem())
        self.parent.rotation_center_image_view.ui.roiBtn.hide()
        self.parent.rotation_center_image_view.ui.menuBtn.hide()
        image_layout = QVBoxLayout()
        image_layout.addWidget(self.parent.rotation_center_image_view)
        self.parent.ui.rotation_center_widget.setLayout(image_layout)
