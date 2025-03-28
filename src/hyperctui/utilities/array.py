#!/usr/bin/env python
"""Utility functions for array and list operations.

This module provides helper functions for common operations on arrays and lists,
such as finding the closest element to a value or formatting lists for display.

Functions
---------
get_nearest_index : Find the index of the closest value in an array
formatting_list_for_print : Convert a list to a formatted, bulleted string
"""

from typing import Any, List, Sequence

import numpy as np


def get_nearest_index(array: Sequence[float], value: float) -> int:
    """Find the index of the value in array that is closest to the specified value.

    Parameters
    ----------
    array : Sequence[float]
        Input array of numeric values
    value : float
        The value for which to find the closest match in the array

    Returns
    -------
    int
        Index of the array element closest to the specified value

    Examples
    --------
    >>> get_nearest_index([1.2, 3.5, 7.8], 3.0)
    1
    """
    idx = int((np.abs(np.array(array) - value)).argmin())
    return idx


def formatting_list_for_print(array: List[Any]) -> str:
    """Format a list into a bulleted string representation.

    Parameters
    ----------
    array : List[Any]
        Input list of elements to format

    Returns
    -------
    str
        Formatted string with each item on a new line, preceded by " - "

    Raises
    ------
    TypeError
        If the input is not a list

    Examples
    --------
    >>> formatting_list_for_print(["apple", "banana"])
    " - apple\\n - banana\\n"
    """
    if not array:
        return ""

    if not isinstance(array, list):
        raise TypeError("input should be a list!")

    str_array = [str(_item) for _item in array]
    formatted_string = ""
    for _str_item in str_array:
        formatted_string += f" - {_str_item}\n"

    return formatted_string
