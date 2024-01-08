"""
GameState.py
"""
from enum import Enum

# ENUMS to represent the game state
class GameState(Enum):
    """
    enum of possible game states

    Args:
        Enum (number): enum of possible game states
    """
    IDLE = 0
    RUNNING = 1
    BUZZIN = 2
    TIMEUP = 3
    INPUT = 4
    SETUP = 100
    SPLASH = 200
    HELP = 300
