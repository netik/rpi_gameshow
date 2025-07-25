"""
Help information and key mappings for the game show application.

This module contains the help text and key mappings that are displayed
to users when they request help or need to understand the controls.
"""

from typing import List, TypedDict


class HelpKey(TypedDict):
    """Type definition for help key entries."""
    key: str
    text: str


HELP_KEYS: List[HelpKey] = [
    {"key": "SPACE", "text": "Stop/Start clock"},
    {"key": "SHIFT-ESC", "text": "Quit"},
    {"key": "H or ?", "text": "HELP"},
    {"key": "1", "text": "+1 point Player 1"},
    {"key": "2", "text": "+1 point Player 2"},
    {"key": "3", "text": "+1 point Player 3"},
    {"key": "4", "text": "+1 point Player 4"},
    {"key": "Q", "text": "-1 point Player 1"},
    {"key": "W", "text": "-1 point Player 2"},
    {"key": "E", "text": "-1 point Player 3"},
    {"key": "R", "text": "-1 point Player 4"},
    {"key": "P", "text": "Clock: +5 seconds"},
    {"key": "L", "text": "Clock: -5 seconds"},
    {"key": "T", "text": 'Play a "time\'s up" sound'},
    {"key": "B", "text": "Play a buzzer sound"},
    {"key": "N", "text": "Name Players"},
    {"key": "I", "text": "Invert Display (toggle)"},
    {"key": "S", "text": "Draw Splash Screen"},
    {"key": "SHIFT-A", "text": "Reset game"},
    {"key": "SHIFT-Z", "text": "Reset Clock"},
]
