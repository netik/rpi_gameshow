"""
Pytest configuration and common fixtures for the game show application tests.
"""

import os
import tempfile
import pytest
from unittest.mock import Mock, patch
import pygame

# Disable pygame display for testing
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'


@pytest.fixture(scope="session", autouse=True)
def setup_pygame():
    """Initialize pygame for testing."""
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def temp_state_file():
    """Create a temporary state file for testing."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pickle') as f:
        temp_file = f.name
    
    yield temp_file
    
    # Cleanup
    if os.path.exists(temp_file):
        os.unlink(temp_file)


@pytest.fixture
def mock_serial_port():
    """Mock serial port for testing."""
    mock_port = Mock()
    mock_port.write = Mock()
    mock_port.flush = Mock()
    mock_port.readline = Mock(return_value=b"OK\n")
    return mock_port


@pytest.fixture
def mock_gpio():
    """Mock GPIO for testing."""
    with patch('RPi.GPIO') as mock_gpio:
        yield mock_gpio


@pytest.fixture
def sample_game_state():
    """Sample game state data for testing."""
    return {
        "player_names": ["Alice", "Bob", "Charlie", "Diana"],
        "scores": [10, 15, 8, 12],
        "invert_display": True
    }


@pytest.fixture
def mock_screen():
    """Mock pygame screen for testing."""
    with patch('pygame.display.set_mode') as mock_set_mode:
        mock_screen = Mock()
        mock_screen.get_size.return_value = (1920, 1080)
        mock_set_mode.return_value = mock_screen
        yield mock_screen


@pytest.fixture
def mock_font():
    """Mock pygame font for testing."""
    mock_font = Mock()
    mock_font.render = Mock(return_value=Mock())
    mock_font.get_height = Mock(return_value=20)
    mock_font.size = Mock(return_value=(100, 20))
    return mock_font 