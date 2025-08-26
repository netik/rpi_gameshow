"""
Sound management system for the game show application.

This module provides a sound class that handles loading and playing
sound effects used throughout the game.
"""

import os
import sys
from typing import Dict
import pygame
import game_config as config

# Required sound files that must be present
REQUIRED_SOUNDS = [
    "BEEP",
    "BUZZ",
    "TIMESUP",
    "PLAYER1",
    "PLAYER2",
    "PLAYER3",
    "PLAYER4",
    "INVALID",
]
TEST_SOUNDS = ["ONE", "TWO", "THREE", "FOUR"]


class Sound:
    """
    Sound management class for all sound operations.

    This class handles loading sound files from the configured directory
    and provides methods to play them during gameplay.
    """

    def __init__(self) -> None:
        """Initialize the sound system and load all sound files."""
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()
        pygame.init()
        self.load_sounds()

    def play(self, sound_name: str) -> None:
        """
        Play a sound by name.

        Args:
            sound_name: Name of the sound to play (without extension)
        """
        self.sounds[sound_name].play()

    def load_sounds(self) -> None:
        """
        Load all sounds from the configured sound directory.

        This method scans the sound directory for files with the configured
        extension and loads them into the sounds dictionary. It also
        validates that all required sounds are present.
        """
        print("Loading sounds...")
        sound_path = config.SOUND_SET_DIR

        for dirpath, _, filenames in os.walk(sound_path):
            print(f"Found directory: {dirpath}")
            print(f"Files: {filenames}")

            for name in filenames:
                if name.endswith(config.SOUND_EXT):
                    key = name[:-4]  # Remove extension
                    self.sounds[key] = pygame.mixer.Sound(
                        os.path.join(sound_path, name)
                    )
                    self.sounds[key].set_volume(0.5)
                    print(f"Loaded sound {key}")

            # Sanity check: ensure all required sounds are loaded
            for key in REQUIRED_SOUNDS:
                if key not in self.sounds:
                    print(f"ERROR: Missing sound {key}")
                    sys.exit(1)

        # Now load the test sounds
        for key in TEST_SOUNDS:
            if key not in self.sounds:
                print(f"Loading test sound {key}")
                self.sounds[key] = pygame.mixer.Sound(
                    os.path.join("sounds/test", f"{key}{config.SOUND_EXT}")
                )
                self.sounds[key].set_volume(0.5)

        print("All Sounds loaded.")
