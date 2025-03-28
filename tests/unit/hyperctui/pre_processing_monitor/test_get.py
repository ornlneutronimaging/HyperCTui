"""Unit tests for the pre_processing_monitor get module."""

import pytest

from hyperctui.pre_processing_monitor.get import Get


class TestGet:
    """Tests for the pre_processing_monitor Get class."""

    @pytest.fixture
    def get_instance(self) -> Get:
        """Create a Get instance for testing.

        Returns
        -------
        Get
            Instance of the Get class
        """
        return Get()

    def test_init(self, get_instance: Get) -> None:
        """Test that the Get instance initializes correctly.

        Parameters
        ----------
        get_instance : Get
            The Get instance
        """
        assert isinstance(get_instance, Get)
        # Add more assertion tests here
