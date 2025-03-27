#!/usr/bin/env python
"""
Configuration handling module for HyperCTui application.

This module provides functionality for loading, parsing, and managing configuration
settings from JSON files. It handles main application configuration, reconstruction
configurations, and sets up the logging system.
"""

import json
import logging
import os
from typing import Any, Optional

from hyperctui.utilities.get import Get


class ConfigHandler:
    """
    Handles configuration loading and management for the application.

    This class is responsible for loading configuration files, setting up
    logging, and managing reconstruction configurations.

    Parameters
    ----------
    parent : Any, optional
        The parent object that will store the loaded configurations.
    """

    def __init__(self, parent: Optional[Any] = None) -> None:
        self.parent = parent

    def load(self) -> None:
        """
        Load the main application configuration.

        Reads the configuration from the config.json file, sets up the
        home path, and initializes the logging system.

        Returns
        -------
        None
        """
        config_file_name = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
        with open(config_file_name) as f:
            config = json.load(f)
        self.parent.config = config

        for _homepath in config["homepath"]:
            if os.path.exists(_homepath):
                self.parent.homepath = _homepath
                break

        o_get = Get(parent=self.parent)
        log_file_name = o_get.get_log_file_name()
        logging.basicConfig(
            filename=log_file_name,
            filemode="a",
            format="[%(levelname)s] - %(asctime)s - %(message)s",
            level=logging.INFO,
        )
        logging.info("*** Starting a new session ***")
        # logging.info(f" Version: {versioneer.get_version()}")

    def load_reconstruction_config(self, file_name: Optional[str] = None) -> None:
        """
        Load reconstruction configuration from a JSON file.

        Parameters
        ----------
        file_name : str, optional
            Path to the reconstruction configuration file.
            If the file doesn't exist, the method returns without action.

        Returns
        -------
        None
        """
        if not os.path.exists(file_name):
            return

        with open(file_name) as f:
            config = json.load(f)

        self.parent.reconstruction_config = config
