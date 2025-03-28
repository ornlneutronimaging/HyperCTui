"""Pytest configuration for HyperCTui tests."""

import os
import sys
from pathlib import Path

import pytest
from pytestqt.plugin import QtBot
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication, QDialog

# Configure Qt for headless operation before QApplication is created
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["QT_LOGGING_RULES"] = "*.debug=false"

# Add the src directory to the path so we can import hyperctui
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))


@pytest.fixture(scope="session")
def qapp():
    """Create a QApplication instance for the entire test session."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
        # Configure app for headless testing
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, False)
        app.setAttribute(Qt.AA_DisableHighDpiScaling, True)
    yield app


@pytest.fixture
def qtbot(qapp):
    """Fixture providing a QtBot instance for GUI testing."""
    bot = QtBot(qapp)
    return bot


@pytest.fixture
def temp_dir(tmpdir):
    """Provide a temporary directory for tests that need file operations."""
    return Path(tmpdir)


@pytest.fixture
def resource_dir():
    """Path to test resources directory."""
    resource_path = Path(__file__).parent / "resources"
    # Create resources directory if it doesn't exist
    if not resource_path.exists():
        os.makedirs(resource_path, exist_ok=True)
    return resource_path


@pytest.fixture
def mock_dialog_exec(monkeypatch):
    """Patch QDialog.exec_ and QDialog.exec to return QDialog.Accepted without showing dialog."""

    def mock_exec(*args, **kwargs):  # noqa ARG001
        return QDialog.Accepted

    monkeypatch.setattr(QDialog, "exec_", mock_exec)
    monkeypatch.setattr(QDialog, "exec", mock_exec)  # For Qt5 compatibility
    return mock_exec
