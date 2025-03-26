from hyperctui import EvaluationRegionKeys
from hyperctui.session import SessionKeys
from hyperctui.utilities.get import Get as TopGet


class Get(TopGet):
    def get_nbr_tof_regions(self):
        """
        returns the number of TOF selected in the autonomous reconstruction tab
        """
        tof_regions_dict = self.parent.session_dict[SessionKeys.tof_regions]
        nbr_tof_regions = 0
        for _key in tof_regions_dict.keys():
            if tof_regions_dict[_key][EvaluationRegionKeys.state]:
                nbr_tof_regions += 1
        return nbr_tof_regions
