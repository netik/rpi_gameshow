"""
events.py

Handles event processing for the gameshow application, including keyboard, serial, clock, and player buzz-in events.
"""

import sys
import math
import pygame
import game_config as config

from GameState import GameState
from particleutil import spawn_exploding_particles
from NameEditor import NameEditor

from render import draw_clock, draw_splash, draw_help, render_all
from hardware import set_led, set_all_leds

DEBUG_SERIAL = False

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
            print(f"recv: {str(received_data)}") if DEBUG_SERIAL else None
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
        print("\n\n Clean Exit: exiting at user request...")
        pygame.display.quit()
        pygame.quit()
        sys.exit()

    # MC Controls
    #
    # 1,2,3,4 = Adds a point to that player 1,2,3,4
    # q,w,e,r = Deduct a point from player 1,2,3,4
    # shift-a = reset all
    # shift-z = reset round
    # (see help for the rest)
    #
    # Player scoring - add points
    score_add_keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]
    for i, key in enumerate(score_add_keys):
        if event.key == key:
            context.scores[i] += 1
            context.save()
            break

    # Player scoring - subtract points
    score_subtract_keys = [pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_r]
    for i, key in enumerate(score_subtract_keys):
        if event.key == key:
            context.scores[i] -= 1
            context.save()
            break

    # Button emulation for non-RPi platforms
    if config.PLATFORM != "rpi" and context.state == GameState.RUNNING:
        # Keypad keys for development mode
        keypad_keys = [pygame.K_KP1, pygame.K_KP2, pygame.K_KP3, pygame.K_KP4]
        for i, key in enumerate(keypad_keys):
            if event.key == key:
                button_event(context, config.PLAYER_MAP[i])
                break

    # PC mode button emulation
    if config.PLATFORM == "pc" and context.state == GameState.RUNNING:
        # Z,X,C,V keys for PC mode
        pc_keys = [pygame.K_z, pygame.K_x, pygame.K_c, pygame.K_v]
        for i, key in enumerate(pc_keys):
            if event.key == key:
                button_event(context, config.PLAYER_MAP[i])
                break

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
    #     context.screen_info,
    #     context.particle_group,
    #     (
    #         (context.player_buzzed_in + 0.5) * context.screen_info.current_w / config.PLAYERS,
    #         120
    #     ),
    #     500
    # )
    spawn_exploding_particles(
         context.screen_info,
         context.particle_group,
         (
           context.screen_info.current_w / 2,
             120
         ),
         500
     )
   

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

