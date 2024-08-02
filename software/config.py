"""
Game configuration
"""

import pygame

# the number of players in the game
PLAYERS = 4

# Frames per second redraw rate
FPS = 60

# starting clock, in milliseconds
CLOCK_ENABLED = True # if false, the clock will not run or display.
MAX_CLOCK = 60000  # in microseconds!
CLOCK_STEP = 1000  # mS
PYGAME_CLOCKEVENT = pygame.USEREVENT + 1

# which directory to look in for sounds.
SOUND_SET_DIR = "sounds/trek/wav"

# the extension of the sound files. all other files will be ignored
SOUND_EXT = ".wav"

# should we play a unique sound per player?
UNIQUE_PLAYER_SOUNDS = False

# Branding
TITLE = "Dirty Talk Game Show"
DRAW_LOGO = True
LOGO = "images/dirtytalk-logo-nobg.png"
SPLASH = "images/dirtytalk-logo-nobg.png"
#LOGO = "images/cupcake.png"
#SPLASH = "images/cake.png"
LOGO_RESIZE_FACTOR = 0.5

# save file name
STATE_FILE_NAME = "gamestate.pickle"

# GPIO Pinout (rPI)
PLAYER_MAP = [16, 17, 18, 19]
PLAYER_REVERSE_MAP = {16: 0, 17: 1, 18: 2, 19: 3}
GPIO_LED_MAP = [20, 21, 22, 23]

# OFFLINE MODE if this is set to anything other than "rpi", we will never
# attempt to access the rPi GPIO pins and we will display a fake LED state on
# the screen

# In any mode, 1-4 on the keypad can be used to simulate buzzers
#
# PLATFORM = "rpi"  # Running the entire game on a raspberry pi using the onboard GPIO
#PLATFORM = "pc"  # Running the game in dev mode on a computer, no GPIO
PLATFORM = "pcserial"  # Running on a computer with a serial connection to GPIO board (rev4)

# Serial port device name (if using serial)
#SERIAL_DEVICE = "/dev/cu.usbserial-21320"
SERIAL_DEVICE = "/dev/cu.usbserial-1320"
#SERIAL_DEVICE = "/dev/cu.usbserial-120"
#SERIAL_DEVICE = "/dev/cu.usbserial-2120"

# What screen do we run the game on?
DISPLAY_STYLE = "fullscreen"  # windowed, borderless, or fullscreen

# right now our minimum is 1080p HDTV @ 1920x1080. 
# Anything smaller breaks layout.
DISPLAY_WINDOW_HEIGHT = 1920
DISPLAY_WINDOW_WIDTH = 1080
DISPLAY_ID = 1

# Should we render the background and animate it?
RENDER_BACKGROUND=False

# Should we render the LED state on the screen
DEBUG_LEDS=False

# --- 
# themes
# ---
# This is a theme for the game. It's a dictionary of colors that are used
# throughout the game. You can change the colors here to customize the game.
# The colors are defined as pygame.Color objects.

# Dirty Talk Game Show Theme (DT_THEME)
# This is the color scheme for the Dirty Talk Game Show. It's a dark theme with
# reds and pinks.
DT_THEME = {
    # We've stoppped using color names here and rely on the theme.
    # saving this for later. 
    "shadow_color": pygame.Color(0x00, 0x00, 0x00, 255),

    "player_score_fg": pygame.Color(0xff, 0xff, 0xff, 255),
    "player_name_fg": pygame.Color(0xff, 0xff, 0xff, 255),
    "player_area_bg": pygame.Color(0x41, 0x00, 0x0d, 255),

    # these colors shown when player buzzed in
    "buzzed_in_message_fg": pygame.Color(0xff, 0xff, 0xff, 255),
    "buzzed_in_bg": pygame.Color(0xfc, 0x79, 0x65, 255),
    "buzzed_in_fg": pygame.Color(0, 0, 0),

    "clock_text": pygame.Color(0xff, 0xff, 0xff, 255),
    "state_text": pygame.Color(0x72, 0x09, 0xb7, 255),
    "title_text": pygame.Color(0xff, 0xff, 0xff, 255),

    # lines around scores
    "separator": pygame.Color(0xff, 0xff, 0xff, 255),

    # used to draw radial background
    "bg_one": pygame.Color(0x51, 0x00, 0x2d, 255),
    "bg_two": pygame.Color(0x41, 0x00, 0x0d, 255),

    # help
    "help_title": pygame.Color(0xfc, 0x79, 0x65, 255),
    "help_fg": pygame.Color(0xff, 0xff, 0xff, 255),
    "help_bg": pygame.Color(0x22,0x22,0x22, 255),
    "help_border": pygame.Color(0xdd, 0x00, 0x00, 255),

    # name input box
    "name_input_modal_fg": pygame.Color(0xff, 0xff, 0xff, 255),
    "name_input_modal_bg": pygame.Color(210,0,100),
    "name_input_active_fg": pygame.Color(0xff, 0xff, 0x00, 255),
    "name_input_active_bg": pygame.Color(0x22,0x22,0x22, 255),
    "name_input_inactive_fg": pygame.Color(0xaa, 0xaa, 0x00, 255),
    "name_input_inactive_bg": pygame.Color(0x11,0x11,0x11, 255),
    "name_input_cursor": pygame.Color(0xff, 0xff, 0xff, 255),

}

