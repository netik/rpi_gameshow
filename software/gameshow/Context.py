"""
GameContext is a container for all the game's global variables.
"""

# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
import os
import pickle
import config
import pygame

from Sound import Sound
from GameState import GameState

class Context:
    """
    Context is a container for all the game's global variables.
    """

    def __init__(self):
        # I/O
        self.serial_port = None

        # globals
        self.clock = config.MAX_CLOCK
        self.prev_sec = 0
        self.fonts = {}
        self.colors = {}
        self.sound_library = {}
        self.screen = None
        self.scores = [0 for i in range(config.PLAYERS)]
        self.led_state = [False for i in range(config.PLAYERS)]
        self.player_names = [f"Player {i+1}" for i in range(config.PLAYERS)]
        self.invert_display = True

        # Track which LED is lit during attract mode
        self.led_attract_cycle = 0

        # game state
        self.player_buzzed_in = -1
        self.state = GameState.IDLE

        # screen
        self.screen = None
        
        # sound effects
        self.sound = Sound()
        
        # init pallette
        self.init_palette()

    def init_palette(self):
        """
        Initialize the color palette
        """
        self.colors["black"] = pygame.Color(0, 0, 0)
        self.colors["white"] = pygame.Color(255, 255, 255)
        self.colors["grey"] = pygame.Color(164, 164, 164, 255)
        self.colors["blue"] = pygame.Color(0, 0, 200, 255)
        self.colors["green"] = pygame.Color(0, 200, 0, 255)
        self.colors["grey"] = pygame.Color(164, 164, 164, 255)
        self.colors["lightgrey"] = pygame.Color(200, 200, 200, 255)
        self.colors["pink"] = pygame.Color(255, 0, 255, 255)


    def reset_game(self):
        """
        resets game context to initial state
        """
        self.scores = [0 for i in range(config.PLAYERS)]

        self.clock = config.MAX_CLOCK
        self.prev_sec = 0
        self.state = GameState.IDLE
        self.player_buzzed_in = -1

    def reset_clock(self):
        """
        resets game clock
        """
        self.clock = config.MAX_CLOCK
        self.prev_sec = 0
        self.state = GameState.IDLE
        self.player_buzzed_in = -1
        
    def restore(self):
        """
        restores game context from file
        """
        if os.path.exists(config.STATEFILE):
            with open(config.STATEFILE, "rb") as file:
                saved_object = pickle.load(file)
    
            self.player_names = saved_object["player_names"]
            self.scores = saved_object["scores"]
            self.invert_display = saved_object["invert_display"]

    def save(self):
        saved_object = {
            "player_names": self.player_names,
            "scores": self.scores,
            "invert_display": self.invert_display,
        }

        with open(config.STATEFILE, "wb") as file:
            pickle.dump(saved_object, file)
