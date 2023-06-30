import numpy as np


def get_nearest_index(array, value):
    idx = int((np.abs(np.array(array) - value)).argmin())
    return idx
