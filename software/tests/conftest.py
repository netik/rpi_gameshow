"""
Pytest configuration and common fixtures for the game show application tests.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from typing import Generator


@pytest.fixture(scope="session", autouse=True)
def setup_pygame():
    """Initialize pygame for testing and clean up afterward."""
    # Set environment variables to disable audio and use dummy video driver
    os.environ['SDL_AUDIODRIVER'] = 'dummy'
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    
    import pygame
    pygame.init()
    
    # Create a dummy display surface for tests that need it
    pygame.display.set_mode((800, 600))
    
    yield
    
    # Clean up
    pygame.quit()


@pytest.fixture
def temp_state_file() -> Generator[str, None, None]:
    """Create a temporary state file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.pkl', delete=False) as f:
        temp_file = f.name
    
    yield temp_file
    
    # Clean up
    if os.path.exists(temp_file):
        os.unlink(temp_file)


@pytest.fixture
def mock_serial_port():
    """Mock serial port for testing."""
    with patch('serial.Serial') as mock_serial:
        mock_serial.return_value.is_open = True
        mock_serial.return_value.read.return_value = b''
        mock_serial.return_value.write.return_value = 1
        yield mock_serial


@pytest.fixture
def mock_gpio():
    """Mock GPIO for testing."""
    with patch('RPi.GPIO') as mock_gpio:
        mock_gpio.setmode.return_value = None
        mock_gpio.setup.return_value = None
        mock_gpio.output.return_value = None
        mock_gpio.input.return_value = False
        mock_gpio.add_event_detect.return_value = None
        yield mock_gpio


@pytest.fixture
def sample_game_state():
    """Sample game state data for testing."""
    return {
        'state': 1,  # RUNNING
        'player_scores': [100, 200, 150, 75],
        'player_names': ['Player 1', 'Player 2', 'Player 3', 'Player 4'],
        'time_remaining': 30,
        'player_buzzed_in': 2
    }


@pytest.fixture
def mock_screen():
    """Mock pygame screen for testing."""
    with patch('pygame.display.set_mode') as mock_screen:
        mock_screen.return_value.get_size.return_value = (1920, 1080)
        mock_screen.return_value.fill.return_value = None
        mock_screen.return_value.blit.return_value = None
        yield mock_screen


@pytest.fixture
def mock_font():
    """Mock pygame font for testing."""
    with patch('pygame.font.Font') as mock_font:
        mock_font.return_value.render.return_value = Mock()
        mock_font.return_value.size.return_value = (100, 20)
        yield mock_font


@pytest.fixture
def mock_pygame_surface():
    """Mock pygame Surface for testing."""
    with patch('pygame.Surface') as mock_surface:
        mock_surface.return_value.convert_alpha.return_value = mock_surface.return_value
        mock_surface.return_value.set_colorkey.return_value = None
        mock_surface.return_value.get_rect.return_value = Mock()
        mock_surface.return_value.fill.return_value = None
        yield mock_surface


@pytest.fixture
def mock_pygame_draw():
    """Mock pygame draw functions for testing."""
    with patch('pygame.draw.circle') as mock_circle:
        mock_circle.return_value = None
        yield mock_circle


@pytest.fixture
def mock_pygame_time():
    """Mock pygame time functions for testing."""
    with patch('pygame.time.get_ticks') as mock_ticks:
        mock_ticks.return_value = 1000
        yield mock_ticks 