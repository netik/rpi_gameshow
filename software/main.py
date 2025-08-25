#!/usr/bin/env python3

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

import game_config as config
from Context import Context
from hardware import setup_gpio, setup_serial
from render import init_game, render_all
from events import event_loop

def main():
    context = Context()
    context.restore()
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