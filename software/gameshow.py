#!/usr/bin/env python
"""
The Dirty Talk Game Show
A four player game show buzzer system with a large clock and score display.


J. Adams <jna@retina.net>
2023
"""

import os
import sys
import math
import serial

import pygame
import pygame.gfxdraw
import ptext
import config

from particleutil import spawn_exploding_particles

from GameState import GameState
from Context import Context
from NameEditor import NameEditor
from drawutil import drawtext

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
    Send a command to the serial port

    Args:
        context (GameContext: current game context
        cmd (str): the command

    Returns:
        bool: True if sent, False if not
    """
    if config.PLATFORM == "pcserial":
        context.serial_port.write(cmd)
        context.serial_port.flush()
        print("sent: " + str(cmd))
        resp = context.serial_port.readline()
        print("recv: " + str(resp))
        return True

    return False


def button_event(context, channel):
    """
    Register a button press event, which we will handle this on the next clock
    tick
    """
    # if it's serial it's a 1:1 map
    if context.serial_port and config.PLATFORM == "pcserial":
        context.player_buzzed_in = channel - 1
        return

    # if GPIO we have to map it back to the right player
    context.player_buzzed_in = config.PLAYER_REVERSE_MAP[channel]


# display the LED state on the main screen for debugging
def draw_leds(context):
    """
    draws all LEDs on the screen for debugging
    """
    if config.PLATFORM != "pc":
        return

    xpos = 20
    ypos = 250
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


# Some hardware abstractions here so we can debug w/o the hardware
# LED abstraction
def set_led(context, led, new_state, exclusive=False):
    """Sets an LED on/off.

    Args:
        context (GameContext): _description_
        led (number): LED number
        new_state (bool): True for on, False for off
        exclusive (bool, optional):  If exclusive is true, turn all others off. Defaults to False.
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
    """Set all LEDs to the same state

    Args:
        context (_type_): current game context
        new_state (bool): new LED state (Defaults to False.)
    """
    for k in range(0, config.PLAYERS):
        set_led(context, k, new_state, False)


def setup_serial(context, device):
    """
    Configure the context with the serial port

    Args:
        context (GameContext): Game Context
        device (str): serial port name

    Returns:
        serial: pyserial serial port object or False if not configured
    """
    if config.PLATFORM != "pcserial":
        return False

    context.serial_port = serial.Serial(
        device, 115200, bytesize=8, parity=serial.PARITY_NONE, stopbits=1
    )  # open serial port

    while not context.serial_port.isOpen():
        pass

    print("Serial port open")
    # sleep for board to reset as it resets on open
    print("Waiting for board to reset...")

    while True:
        line = context.serial_port.readline()
        print("recv: " + str(line))
        if line == b"RESET OK\r\n":
            break

    print("Board reset")

    # flush the serial buffers at the start of the game
    if context.serial_port:
        context.serial_port.reset_input_buffer()
        context.serial_port.reset_output_buffer()

    return context.serial_port


def setup_gpio(context):
    """Setup rPI GPIO Pins

    Args:
        context (GameContext): Game Context
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
    clear screen

    Args:
        context (Context): current game context
    """
    context.screen.fill((0, 0, 0))


def init_game(context):
    """
    initializes the game and screen
    """
    # set display ID here via display = 1 if needed.
    context.screen = pygame.display.set_mode(
        (0, 0), pygame.FULLSCREEN, display=config.DISPLAY_ID
    )
    context.screenInfo = pygame.display.Info()
    print(context.screenInfo)

    # hide mouse
    pygame.mouse.set_visible(False)

    clear_display(context)

    # load fonts
    context.load_font("bebas40", "BebasKai-Regular.otf", 40)
    context.load_font("robo36", "RobotoCondensed-Bold.ttf", 36)
    context.load_font("robo50", "RobotoCondensed-Bold.ttf", 50)
    context.load_font("robo90", "RobotoCondensed-Bold.ttf", 90)
    context.load_font("robo250", "RobotoCondensed-Bold.ttf", 250)


def handle_buzz_in(context):
    # stop the clock by changing state.
    context.state = GameState.BUZZIN

    # play a sound
    context.sound.play("BUZZ")

    # light only that player
    set_led(context, context.player_buzzed_in, True, True)

    # explode some particles
    spawn_exploding_particles(
        context.screenInfo,
        context.particle_group,
        (
            (context.player_buzzed_in + 0.5) * context.screenInfo.current_w / config.PLAYERS,
            120
        ),
        500
    )

def draw_scores(context):
    i = 1

    while i < config.PLAYERS + 1:
        if context.invert_display:
            pygame.draw.rect(
                context.screen,
                context.colors["salmon"] if context.player_buzzed_in == (i - 1) else context.colors["bg_two"],
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
                color=context.colors["black"] if context.player_buzzed_in == (i - 1) else context.colors["lightgrey"],
                fontname="fonts/RobotoCondensed-Bold.ttf",
                fontsize=80,
                shadow=(1,1) if context.player_buzzed_in != (i - 1) else None
            )

            # score
            ptext.draw(
                f"{context.scores[i - 1]:d}",
                centerx=(context.screenInfo.current_w / 8 * ((i * 2) - 1)),
                centery=170,
                color=context.colors["black"] if context.player_buzzed_in == (i - 1) else context.colors["white"],
                fontname="fonts/RobotoCondensed-Bold.ttf",
                fontsize=120,
                shadow=(1,1) if context.player_buzzed_in != (i - 1) else None
            )

            # divider
            if i < config.PLAYERS:
                pygame.draw.line(
                    context.screen,
                    context.colors["grey"],
                    ((context.screenInfo.current_w / 4 * i - 2), 0),
                    ((context.screenInfo.current_w / 4 * i - 2), 240),
                    width=3,
                )

        else:
            pygame.draw.rect(
                context.screen,
                context.colors["salmon"] if context.player_buzzed_in == (i - 1) else context.colors["bg_two"],
                (
                    (i - 1) * context.screenInfo.current_w / 4,
                    context.screenInfo.current_h / 2 + 150,
                    (context.screenInfo.current_w / 4),
                    context.screenInfo.current_h,
                ),
            )

            ptext.draw(
                context.player_names[i - 1],
                centerx=(context.screenInfo.current_w / 8 * ((i * 2) - 1)),
                centery=context.screenInfo.current_h / 2 + 200,
                color=context.colors["black"] if context.player_buzzed_in == (i - 1) else context.colors["lightgrey"],
                fontname="fonts/RobotoCondensed-Bold.ttf",
                fontsize=80,
                shadow=(1,1) if context.player_buzzed_in != (i - 1) else None
            )

            ptext.draw(
                f"{context.scores[i - 1]:d}",
                centerx=(context.screenInfo.current_w / 8 * ((i * 2) - 1)),
                centery=(context.screenInfo.current_h / 2) + 350,
                color=context.colors["black"] if context.player_buzzed_in == (i - 1) else context.colors["white"],
                fontname="fonts/RobotoCondensed-Bold.ttf",
                fontsize=120,
                shadow=(1,1) if context.player_buzzed_in != (i - 1) else None
            )
            pygame.draw.line(
                context.screen,
                context.colors["grey"],
                (
                    (context.screenInfo.current_w / 4 * i - 2),
                    context.screenInfo.current_h / 2 + 150,
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
            context.colors["grey"],
            (0, 240),
            (context.screenInfo.current_w, 240),
            width=2,
        )


def draw_title(context):
    """
    Draw the game title

    Args:
        context (Context): current game context
    """
    img = pygame.image.load(config.LOGO).convert_alpha()
    line_padding = 60

    if context.invert_display:
        # logo left and right
        context.screen.blit(
            img,
            (
                line_padding,
                context.screenInfo.current_h - img.get_height() - line_padding,
            ),
        )
        context.screen.blit(
            img,
            (
                context.screenInfo.current_w - img.get_width() - line_padding,
                context.screenInfo.current_h - img.get_height() - line_padding,
            ),
        )
        # title
        ptext.draw(
            config.TITLE,
            centerx=context.screenInfo.current_w / 2 + 4,
            centery=context.screenInfo.current_h + 4
            - (img.get_height() / 2)
            - line_padding,
            color="white",
            fontname="fonts/RobotoCondensed-Bold.ttf",
            fontsize=80,
            shadow=(1,1),
            scolor="black"
        )
    else:
        context.screen.blit(img, (line_padding, line_padding))
        context.screen.blit(
            img,
            (
                context.screenInfo.current_w - img.get_width() - line_padding,
                line_padding,
            ),
        )

        ptext.draw(
            config.TITLE,
            centerx=context.screenInfo.current_w / 2,
            centery=50 + img.get_height() / 2,
            color="white",
            fontname="fonts/RobotoCondensed-Bold.ttf",
            fontsize=80,
            shadow=(1,1),
            scolor="black"
        )


def draw_splash(context):
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

    # black out that box
    width = context.screenInfo.current_w * 0.15  # 85% total
    height = 10

    # inside box
    pygame.draw.rect(
        context.screen,
        (60, 60, 60),
        (
            width,
            height,
            context.screenInfo.current_w - (width * 2),
            context.screenInfo.current_h - (height * 2),
        ),
    )
    # outside perimeter
    pygame.draw.rect(
        context.screen,
        (210, 0, 100),
        (
            width,
            height,
            context.screenInfo.current_w - (width * 2),
            context.screenInfo.current_h - (height * 2),
        ),
        2,
    )

    xpos = width + 60
    ypos = height + 30

    # draw help text
    ptext.draw(
        "HELP",
        centerx=context.screenInfo.current_w / 2,
        centery=ypos,
        fontname="fonts/RobotoCondensed-Bold.ttf",
        fontsize=50,
    )

    ypos = ypos + 60

    for k in helpstr:
        drawtext(context, "robo36", k["key"], xpos, ypos, (255, 255, 255), (60, 60, 60))
        drawtext(
            context,
            "robo36",
            k["text"],
            context.screenInfo.current_w / 2,
            ypos,
            (255, 255, 255),
            (60, 60, 60),
        )
        ypos = ypos + context.fonts["robo36"].get_height()

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
        color="purple",
        fontname="fonts/RobotoCondensed-Bold.ttf",
        fontsize=90,
        shadow=(1,1),
        scolor="black"
    )


def draw_clock(context):
    """draw the large clock in the center of the screen

    Args:
        context (Context): current game context
    """
    minutes = math.floor(context.clock / 60000)
    sec = int((context.clock - (minutes * 60000)) / 1000)

    # draw clock
    ptext.draw(
        f"{minutes:d}:{sec:02d}",
        centerx=context.screenInfo.current_w / 2,
        centery=context.screenInfo.current_h / 3 + 100,
        color="pink",
        fontname="fonts/RobotoCondensed-Bold.ttf",
        fontsize=250,
        shadow=(1,1),
        scolor="black"
    )

    draw_state(context)


def draw_gamestate(context):
    if context.state == GameState.BUZZIN:
        # draw their name
        msg = f"{context.player_names[context.player_buzzed_in]} Buzzed in!"

        message_y = 180
        if context.invert_display:
            message_y = 300

        ptext.draw(
            msg,
            centerx=context.screenInfo.current_w / 2,
            centery=message_y,
            shadow=(1,1),
            color=context.colors["dropbrown"],
            fontname="fonts/RobotoCondensed-Bold.ttf",
            fontsize=90
        )

def draw_radial(context, color1, color2, width=40):
    """
    Draws a radial circus-tent like background
    """
    center = [context.screenInfo.current_w/2, context.screenInfo.current_h+100]
    w = context.screenInfo.current_w
    h = context.screenInfo.current_h
    # radius = math.sqrt((w/2)**2 + (h/2)**2)  # maximum distance to the window boundary
    radius = w * 3
    i = 0
    color_flip=False
    while i < max(w, h):
        r = i / max(w, h)
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
    Render the background
    """
    if not config.RENDER_BACKGROUND:
        return

    color1 = context.colors["bg_one"]
    color2 = context.colors["bg_two"]    
    draw_radial(context, color1, color2)

def draw_particles(context):
    context.particle_group.draw(context.screen)

    # update
    dt = context.pyclock.tick() / 1000
    context.particle_group.update(dt)
    pygame.display.update()

def render_all(context):
    """Render the entire screen"""
    clear_display(context)
    render_background(context)
    draw_title(context)
    draw_clock(context)
    draw_scores(context)
    draw_gamestate(context)

    draw_particles(context)
    # draw LED and debugging if config.PLATFORM is not rpi
    draw_leds(context)

    pygame.display.flip()


def handle_serial_input(context):
    """
    process any incoming serial data

    Args:
        context (Context): current game context
    """

    # do we have serial data?
    if context.serial_port:
        if context.serial_port.inWaiting() > 0:
            received_data = context.serial_port.read(context.serial_port.inWaiting())
            print("recv: " + received_data)
            parts = received_data.split()
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
    process one tick of the clock

    Args:
        context (Context): current game context
    """
    if context.clock > 0:
        if context.state == GameState.RUNNING:
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
        context.led_attract_cycle += 1
        if context.led_attract_cycle > config.PLAYERS - 1:
            context.led_attract_cycle = 0
        set_led(context, context.led_attract_cycle, True, True)


def handle_keyboard_event(context, event):
    # handle quit event (shift-escape)
    if event.key == pygame.K_ESCAPE and pygame.key.get_mods() & pygame.KMOD_SHIFT:
        print("Exiting at user request...")
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
        draw_splash()

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
    main game event loop

    Args:
        context (_type_): _description_
    """
    # ------------------ main event loop ------------------
    running = 1
    pygame.time.set_timer(config.PYGAME_CLOCKEVENT, config.CLOCK_STEP)

    print("\nStarting main loop...\n")

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
        pygame.display.flip()
        context.pyclock.tick(config.FPS)


def main():
    """
    Main Program Start
    """
    context = Context()
    context.restore()

    # I/O
    setup_gpio(context)
    context.serial_port = setup_serial(context, config.SERIAL_DEVICE)

    init_game(context)
    render_all(context)
    event_loop(context)


if __name__ == "__main__":
    main()
