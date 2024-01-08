# pylint: disable=too-few-public-methods
"""
Generic sound class for all sound operations
"""

import os
import pygame
import config

class Sound:
    """
    Generic sound class for all sound operations
    """
    def __init__(self):
        self.sounds = {}
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()
        pygame.init()
        self.load_sounds()

    def play(self,sound_name):
        """Play a sound"""
        self.sounds[sound_name].play()

    def load_sounds(self):
        """Load all sounds from subdirectories in a dictionary"""
        print("Loading sounds...")
        sound_path = f"sounds/Soundsets/{config.SOUND_SET}"
        for dirpath, _, filenames in os.walk(sound_path):
            print("Found directory: %s" % dirpath)
            print("Files: %s" % filenames)

            for name in filenames:
                if name.endswith(".mp3"):
                    key = name[:-4]
                    self.sounds[key] = pygame.mixer.Sound(
                        os.path.join(sound_path, name)
                    )
                    print("Loaded sound %s" % key)
