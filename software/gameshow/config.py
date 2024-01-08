"""
Game configuration
"""

import pygame

# the number of players in the game
PLAYERS = 4

# Frames per second redraw rate
FPS = 60

# starting clock, in milliseconds
MAX_CLOCK = 60000  # in microseconds!
CLOCK_STEP = 1000  # mS
PYGAME_CLOCKEVENT = pygame.USEREVENT + 1

# which directory to look in for sounds.
SOUND_SET = 2

# main title on all screens
TITLE = "The Dirty Talk Game Show"
LOGO = "images/logo.jpg"
SPLASH = "images/dirtytalk-fs.jpg"

# save file name
STATE_FILE_NAME = "gamestate.pickle"

# GPIO Pinout (rPI)
PLAYER_MAP = [16, 17, 18, 19]
PLAYER_REVERSE_MAP = {16: 0, 17: 1, 18: 2, 19: 3}
GPIO_LED_MAP = [20, 21, 22, 23]

# Serial port device name
SERIAL_DEVICE = "/dev/cu.usbserial-21320"

# OFFLINE MODE if this is set to anything other than "rpi", we will never
# attempt to access the rPi GPIO pins and we will display a fake LED state on
# the screen

# In any mode, 1-4 on the keypad can be used to simulate buzzers
#
# PLATFORM = f "rpi"  # Running the entire game on a raspberry pi using the onboard GPIO
# PLATFORM = "pc"  # Running the game in dev mode on a computer, no GPIO
PLATFORM = "pc"  # Running on a computer with a serial connection to GPIO board (rev4)

# What screen do we run the game on?
DISPLAY_ID = 0

if PLATFORM == "pcserial":
    # if we're using serial, retain this screen as a console and show on
    # external display
    DISPLAY_ID = 1
else:
    DISPLAY_ID = 0