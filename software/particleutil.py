import pygame
from Particle import Particle, ExplodingParticle
from random import choice, randint, uniform
"""
    some utility functions for spawning particles
"""

def spawn_exploding_particles(screen_info, particle_group, pos, n: int):
    for _ in range(n):
        color = choice(("red", "yellow", "orange"))
        direction = pygame.math.Vector2(uniform(-1,1), uniform(-1, 1))
        direction = direction.normalize()
        speed = randint(50, 400)
        ExplodingParticle(screen_info, particle_group, pos, color, direction, speed)
