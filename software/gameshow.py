#!/usr/bin/env python

"""
The Dirty Talk Game Show
A four player game show buzzer system with a large clock and score display.

This module implements the main game logic for a game show buzzer system that supports
multiple platforms (Raspberry Pi with GPIO, PC with serial, PC development mode).
It handles player input, scoring, timing, sound effects, and visual rendering.

Features:
- 4-player buzzer system with LED indicators
- Configurable countdown timer
- Score tracking and display
- Multiple display modes (windowed, borderless, fullscreen)
- Theme support with customizable colors
- Particle effects and animations
- Cross-platform support (RPi GPIO, PC Serial, PC Development)

Author: J. Adams <jna@retina.net>
Date: 2023
"""

import os
import sys
import math
import serial

import pygame
import pygame.gfxdraw
import ptext
import game_config as config

from particleutil import spawn_exploding_particles

from GameState import GameState
from Context import Context
from NameEditor import NameEditor
from drawutil import drawtext

DEBUG_SERIAL = False

if config.PLATFORM == "rpi":
    from RPi.GPIO import GPIO

# set working dir
if config.PLATFORM == "rpi":
    os.chdir("/home/pi/src/gameshow")

    # can't hurt.
    os.system("/usr/bin/amixer set PCM -- 1000")

    # force 1/8" output no matter what
    os.system("/usr/bin/amixer cset numid-3 1")


def serial_send(context, cmd):
    """
    Send a command to the serial port for hardware communication.
    
    This function sends commands to external hardware (like Arduino) via serial
    communication when running in pcserial mode. It's used for controlling LEDs
    and receiving button presses from external hardware.

    Args:
        context (Context): Current game context containing serial port information
        cmd (bytes): The command to send to the serial port

    Returns:
        bool: True if command was sent successfully, False if not in pcserial mode

    Note:
        Only works when PLATFORM is set to "pcserial". In other modes,
        this function returns False without sending anything.
    """
    if config.PLATFORM == "pcserial":
        context.serial_port.write(cmd)
        context.serial_port.flush()
        print("sent: " + str(cmd)) if DEBUG_SERIAL else None
        resp = context.serial_port.readline()
        print("recv: " + str(resp)) if DEBUG_SERIAL else None
        return True

    return False


def button_event(context, channel):
    """
    Register a button press event from a player buzzer.
    
    This function is called when a player presses their buzzer button. It maps
    the hardware channel (GPIO pin or serial input) to the correct player number
    and stores the information for processing in the main game loop.

    Args:
        context (Context): Current game context containing player and LED state
        channel (int): Hardware channel number (GPIO pin or serial input number)

    Note:
        - For GPIO mode: Maps channel to player using PLAYER_REVERSE_MAP
        - For serial mode: Assumes 1:1 mapping (channel-1 = player index)
        - The actual game state transition happens in the main event loop
    """
    # if it's serial it's a 1:1 map
    if context.serial_port and config.PLATFORM == "pcserial":
        context.player_buzzed_in = channel - 1
        return

    # if GPIO we have to map it back to the right player
    context.player_buzzed_in = config.PLAYER_REVERSE_MAP[channel]


def draw_leds(context):
    """
    Draw debug LED indicators on screen for development and testing.
    
    This function renders visual representations of the physical LED states
    on the screen when DEBUG_LEDS is enabled. It shows the current state
    of each player's LED indicator with colored circles.

    Args:
        context (Context): Current game context containing LED state information

    Note:
        - Only renders when config.DEBUG_LEDS is True
        - Shows LED states as colored circles (blue for on, dark gray for off)
        - Positioned on the left side of the screen for easy visibility
        - Useful for debugging when running without physical hardware
    """
    if config.DEBUG_LEDS is False:
        return

    xpos = 20
    ypos = 300
    drawtext(
        context, "robo36", "(debug) LEDs:", xpos, ypos - 50, (255, 255, 255), (0, 0, 0)
    )

    pygame.draw.rect(
        context.screen, (255, 255, 255), (xpos, ypos, config.PLAYERS * 85, 80), 2
    )

    for k in range(0, config.PLAYERS):
        if context.led_state[k]:
            color = (0, 0, 255)
        else:
            color = (20, 20, 20)

        pygame.draw.circle(
            context.screen, color, (xpos + 50, ypos + 40), 30, 0
        )  # filled
        xpos = xpos + 80


def set_led(context, led, new_state, exclusive=False):
    """
    Set an individual LED to on or off state.
    
    This function controls the physical LED indicators for each player.
    It handles the platform-specific implementation (GPIO, serial, or simulation)
    and updates the internal LED state tracking.

    Args:
        context (Context): Current game context containing LED state and hardware info
        led (int): LED number (0-3, corresponding to player 1-4)
        new_state (bool): True to turn LED on, False to turn off
        exclusive (bool, optional): If True, turn all other LEDs off first. Defaults to False.

    Note:
        - For GPIO mode: Directly controls Raspberry Pi GPIO pins
        - For serial mode: Sends LED commands via serial communication
        - For PC mode: Only updates internal state (no physical hardware)
        - When exclusive=True, all other LEDs are turned off before setting this one
    """
    # print("set_led(%d, %s)" % (led, state))

    if exclusive:
        set_all_leds(context, False)

    if config.PLATFORM == "rpi":
        GPIO.output(config.GPIO_LED_MAP[led], new_state)

    if config.PLATFORM == "pcserial":
        serial_send(context, b"LED %d %d\n" % ((led + 1), new_state))

    context.led_state[led] = new_state


