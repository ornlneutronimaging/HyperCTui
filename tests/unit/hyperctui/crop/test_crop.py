"""Unit tests for the crop module."""

import pytest

from hyperctui.crop.crop import Crop


class TestCrop:
    """Tests for the Crop class."""

    @pytest.fixture
    def crop(self) -> Crop:
        """Create a Crop instance for testing.

        Returns
        -------
        Crop
            Instance of the Crop class
        """
        return Crop()

    def test_init(self, crop: Crop) -> None:
        """Test that the crop instance initializes correctly.

        Parameters
        ----------
        crop : Crop
            The crop instance
        """
        assert isinstance(crop, Crop)
        # Add more assertion tests here
