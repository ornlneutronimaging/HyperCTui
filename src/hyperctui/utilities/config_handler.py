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
import sys
from typing import Any, Optional

from loguru import logger

import hyperctui
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

        # Set up loguru logging
        o_get = Get(parent=self.parent)
        log_file_name = o_get.get_log_file_name()

        # Remove default handler and configure loguru
        logger.remove()
        logger.add(
            log_file_name,
            rotation="10 MB",
            format="[{level}] - {time:YYYY-MM-DD HH:mm:ss} - {name}:{function}:{line} - {message}",
            level="INFO",
            enqueue=True,
            backtrace=True,
            diagnose=True,
        )

        # Add stderr handler for console output with colored formatting
        logger.add(
            sys.stderr,
            level="INFO",
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",  # noqa: E501
            colorize=True,
        )

        # Intercept standard logging to loguru
        class InterceptHandler(logging.Handler):
            def emit(self, record):
                # Get corresponding Loguru level if it exists
                try:
                    level = logger.level(record.levelname).name
                except ValueError:
                    level = record.levelno

                # Find caller from where the logged message originated
                frame, depth = logging.currentframe(), 2
                while frame.f_code.co_filename == logging.__file__:
                    frame = frame.f_back
                    depth += 1

                logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

        # Configure standard logging to use loguru
        logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

        logger.info("*** Starting a new session ***")
        logger.info(f" Version: {hyperctui.__version__}")

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
