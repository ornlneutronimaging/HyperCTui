"""Unit tests for the pre_autonomous_monitor initialization module."""

import pytest

from hyperctui.pre_autonomous_monitor.initialization import Initialization


class TestInitialization:
    """Tests for the Initialization class."""

    @pytest.fixture
    def initialization(self) -> Initialization:
        """Create an Initialization instance for testing.

        Returns
        -------
        Initialization
            Instance of the Initialization class
        """
        return Initialization()

    def test_init(self, initialization: Initialization) -> None:
        """Test that the initialization instance initializes correctly.

        Parameters
        ----------
        initialization : Initialization
            The initialization instance
        """
        assert isinstance(initialization, Initialization)
        # Add more assertion tests here
