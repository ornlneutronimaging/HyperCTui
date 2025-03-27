#!/usr/bin/env python
"""
Utility functions for checking data types and comparing values.

This module provides a collection of helper functions for verifying data types,
checking for NaN values, and comparing numeric values with tolerance.

Functions:
    is_int: Check if a value can be converted to an integer.
    is_nan: Check if a value is NaN (Not a Number).
    is_float: Check if a value can be converted to a float.
    are_equal: Check if two numeric values are equal within a given tolerance.
"""

from typing import Any, TypeVar, Union

import numpy as np

NumericType = TypeVar("NumericType", int, float)


def is_int(value: Any) -> bool:
    """
    Check if the value can be converted to an integer.

    Parameters
    ----------
    value : Any
        The value to check.

    Returns
    -------
    bool
        True if the value can be converted to an integer, False otherwise.

    Examples
    --------
    >>> is_int(5)
    True
    >>> is_int("123")
    True
    >>> is_int("abc")
    False
    """
    is_number = True
    try:
        int(value)
    except ValueError:
        is_number = False

    return is_number


def is_nan(value: Any) -> bool:
    """
    Check if the value is NaN (Not a Number).

    Parameters
    ----------
    value : Any
        The value to check.

    Returns
    -------
    bool
        True if the value is NaN, False otherwise.

    Examples
    --------
    >>> is_nan(np.nan)
    True
    >>> is_nan(5)
    False
    """
    if np.isnan(value):
        return True

    return False


def is_float(value: Any) -> bool:
    """
    Check if the value can be converted to a float.

    Parameters
    ----------
    value : Any
        The value to check.

    Returns
    -------
    bool
        True if the value can be converted to a float, False otherwise.

    Examples
    --------
    >>> is_float(5.5)
    True
    >>> is_float("123.45")
    True
    >>> is_float("abc")
    False
    """
    is_number = True
    try:
        float(value)
    except ValueError:
        is_number = False

    return is_number


def are_equal(value1: Union[int, float], value2: Union[int, float], tolerance: float = 0.001) -> bool:
    """
    Check if two numeric values are equal within a given tolerance.

    Parameters
    ----------
    value1 : Union[int, float]
        The first value to compare.
    value2 : Union[int, float]
        The second value to compare.
    tolerance : float, optional
        The maximum allowed difference between the values, by default 0.001.

    Returns
    -------
    bool
        True if the absolute difference between the values is less than or equal
        to the tolerance, False otherwise.

    Examples
    --------
    >>> are_equal(1.0, 1.0005, tolerance=0.001)
    True
    >>> are_equal(1.0, 1.01, tolerance=0.001)
    False
    """
    if np.abs(value2 - value1) <= tolerance:
        return True
    return False
