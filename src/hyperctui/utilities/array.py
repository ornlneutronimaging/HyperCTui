import numpy as np


def get_nearest_index(array, value):
    idx = int((np.abs(np.array(array) - value)).argmin())
    return idx


def formatting_list_for_print(array):

    if not array:
        return ""

    if not (type(array) == list):
        raise TypeError("input should be a list!")

    str_array = [str(_item) for _item in array]
    formatted_string = ""
    for _str_item in str_array:
        formatted_string += f" - {_str_item}\n"

    return formatted_string
