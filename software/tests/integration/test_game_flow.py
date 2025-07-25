"""
Integration tests for game flow and state transitions.
"""

from unittest.mock import Mock, patch
import pytest

from Context import Context
from GameState import GameState
import config


class TestGameFlow:
    """Test cases for game flow and state transitions."""
    
    def test_game_initialization_flow(self):
        """Test complete game initialization flow."""
        with patch('pygame.time.Clock'), \
             patch('Sound.Sound'), \
             patch('pygame.sprite.Group'), \
             patch('pygame.display.set_mode') as mock_display, \
             patch('pygame.init'):
            
            # Mock screen
            mock_screen = Mock()
            mock_screen.get_size.return_value = (1920, 1080)
            mock_display.return_value = mock_screen
            
            # Initialize context
            context = Context()
            context.screen = mock_screen
            
            # Test initial state
            assert context.state == GameState.IDLE if config.CLOCK_ENABLED else GameState.RUNNING
            assert context.scores == [0] * config.PLAYERS
            assert context.clock == config.MAX_CLOCK
            assert context.player_buzzed_in == -1
            assert all(not led for led in context.led_state)
    
    def test_game_reset_flow(self):
        """Test game reset flow."""
        with patch('pygame.time.Clock'), \
             patch('Sound.Sound'), \
             patch('pygame.sprite.Group'):
            
            context = Context()
            
            # Simulate some game state
            context.scores = [10, 20, 30, 40]
            context.clock = 30000
            context.state = GameState.RUNNING
            context.player_buzzed_in = 2
            context.led_state = [True, False, True, False]
            
            # Reset game
            context.reset_game()
            
            # Verify reset
            assert context.scores == [0] * config.PLAYERS
            assert context.clock == config.MAX_CLOCK
            assert context.state == GameState.IDLE
            assert context.player_buzzed_in == -1
            # LED state should remain unchanged (not part of reset)
            assert context.led_state == [True, False, True, False]
    
    def test_clock_reset_flow(self):
        """Test clock reset flow."""
        with patch('pygame.time.Clock'), \
             patch('Sound.Sound'), \
             patch('pygame.sprite.Group'):
            
            context = Context()
            
            # Simulate some clock state
            context.clock = 30000
            context.prev_sec = 30
            context.state = GameState.RUNNING
            context.player_buzzed_in = 2
            
            # Reset clock
            context.reset_clock()
            
            # Verify clock reset
            assert context.clock == config.MAX_CLOCK
            assert context.prev_sec == 0
            assert context.state == GameState.IDLE
            assert context.player_buzzed_in == -1
    
    def test_state_persistence_flow(self):
        """Test state save and restore flow."""
        with patch('pygame.time.Clock'), \
             patch('Sound.Sound'), \
             patch('pygame.sprite.Group'), \
             patch('config.STATE_FILE_NAME', 'test_gamestate.pickle'):
            
            context = Context()
            
            # Modify some state
            context.player_names = ["Alice", "Bob", "Charlie", "Diana"]
            context.scores = [10, 20, 30, 40]
            context.invert_display = False
            
            # Save state
            context.save()
            
            # Create new context and restore
            new_context = Context()
            new_context.restore()
            
            # Verify state was restored
            assert new_context.player_names == ["Alice", "Bob", "Charlie", "Diana"]
            assert new_context.scores == [10, 20, 30, 40]
            assert new_context.invert_display is False
    
    def test_font_loading_flow(self):
        """Test font loading flow."""
        with patch('pygame.time.Clock'), \
             patch('Sound.Sound'), \
             patch('pygame.sprite.Group'), \
             patch('pygame.font.Font') as mock_font, \
             patch('os.path.join') as mock_join:
            
            context = Context()
            
            # Mock font
            mock_font_instance = Mock()
            mock_font.return_value = mock_font_instance
            mock_join.return_value = "fonts/test.ttf"
            
            # Load font
            context.load_font("testfont", "test.ttf", 24)
            
            # Verify font was loaded
            assert "testfont" in context.fonts
            assert context.fonts["testfont"] == mock_font_instance
            mock_font.assert_called_once_with("fonts/test.ttf", 24)
    
    def test_player_management_flow(self):
        """Test player management flow."""
        with patch('pygame.time.Clock'), \
             patch('Sound.Sound'), \
             patch('pygame.sprite.Group'):
            
            context = Context()
            
            # Test initial player setup
            assert len(context.player_names) == config.PLAYERS
            assert len(context.scores) == config.PLAYERS
            assert len(context.led_state) == config.PLAYERS
            
            # Test player name modification
            context.player_names[0] = "Alice"
            assert context.player_names[0] == "Alice"
            
            # Test score modification
            context.scores[1] = 25
            assert context.scores[1] == 25
            
            # Test LED state modification
            context.led_state[2] = True
            assert context.led_state[2] is True
    
    def test_game_state_transitions(self):
        """Test game state transition flow."""
        with patch('pygame.time.Clock'), \
             patch('Sound.Sound'), \
             patch('pygame.sprite.Group'):
            
            context = Context()
            
            # Test initial state
            initial_state = context.state
            
            # Test state transitions
            context.state = GameState.RUNNING
            assert context.state == GameState.RUNNING
            
            context.state = GameState.BUZZIN
            assert context.state == GameState.BUZZIN
            
            context.state = GameState.TIMEUP
            assert context.state == GameState.TIMEUP
            
            context.state = GameState.IDLE
            assert context.state == GameState.IDLE
    
    def test_buzzer_management_flow(self):
        """Test buzzer management flow."""
        with patch('pygame.time.Clock'), \
             patch('Sound.Sound'), \
             patch('pygame.sprite.Group'):
            
            context = Context()
            
            # Test initial buzzer state
            assert context.player_buzzed_in == -1
            
            # Test player buzz in
            context.player_buzzed_in = 1
            assert context.player_buzzed_in == 1
            
            # Test player buzz in another player
            context.player_buzzed_in = 3
            assert context.player_buzzed_in == 3
            
            # Test reset buzzer
            context.player_buzzed_in = -1
            assert context.player_buzzed_in == -1 