# bright theme
BRIGHT_THEME = {
    # We've stoppped using color names here and rely on the theme.
    # saving this for later. 
    "shadow_color": pygame.Color(0x00, 0x00, 0x00, 255),

    "player_score_fg": pygame.Color(0xff, 0xff, 0xff, 255),
    "player_name_fg": pygame.Color(0xff, 0xff, 0xff, 255),
    "player_area_bg": pygame.Color(0x3a, 0x86, 0xff, 255),

    # these colors shown when player buzzed in
    "buzzed_in_message_fg": pygame.Color(0xff, 0xff, 0xff, 255),
    "buzzed_in_bg": pygame.Color(0xfb, 0x56, 0x07, 255),
    "buzzed_in_fg": pygame.Color(0, 0, 0),

    # center text fb5607
    "clock_text": pygame.Color(0xff, 0xff, 0xff, 255),
    "state_text": pygame.Color(0xfb, 0x56, 0x07, 255),
    "title_text": pygame.Color(0xff, 0xff, 0xff, 255),

    # lines around scores
    "separator": pygame.Color(0xff, 0xff, 0xff, 255),

    # used to draw radial background 3a86ff 8338ec
    "bg_one": pygame.Color(0x3a, 0x86, 0xff, 255),
    "bg_two": pygame.Color(0x83, 0x38, 0xec, 255),

    # help
    "help_title": pygame.Color(0xfc, 0x79, 0x65, 255),
    "help_fg": pygame.Color(0xff, 0xff, 0xff, 255),
    "help_bg": pygame.Color(0x22,0x22,0x22, 255),
    "help_border": pygame.Color(0xdd, 0x00, 0x00, 255),

    # name input box
    "name_input_modal_fg": pygame.Color(0xff, 0xff, 0xff, 255),
    "name_input_modal_bg": pygame.Color(210,0,100),
    "name_input_active_fg": pygame.Color(0xff, 0xbe, 0x0b, 255),
    "name_input_active_bg": pygame.Color(0x22,0x22,0x22, 255),
    "name_input_inactive_fg": pygame.Color(0xaa, 0xaa, 0x00, 255),
    "name_input_inactive_bg": pygame.Color(0x11,0x11,0x11, 255),
    "name_input_cursor": pygame.Color(0xff, 0xff, 0xff, 255),
}

# bright theme
CLASSY_THEME = {
    # We've stoppped using color names here and rely on the theme.
    # saving this for later. 
    "shadow_color": pygame.Color(0x00, 0x00, 0x00, 255),

    "player_score_fg": pygame.Color(0xff, 0xff, 0xff, 255),
    "player_name_fg": pygame.Color(0xff, 0xff, 0xff, 255),
    "player_area_bg": pygame.Color("#1d3557"),

    # these colors shown when player buzzed in
    "buzzed_in_message_fg": pygame.Color(0xff, 0xff, 0xff, 255),
    "buzzed_in_bg": pygame.Color(0xfb, 0x56, 0x07, 255),
    "buzzed_in_fg": pygame.Color(0, 0, 0),

    # center text fb5607
    "clock_text": pygame.Color("#ced4da"),
    "state_text": pygame.Color("#e9ecef"),
    "title_text": pygame.Color("#e9ecef"),

    # lines around scores
    "separator": pygame.Color("#ced4da"),

    # used to draw radial background
    "bg_one": pygame.Color("#457b9d"),
    "bg_two": pygame.Color("#1d3557"),

    # help
    "help_title": pygame.Color(0xfc, 0x79, 0x65, 255),
    "help_fg": pygame.Color(0xff, 0xff, 0xff, 255),
    "help_bg": pygame.Color(0x22,0x22,0x22, 255),
    "help_border": pygame.Color(0xdd, 0x00, 0x00, 255),

    # name input box
    "name_input_modal_fg": pygame.Color(0xff, 0xff, 0xff, 255),
    "name_input_modal_bg": pygame.Color(210,0,100),
    "name_input_active_fg": pygame.Color(0xff, 0xbe, 0x0b, 255),
    "name_input_active_bg": pygame.Color(0x22,0x22,0x22, 255),
    "name_input_inactive_fg": pygame.Color(0xaa, 0xaa, 0x00, 255),
    "name_input_inactive_bg": pygame.Color(0x11,0x11,0x11, 255),
    "name_input_cursor": pygame.Color(0xff, 0xff, 0xff, 255),
}

# select a theme here
THEME_COLORS=CLASSY_THEME
