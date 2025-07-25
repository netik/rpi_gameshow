"""
Unit tests for Context class.
"""

import os
import pickle
import tempfile
from unittest.mock import Mock, patch
import pytest

from Context import Context
from GameState import GameState
import config


class TestContext:
    """Test cases for Context class."""
    
    def test_context_initialization(self):
        """Test Context initialization with default values."""
        with patch('pygame.time.Clock') as mock_clock, \
             patch('Sound.Sound') as mock_sound, \
             patch('pygame.sprite.Group') as mock_group:
            
            context = Context()
            
            assert context.serial_port is None
            assert context.clock == config.MAX_CLOCK
            assert context.prev_sec == 0
            assert context.fonts == {}
            assert context.colors == {}
            assert context.sound_library == {}
            assert context.screen is None
            assert context.scores == [0] * config.PLAYERS
            assert context.led_state == [False] * config.PLAYERS
            assert context.player_names == [f"Player {i+1}" for i in range(config.PLAYERS)]
            assert context.invert_display is True
            assert context.led_attract_cycle == 0
            assert context.player_buzzed_in == -1
            assert context.state == GameState.IDLE if config.CLOCK_ENABLED else GameState.RUNNING
            assert context.particle_group is not None
    
    def test_reset_game(self):
        """Test reset_game method."""
        with patch('pygame.time.Clock') as mock_clock, \
             patch('Sound.Sound') as mock_sound, \
             patch('pygame.sprite.Group') as mock_group:
            
            context = Context()
            
            # Modify some values
            context.scores = [10, 20, 30, 40]
            context.clock = 30000
            context.prev_sec = 30
            context.state = GameState.RUNNING
            context.player_buzzed_in = 2
            
            # Reset
            context.reset_game()
            
            assert context.scores == [0] * config.PLAYERS
            assert context.clock == config.MAX_CLOCK
            assert context.prev_sec == 0
            assert context.state == GameState.IDLE
            assert context.player_buzzed_in == -1
    
    def test_reset_clock(self):
        """Test reset_clock method."""
        with patch('pygame.time.Clock') as mock_clock, \
             patch('Sound.Sound') as mock_sound, \
             patch('pygame.sprite.Group') as mock_group:
            
            context = Context()
            
            # Modify some values
            context.clock = 30000
            context.prev_sec = 30
            context.state = GameState.RUNNING
            context.player_buzzed_in = 2
            
            # Reset clock
            context.reset_clock()
            
            assert context.clock == config.MAX_CLOCK
            assert context.prev_sec == 0
            assert context.state == GameState.IDLE
            assert context.player_buzzed_in == -1
    
    def test_save_and_restore(self, temp_state_file):
        """Test save and restore methods."""
        with patch('pygame.time.Clock') as mock_clock, \
             patch('Sound.Sound') as mock_sound, \
             patch('pygame.sprite.Group') as mock_group, \
             patch('config.STATE_FILE_NAME', temp_state_file):
            
            context = Context()
            
            # Modify some values
            context.player_names = ["Alice", "Bob", "Charlie", "Diana"]
            context.scores = [10, 20, 30, 40]
            context.invert_display = False
            
            # Save
            context.save()
            
            # Create new context and restore
            new_context = Context()
            new_context.restore()
            
            assert new_context.player_names == ["Alice", "Bob", "Charlie", "Diana"]
            assert new_context.scores == [10, 20, 30, 40]
            assert new_context.invert_display is False
    
    def test_restore_nonexistent_file(self):
        """Test restore method when state file doesn't exist."""
        with patch('pygame.time.Clock') as mock_clock, \
             patch('Sound.Sound') as mock_sound, \
             patch('pygame.sprite.Group') as mock_group, \
             patch('config.STATE_FILE_NAME', 'nonexistent.pickle'):
            
            context = Context()
            original_names = context.player_names.copy()
            original_scores = context.scores.copy()
            original_invert = context.invert_display
            
            # Should not raise an exception
            context.restore()
            
            # Values should remain unchanged
            assert context.player_names == original_names
            assert context.scores == original_scores
            assert context.invert_display == original_invert
    
    def test_load_font(self):
        """Test load_font method."""
        with patch('pygame.time.Clock') as mock_clock, \
             patch('Sound.Sound') as mock_sound, \
             patch('pygame.sprite.Group') as mock_group, \
             patch('pygame.font.Font') as mock_font, \
             patch('os.path.join') as mock_join:
            
            context = Context()
            mock_join.return_value = "fonts/test.ttf"
            
            context.load_font("testfont", "test.ttf", 24)
            
            mock_join.assert_called_once_with("fonts", "test.ttf")
            mock_font.assert_called_once_with("fonts/test.ttf", 24)
            assert "testfont" in context.fonts 