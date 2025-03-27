#!/usr/bin/env python
"""
Time utility functions for HyperCTui.

This module provides functions for formatting time in various ways
for use within the HyperCTui application.
"""

import datetime


def get_current_time_in_special_file_name_format() -> str:
    """
    Format the current date and time into a filename-friendly string.

    Returns:
        str: A formatted string representing the current time in the format:
             'MMm_DDd_YYYYy_HHh_MMmn'
             Example: '04m_07d_2022y_08h_06mn'
    """
    current_time = datetime.datetime.now().strftime("%mm_%dd_%Yy_%Hh_%Mmn")
    return current_time