def set_all_leds(context, new_state=False):
    """
    Set all LEDs to the same state simultaneously.
    
    This function provides a convenient way to control all player LEDs at once,
    commonly used for resetting all indicators or setting them to a known state.

    Args:
        context (Context): Current game context containing LED state information
        new_state (bool, optional): New state for all LEDs. Defaults to False (off).

    Note:
        - Calls set_led() for each player LED
        - Useful for game state transitions (e.g., clearing all LEDs when starting)
        - More efficient than calling set_led() multiple times
    """
    for k in range(0, config.PLAYERS):
        set_led(context, k, new_state, False)


def setup_serial(context, device):
    """
    Configure and initialize serial communication for external hardware.
    
    This function sets up serial communication with external hardware (typically
    Arduino) that handles physical buttons and LEDs. It establishes the connection,
    waits for the hardware to reset, and verifies communication is working.

    Args:
        context (Context): Game context to store the serial port object
        device (str): Serial port device name (e.g., "/dev/cu.usbserial*")

    Returns:
        serial.Serial: Configured serial port object, or False if setup fails

    Note:
        - Only works when PLATFORM is set to "pcserial"
        - Falls back to PC mode if serial device doesn't exist
        - Waits for hardware reset and "RESET OK" message
        - Flushes input/output buffers after successful connection
        - Baud rate is fixed at 115200 with 8N1 configuration
    """
    if config.PLATFORM != "pcserial":
        return False

    # does the device exist?
    if not os.path.exists(config.SERIAL_DEVICE):
        print("Serial device %s does not exist." % config.SERIAL_DEVICE)
        print("Falling back to PC mode.")
        config.PLATFORM="pc"
        return False

    context.serial_port = serial.Serial(
        device, 115200, bytesize=8, parity=serial.PARITY_NONE, stopbits=1, timeout=None
    )  # open serial port

    while not context.serial_port.isOpen():
        pass

    print("Serial port open")
    # sleep for board to reset as it resets on open
    print("Waiting for board to reset...")

    while True:
        line = context.serial_port.readline()
        print("recv: " + str(line)) if DEBUG_SERIAL else None
        if line == b"RESET OK\r\n":
            break

    print("Board reset")

    # flush the serial buffers at the start of the game
    if context.serial_port:
        context.serial_port.reset_input_buffer()
        context.serial_port.reset_output_buffer()

    return context.serial_port


