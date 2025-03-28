"""Unit tests for the setup_ob event_handler module."""

import pytest

from hyperctui.setup_ob.event_handler import EventHandler


class TestEventHandler:
    """Tests for the setup_ob EventHandler class."""

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
