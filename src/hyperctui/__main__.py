#!/usr/bin/env python3

import multiprocessing
import sys

from hyperctui.hyperctui import main

__file__ = "asui"

# Run the GUI
multiprocessing.freeze_support()
sys.exit(main(sys.argv))
