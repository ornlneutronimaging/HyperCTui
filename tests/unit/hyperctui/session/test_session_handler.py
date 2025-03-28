"""Unit tests for the session_handler module."""

import pytest

from hyperctui.session.session_handler import SessionHandler


class TestSessionHandler:
    """Tests for the SessionHandler class."""

    @pytest.fixture
    def session_handler(self) -> SessionHandler:
        """Create a SessionHandler instance for testing.

        Returns
        -------
        SessionHandler
            Instance of the SessionHandler class
        """
        return SessionHandler()

    def test_init(self, session_handler: SessionHandler) -> None:
        """Test that the session handler initializes correctly.

        Parameters
        ----------
        session_handler : SessionHandler
            The session handler instance
        """
        assert isinstance(session_handler, SessionHandler)
        # Add more assertion tests here
