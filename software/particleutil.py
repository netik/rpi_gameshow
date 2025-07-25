"""
Utility functions for spawning particles in the game show application.

This module provides functions for creating and managing particle effects
such as exploding particles for visual feedback.
"""

from typing import Tuple
import pygame
from random import choice, randint, uniform

from Particle import ExplodingParticle


def spawn_exploding_particles(
    screen_info: pygame.display.Info,
    particle_group: pygame.sprite.Group,
    pos: Tuple[int, int],
    n: int
) -> None:
    """
    Spawn a specified number of exploding particles at a given position.

    Args:
        screen_info: Pygame display info for screen dimensions
        particle_group: Sprite group to add particles to
        pos: Position (x, y) where particles should spawn
        n: Number of particles to spawn
    """
    for _ in range(n):
        color = choice(("pink", "white", "grey"))
        direction = pygame.math.Vector2(uniform(-1, 1), uniform(-1, 1))
        direction = direction.normalize()
        speed = randint(50, 400)
        ExplodingParticle(screen_info, particle_group, pos, color, direction, speed)
