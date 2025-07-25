"""
Unit tests for GameState enum.
"""

from GameState import GameState


class TestGameState:
    """Test cases for GameState enum."""
    
    def test_game_state_values(self):
        """Test that GameState enum has expected values."""
        assert GameState.IDLE.value == 0
        assert GameState.RUNNING.value == 1
        assert GameState.BUZZIN.value == 2
        assert GameState.TIMEUP.value == 3
        assert GameState.INPUT.value == 4
        assert GameState.SETUP.value == 100
        assert GameState.SPLASH.value == 200
        assert GameState.HELP.value == 300
    
    def test_game_state_names(self):
        """Test that GameState enum has expected names."""
        assert GameState.IDLE.name == "IDLE"
        assert GameState.RUNNING.name == "RUNNING"
        assert GameState.BUZZIN.name == "BUZZIN"
        assert GameState.TIMEUP.name == "TIMEUP"
        assert GameState.INPUT.name == "INPUT"
        assert GameState.SETUP.name == "SETUP"
        assert GameState.SPLASH.name == "SPLASH"
        assert GameState.HELP.name == "HELP"
    
    def test_game_state_comparison(self):
        """Test GameState enum comparison operations."""
        # Test value comparison
        assert GameState.IDLE.value < GameState.RUNNING.value
        assert GameState.RUNNING.value < GameState.BUZZIN.value
        assert GameState.BUZZIN.value < GameState.TIMEUP.value
        assert GameState.TIMEUP.value < GameState.INPUT.value
        assert GameState.INPUT.value < GameState.SETUP.value
        assert GameState.SETUP.value < GameState.SPLASH.value
        assert GameState.SPLASH.value < GameState.HELP.value
        
        # Test enum comparison using values
        assert GameState.IDLE.value < GameState.RUNNING.value
        assert GameState.RUNNING.value > GameState.IDLE.value
        assert GameState.IDLE.value == GameState.IDLE.value
    
    def test_game_state_iteration(self):
        """Test that GameState enum can be iterated."""
        states = list(GameState)
        assert len(states) == 8
        assert GameState.IDLE in states
        assert GameState.RUNNING in states
        assert GameState.BUZZIN in states
        assert GameState.TIMEUP in states
        assert GameState.INPUT in states
        assert GameState.SETUP in states
        assert GameState.SPLASH in states
        assert GameState.HELP in states
    
    def test_game_state_string_representation(self):
        """Test GameState enum string representation."""
        assert str(GameState.IDLE) == "GameState.IDLE"
        assert repr(GameState.RUNNING) == "<GameState.RUNNING: 1>" 