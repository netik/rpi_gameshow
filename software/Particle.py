"""
Particle system for visual effects in the game show application.

This module provides particle classes for creating visual effects such as
explosions and other animated elements.
"""

from typing import Tuple
import pygame
from random import randint


class Particle(pygame.sprite.Sprite):
    """
    Base particle class for visual effects.
    
    Particles are small animated objects that can move, fade, and be removed
    when they go off-screen or become transparent.
    """
    
    def __init__(
        self,
        screen_info: pygame.display.Info,
        groups: pygame.sprite.Group,
        pos: Tuple[int, int],
        color: str,
        direction: pygame.math.Vector2,
        speed: int
    ) -> None:
        """
        Initialize a new particle.
        
        Args:
            screen_info: Pygame display info for screen dimensions
            groups: Sprite groups to add this particle to
            pos: Initial position (x, y)
            color: Color of the particle
            direction: Normalized direction vector
            speed: Movement speed in pixels per second
        """
        super().__init__(groups)
        self.screen_info = screen_info
        self.pos = pygame.math.Vector2(pos)
        self.color = color
        self.direction = direction
        self.speed = speed
        self.alpha = 255
        self.fade_speed = 200
        self.size = 4

        self.create_surf()

    def create_surf(self) -> None:
        """Create the particle's surface and rectangle."""
        self.image = pygame.Surface((self.size, self.size)).convert_alpha()
        self.image.set_colorkey("black")
        pygame.draw.circle(
            surface=self.image,
            color=self.color,
            center=(self.size / 2, self.size / 2),
            radius=self.size / 2
        )
        self.rect = self.image.get_rect(center=self.pos)

    def move(self, dt: float) -> None:
        """
        Move the particle based on its direction and speed.
        
        Args:
            dt: Delta time in seconds
        """
        self.pos += self.direction * self.speed * dt
        self.rect.center = self.pos

    def fade(self, dt: float) -> None:
        """
        Fade the particle's alpha value.
        
        Args:
            dt: Delta time in seconds
        """
        self.alpha -= self.fade_speed * dt
        self.image.set_alpha(self.alpha)

    def check_pos(self) -> None:
        """Check if particle is off-screen and remove if so."""
        if (
            self.pos[0] < -50 or
            self.pos[0] > self.screen_info.current_w + 50 or
            self.pos[1] < -50 or
            self.pos[1] > self.screen_info.current_h + 50
        ):
            self.kill()

    def check_alpha(self) -> None:
        """Check if particle is fully transparent and remove if so."""
        if self.alpha <= 0:
            self.kill()

    def update(self, dt: float) -> None:
        """
        Update particle state.
        
        Args:
            dt: Delta time in seconds
        """
        self.move(dt)
        self.fade(dt)
        self.check_pos()
        self.check_alpha()


class ExplodingParticle(Particle):
    """
    Particle that explodes after a certain lifetime.
    
    These particles move normally for a period, then expand and fade out
    to create an explosion effect.
    """
    
    def __init__(
        self,
        screen_info: pygame.display.Info,
        groups: pygame.sprite.Group,
        pos: Tuple[int, int],
        color: str,
        direction: pygame.math.Vector2,
        speed: int
    ) -> None:
        """
        Initialize an exploding particle.
        
        Args:
            screen_info: Pygame display info for screen dimensions
            groups: Sprite groups to add this particle to
            pos: Initial position (x, y)
            color: Color of the particle
            direction: Normalized direction vector
            speed: Movement speed in pixels per second
        """
        super().__init__(screen_info, groups, pos, color, direction, speed)
        self.screen_info = screen_info
        self.t0 = pygame.time.get_ticks()
        self.lifetime = randint(1000, 2000)
        self.exploding = False
        self.size = 4
        self.max_size = 50
        self.inflate_speed = 70
        self.fade_speed = 2500

    def explosion_timer(self) -> None:
        """Check if it's time to start the explosion phase."""
        if not self.exploding:
            t = pygame.time.get_ticks()
            if t - self.t0 > self.lifetime:
                self.exploding = True

    def inflate(self, dt: float) -> None:
        """
        Increase the particle size during explosion.
        
        Args:
            dt: Delta time in seconds
        """
        self.size += self.inflate_speed * dt
        self.create_surf()

    def check_size(self) -> None:
        """Check if particle has reached maximum size and remove if so."""
        if self.size > self.max_size:
            self.kill()

    def update(self, dt: float) -> None:
        """
        Update exploding particle state.
        
        Args:
            dt: Delta time in seconds
        """
        self.move(dt)
        self.explosion_timer()
        if self.exploding:
            self.inflate(dt)
            self.fade(dt)

        self.check_pos()
        self.check_size()
        self.check_alpha()
