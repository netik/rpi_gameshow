"""
Unit tests for Particle classes.
"""

from unittest.mock import Mock, patch
import pytest
import pygame

from Particle import Particle, ExplodingParticle


class TestParticle:
    """Test cases for base Particle class."""
    
    def test_particle_initialization(self):
        """Test Particle initialization."""
        with patch('pygame.sprite.Sprite.__init__') as mock_sprite_init:
            mock_screen_info = Mock()
            mock_screen_info.current_w = 1920
            mock_screen_info.current_h = 1080
            
            mock_groups = Mock()
            pos = (100, 200)
            color = "red"
            direction = pygame.math.Vector2(1, 0)
            speed = 100
            
            particle = Particle(mock_screen_info, mock_groups, pos, color, direction, speed)
            
            assert particle.screen_info == mock_screen_info
            assert particle.pos == pygame.math.Vector2(pos)
            assert particle.color == color
            assert particle.direction == direction
            assert particle.speed == speed
            assert particle.alpha == 255
            assert particle.fade_speed == 200
            assert particle.size == 4
    
    def test_particle_create_surf(self):
        """Test particle surface creation."""
        with patch('pygame.sprite.Sprite.__init__'), \
             patch('pygame.Surface') as mock_surface, \
             patch('pygame.draw.circle') as mock_circle:
            
            mock_screen_info = Mock()
            mock_screen_info.current_w = 1920
            mock_screen_info.current_h = 1080
            
            mock_groups = Mock()
            pos = (100, 200)
            color = "red"
            direction = pygame.math.Vector2(1, 0)
            speed = 100
            
            particle = Particle(mock_screen_info, mock_groups, pos, color, direction, speed)
            
            # Test create_surf method
            particle.create_surf()
            
            mock_surface.assert_called_once_with((4, 4))
            mock_circle.assert_called_once()
    
    def test_particle_move(self):
        """Test particle movement."""
        with patch('pygame.sprite.Sprite.__init__'):
            mock_screen_info = Mock()
            mock_screen_info.current_w = 1920
            mock_screen_info.current_h = 1080
            
            mock_groups = Mock()
            pos = (100, 200)
            color = "red"
            direction = pygame.math.Vector2(1, 0)
            speed = 100
            
            particle = Particle(mock_screen_info, mock_groups, pos, color, direction, speed)
            particle.rect = Mock()
            particle.rect.center = (100, 200)
            
            original_pos = particle.pos.copy()
            dt = 0.016  # 60 FPS
            
            particle.move(dt)
            
            # Position should have moved
            assert particle.pos != original_pos
            assert particle.rect.center == particle.pos
    
    def test_particle_fade(self):
        """Test particle fading."""
        with patch('pygame.sprite.Sprite.__init__'):
            mock_screen_info = Mock()
            mock_screen_info.current_w = 1920
            mock_screen_info.current_h = 1080
            
            mock_groups = Mock()
            pos = (100, 200)
            color = "red"
            direction = pygame.math.Vector2(1, 0)
            speed = 100
            
            particle = Particle(mock_screen_info, mock_groups, pos, color, direction, speed)
            particle.image = Mock()
            
            original_alpha = particle.alpha
            dt = 0.016  # 60 FPS
            
            particle.fade(dt)
            
            # Alpha should have decreased
            assert particle.alpha < original_alpha
            particle.image.set_alpha.assert_called_once_with(particle.alpha)
    
    def test_particle_check_pos_off_screen(self):
        """Test particle removal when off screen."""
        with patch('pygame.sprite.Sprite.__init__'):
            mock_screen_info = Mock()
            mock_screen_info.current_w = 1920
            mock_screen_info.current_h = 1080
            
            mock_groups = Mock()
            pos = (100, 200)
            color = "red"
            direction = pygame.math.Vector2(1, 0)
            speed = 100
            
            particle = Particle(mock_screen_info, mock_groups, pos, color, direction, speed)
            
            # Move particle off screen
            particle.pos = pygame.math.Vector2(-100, 100)
            
            particle.check_pos()
            
            # Should be killed
            assert particle.kill.called
    
    def test_particle_check_alpha_zero(self):
        """Test particle removal when alpha reaches zero."""
        with patch('pygame.sprite.Sprite.__init__'):
            mock_screen_info = Mock()
            mock_screen_info.current_w = 1920
            mock_screen_info.current_h = 1080
            
            mock_groups = Mock()
            pos = (100, 200)
            color = "red"
            direction = pygame.math.Vector2(1, 0)
            speed = 100
            
            particle = Particle(mock_screen_info, mock_groups, pos, color, direction, speed)
            
            # Set alpha to zero
            particle.alpha = 0
            
            particle.check_alpha()
            
            # Should be killed
            assert particle.kill.called


