"""Regression tests for the OB-vs-sample folder classification (audit H4).

The previous bare 'ob' substring test misrouted any sample title containing
'ob' (Niobium, Cobalt, ...) into the OB list, leaving the sample list empty
and stalling the projections monitor forever.
"""

import pytest

from hyperctui.setup_ob.get import is_ob_folder


@pytest.mark.parametrize(
    "folder_name",
    ["OB_Niobium_rod_20260611", "OBs_cobalt_sample", "ob_run_0001", "obs_whatever"],
)
def test_ob_prefixes_classify_as_ob(folder_name):
    assert is_ob_folder(folder_name)


@pytest.mark.parametrize(
    "folder_name",
    [
        "Niobium_rod_20260611",  # previously misrouted: contains 'ob'
        "cobalt_sample_0002",  # previously misrouted: contains 'ob'
        "Strobe_test",  # previously misrouted: contains 'ob'
        "sample_run_0001",
    ],
)
def test_sample_titles_containing_ob_are_not_ob(folder_name):
    assert not is_ob_folder(folder_name)
