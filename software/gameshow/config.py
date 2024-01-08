'''
Game configuration
'''

import pygame

# config
PLAYERS = 4
FPS = 30
MAX_CLOCK = 60000  # in microseconds!
CLOCK_STEP = 1000  # mS
PYGAME_CLOCKEVENT = pygame.USEREVENT + 1
SOUNDSET = 2
TITLE = "The Dirty Talk Game Show"
LOGO = "images/logo.jpg"
SPLASH = "images/dirtytalk-fs.jpg"
STATEFILE = "gamestate.pickle"

# GPIO Pinout
PLAYER_MAP = [16, 17, 18, 19]
PLAYER_REVERSE_MAP = {16: 0, 17: 1, 18: 2, 19: 3}
GPIO_LED_MAP = [20, 21, 22, 23]

# Serial port device name
SERIAL_DEVICE = "/dev/cu.usbserial-21320"

# OFFLINE MODE if this is set to anything other than "rpi", we will never
# attempt to access the rPi GPIO pins and we will display a fake LED state on
# the screen

# In any mode, 1-4 on the keypad can be used to simulate buzzers
# PLATFORM = "rpi"  # Running the entire game on a raspberry pi using the onboard GPIO
# PLATFORM = "pc"  # Running the game in dev mode on a computer, no GPIO
PLATFORM = "pc"  # Running on a computer with a serial connection to GPIO board (rev4)

# What screen do we run the game on?
DISPLAY_ID = 0

if PLATFORM == "pcserial":
    # if we're using serial,retain this screen as a console.
    DISPLAY_ID = 1
else:
    DISPLAY_ID = 0

