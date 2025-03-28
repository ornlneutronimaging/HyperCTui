"""Unit tests for the pre_processing_monitor monitor module."""

from typing import Any

import pytest
from qtpy.QtWidgets import QDialog

from hyperctui.pre_processing_monitor.monitor import Monitor


class TestMonitor:
    """Tests for the Monitor class."""

    @pytest.fixture
    def monitor(self, qtbot: Any) -> Monitor:
        """Create a Monitor instance for testing.

        Parameters
        ----------
        qtbot : Any
            The Qt robot for UI testing

        Returns
        -------
        Monitor
            Instance of the Monitor class
        """
        monitor_instance = Monitor()
        qtbot.addWidget(monitor_instance)
        return monitor_instance

    def test_init(self, monitor: Monitor) -> None:
        """Test that the monitor initializes correctly.

        Parameters
        ----------
        monitor : Monitor
            The monitor instance
        """
        assert isinstance(monitor, QDialog)
        # Add more assertion tests here
