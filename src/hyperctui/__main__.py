#!/usr/bin/env python3
"""
HyperCTui entry point module.

This module serves as the main entry point for the HyperCTui application.
When the package is executed directly (using `python -m hyperctui`), this
module initializes the application and launches the GUI interface.

Examples
--------
To run the application from the command line:
    $ python -m hyperctui [arguments]

Notes
-----
The module uses multiprocessing freeze support for compatibility with
packaged executables on Windows platforms.
"""

import multiprocessing
import sys

from hyperctui.hyperctui import main

__file__ = "asui"

# Run the GUI
multiprocessing.freeze_support()
sys.exit(main(sys.argv))  # type: List[str]
