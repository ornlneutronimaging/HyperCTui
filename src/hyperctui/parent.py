#!/usr/bin/env python
"""
Parent module providing base class functionality for hierarchical components.

This module defines the Parent class which implements a parent-child
relationship structure used throughout the application.
"""

from typing import Optional


class Parent:
    """
    A base class that implements parent-child relationship functionality.

    This class serves as a foundation for components that need to maintain
    hierarchical relationships.

    Parameters
    ----------
    parent : Parent, optional
        The parent object to which this instance belongs
    """

    def __init__(self, parent: Optional["Parent"] = None) -> None:
        """
        Initialize a Parent instance.

        Parameters
        ----------
        parent : Parent, optional
            The parent object to which this instance belongs. Default is None.
        """
        self.parent = parent
