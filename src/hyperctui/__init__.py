"""
HyperCTui initialization module.

This module provides constants, helper functions, and configuration settings for the
HyperCT UI application. It includes path definitions, UI styling properties,
and class definitions to organize application structure and data.
"""

import os
from typing import Any, Dict, Union

from qtpy.uic import loadUi

try:
    from ._version import __version__  # noqa: F401
except ImportError:
    __version__ = "unknown"


__all__ = ["load_ui"]

root = os.path.dirname(os.path.realpath(__file__))

golden_ratio_file = os.path.join(os.path.dirname(__file__), os.path.join("static", "golden_angle.csv"))

refresh_image = os.path.join(root, "static/refresh.png")
refresh_large_image = os.path.join(root, "static/refresh_large.png")
more_infos = os.path.join(root, "static/more_infos.png")
tab0_icon = os.path.join(root, "static/tab0.png")
tab1_icon = os.path.join(root, "static/tab1.png")
tab2_icon = os.path.join(root, "static/tab2.png")
tab3_icon = os.path.join(root, "static/tab3.png")
tab4_icon = os.path.join(root, "static/tab4.png")

UI_TITLE = "hyperCT UI"

interact_me_style = "background-color: lime"
error_style = "background-color: red"
normal_style = ""

label_in_focus_style = "color: blue"
label_out_focus_style = ""

SOURCE_DETECTOR_DISTANCE = 19.855  # m, at SNAP
DETECTOR_OFFSET = 0  # micros

DEFAULT_EVALUATION_REGIONS: Dict[int, Dict[str, Union[str, int]]] = {
    0: {
        "name": "Region 1",
        "from": 20,
        "to": 30,
    },
    1: {
        "name": "Region 2",
        "from": 50,
        "to": 60,
    },
    2: {
        "name": "Region 3",
        "from": 200,
        "to": 230,
    },
}


# main window dimensions
class UiSizeSmall:
    """
    Small UI window size configuration.

    Attributes
    ----------
    width : int
        Width of the UI window in pixels.
    height : int
        Height of the UI window in pixels.
    """

    width = 800
    height = 300


class UiSizeLarge:
    """
    Large UI window size configuration.

    Attributes
    ----------
    width : int
        Width of the UI window in pixels.
    height : int
        Height of the UI window in pixels.
    """

    width = 800
    height = 800


class DataType:
    """
    Constants defining data types used in the application.

    Attributes
    ----------
    projection : str
        String identifier for projection data.
    ob : str
        String identifier for open beam data.
    """

    projection = "projections"
    ob = "ob"


class TabNames:
    """
    Names for the application tabs.

    Attributes
    ----------
    tab0 : str
        Open beam setup tab label.
    tab1 : str
        Initial projections tab label.
    tab2 : str
        Crop tab label.
    tab3 : str
        Rotation center tab label.
    tab4 : str
        Autonomous reconstruction tab label.
    tab5 : str
        Settings tab label.
    """

    tab0 = " - Setup the open beams"
    tab1 = " - Initialize first projections (0\u00b0 and 180\u00b0)"
    tab2 = " - Crop"
    tab3 = " - Rotation center"
    tab4 = " - Autonomous reconstruction"
    tab5 = " - Settings"


class ObTabNames:
    """
    Constants for the open beam tab indices.

    Attributes
    ----------
    new_obs : int
        Index for the new open beams tab.
    selected_obs : int
        Index for the selected open beams tab.
    """

    new_obs = 0
    selected_obs = 1


class EvaluationRegionKeys:
    """
    Keys used in evaluation region dictionaries.

    Attributes
    ----------
    state : str
        Key for checkbox state.
    from_value : str
        Key for start value.
    to_value : str
        Key for end value.
    id : str
        Key for horizontal line ID.
    name : str
        Key for region name.
    label_id : str
        Key for label ID.
    from_index : str
        Key for start file index.
    to_index : str
        Key for end file index.
    str_from_to_value : str
        Key for string representation of range.
    """

    state = "state of the checkbox"
    from_value = "from value"
    to_value = "to value"
    id = "id of the pg horizontal line"
    name = "name of the region"
    label_id = "id of the label naming the region"
    from_index = "from file index"
    to_index = "to file index"
    str_from_to_value = "string form of from -> to range"


def load_ui(ui_filename: str, baseinstance: Any) -> Any:
    """
    Load a Qt UI file and apply it to the specified base instance.

    Parameters
    ----------
    ui_filename : str
        Path to the UI file to load.
    baseinstance : Any
        Instance to which the UI should be applied.

    Returns
    -------
    Any
        The baseinstance with the UI applied.
    """
    return loadUi(ui_filename, baseinstance=baseinstance)
