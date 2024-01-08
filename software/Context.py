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
        """
        Init
        """
        # I/O pyserial device
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
        Resets game context to initial state
        """
        self.scores = [0 for i in range(config.PLAYERS)]

        self.clock = config.MAX_CLOCK
        self.prev_sec = 0
        self.state = GameState.IDLE
        self.player_buzzed_in = -1

    def reset_clock(self):
        """
        Resets game clock
        """
        self.clock = config.MAX_CLOCK
        self.prev_sec = 0
        self.state = GameState.IDLE
        self.player_buzzed_in = -1

    def restore(self):
        """
        Restores game context from file
        """
        if os.path.exists(config.STATE_FILE_NAME):
            with open(config.STATE_FILE_NAME, "rb") as file:
                saved_object = pickle.load(file)

            self.player_names = saved_object["player_names"]
            self.scores = saved_object["scores"]
            self.invert_display = saved_object["invert_display"]

    def save(self):
        """
        Saves game context to file
        """
        saved_object = {
            "player_names": self.player_names,
            "scores": self.scores,
            "invert_display": self.invert_display,
        }

        with open(config.STATE_FILE_NAME, "wb") as file:
            pickle.dump(saved_object, file)


    def load_font(self, shortname, filename, size):
        """loads fonts into the context

        Args:
            context (GameContext): Game Context
            shortname (str): name to reference the font by
            filename (str): font filename
            size (number): size of font to load
        """
        self.fonts[shortname] = pygame.font.Font(os.path.join("fonts", filename), size)