class TestExplodingParticle:
    """Test cases for ExplodingParticle class."""
    
    def test_exploding_particle_initialization(self):
        """Test ExplodingParticle initialization."""
        with patch('pygame.sprite.Sprite.__init__'), \
             patch('pygame.time.get_ticks') as mock_ticks:
            
            mock_ticks.return_value = 1000
            
            mock_screen_info = Mock()
            mock_screen_info.current_w = 1920
            mock_screen_info.current_h = 1080
            
            mock_groups = Mock()
            pos = (100, 200)
            color = "red"
            direction = pygame.math.Vector2(1, 0)
            speed = 100
            
            particle = ExplodingParticle(mock_screen_info, mock_groups, pos, color, direction, speed)
            
            assert particle.screen_info == mock_screen_info
            assert particle.t0 == 1000
            assert particle.lifetime >= 1000 and particle.lifetime <= 2000
            assert particle.exploding is False
            assert particle.size == 4
            assert particle.max_size == 50
            assert particle.inflate_speed == 70
            assert particle.fade_speed == 2500
    
    def test_explosion_timer_not_exploding(self):
        """Test explosion timer when not yet exploding."""
        with patch('pygame.sprite.Sprite.__init__'), \
             patch('pygame.time.get_ticks') as mock_ticks:
            
            mock_ticks.side_effect = [1000, 1500]  # t0, current time
            
            mock_screen_info = Mock()
            mock_screen_info.current_w = 1920
            mock_screen_info.current_h = 1080
            
            mock_groups = Mock()
            pos = (100, 200)
            color = "red"
            direction = pygame.math.Vector2(1, 0)
            speed = 100
            
            particle = ExplodingParticle(mock_screen_info, mock_groups, pos, color, direction, speed)
            particle.lifetime = 1000  # Set fixed lifetime for testing
            
            particle.explosion_timer()
            
            # Should not be exploding yet
            assert particle.exploding is False
    
    def test_explosion_timer_exploding(self):
        """Test explosion timer when it's time to explode."""
        with patch('pygame.sprite.Sprite.__init__'), \
             patch('pygame.time.get_ticks') as mock_ticks:
            
            mock_ticks.side_effect = [1000, 2500]  # t0, current time (past lifetime)
            
            mock_screen_info = Mock()
            mock_screen_info.current_w = 1920
            mock_screen_info.current_h = 1080
            
            mock_groups = Mock()
            pos = (100, 200)
            color = "red"
            direction = pygame.math.Vector2(1, 0)
            speed = 100
            
            particle = ExplodingParticle(mock_screen_info, mock_groups, pos, color, direction, speed)
            particle.lifetime = 1000  # Set fixed lifetime for testing
            
            particle.explosion_timer()
            
            # Should be exploding now
            assert particle.exploding is True
    
    def test_inflate(self):
        """Test particle inflation during explosion."""
        with patch('pygame.sprite.Sprite.__init__'), \
             patch('pygame.time.get_ticks'):
            
            mock_screen_info = Mock()
            mock_screen_info.current_w = 1920
            mock_screen_info.current_h = 1080
            
            mock_groups = Mock()
            pos = (100, 200)
            color = "red"
            direction = pygame.math.Vector2(1, 0)
            speed = 100
            
            particle = ExplodingParticle(mock_screen_info, mock_groups, pos, color, direction, speed)
            particle.create_surf = Mock()
            
            original_size = particle.size
            dt = 0.016  # 60 FPS
            
            particle.inflate(dt)
            
            # Size should have increased
            assert particle.size > original_size
            particle.create_surf.assert_called_once()
    
    def test_check_size_max_reached(self):
        """Test particle removal when max size is reached."""
        with patch('pygame.sprite.Sprite.__init__'), \
             patch('pygame.time.get_ticks'):
            
            mock_screen_info = Mock()
            mock_screen_info.current_w = 1920
            mock_screen_info.current_h = 1080
            
            mock_groups = Mock()
            pos = (100, 200)
            color = "red"
            direction = pygame.math.Vector2(1, 0)
            speed = 100
            
            particle = ExplodingParticle(mock_screen_info, mock_groups, pos, color, direction, speed)
            
            # Set size to max
            particle.size = particle.max_size + 1
            
            particle.check_size()
            
            # Should be killed
            assert particle.kill.called 