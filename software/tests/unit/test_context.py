"""
Unit tests for Context class.
"""

import pickle
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from Context import Context
from GameState import GameState
import game_config as config


class TestContext:
    """Test cases for Context class."""
    
    @patch('Context.Sound')
    def test_context_initialization(self, mock_sound_class):
        """Test Context initialization with default values."""
        with patch('pygame.time.Clock') as mock_clock, \
             patch('pygame.sprite.Group') as mock_group:
            
            # Mock Sound class to avoid file loading
            mock_sound_instance = Mock()
            mock_sound_class.return_value = mock_sound_instance
            
            context = Context()
            
            assert context.state == (GameState.IDLE if config.CLOCK_ENABLED else GameState.RUNNING)
            assert context.scores == [0] * config.PLAYERS
            assert context.player_names == [f"Player {i+1}" for i in range(config.PLAYERS)]
            assert context.clock == config.MAX_CLOCK
            assert context.player_buzzed_in == -1
            assert context.invert_display is True
            
            mock_clock.assert_called_once()
            mock_sound_class.assert_called_once()
            mock_group.assert_called_once()
    
    @patch('Context.Sound')
    def test_reset_game(self, mock_sound_class):
        """Test reset_game method."""
        with patch('pygame.time.Clock') as mock_clock, \
             patch('pygame.sprite.Group') as mock_group:
            
            # Mock Sound class to avoid file loading
            mock_sound_instance = Mock()
            mock_sound_class.return_value = mock_sound_instance
            
            context = Context()
            
            # Modify some values
            context.state = GameState.RUNNING
            context.scores = [100, 200, 150, 75]
            context.clock = 10000
            context.player_buzzed_in = 2
            
            # Reset game
            context.reset_game()
            
            assert context.state == GameState.IDLE
            assert context.scores == [0] * config.PLAYERS
            assert context.clock == config.MAX_CLOCK
            assert context.player_buzzed_in == -1
    
    @patch('Context.Sound')
    def test_reset_clock(self, mock_sound_class):
        """Test reset_clock method."""
        with patch('pygame.time.Clock') as mock_clock, \
             patch('pygame.sprite.Group') as mock_group:
            
            # Mock Sound class to avoid file loading
            mock_sound_instance = Mock()
            mock_sound_class.return_value = mock_sound_instance
            
            context = Context()
            
            # Modify time
            context.clock = 5000
            
            # Reset clock
            context.reset_clock()
            
            assert context.clock == config.MAX_CLOCK
            assert context.state == GameState.IDLE
            assert context.player_buzzed_in == -1
    
    @patch('Context.Sound')
    def test_save_and_restore(self, mock_sound_class, temp_state_file):
        """Test save and restore functionality."""
        with patch('pygame.time.Clock') as mock_clock, \
             patch('pygame.sprite.Group') as mock_group, \
             patch('game_config.STATE_FILE_NAME', temp_state_file):
            
            # Mock Sound class to avoid file loading
            mock_sound_instance = Mock()
            mock_sound_class.return_value = mock_sound_instance
            
            context = Context()
            
            # Modify some values
            context.state = GameState.RUNNING
            context.scores = [100, 200, 150, 75]
            context.player_names = ["Alice", "Bob", "Charlie", "Diana"]
            context.invert_display = False
            
            # Save state
            context.save()
            
            # Create new context and restore
            new_context = Context()
            new_context.restore()
            
            assert new_context.scores == context.scores
            assert new_context.player_names == context.player_names
            assert new_context.invert_display == context.invert_display
    
    @patch('Context.Sound')
    def test_restore_nonexistent_file(self, mock_sound_class):
        """Test restore method with nonexistent file."""
        with patch('pygame.time.Clock') as mock_clock, \
             patch('pygame.sprite.Group') as mock_group, \
             patch('game_config.STATE_FILE_NAME', 'nonexistent_file.pkl'):
            
            # Mock Sound class to avoid file loading
            mock_sound_instance = Mock()
            mock_sound_class.return_value = mock_sound_instance
            
            context = Context()
            original_names = context.player_names.copy()
            original_scores = context.scores.copy()
            
            # Try to restore from nonexistent file
            context.restore()
            
            # Should remain unchanged
            assert context.player_names == original_names
            assert context.scores == original_scores
    
    @patch('Context.Sound')
    def test_load_font(self, mock_sound_class):
        """Test load_font method."""
        with patch('pygame.time.Clock') as mock_clock, \
             patch('pygame.sprite.Group') as mock_group, \
             patch('pygame.font.Font') as mock_font, \
             patch('os.path.join') as mock_join:
            
            # Mock Sound class to avoid file loading
            mock_sound_instance = Mock()
            mock_sound_class.return_value = mock_sound_instance
            
            # Mock the font loading
            mock_font.return_value = MagicMock()
            mock_join.return_value = "fonts/test_font.ttf"
            
            context = Context()
            
            # Test loading a font
            context.load_font("test_font", "test_font.ttf", 24)
            
            mock_join.assert_called_with("fonts", "test_font.ttf")
            mock_font.assert_called_with("fonts/test_font.ttf", 24)
            assert "test_font" in context.fonts 