def setup_gpio(context):
    """
    Setup Raspberry Pi GPIO pins for buttons and LEDs.
    
    This function configures the GPIO pins for player button inputs and LED outputs
    when running on Raspberry Pi hardware. It sets up button detection with
    debouncing and configures LED pins as outputs.

    Args:
        context (Context): Game context (not used in this function but required for consistency)

    Note:
        - Only runs when PLATFORM is set to "rpi"
        - Uses BCM pin numbering scheme
        - Button pins are configured as inputs with internal pull-up resistors
        - LED pins are configured as outputs
        - Button events are detected on falling edge (button press to ground)
        - Debounce time is set to 50ms to prevent false triggers
        - GPIO warnings are disabled to suppress pin 20 warnings
        - All LEDs are initialized to off state
    """
    if config.PLATFORM != "rpi":
        return

    # Setup the GPIOs as inputs with Pull Ups since the buttons are connected to GND
    GPIO.setmode(GPIO.BCM)
    for k in config.PLAYER_MAP:
        GPIO.setup(k, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(k, GPIO.FALLING, button_event, bouncetime=50)

    for k in config.GPIO_LED_MAP:
        GPIO.setup(k, GPIO.OUT)

    # I have no idea where these warnings are coming from on pin 20, let's
    # disable them. maybe it's complaining because pin 20 is MOSI/SPI but we're
    # not using that and everything works fine.
    GPIO.setwarnings(False)

    set_all_leds(context)


def clear_display(context):
    """
    Clear the entire display screen to black.
    
    This function fills the entire screen with black color, effectively
    clearing all previously drawn content. It's called at the beginning
    of each frame to ensure a clean drawing surface.

    Args:
        context (Context): Current game context containing the screen surface

    Note:
        - Uses pygame's fill() method with black color (0, 0, 0)
        - Called at the start of render_all() for each frame
        - Ensures no artifacts from previous frames remain visible
    """
    context.screen.fill((0, 0, 0))


def init_game(context):
    """
    Initialize the game display, fonts, and basic game state.
    
    This function sets up the Pygame display surface based on configuration,
    loads all required fonts, and prepares the game for rendering. It handles
    different display modes (windowed, borderless, fullscreen) and platform-specific
    initialization.

    Args:
        context (Context): Game context to initialize with display and font information

    Note:
        - Creates display surface based on DISPLAY_STYLE configuration
        - Supports multiple display modes: windowed, borderless, fullscreen
        - Can target specific display monitors using DISPLAY_ID
        - Hides the mouse cursor for cleaner game appearance
        - Loads multiple font sizes for different UI elements
        - Fonts are loaded from the fonts/ directory
        - Clears the display after initialization
        - Platform-specific working directory changes for Raspberry Pi
    """
    # set display ID here via display = 1 if needed.
    context.screen = None
    
    if config.DISPLAY_STYLE == "windowed":
        # uses default display
        context.screen = pygame.display.set_mode(
            (config.DISPLAY_WINDOW_HEIGHT, config.DISPLAY_WINDOW_WIDTH), pygame.SHOWN)
        context.screenInfo = pygame.display.Info()
    elif config.DISPLAY_STYLE == "borderless":
        # now let's see how big our screen is
        # and create a borderless window that's as big as the entire screen
        context.screen = pygame.display.set_mode(
            (0,0), 
            pygame.NOFRAME,
            display=config.DISPLAY_ID)
        context.screenInfo = pygame.display.Info()
    elif config.DISPLAY_STYLE == "fullscreen":
        context.screen = pygame.display.set_mode(
            (0, 0), 
            pygame.FULLSCREEN, 
            display=config.DISPLAY_ID)
        context.screenInfo = pygame.display.Info()
    
    print("Screen Info: ")
    print(context.screenInfo)

    # hide mouse
    pygame.mouse.set_visible(False)

    clear_display(context)

    # load fonts
    context.load_font("bebas40", "BebasKai-Regular.otf", 40)
    context.load_font("robo24", "RobotoCondensed-Bold.ttf", 24)
    context.load_font("robo36", "RobotoCondensed-Bold.ttf", 36)
    context.load_font("robo50", "RobotoCondensed-Bold.ttf", 50)
    context.load_font("robo90", "RobotoCondensed-Bold.ttf", 90)
    context.load_font("robo250", "RobotoCondensed-Bold.ttf", 250)


def handle_buzz_in(context):
    """
    Handle player buzz-in event and transition game state.
    
    This function is called when a player successfully buzzes in during gameplay.
    It plays appropriate sound effects, controls LED indicators, and spawns
    particle effects for visual feedback.

    Args:
        context (Context): Current game context containing player and game state

    Note:
        - Transitions game state to BUZZIN
        - Plays unique player sound if enabled, otherwise plays generic BUZZ sound
        - Turns on only the buzzing player's LED (exclusive mode)
        - Spawns particle explosion effect at screen center
        - Particle effects provide visual feedback for successful buzz-in
    """
    context.state = GameState.BUZZIN

    # play a sound
    if config.UNIQUE_PLAYER_SOUNDS:
        context.sound.play(f"PLAYER{context.player_buzzed_in + 1:d}")
    else:
        context.sound.play("BUZZ")

    # light only that player
    set_led(context, context.player_buzzed_in, True, True)

    # explode some particles
    #spawn_exploding_particles(
    #     context.screenInfo,
    #     context.particle_group,
    #     (
    #         (context.player_buzzed_in + 0.5) * context.screenInfo.current_w / config.PLAYERS,
    #         120
    #     ),
    #     500
    # )
    spawn_exploding_particles(
         context.screenInfo,
         context.particle_group,
         (
           context.screenInfo.current_w / 2,
             120
         ),
         500
     )
    

def draw_scores(context):
    """
    Draw player scores and names in the score display area.
    
    This function renders the player score display showing each player's name
    and current score. The display adapts to the invert_display setting,
    positioning scores either at the top or bottom of the screen.

    Args:
        context (Context): Current game context containing player scores and names

    Note:
        - Supports both normal and inverted display modes
        - Shows player names and scores in themed colors
        - Highlights the currently buzzing player with different colors
        - Draws separators between player areas
        - Uses theme colors for consistent visual appearance
        - Responsive layout that adapts to screen dimensions
    """
    i = 1

    if context.invert_display:
        top_y = 0
    else:
        top_y = context.screenInfo.current_h - 240

    while i < config.PLAYERS + 1:
        if context.invert_display:
            # background
            pygame.draw.rect(
                context.screen,
                config.THEME_COLORS["buzzed_in_bg"] if context.player_buzzed_in == (i - 1) else config.THEME_COLORS["player_area_bg"],
                (
                    (i - 1) * context.screenInfo.current_w / config.PLAYERS,
                    0,
                    (context.screenInfo.current_w / config.PLAYERS),
                    240,
                ),
            )

            # player name
            ptext.draw(
                context.player_names[i - 1],
                centerx=(context.screenInfo.current_w / 8 * ((i * 2) - 1)),
                centery=60,
                color=config.THEME_COLORS["buzzed_in_fg"] if context.player_buzzed_in == (i - 1) else config.THEME_COLORS["player_name_fg"],
                fontname="fonts/RobotoCondensed-Bold.ttf",
                fontsize=70,
                shadow=(1,1) if context.player_buzzed_in != (i - 1) else None 
            )

            # score
            ptext.draw(
                f"{context.scores[i - 1]:d}",
                centerx=(context.screenInfo.current_w / 8 * ((i * 2) - 1)),
                centery=170,
                color=config.THEME_COLORS["buzzed_in_fg"] if context.player_buzzed_in == (i - 1) else config.THEME_COLORS["player_score_fg"],
                fontname="fonts/RobotoCondensed-Bold.ttf",
                fontsize=120,
                shadow=(1,1) if context.player_buzzed_in != (i - 1) else None
            )

            # divider
            if i < config.PLAYERS:
                pygame.draw.line(
                    context.screen,
                    config.THEME_COLORS["separator"],
                    ((context.screenInfo.current_w / 4 * i - 2), 0),
                    ((context.screenInfo.current_w / 4 * i - 2), 240),
                    width=3,
                )
        else:
            # background
            pygame.draw.rect(
                context.screen,
                config.THEME_COLORS["buzzed_in_bg"] if context.player_buzzed_in == (i - 1) else config.THEME_COLORS["player_area_bg"],
                (
                    (i - 1) * context.screenInfo.current_w / 4,
                    top_y,
                    (context.screenInfo.current_w / 4),
                    context.screenInfo.current_h,
                ),
            )

            # player name
            ptext.draw(
                context.player_names[i - 1],
                centerx=(context.screenInfo.current_w / 8 * ((i * 2) - 1)),
                centery=top_y + 50,
                color=config.THEME_COLORS["buzzed_in_fg"] if context.player_buzzed_in == (i - 1) else config.THEME_COLORS["player_name_fg"],
                fontname="fonts/RobotoCondensed-Bold.ttf",
                fontsize=70,
                shadow=(1,1) if context.player_buzzed_in != (i - 1) else None
            )

            # score
            ptext.draw(
                f"{context.scores[i - 1]:d}",
                centerx=(context.screenInfo.current_w / 8 * ((i * 2) - 1)),
                centery=top_y + 170,
                color=config.THEME_COLORS["buzzed_in_fg"] if context.player_buzzed_in == (i - 1) else config.THEME_COLORS["player_score_fg"],
                fontname="fonts/RobotoCondensed-Bold.ttf",
                fontsize=120,
                shadow=(1,1) if context.player_buzzed_in != (i - 1) else None
            )

            # divider
            if i < config.PLAYERS:
                pygame.draw.line(
                    context.screen,
                    config.THEME_COLORS["separator"],
                    (
                        (context.screenInfo.current_w / 4 * i - 2),
                        top_y,
                    ),
                    (
                        (context.screenInfo.current_w / 4 * i - 2),
                        context.screenInfo.current_h,
                    ),
                    width=3,
                )

        i += 1

    if context.invert_display:
        # draw separator under scores
        pygame.draw.line(
            context.screen,
            config.THEME_COLORS["separator"],
            (0, 240),
            (context.screenInfo.current_w, 240),
            width=2,
        )
    else:
        # draw separateor above scores
        pygame.draw.line(
            context.screen,
            config.THEME_COLORS["separator"],
            (0, top_y),
            (context.screenInfo.current_w, top_y),
            width=2,
        )


def draw_title(context):
    """
    Draw the game title and logo.
    
    This function renders the game title text and logo images. The layout
    adapts to the invert_display setting, positioning elements either at
    the top or bottom of the screen.

    Args:
        context (Context): Current game context containing display information

    Note:
        - Loads and scales logo image based on LOGO_RESIZE_FACTOR
        - Supports both normal and inverted display modes
        - Logo is drawn on both left and right sides for symmetry
        - Title text is centered between the logos
        - Uses theme colors for consistent appearance
        - Only draws logo when DRAW_LOGO is enabled
    """
    img = pygame.image.load(config.LOGO).convert_alpha()
    line_padding = 60
    resized_img = pygame.transform.scale(img, (int(img.get_width() * config.LOGO_RESIZE_FACTOR), int(img.get_height() * config.LOGO_RESIZE_FACTOR)))

    if context.invert_display:
        # logo left and right on bottom
        if config.DRAW_LOGO:
            context.screen.blit(
                resized_img,
                (
                    line_padding,
                    context.screenInfo.current_h - resized_img.get_height() - line_padding,
                ),
            )
            context.screen.blit(
                resized_img,
                (
                    context.screenInfo.current_w - resized_img.get_width() - line_padding,
                    context.screenInfo.current_h - resized_img.get_height() - line_padding,
                ),
            )
        # title
        ptext.draw(
            config.TITLE,
            centerx=context.screenInfo.current_w / 2,
            # 35 here is a guess, given the font is 80 pixels(?) high
            centery=context.screenInfo.current_h - (resized_img.get_height() / 2) - line_padding,
            color=config.THEME_COLORS["title_text"],
            fontname="fonts/RobotoCondensed-Bold.ttf",
            fontsize=70,
            shadow=(1,1),
            scolor="black"
        )
    else:
        # logo left and right on top
        if config.DRAW_LOGO:
            context.screen.blit(resized_img, (line_padding, line_padding))
            context.screen.blit(
                resized_img,
                (   
                    context.screenInfo.current_w - resized_img.get_width() - line_padding,
                    line_padding,
                ),
            )

        ptext.draw(
            config.TITLE,
            centerx=context.screenInfo.current_w / 2,
            centery=line_padding + (resized_img.get_height() / 2),
            color=config.THEME_COLORS["title_text"],
            fontname="fonts/RobotoCondensed-Bold.ttf",
            fontsize=70,
            shadow=(1,1),
            scolor="black"
        )


def draw_splash(context):
    """
    Display splash screen and wait for user input.
    
    This function shows a splash screen image and pauses the game until
    the user presses any key. It's used for game startup and can be
    triggered manually during gameplay.

    Args:
        context (Context): Current game context containing display information

    Note:
        - Loads and displays splash image from config.SPLASH
        - Centers the image on screen
        - Blocks execution until any key is pressed
        - Transitions game state to SPLASH during display
        - Returns to IDLE state after keypress
        - Calls render_all() to refresh the display
        - Uses pygame.display.flip() for immediate visual feedback
    """
    print("Drawing splash screen and pausing. Press any key to resume.")
    context.state = GameState.SPLASH
    clear_display(context)

    img = pygame.image.load(config.SPLASH)
    context.screen.blit(
        img,
        (
            context.screenInfo.current_w / 2 - img.get_width() / 2,
            context.screenInfo.current_h / 2 - img.get_width() / 2,
        ),
    )
    pygame.display.flip()

    # block for keypress
    waiting = True
    while waiting:
        event = pygame.event.wait()
        if event.type == pygame.KEYDOWN:
            waiting = False

    pygame.display.flip()

    context.state = GameState.IDLE
    render_all(context)


def draw_help(context):
    """
    Display help screen with game controls and instructions.
    
    This function renders a modal help screen showing all available
    keyboard shortcuts and their functions. It pauses the game until
    the user dismisses it with any keypress.

    Args:
        context (Context): Current game context containing display information

    Note:
        - Creates a modal dialog box centered on screen
        - Lists all keyboard shortcuts with descriptions
        - Uses theme colors for consistent appearance
        - Blocks execution until any key is pressed
        - Transitions game state to HELP during display
        - Returns to IDLE state after dismissal
        - Calls render_all() to refresh the display
        - Help text includes scoring, timing, and game control shortcuts
    """
    helpstr = [
        {"key": "SPACE", "text": "Stop/Start clock"},
        {"key": "SHIFT-ESC", "text": "Quit"},
        {"key": "H or ?", "text": "HELP"},
        {"key": "1", "text": "+1 point Player 1"},
        {"key": "2", "text": "+1 point Player 2"},
        {"key": "3", "text": "+1 point Player 3"},
        {"key": "4", "text": "+1 point Player 4"},
        {"key": "Q", "text": "-1 point Player 1"},
        {"key": "W", "text": "-1 point Player 2"},
        {"key": "E", "text": "-1 point Player 3"},
        {"key": "R", "text": "-1 point Player 4"},
        {"key": "P", "text": "Clock: +5 seconds"},
        {"key": "L", "text": "Clock: -5 seconds"},
        {"key": "T", "text": 'Play a "time\'s up" sound'},
        {"key": "B", "text": "Play a buzzer sound"},
        {"key": "N", "text": "Name Players"},
        {"key": "I", "text": "Invert Display (toggle)"},
        {"key": "S", "text": "Draw Splash Screen"},
        {"key": "SHIFT-A", "text": "Reset game"},
        {"key": "SHIFT-Z", "text": "Reset Clock"},
    ]

    # draw a modal box at 85% of the screen. Stop the clock.
    context.state = GameState.HELP

    width = context.screenInfo.current_w * 0.30
    height = context.screenInfo.current_h * 0.75

    xtop = (context.screenInfo.current_w - width)  / 2
    ytop = (context.screenInfo.current_h - height)  / 2
    
    # inside box (fill)
    pygame.draw.rect(
        context.screen,
        config.THEME_COLORS['help_bg'],
        (
            xtop,
            ytop,
            width,
            height
        ),
    )

    # outside perimeter (line)
    pygame.draw.rect(
        context.screen,
        config.THEME_COLORS['help_border'],
        (
            xtop,
            ytop,
            width,
            height
        ),
        2,
    )

    xpos = xtop + 60
    ypos = ytop + 30

    # draw help text
    ptext.draw(
        "HELP",
        color=config.THEME_COLORS["help_title"],
        centerx=(xtop + (width/2)),
        centery=ypos,
        fontname="fonts/RobotoCondensed-Bold.ttf",
        fontsize=50,
    )

    ypos = ypos + 60

    for k in helpstr:
        drawtext(context, 
                 "robo24", 
                 k["key"], 
                 xpos, 
                 ypos,             
                 config.THEME_COLORS["help_fg"],
                 config.THEME_COLORS["help_bg"])

        drawtext(
            context,
            "robo24",
            k["text"],
            xpos + 200,
            ypos,
            config.THEME_COLORS["help_fg"],
            config.THEME_COLORS["help_bg"]
        )
        ypos = ypos + context.fonts["robo24"].get_height()

    ypos = ypos + context.fonts["robo24"].get_height()

    ptext.draw(
        "Hit any Key to continue",
        color=config.THEME_COLORS["help_title"],
        centerx=(xtop + (width/2)),
        centery=ypos,
        fontname="fonts/RobotoCondensed-Bold.ttf",
        fontsize=16,
    )

    pygame.display.flip()

    # block for keypress
    waiting = True
    while waiting:
        event = pygame.event.wait()
        if event.type == pygame.KEYDOWN:
            waiting = False

    pygame.display.flip()

    context.state = GameState.IDLE
    render_all(context)


def draw_state(context):
    """
    Draw the current game state text on screen.
    
    This function displays text indicating the current game state
    (e.g., "TIME'S UP!", "STOPPED", or nothing for running games).
    The text is positioned below the clock display.

    Args:
        context (Context): Current game context containing game state

    Note:
        - Shows different text based on current GameState
        - TIMEUP state displays "TIME'S UP!"
        - IDLE state displays "STOPPED"
        - RUNNING state shows no text
        - Uses theme colors for consistent appearance
        - Positioned below the clock display area
        - Text includes shadow effects for better visibility
    """
    statestr = ""

    if context.state == GameState.TIMEUP:
        statestr = "TIME'S UP!"

    if context.state == GameState.IDLE:
        statestr = "STOPPED"

    if context.state == GameState.RUNNING:
        statestr = ""

    message_y = context.screenInfo.current_h / 3 + 260

    ptext.draw(
        statestr,
        centerx=context.screenInfo.current_w / 2,
        centery=message_y,
        color=config.THEME_COLORS["state_text"],
        fontname="fonts/RobotoCondensed-Bold.ttf",
        fontsize=90,
        shadow=(1,1),
        scolor="black"
    )


def draw_clock(context):
    """
    Draw the large countdown clock in the center of the screen.
    
    This function renders the main game timer display showing minutes and seconds
    remaining. It also calls draw_state() to show the current game state below
    the clock. The clock is only displayed when CLOCK_ENABLED is True.

    Args:
        context (Context): Current game context containing clock and game state

    Note:
        - Converts milliseconds to minutes:seconds format
        - Centers the clock on screen
        - Uses large font (200pt) for visibility
        - Includes shadow effects for better readability
        - Only renders when CLOCK_ENABLED is True
        - Calls draw_state() to show game state below clock
        - Positioned in the upper third of the screen
    """
    minutes = math.floor(context.clock / 60000)
    sec = int((context.clock - (minutes * 60000)) / 1000)

    draw_state(context)

    if config.CLOCK_ENABLED == False:
        return

    # draw clock
    ptext.draw(
        f"{minutes:d}:{sec:02d}",
        centerx=context.screenInfo.current_w / 2,
        centery=context.screenInfo.current_h / 3 + 100,
        color=config.THEME_COLORS["clock_text"],
        fontname="fonts/RobotoCondensed-Bold.ttf",
        fontsize=200,
        shadow=(1,1),
        scolor="black"
    )


def draw_gamestate(context):
    """
    Draw game state-specific information on screen.
    
    This function renders information that changes based on the current
    game state. Currently, it shows the "buzzed in" message when a
    player has successfully buzzed in.

    Args:
        context (Context): Current game context containing player and game state

    Note:
        - Only renders content when state is BUZZIN
        - Shows player name with "Buzzed in!" message
        - Message position adapts to invert_display setting
        - Uses large font (150pt) for visibility
        - Includes shadow effects for better readability
        - Positioned either at top or bottom based on display orientation
    """
    if context.state == GameState.BUZZIN:
        # draw their name
        msg = f"{context.player_names[context.player_buzzed_in]} Buzzed in!"

        if context.invert_display:
            message_y = 125
        else:
            message_y = context.screenInfo.current_h - 125
      
        ptext.draw(
            msg,
            centerx=context.screenInfo.current_w / 2,
            centery=message_y,
            shadow=(1,1),
            color=config.THEME_COLORS["buzzed_in_message_fg"],
            fontname="fonts/RobotoCondensed-Bold.ttf",
            fontsize=150
        )


def draw_radial(context, color1, color2, width=40):
    """
    Draw a radial circus-tent like animated background.
    
    This function creates an animated radial background effect using
    triangular segments that rotate around a center point. It's used
    to create visual interest when RENDER_BACKGROUND is enabled.

    Args:
        context (Context): Current game context containing display information
        color1 (pygame.Color): First color for alternating segments
        color2 (pygame.Color): Second color for alternating segments
        width (int, optional): Width of each radial segment. Defaults to 40.

    Note:
        - Creates animated effect by rotating segments over time
        - Uses pygame.gfxdraw.filled_polygon for smooth rendering
        - Segments extend beyond screen boundaries for full coverage
        - Colors alternate between segments for visual variety
        - Animation speed is tied to pygame time for consistent motion
        - Creates a circus-tent or sunburst visual effect
    """
    center = [context.screenInfo.current_w/2, context.screenInfo.current_h+100]
    w = context.screenInfo.current_w
    h = context.screenInfo.current_h
    # radius = math.sqrt((w/2)**2 + (h/2)**2)  # maximum distance to the window boundary
    radius = w * 3
    i = 0
    color_flip=False
    while i < max(w, h):
        if color_flip:
            color = color1
        else:
            color = color2
        
        # gradient
        #color = (
        #    color1[0] * (1 - r) + color2[0] * r,
        #    color1[1] * (1 - r) + color2[1] * r,
        #    color1[2] * (1 - r) + color2[2] * r
        #)

        angle = 2 * math.pi * i / max(w, h) + pygame.time.get_ticks() / 100 / 360
        end_pos = (center[0] + radius * math.cos(angle), center[1] + radius * math.sin(angle))

        next_angle = 2 * math.pi * (i+width) / max(w, h) + pygame.time.get_ticks() / 100 / 360
        next_end_pos = (center[0] + radius * math.cos(next_angle + 0.1), center[1] + radius * math.sin(next_angle + 0.1))

        # draw a triangle that ends outside the viewport to get a sort of circus-tent look
        pygame.gfxdraw.filled_polygon(context.screen, [center, end_pos, next_end_pos], color)
        color_flip = not color_flip
        i = i + width


def render_background(context):
    """
    Render the animated background if enabled.
    
    This function conditionally renders the radial background effect
    based on the RENDER_BACKGROUND configuration setting.

    Args:
        context (Context): Current game context containing display information

    Note:
        - Only renders when config.RENDER_BACKGROUND is True
        - Uses theme colors bg_one and bg_two for the effect
        - Calls draw_radial() to create the animated background
        - Background provides visual interest without interfering with gameplay
    """
    if not config.RENDER_BACKGROUND:
        return

    color1 = config.THEME_COLORS["bg_one"]
    color2 = config.THEME_COLORS["bg_two"]    
    draw_radial(context, color1, color2)


def draw_particles(context):
    """
    Draw and update particle effects on screen.
    
    This function renders all active particle effects and updates their
    physics simulation. Particles are used for visual feedback during
    game events like player buzz-ins.

    Args:
        context (Context): Current game context containing particle group

    Note:
        - Draws all particles in the particle group
        - Updates particle physics with delta time
        - Particles are used for explosion effects and visual feedback
        - Delta time is calculated from pygame clock for smooth animation
        - Particle system is managed by the particleutil module
    """
    context.particle_group.draw(context.screen)

    # update
    dt = context.pyclock.tick() / 1000
    context.particle_group.update(dt)


def render_all(context):
    """
    Render the complete game screen for one frame.
    
    This function orchestrates the rendering of all game elements in
    the correct order. It clears the screen, draws background, UI elements,
    game state, particles, and debug information, then updates the display.

    Args:
        context (Context): Current game context containing all game state and display info

    Note:
        - Clears the screen at the start of each frame
        - Renders elements in back-to-front order: background, title, clock, scores, game state, particles, debug LEDs
        - Only shows scores when not in BUZZIN state
        - Debug LEDs are drawn last for visibility
        - Calls pygame.display.flip() once at the end for efficient rendering
        - This is the main rendering pipeline called each frame
    """
    clear_display(context)
    render_background(context)
    draw_title(context)
    draw_clock(context)
    if context.state != GameState.BUZZIN:
        draw_scores(context)

    draw_gamestate(context)

    draw_particles(context)
    # draw LED and debugging if config.PLATFORM is not rpi
    draw_leds(context)

    pygame.display.flip()


def handle_serial_input(context):
    """
    Process incoming serial data from external hardware.
    
    This function checks for incoming serial data and processes button press
    events from external hardware (typically Arduino). It converts serial
    messages into pygame events for integration with the main event system.

    Args:
        context (Context): Current game context containing serial port information

    Note:
        - Only processes data when serial port is available
        - Expects messages in format: "SWITCH <number> PRESSED"
        - Only processes button presses when game state is RUNNING
        - Converts serial events to pygame events for consistent handling
        - Button numbers are mapped to player indices
        - Debug output is controlled by DEBUG_SERIAL flag
    """
    # do we have serial data?
    if context.serial_port:
        if context.serial_port.inWaiting() > 0:
            received_data = context.serial_port.readline(context.serial_port.inWaiting())
            print("recv: " + str(received_data)) if DEBUG_SERIAL else None
            parts = received_data.split()
            if ( parts and len(parts) >= 3 ):
                if (
                    parts[0] == b"SWITCH"
                    and parts[2] == b"PRESSED"
                    and context.state == GameState.RUNNING
                ):
                    button_event(context, int(parts[1]))
                    ser_event = pygame.event.Event(int(parts[1]))
                    pygame.event.post(ser_event)
            

def handle_clock_event(context):
    """
    Process one tick of the game clock timer.
    
    This function handles the countdown timer logic, updating the clock
    value and triggering appropriate events when time runs out. It also
    manages LED attraction mode when the game is idle.

    Args:
        context (Context): Current game context containing clock and game state

    Note:
        - Decrements clock by CLOCK_STEP milliseconds each tick
        - Plays warning beep when 4 seconds or less remain
        - Triggers time's up event when clock reaches zero
        - Sets all LEDs on when time expires
        - Plays TIMESUP sound effect
        - Transitions game state to TIMEUP
        - In idle mode, cycles through LEDs for attraction effect
        - LED cycling creates a "walking light" pattern
    """
    if context.clock > 0:
        if context.state == GameState.RUNNING:
            if config.CLOCK_ENABLED:
                context.clock = context.clock - config.CLOCK_STEP
                minutes = math.floor(context.clock / 60000)
                sec = int((context.clock - (minutes * 60000)) / 1000)

                if context.prev_sec != sec:
                    context.prev_sec = sec
                    if context.prev_sec <= 4:
                        context.sound.play("BEEP")

                # handle timeout
                if context.clock == 0:
                    # play sound
                    set_all_leds(context, True)

                    context.sound.play("TIMESUP")
                    context.state = GameState.TIMEUP

    if context.state == GameState.IDLE:
        # in idle state, walk the LEDs.
        set_led(context, context.led_attract_cycle, True, True)

        context.led_attract_cycle += 1
        if context.led_attract_cycle > config.PLAYERS - 1:
            context.led_attract_cycle = 0


def handle_keyboard_event(context, event):
    """
    Process keyboard input events and execute corresponding actions.
    
    This function handles all keyboard input for the game, including
    player scoring, game control, sound effects, and system commands.
    It provides both MC (Master of Ceremonies) controls and player
    simulation controls.

    Args:
        context (Context): Current game context containing game state and scores
        event (pygame.event.Event): The keyboard event to process

    Note:
        - Any keypress exits BUZZIN state
        - Shift+Escape provides clean exit
        - Number keys 1-4 add points to respective players
        - Q,W,E,R keys subtract points from respective players
        - Space bar controls game state transitions
        - P/L keys adjust clock time (+/- 5 seconds)
        - B/T keys play sound effects
        - H key shows help screen
        - I key toggles display inversion
        - N key opens name editor
        - S key shows splash screen
        - Shift+A resets entire game
        - Shift+Z resets clock only
        - Keypad keys simulate player buttons in development mode
        - Z,X,C,V keys simulate player buttons in PC mode
    """
    # any keypress will take us out of buzzed in.
    if context.state == GameState.BUZZIN:
        context.state = GameState.IDLE

    # handle quit event (shift-escape)
    if event.key == pygame.K_ESCAPE and pygame.key.get_mods() & pygame.KMOD_SHIFT:
        print("\n\n Clean Exit: exiting at user request..   .")
        pygame.display.quit()
        pygame.quit()
        sys.exit()
        return
    
    # MC Controls
    #
    # 1,2,3,4 = Adds a point to that player 1,2,3,4
    # q,w,e,r = Deduct a point from player 1,2,3,4
    # shift-a = reset all
    # shift-z = reset round
    # (see help for the rest)
    #
    if event.key == pygame.K_1:
        context.scores[0] += 1
        context.save()

    if event.key == pygame.K_2:
        context.scores[1] += 1
        context.save()

    if event.key == pygame.K_3:
        context.scores[2] += 1
        context.save()

    if event.key == pygame.K_4:
        context.scores[3] += 1
        context.save()

    if event.key == pygame.K_q:
        context.scores[0] -= 1
        context.save()

    if event.key == pygame.K_w:
        context.scores[1] -= 1
        context.save()

    if event.key == pygame.K_e:
        context.scores[2] -= 1
        context.save()

    if event.key == pygame.K_r:
        context.scores[3] -= 1
        context.save()

    # if we are not running in debug mode we can emulate the buttons
    # with the keypad
    if config.PLATFORM != "rpi" and context.state == GameState.RUNNING:
        if event.key == pygame.K_KP1:
            button_event(context, config.PLAYER_MAP[0])

        if event.key == pygame.K_KP2:
            button_event(context, config.PLAYER_MAP[1])

        if event.key == pygame.K_KP3:
            button_event(context, config.PLAYER_MAP[2])

        if event.key == pygame.K_KP4:
            button_event(context, config.PLAYER_MAP[3])
            
    if config.PLATFORM == "pc" and context.state == GameState.RUNNING:
        if event.key == pygame.K_z:
            button_event(context, config.PLAYER_MAP[0])

        if event.key == pygame.K_x:
            button_event(context, config.PLAYER_MAP[1])

        if event.key == pygame.K_c:
            button_event(context, config.PLAYER_MAP[2])

        if event.key == pygame.K_v:
            button_event(context, config.PLAYER_MAP[3])

    # sounds
    if event.key == pygame.K_b:
        context.sound.play("BUZZ")

    if event.key == pygame.K_t:
        context.sound.play("TIMESUP")

    # clock changes
    if event.key == pygame.K_p:
        context.clock = context.clock + 5000

    if event.key == pygame.K_l:
        context.clock = context.clock - 5000
        context.clock = max(context.clock, 0)

    # reset all
    if event.key == pygame.K_a and pygame.key.get_mods() & pygame.KMOD_SHIFT:
        context.reset_game()
        draw_clock(context)
        context.save()

    # reset round
    if event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_SHIFT:
        context.reset_clock()
        draw_clock(context)

    if event.key == pygame.K_h:
        draw_help(context)

    if event.key == pygame.K_i:
        context.invert_display = not context.invert_display

    if event.key == pygame.K_n:
        modal = NameEditor(context)
        modal.run()

    if event.key == pygame.K_s and context.state == GameState.IDLE:
        draw_splash(context)

    # space -- transitions state
    if event.key == pygame.K_SPACE:
        set_all_leds(context, False)
        context.player_buzzed_in = -1
        if context.state == GameState.BUZZIN:
            context.sound.play("BEEP")
            context.state = GameState.RUNNING
        else:
            if context.state == GameState.IDLE:
                context.sound.play("BEEP")
                context.state = GameState.RUNNING
            else:
                if context.state == GameState.TIMEUP:
                    # you can either add time here, or if we
                    # are at zero we will start at zero
                    if context.clock == 0:
                        context.clock = config.MAX_CLOCK
                    context.state = GameState.RUNNING
                else:
                    context.state = GameState.IDLE


def event_loop(context):
    """
    Main game event loop that processes input and updates the game.
    
    This function contains the primary game loop that runs continuously
    while the game is active. It handles all input events, updates game
    state, and renders the screen at the configured frame rate.

    Args:
        context (Context): Current game context containing all game state and systems

    Note:
        - Sets up timer for clock events using PYGAME_CLOCKEVENT
        - Processes serial input for external hardware
        - Handles pygame events (quit, keyboard, custom timer)
        - Manages player buzz-in state transitions
        - Calls render_all() to update the display
        - Maintains consistent frame rate using pygame clock
        - Continues until running flag is set to 0
        - Handles both hardware and simulated input methods
    """
    # ------------------ main event loop ------------------
    running = 1
    pygame.time.set_timer(config.PYGAME_CLOCKEVENT, config.CLOCK_STEP)

    print("\nAll systems go! Game Running.\n")

    while running:
        # Handle Serial Input
        handle_serial_input(context)
        # Handle Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = 0

            if event.type == pygame.KEYDOWN:
                handle_keyboard_event(context, event)

            if event.type == config.PYGAME_CLOCKEVENT:
                handle_clock_event(context)

            if context.player_buzzed_in > -1:
                # now handle player buzz-in. The player number will have been set via
                # button_event()
                if context.state == GameState.RUNNING:
                    # advance to next state, let render figure it out
                    # make some blinking lights and sound
                    handle_buzz_in(context)
                    context.state = GameState.BUZZIN

        # the pattern here is to set the state of the game and then render
        # no rendering should happen before this line.
        render_all(context)
       
        context.pyclock.tick(config.FPS)


def main():
    """
    Main program entry point and initialization.
    
    This function initializes the game, sets up hardware connections,
    and starts the main event loop. It handles platform-specific setup
    and ensures all systems are ready before gameplay begins.

    Note:
        - Creates and restores game context from saved state
        - Sets up GPIO pins for Raspberry Pi mode
        - Configures serial communication for PC serial mode
        - Initializes display, fonts, and game systems
        - Renders initial screen state
        - Enters main event loop
        - Handles platform-specific initialization requirements
        - Restores previous game state if available
    """
    context = Context()
    context.restore()

    # I/O
    setup_gpio(context)

    if config.PLATFORM == "pcserial":
        context.serial_port = None
        if config.SERIAL_DEVICE:
            print("Setting up serial port %s" % config.SERIAL_DEVICE)
        context.serial_port = setup_serial(context, config.SERIAL_DEVICE)

    init_game(context)
    render_all(context)
    event_loop(context)


if __name__ == "__main__":
    main()
