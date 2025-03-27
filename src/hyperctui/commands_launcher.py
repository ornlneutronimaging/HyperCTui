#!/usr/bin/env python
"""
Module for launching various commands in the HyperCTui application.

This module provides functionality to launch different acquisition and
reconstruction operations through the CommandLauncher class.
"""

from hyperctui.utilities.parent import Parent


class CommandLauncher(Parent):
    """
    Class for launching various command operations in the HyperCTui application.

    This class provides methods to trigger different acquisition and
    reconstruction processes within the application.

    Parameters
    ----------
    *args : tuple
        Arguments to pass to the parent class.
    **kwargs : dict
        Keyword arguments to pass to the parent class.

    Attributes
    ----------
    Inherits attributes from Parent class.
    """

    def launch_ob_first_projections_acquisition(self) -> None:
        """
        Launch open beam first projections acquisition process.

        This method handles the acquisition of open beam (OB) projections,
        including determining the number of OBs requested and setting an
        appropriate title for the operation.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # get the number of OBs requested (if any)

        # get the title

        pass

    def launch_preprocessing_autonomous_reconstruction(self) -> None:
        """
        Launch preprocessing and autonomous reconstruction process.

        This method sets up and executes the preprocessing and autonomous
        reconstruction with appropriate parameters including angles,
        evaluation regions, and TOF (Time of Flight) regions.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # list of angles
        # evaluation regions
        # TOF regions

        pass
