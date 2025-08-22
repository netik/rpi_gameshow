"""
Game configuration settings for the Dirty Talk Game Show application.

This module uses dynaconf to load configuration from settings.toml and provides
a compatible interface for the existing codebase.
"""

import glob
from dynaconf import Dynaconf
from typing import List, Dict, Optional, Any

# Conditional pygame import for when running outside of the game
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    # Create a mock pygame.Color class for configuration loading
    class MockColor:
        def __init__(self, *args):
            self.r = args[0] if len(args) > 0 else 0
            self.g = args[1] if len(args) > 1 else 0
            self.b = args[2] if len(args) > 2 else 0
            self.a = args[3] if len(args) > 3 else 255
    
    pygame = type('MockPygame', (), {'Color': MockColor, 'USEREVENT': 24})()

# Initialize dynaconf
settings = Dynaconf(
    settings_files=['settings.toml', 'development.toml'],
    environments=True,
    load_dotenv=True,
)

# =============================================================================
# Configuration Access Functions
# =============================================================================

def get_theme_colors() -> Dict[str, Any]:
    """Get the currently active theme colors, converting them to pygame Color objects."""
    theme_name = settings.get('THEME_COLORS', 'CLASSY_THEME')

    # Define themes in Python since TOML doesn't handle complex nested structures well
    themes = {
        'DT_THEME': {
            "shadow_color": pygame.Color(0x00, 0x00, 0x00, 255),
            "player_score_fg": pygame.Color(0xff, 0xff, 0xff, 255),
            "player_name_fg": pygame.Color(0xff, 0xff, 0xff, 255),
            "player_area_bg": pygame.Color(0x41, 0x00, 0x0d, 255),
            "buzzed_in_message_fg": pygame.Color(0xff, 0xff, 0xff, 255),
            "buzzed_in_bg": pygame.Color(0xfc, 0x79, 0x65, 255),
            "buzzed_in_fg": pygame.Color(0, 0, 0),
            "clock_text": pygame.Color(0xff, 0xff, 0xff, 255),
            "state_text": pygame.Color(0x72, 0x09, 0xb7, 255),
            "title_text": pygame.Color(0xff, 0xff, 0xff, 255),
            "separator": pygame.Color(0xff, 0xff, 0xff, 255),
            "bg_one": pygame.Color(0x51, 0x00, 0x2d, 255),
            "bg_two": pygame.Color(0x41, 0x00, 0x0d, 255),
            "help_title": pygame.Color(0xfc, 0x79, 0x65, 255),
            "help_fg": pygame.Color(0xff, 0xff, 0xff, 255),
            "help_bg": pygame.Color(0x22, 0x22, 0x22, 255),
            "help_border": pygame.Color(0xdd, 0x00, 0x00, 255),
            "name_input_modal_fg": pygame.Color(0xff, 0xff, 0xff, 255),
            "name_input_modal_bg": pygame.Color(210, 0, 100),
            "name_input_active_fg": pygame.Color(0xff, 0xff, 0x00, 255),
            "name_input_active_bg": pygame.Color(0x22, 0x22, 0x22, 255),
            "name_input_inactive_fg": pygame.Color(0xaa, 0xaa, 0x00, 255),
            "name_input_inactive_bg": pygame.Color(0x11, 0x11, 0x11, 255),
            "name_input_cursor": pygame.Color(0xff, 0xff, 0xff, 255),
        },
        'BRIGHT_THEME': {
            "shadow_color": pygame.Color(0x00, 0x00, 0x00, 255),
            "player_score_fg": pygame.Color(0xff, 0xff, 0xff, 255),
            "player_name_fg": pygame.Color(0xff, 0xff, 0xff, 255),
            "player_area_bg": pygame.Color(0x3a, 0x86, 0xff, 255),
            "buzzed_in_message_fg": pygame.Color(0xff, 0xff, 0xff, 255),
            "buzzed_in_bg": pygame.Color(0xfb, 0x56, 0x07, 255),
            "buzzed_in_fg": pygame.Color(0, 0, 0),
            "clock_text": pygame.Color(0xff, 0xff, 0xff, 255),
            "state_text": pygame.Color(0xfb, 0x56, 0x07, 255),
            "title_text": pygame.Color(0xff, 0xff, 0xff, 255),
            "separator": pygame.Color(0xff, 0xff, 0xff, 255),
            "bg_one": pygame.Color(0x3a, 0x86, 0xff, 255),
            "bg_two": pygame.Color(0x83, 0x38, 0xec, 255),
            "help_title": pygame.Color(0xfc, 0x79, 0x65, 255),
            "help_fg": pygame.Color(0xff, 0xff, 0xff, 255),
            "help_bg": pygame.Color(0x22, 0x22, 0x22, 255),
            "help_border": pygame.Color(0xdd, 0x00, 0x00, 255),
            "name_input_modal_fg": pygame.Color(0xff, 0xff, 0xff, 255),
            "name_input_modal_bg": pygame.Color(210, 0, 100),
            "name_input_active_fg": pygame.Color(0xff, 0xbe, 0x0b, 255),
            "name_input_active_bg": pygame.Color(0x22, 0x22, 0x22, 255),
            "name_input_inactive_fg": pygame.Color(0xaa, 0xaa, 0x00, 255),
            "name_input_inactive_bg": pygame.Color(0x11, 0x11, 0x11, 255),
            "name_input_cursor": pygame.Color(0xff, 0xff, 0xff, 255),
        },
        'CLASSY_THEME': {
            "shadow_color": pygame.Color(0x00, 0x00, 0x00, 255),
            "player_score_fg": pygame.Color(0xff, 0xff, 0xff, 255),
            "player_name_fg": pygame.Color(0xff, 0xff, 0xff, 255),
            "player_area_bg": pygame.Color("#1d3557"),
            "buzzed_in_message_fg": pygame.Color(0xff, 0xff, 0xff, 255),
            "buzzed_in_bg": pygame.Color(0xfb, 0x56, 0x07, 255),
            "buzzed_in_fg": pygame.Color(0, 0, 0),
            "clock_text": pygame.Color("#ced4da"),
            "state_text": pygame.Color("#e9ecef"),
            "title_text": pygame.Color("#e9ecef"),
            "separator": pygame.Color("#ced4da"),
            "bg_one": pygame.Color("#457b9d"),
            "bg_two": pygame.Color("#1d3557"),
            "help_title": pygame.Color(0xfc, 0x79, 0x65, 255),
            "help_fg": pygame.Color(0xff, 0xff, 0xff, 255),
            "help_bg": pygame.Color(0x22, 0x22, 0x22, 255),
            "help_border": pygame.Color(0xdd, 0x00, 0x00, 255),
            "name_input_modal_fg": pygame.Color(0xff, 0xff, 0xff, 255),
            "name_input_modal_bg": pygame.Color(210, 0, 100),
            "name_input_active_fg": pygame.Color(0xff, 0xbe, 0x0b, 255),
            "name_input_active_bg": pygame.Color(0x22, 0x22, 0x22, 255),
            "name_input_inactive_fg": pygame.Color(0xaa, 0xaa, 0x00, 255),
            "name_input_inactive_bg": pygame.Color(0x11, 0x11, 0x11, 255),
            "name_input_cursor": pygame.Color(0xff, 0xff, 0xff, 255),
        }
    }
    
    return themes.get(theme_name, themes['CLASSY_THEME'])

