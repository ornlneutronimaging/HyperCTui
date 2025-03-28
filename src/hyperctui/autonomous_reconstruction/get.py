#!/usr/bin/env python
"""
This module provides functionality for retrieving data from the autonomous reconstruction tab.

It contains a Get class that extends the base Get class with specialized methods
for autonomous reconstruction data access.
"""

from hyperctui import EvaluationRegionKeys
from hyperctui.session import SessionKeys
from hyperctui.utilities.get import Get as TopGet


class Get(TopGet):
    """
    Class for retrieving data from the autonomous reconstruction tab.

    This class extends the base Get class with methods specific to accessing
    autonomous reconstruction data.
    """

    def get_nbr_tof_regions(self) -> int:
        """
        Get the number of active TOF regions in the autonomous reconstruction tab.

        Returns
        -------
        int
            The count of active TOF regions.
        """
        tof_regions_dict = self.parent.session_dict[SessionKeys.tof_regions]
        nbr_tof_regions = 0
        for _key in tof_regions_dict.keys():
            if tof_regions_dict[_key][EvaluationRegionKeys.state]:
                nbr_tof_regions += 1
        return nbr_tof_regions
