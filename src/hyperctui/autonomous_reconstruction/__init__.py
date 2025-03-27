#!/usr/bin/env python
"""
Module containing constants and indices definitions for autonomous reconstruction.

This module defines column indices for various table views and configuration keys
used in the autonomous reconstruction process.
"""


class ColumnIndex:
    """
    Column indices for general table views.

    Attributes
    ----------
    enabled_state : int
        Index for the column containing enabled/disabled state.
    name : int
        Index for the column containing names.
    from_value : int
        Index for the column containing 'from' values.
    to_value : int
        Index for the column containing 'to' values.
    """

    enabled_state: int = 0
    name: int = 1
    from_value: int = 2
    to_value: int = 3


class ProjectionsTableColumnIndex:
    """
    Column indices for the projections table.

    Attributes
    ----------
    folder_name : int
        Index for the column containing folder names.
    log : int
        Index for the column containing log information.
    err : int
        Index for the column containing error information.
    meta : int
        Index for the column containing metadata.
    preview : int
        Index for the column containing previews.
    status : int
        Index for the column containing status information.
    """

    folder_name: int = 0
    log: int = 1
    err: int = 2
    meta: int = 3
    preview: int = 4
    status: int = 5


class ReconstructionTableColumnIndex:
    """
    Column indices for the reconstruction table.

    Attributes
    ----------
    folder_name : int
        Index for the column containing folder names.
    preview : int
        Index for the column containing previews.
    status : int
        Index for the column containing status information.
    """

    folder_name: int = 0
    preview: int = 1
    status: int = 2


class KeysTofReconstructionConfig:
    """
    String keys used for Time-of-Flight reconstruction configuration.

    Attributes
    ----------
    tof_reconstruction_folders : str
        Key for storing ToF reconstruction folders.
    process_id : str
        Key for storing process identification.
    """

    tof_reconstruction_folders: str = "tof reconstruction folders"
    process_id: str = "process id"
