"""
Various drawing utility functions for the game show application.

This module provides utility functions for rendering text and other visual
elements to the game screen.
"""

from typing import Tuple, Union
import pygame

from Context import Context


def drawtext(
    context: Context,
    font_name: str,
    text: str,
    xpos: int,
    ypos: int,
    fg_color: Union[pygame.Color, Tuple[int, int, int], Tuple[int, int, int, int]],
    bg_color: Union[pygame.Color, Tuple[int, int, int], Tuple[int, int, int, int]]
) -> None:
    """
    Render text to the screen at a specific location with specified font and colors.

    Args:
        context: Game context containing screen and fonts
        font_name: Name of the font to use (must be loaded in context)
        text: Text string to display
        xpos: X coordinate for text position
        ypos: Y coordinate for text position
        fg_color: Foreground color for the text
        bg_color: Background color for the text
    """
    text_surface = context.fonts[font_name].render(text, True, fg_color, bg_color)
    context.screen.blit(text_surface, (xpos, ypos))