def get_player_reverse_map() -> Dict[int, int]:
    """Generate the reverse mapping for player GPIO pins."""
    player_map = settings.get('PLAYER_MAP', [16, 17, 18, 19])
    return {pin: index for index, pin in enumerate(player_map)}

# =============================================================================
# Configuration Properties (for backward compatibility)
# =============================================================================

# Game Settings
PLAYERS: int = settings.get('PLAYERS', 4)
FPS: int = settings.get('FPS', 60)
CLOCK_ENABLED: bool = settings.get('CLOCK_ENABLED', True)
MAX_CLOCK: int = settings.get('MAX_CLOCK', 60000)
CLOCK_STEP: int = settings.get('CLOCK_STEP', 1000)
PYGAME_CLOCKEVENT: int = settings.get('PYGAME_CLOCKEVENT', pygame.USEREVENT + 1)

# Sound Settings
SOUND_SET_DIR: str = settings.get('SOUND_SET_DIR', 'sounds/trek/wav')
SOUND_EXT: str = settings.get('SOUND_EXT', '.wav')
UNIQUE_PLAYER_SOUNDS: bool = settings.get('UNIQUE_PLAYER_SOUNDS', False)

# Branding and Assets
TITLE: str = settings.get('TITLE', 'Dirty Talk Game Show')
DRAW_LOGO: bool = settings.get('DRAW_LOGO', True)
LOGO: str = settings.get('LOGO', 'images/dirtytalk-logo-nobg.png')
SPLASH: str = settings.get('SPLASH', 'images/dirtytalk-logo-nobg.png')
LOGO_RESIZE_FACTOR: float = settings.get('LOGO_RESIZE_FACTOR', 0.5)
STATE_FILE_NAME: str = settings.get('STATE_FILE_NAME', 'gamestate.pickle')

