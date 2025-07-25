"""
Unit tests for GameState enum.
"""

import pytest
from GameState import GameState


class TestGameState:
    """Test cases for GameState enum."""
    
    def test_game_state_values(self):
        """Test that GameState enum has expected values."""
        assert GameState.IDLE == 0
        assert GameState.RUNNING == 1
        assert GameState.BUZZIN == 2
        assert GameState.TIMEUP == 3
        assert GameState.INPUT == 4
        assert GameState.SETUP == 100
        assert GameState.SPLASH == 200
        assert GameState.HELP == 300
    
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
        assert GameState.IDLE < GameState.RUNNING
        assert GameState.RUNNING < GameState.BUZZIN
        assert GameState.BUZZIN < GameState.TIMEUP
        assert GameState.TIMEUP < GameState.INPUT
        assert GameState.INPUT < GameState.SETUP
        assert GameState.SETUP < GameState.SPLASH
        assert GameState.SPLASH < GameState.HELP
    
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