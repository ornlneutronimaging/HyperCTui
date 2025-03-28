"""Unit tests for the commands_launcher module."""

import pytest

# Import the relevant classes/functions from commands_launcher
from hyperctui.commands_launcher import CommandLauncher


class TestCommandLauncher:
    """Tests for the CommandLauncher class."""

    @pytest.fixture
    def command_launcher(self) -> CommandLauncher:
        """Create a CommandLauncher instance for testing.

        Returns
        -------
        CommandLauncher
            Instance of the CommandLauncher class
        """
        return CommandLauncher()

    def test_init(self, command_launcher: CommandLauncher) -> None:
        """Test that the command launcher initializes correctly.

        Parameters
        ----------
        command_launcher : CommandLauncher
            The command launcher instance
        """
        assert isinstance(command_launcher, CommandLauncher)
        # Add more assertion tests here
