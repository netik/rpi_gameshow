"""
Game configuration settings for the Dirty Talk Game Show application.

This module contains all configuration constants and settings used throughout
the game, including display settings, GPIO pin mappings, sound settings,
and theme configurations.
"""

from typing import List, Dict, Optional, Any
import glob
import pygame

# =============================================================================
# Game Settings
# =============================================================================

# Number of players in the game
PLAYERS: int = 4

# Frames per second for the game loop
FPS: int = 60

# Clock settings
CLOCK_ENABLED: bool = True  # If false, the clock will not run or display
MAX_CLOCK: int = 60000      # Maximum clock time in milliseconds
CLOCK_STEP: int = 1000      # Clock update interval in milliseconds
PYGAME_CLOCKEVENT: int = pygame.USEREVENT + 1

# =============================================================================
# Sound Settings
# =============================================================================

# Directory containing sound files
SOUND_SET_DIR: str = "sounds/trek/wav"

# File extension for sound files (all other files will be ignored)
SOUND_EXT: str = ".wav"

# Whether to play unique sounds for each player
UNIQUE_PLAYER_SOUNDS: bool = False

# =============================================================================
# Branding and Assets
# =============================================================================

TITLE: str = "Dirty Talk Game Show"
DRAW_LOGO: bool = True
LOGO: str = "images/dirtytalk-logo-nobg.png"
SPLASH: str = "images/dirtytalk-logo-nobg.png"
LOGO_RESIZE_FACTOR: float = 0.5

# Save file for persistent game state
STATE_FILE_NAME: str = "gamestate.pickle"

# =============================================================================
# Hardware Configuration
# =============================================================================

# GPIO Pin mappings for Raspberry Pi
PLAYER_MAP: List[int] = [16, 17, 18, 19]  # GPIO pins for player buttons
PLAYER_REVERSE_MAP: Dict[int, int] = {16: 0, 17: 1, 18: 2, 19: 3}  # Reverse mapping
GPIO_LED_MAP: List[int] = [20, 21, 22, 23]  # GPIO pins for LED indicators

# Platform configuration
# Options: "rpi" (Raspberry Pi with GPIO), "pc" (development mode), "pcserial" (PC with serial)
PLATFORM: str = "pc"

# Serial port configuration (for pcserial mode)
serial_devices: List[str] = glob.glob("/dev/cu.usbserial*")
SERIAL_DEVICE: Optional[str] = None

print(f"Game show is starting for platform {PLATFORM} with serial devices: {serial_devices}")

if PLATFORM == "pcserial":
    if not serial_devices:
        raise FileNotFoundError("No serial devices found in /dev/cu.usbserial*")
    SERIAL_DEVICE = serial_devices[0]
    print(f"SERIAL_DEVICE set to: {SERIAL_DEVICE}")

# =============================================================================
# Display Settings
# =============================================================================

# Display mode: "windowed", "borderless", or "fullscreen"
DISPLAY_STYLE: str = "windowed"

# Display dimensions (minimum 1080p HDTV @ 1920x1080)
DISPLAY_WINDOW_HEIGHT: int = 1920
DISPLAY_WINDOW_WIDTH: int = 1080
DISPLAY_ID: int = 0

# Rendering options
RENDER_BACKGROUND: bool = False  # Whether to render animated background
DEBUG_LEDS: bool = False         # Whether to show LED state on screen

# =============================================================================
# Theme Configuration
# =============================================================================

# Dirty Talk Game Show Theme (DT_THEME)
# Dark theme with reds and pinks
DT_THEME: Dict[str, Any] = {
    "shadow_color": pygame.Color(0x00, 0x00, 0x00, 255),

    "player_score_fg": pygame.Color(0xff, 0xff, 0xff, 255),
    "player_name_fg": pygame.Color(0xff, 0xff, 0xff, 255),
    "player_area_bg": pygame.Color(0x41, 0x00, 0x0d, 255),

    # Colors shown when player buzzed in
    "buzzed_in_message_fg": pygame.Color(0xff, 0xff, 0xff, 255),
    "buzzed_in_bg": pygame.Color(0xfc, 0x79, 0x65, 255),
    "buzzed_in_fg": pygame.Color(0, 0, 0),

    "clock_text": pygame.Color(0xff, 0xff, 0xff, 255),
    "state_text": pygame.Color(0x72, 0x09, 0xb7, 255),
    "title_text": pygame.Color(0xff, 0xff, 0xff, 255),

    # Lines around scores
    "separator": pygame.Color(0xff, 0xff, 0xff, 255),

    # Used to draw radial background
    "bg_one": pygame.Color(0x51, 0x00, 0x2d, 255),
    "bg_two": pygame.Color(0x41, 0x00, 0x0d, 255),

    # Help screen colors
    "help_title": pygame.Color(0xfc, 0x79, 0x65, 255),
    "help_fg": pygame.Color(0xff, 0xff, 0xff, 255),
    "help_bg": pygame.Color(0x22, 0x22, 0x22, 255),
    "help_border": pygame.Color(0xdd, 0x00, 0x00, 255),

    # Name input box colors
    "name_input_modal_fg": pygame.Color(0xff, 0xff, 0xff, 255),
    "name_input_modal_bg": pygame.Color(210, 0, 100),
    "name_input_active_fg": pygame.Color(0xff, 0xff, 0x00, 255),
    "name_input_active_bg": pygame.Color(0x22, 0x22, 0x22, 255),
    "name_input_inactive_fg": pygame.Color(0xaa, 0xaa, 0x00, 255),
    "name_input_inactive_bg": pygame.Color(0x11, 0x11, 0x11, 255),
    "name_input_cursor": pygame.Color(0xff, 0xff, 0xff, 255),
}

