"""Regression tests for the make_tabs_visible state guard (audit M finding).

Hiding when already hidden used to remove the Settings tab (reachable when a
CropError fires during session load); showing twice duplicated tabs.
"""

from unittest.mock import MagicMock

import pytest

from hyperctui.utilities.widgets import Widgets

# every test needs the session QApplication (offscreen)
pytestmark = pytest.mark.usefixtures("qapp")


def _parent(all_tabs_visible: bool) -> MagicMock:
    parent = MagicMock()
    parent.all_tabs_visible = all_tabs_visible
    return parent


def test_hide_when_visible_removes_three_tabs():
    parent = _parent(True)
    Widgets(parent=parent).make_tabs_visible(is_visible=False)
    assert parent.ui.tabWidget.removeTab.call_count == 3
    assert parent.all_tabs_visible is False


def test_hide_when_already_hidden_is_a_noop():
    """the Settings-tab destruction bug: a second hide must not remove more tabs"""
    parent = _parent(False)
    Widgets(parent=parent).make_tabs_visible(is_visible=False)
    parent.ui.tabWidget.removeTab.assert_not_called()


def test_show_when_hidden_inserts_three_tabs():
    parent = _parent(False)
    Widgets(parent=parent).make_tabs_visible(is_visible=True)
    assert parent.ui.tabWidget.insertTab.call_count == 3
    assert parent.all_tabs_visible is True


def test_show_when_already_visible_is_a_noop():
    parent = _parent(True)
    Widgets(parent=parent).make_tabs_visible(is_visible=True)
    parent.ui.tabWidget.insertTab.assert_not_called()
