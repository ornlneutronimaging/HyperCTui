#!/usr/bin/env python
"""
Parent-child relationship management module.

This module provides classes for managing parent-child hierarchical relationships
between objects. It serves as a foundation for building tree-like structures
where objects need to reference their parent elements.

Classes
-------
Parent
    Base class that provides parent reference functionality.
"""

from typing import Any, Optional


class Parent:
    """
    A class that maintains a parent-child relationship.

    This class serves as a base for objects that need to maintain a reference
    to a parent object, enabling hierarchical structures.

    Attributes
    ----------
    parent : Optional[Any]
        The parent object reference. None if this object has no parent.
    """

    def __init__(self, parent: Optional[Any] = None) -> None:
        """
        Initialize a Parent object.

        Parameters
        ----------
        parent : Optional[Any], optional
            The parent object to reference. Default is None.
        """
        self.parent = parent