# Bright theme with blues and purples
BRIGHT_THEME: Dict[str, Any] = {
    "shadow_color": pygame.Color(0x00, 0x00, 0x00, 255),

    "player_score_fg": pygame.Color(0xff, 0xff, 0xff, 255),
    "player_name_fg": pygame.Color(0xff, 0xff, 0xff, 255),
    "player_area_bg": pygame.Color(0x3a, 0x86, 0xff, 255),

    # Colors shown when player buzzed in
    "buzzed_in_message_fg": pygame.Color(0xff, 0xff, 0xff, 255),
    "buzzed_in_bg": pygame.Color(0xfb, 0x56, 0x07, 255),
    "buzzed_in_fg": pygame.Color(0, 0, 0),

    "clock_text": pygame.Color(0xff, 0xff, 0xff, 255),
    "state_text": pygame.Color(0xfb, 0x56, 0x07, 255),
    "title_text": pygame.Color(0xff, 0xff, 0xff, 255),

    # Lines around scores
    "separator": pygame.Color(0xff, 0xff, 0xff, 255),

    # Used to draw radial background
    "bg_one": pygame.Color(0x3a, 0x86, 0xff, 255),
    "bg_two": pygame.Color(0x83, 0x38, 0xec, 255),

    # Help screen colors
    "help_title": pygame.Color(0xfc, 0x79, 0x65, 255),
    "help_fg": pygame.Color(0xff, 0xff, 0xff, 255),
    "help_bg": pygame.Color(0x22, 0x22, 0x22, 255),
    "help_border": pygame.Color(0xdd, 0x00, 0x00, 255),

    # Name input box colors
    "name_input_modal_fg": pygame.Color(0xff, 0xff, 0xff, 255),
    "name_input_modal_bg": pygame.Color(210, 0, 100),
    "name_input_active_fg": pygame.Color(0xff, 0xbe, 0x0b, 255),
    "name_input_active_bg": pygame.Color(0x22, 0x22, 0x22, 255),
    "name_input_inactive_fg": pygame.Color(0xaa, 0xaa, 0x00, 255),
    "name_input_inactive_bg": pygame.Color(0x11, 0x11, 0x11, 255),
    "name_input_cursor": pygame.Color(0xff, 0xff, 0xff, 255),
}

# Classy theme with professional blues and grays
CLASSY_THEME: Dict[str, Any] = {
    "shadow_color": pygame.Color(0x00, 0x00, 0x00, 255),

    "player_score_fg": pygame.Color(0xff, 0xff, 0xff, 255),
    "player_name_fg": pygame.Color(0xff, 0xff, 0xff, 255),
    "player_area_bg": pygame.Color("#1d3557"),

    # Colors shown when player buzzed in
    "buzzed_in_message_fg": pygame.Color(0xff, 0xff, 0xff, 255),
    "buzzed_in_bg": pygame.Color(0xfb, 0x56, 0x07, 255),
    "buzzed_in_fg": pygame.Color(0, 0, 0),

    "clock_text": pygame.Color("#ced4da"),
    "state_text": pygame.Color("#e9ecef"),
    "title_text": pygame.Color("#e9ecef"),

    # Lines around scores
    "separator": pygame.Color("#ced4da"),

    # Used to draw radial background
    "bg_one": pygame.Color("#457b9d"),
    "bg_two": pygame.Color("#1d3557"),

    # Help screen colors
    "help_title": pygame.Color(0xfc, 0x79, 0x65, 255),
    "help_fg": pygame.Color(0xff, 0xff, 0xff, 255),
    "help_bg": pygame.Color(0x22, 0x22, 0x22, 255),
    "help_border": pygame.Color(0xdd, 0x00, 0x00, 255),

    # Name input box colors
    "name_input_modal_fg": pygame.Color(0xff, 0xff, 0xff, 255),
    "name_input_modal_bg": pygame.Color(210, 0, 100),
    "name_input_active_fg": pygame.Color(0xff, 0xbe, 0x0b, 255),
    "name_input_active_bg": pygame.Color(0x22, 0x22, 0x22, 255),
    "name_input_inactive_fg": pygame.Color(0xaa, 0xaa, 0x00, 255),
    "name_input_inactive_bg": pygame.Color(0x11, 0x11, 0x11, 255),
    "name_input_cursor": pygame.Color(0xff, 0xff, 0xff, 255),
}

# Currently active theme (change this to switch themes)
THEME_COLORS: Dict[str, Any] = CLASSY_THEME
