"""Unit tests for the parent module."""

import pytest

from hyperctui.parent import Parent


class TestParent:
    """Tests for the Parent class."""

    @pytest.fixture
    def parent(self) -> Parent:
        """Create a Parent instance for testing.

        Returns
        -------
        Parent
            Instance of the Parent class
        """
        return Parent()

    def test_init(self, parent: Parent) -> None:
        """Test that the parent initializes correctly.

        Parameters
        ----------
        parent : Parent
            The parent instance
        """
        assert isinstance(parent, Parent)
        # Add more assertion tests here
