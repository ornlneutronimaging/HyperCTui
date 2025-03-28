"""Unit tests for the pre_autonomous_monitor event_handler module."""

import pytest

from hyperctui.pre_autonomous_monitor.event_handler import EventHandler


class TestEventHandler:
    """Tests for the pre_autonomous_monitor EventHandler class."""

    @pytest.fixture
    def event_handler(self) -> EventHandler:
        """Create an EventHandler instance for testing.

        Returns
        -------
        EventHandler
            Instance of the EventHandler class
        """
        return EventHandler()

    def test_init(self, event_handler: EventHandler) -> None:
        """Test that the event handler initializes correctly.

        Parameters
        ----------
        event_handler : EventHandler
            The event handler instance
        """
        assert isinstance(event_handler, EventHandler)
        # Add more assertion tests here