# Hardware Configuration
PLAYER_MAP: List[int] = settings.get('PLAYER_MAP', [16, 17, 18, 19])
GPIO_LED_MAP: List[int] = settings.get('GPIO_LED_MAP', [20, 21, 22, 23])
PLATFORM: str = settings.get('PLATFORM', 'pcserial')

# Serial port configuration
serial_devices: List[str] = glob.glob("/dev/cu.usbserial*")
SERIAL_DEVICE: Optional[str] = settings.get('SERIAL_DEVICE', None)

# Auto-detect serial device if in pcserial mode
if PLATFORM == "pcserial":
    if not serial_devices:
        raise FileNotFoundError("No serial devices found in /dev/cu.usbserial*")
    SERIAL_DEVICE = serial_devices[0]
    print(f"Game show is starting for platform {PLATFORM} with serial devices: {serial_devices}")
    print(f"SERIAL_DEVICE set to: {SERIAL_DEVICE}")

# Display Settings
DISPLAY_STYLE: str = settings.get('DISPLAY_STYLE', 'fullscreen')
DISPLAY_WINDOW_HEIGHT: int = settings.get('DISPLAY_WINDOW_HEIGHT', 1920)
DISPLAY_WINDOW_WIDTH: int = settings.get('DISPLAY_WINDOW_WIDTH', 1080)
DISPLAY_ID: int = settings.get('DISPLAY_ID', 0)
RENDER_BACKGROUND: bool = settings.get('RENDER_BACKGROUND', False)
DEBUG_LEDS: bool = settings.get('DEBUG_LEDS', False)

# Theme Configuration
THEME_COLORS: Dict[str, Any] = get_theme_colors()

# Player reverse mapping
PLAYER_REVERSE_MAP: Dict[int, int] = get_player_reverse_map()

# =============================================================================
# Configuration Management Functions
# =============================================================================

def reload_config():
    """Reload configuration from files."""
    settings.reload()
    global THEME_COLORS, PLAYER_REVERSE_MAP
    THEME_COLORS = get_theme_colors()
    PLAYER_REVERSE_MAP = get_player_reverse_map()

def get_setting(key: str, default: Any = None) -> Any:
    """Get a configuration setting by key."""
    return settings.get(key, default)

def set_setting(key: str, value: Any):
    """Set a configuration setting."""
    settings.set(key, value)

def switch_theme(theme_name: str):
    """Switch to a different theme."""
    if theme_name in ['DT_THEME', 'BRIGHT_THEME', 'CLASSY_THEME']:
        settings.set('THEME_COLORS', theme_name)
        global THEME_COLORS
        THEME_COLORS = get_theme_colors()
    else:
        raise ValueError(f"Unknown theme: {theme_name}")

# Print startup information
print(f"Game show is starting for platform {PLATFORM}")
print(f"Active theme: {settings.get('THEME_COLORS', 'CLASSY_THEME')}")
