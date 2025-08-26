"""
Context is a container for all the game's global variables.
"""

import os
import json
import pickle
from typing import Optional, Dict, List, Any

import pygame
import game_config as config

from Sound import Sound
from GameState import GameState

class Context:
    """
    Context is a container for all the game's global variables.
    """

    def __init__(self) -> None:
        # I/O pyserial device
        self.serial_port: Optional[Any] = None

        self.pyclock: pygame.time.Clock = pygame.time.Clock()
        self.clock: int = config.MAX_CLOCK
        self.prev_sec: int = 0
        self.fonts: Dict[str, pygame.font.Font] = {}
        self.colors: Dict[str, Any] = {}
        self.sound_library: Dict[str, Any] = {}
        self.screen: Optional[pygame.Surface] = None
        self.screen_info: Optional[pygame.display.Info] = None
        self.scores: List[int] = [0 for _ in range(config.PLAYERS)]
        self.led_state: List[bool] = [False for _ in range(config.PLAYERS)]
        self.player_names: List[str] = [f"Player {i+1}" for i in range(config.PLAYERS)]
        self.invert_display: bool = True

        # Track which LED is lit during attract mode
        self.led_attract_cycle: int = 0

        # game state
        self.player_buzzed_in: int = -1
        self.state: GameState = GameState.IDLE if config.CLOCK_ENABLED else GameState.RUNNING
        self.button_test: bool = False

        # load sound effects
        self.sound: Sound = Sound()

        # particles
        self.particle_group: pygame.sprite.Group = pygame.sprite.Group()

    def reset_game(self) -> None:
        """Resets game context to initial state."""
        self.scores = [0 for _ in range(config.PLAYERS)]
        self.clock = config.MAX_CLOCK
        self.prev_sec = 0
        self.state = GameState.IDLE
        self.player_buzzed_in = -1

    def reset_clock(self) -> None:
        """Resets game clock."""
        self.clock = config.MAX_CLOCK
        self.prev_sec = 0
        self.state = GameState.IDLE
        self.player_buzzed_in = -1

    def restore(self) -> None:
        """Restores game context from file."""
        if os.path.exists(config.STATE_FILE_NAME):
            with open(config.STATE_FILE_NAME, "rb") as file:
                saved_object = pickle.load(file)
            self.player_names = saved_object["player_names"]
            self.scores = saved_object["scores"]
            self.invert_display = saved_object["invert_display"]

    def save(self) -> None:
        """Saves game context to file."""
        saved_object = {
            "player_names": self.player_names,
            "scores": self.scores,
            "invert_display": self.invert_display,
        }
        with open(config.STATE_FILE_NAME, "wb") as file:
            pickle.dump(saved_object, file)

    def load_font(self, shortname: str, filename: str, size: int) -> None:
        """Loads fonts into the context.

        Args:
            shortname (str): name to reference the font by
            filename (str): font filename
            size (int): size of font to load
        """
        self.fonts[shortname] = pygame.font.Font(os.path.join("fonts", filename), size)

    def dump(self):
        """
        Dumps the current context state to the console. Handy for debugging.
        """
        print(json.dumps(self.__dict__, indent=4, default=str))
