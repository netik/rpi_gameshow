# pylint: disable=too-few-public-methods
"""
Generic sound class for all sound operations
"""

import os
import pygame
import config

REQUIRED_SOUNDS = ['BEEP', 'BUZZ', 'TIMESUP', 'PLAYER1', 'PLAYER2', 'PLAYER3', 'PLAYER4', 'INVALID']
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
        sound_path = config.SOUND_SET_DIR
        for dirpath, _, filenames in os.walk(sound_path):
            print("Found directory: %s" % dirpath)
            print("Files: %s" % filenames)

            for name in filenames:
                if name.endswith(config.SOUND_EXT):
                    key = name[:-4]
                    self.sounds[key] = pygame.mixer.Sound(
                        os.path.join(sound_path, name)
                    )
                    self.sounds[key].set_volume(0.5)
                    print("Loaded sound %s" % key)

            # sanity check, make sure all files are loaded
            for key in REQUIRED_SOUNDS:
                if key not in self.sounds:
                    print("ERROR: Missing sound %s" % key)
                    exit(1)

            print("All Sounds loaded.")