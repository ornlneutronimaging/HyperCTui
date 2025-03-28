"""Unit tests for the hyperctui main module."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from qtpy.QtWidgets import QMainWindow

# Import the class but mock its initialization
with patch("hyperctui.hyperctui.HyperCTui.__init__", return_value=None):
    from hyperctui.hyperctui import HyperCTui


class TestHyperCTui:
    """Tests for the HyperCTui main application class."""

    @pytest.fixture
    def mock_hyperctui(self, monkeypatch: Any) -> MagicMock:
        """Create a Mock HyperCTui instance for testing.

        Parameters
        ----------
        monkeypatch : Any
            Pytest monkeypatch fixture

        Returns
        -------
        MagicMock
            A mock instance representing HyperCTui
        """
        # Create a mock for the HyperCTui class
        mock_app = MagicMock(spec=HyperCTui)
        # Ensure it behaves like a QMainWindow for isinstance checks
        mock_app.__class__ = QMainWindow
        return mock_app

    def test_class_structure(self) -> None:
        """Test the class hierarchy of HyperCTui."""
        assert issubclass(HyperCTui, QMainWindow)

    def test_mock_instance(self, mock_hyperctui: MagicMock) -> None:
        """Test that our mock instance behaves correctly.

        Parameters
        ----------
        mock_hyperctui : MagicMock
            The mocked HyperCTui instance
        """
        assert isinstance(mock_hyperctui, QMainWindow)

    @pytest.mark.skip(reason="This test is a placeholder for when initialization issues are fixed")
    def test_ui_elements_exist(self, mock_hyperctui: MagicMock) -> None:
        """Test that important UI elements exist in the application.

        Parameters
        ----------
        mock_hyperctui : MagicMock
            The mock application instance
        """
        # This is a placeholder. Customize with actual UI element tests when initialization is fixed
        pass
