import numpy as np


def is_int(value):
    is_number = True
    try:
        int(value)
    except ValueError:
        is_number = False

    return is_number


def is_nan(value):
    if np.isnan(value):
        return True

    return False


def is_float(value):
    is_number = True
    try:
        float(value)
    except ValueError:
        is_number = False

    return is_number


def are_equal(value1, value2, tolerance=0.001):
    if np.abs(value2 - value1) <= tolerance:
        return True
    return False
