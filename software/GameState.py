"""
Game state enumeration for the game show application.

This module defines the various states that the game can be in,
which control the behavior and display of the game interface.
"""

from enum import Enum


class GameState(Enum):
    """
    Enumeration of possible game states.
    
    The game can be in various states that control what is displayed
    and how user input is handled.
    """
    IDLE = 0      # Game is idle, waiting to start
    RUNNING = 1   # Game is actively running with timer
    BUZZIN = 2    # A player has buzzed in
    TIMEUP = 3    # Time has run out
    INPUT = 4     # Waiting for text input
    SETUP = 100   # In setup/configuration mode
    SPLASH = 200  # Showing splash screen
    HELP = 300    # Showing help screen
