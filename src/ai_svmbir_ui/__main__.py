from .pyMBIR_UI import main

import multiprocessing
import sys

__file__ = "pyMBIR_UI"

# Run the GUI
#multiprocessing.freeze_support()
    
sys.exit(main(sys.argv))
