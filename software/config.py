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
TITLE = ""
LOGO = "images/dirtytalk-logo-nobg.png"
SPLASH = "images/dirtytalk-logo-nobg.png"

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
#SERIAL_DEVICE = "/dev/cu.usbserial-120"
SERIAL_DEVICE = "/dev/cu.usbserial-2120"

# What screen do we run the game on?
DISPLAY_STYLE = "borderless"  # windowed, borderless, or fullscreen
DISPLAY_ID = 1

# Should we render the background and animate it?
RENDER_BACKGROUND=False

# Should we render the LED state on the screen
DEBUG_LEDS=False
