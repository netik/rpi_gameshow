"""
GUI tests for display functionality.

These tests require a display and test actual rendering.
Marked with @pytest.mark.gui to run separately from other tests.
"""

import pytest
from unittest.mock import Mock, patch
import pygame

from Context import Context
from drawutil import drawtext


@pytest.mark.gui
class TestDisplay:
    """Test cases for display functionality."""
    
    def test_drawtext_rendering(self):
        """Test text rendering functionality."""
        # Initialize pygame display
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        
        # Create context with screen
        context = Context()
        context.screen = screen
        
        # Load a test font
        context.load_font("testfont", "RobotoCondensed-Regular.ttf", 24)
        
        # Test text rendering
        test_text = "Hello, World!"
        x, y = 100, 100
        fg_color = (255, 255, 255)  # White
        bg_color = (0, 0, 0)        # Black
        
        # This should not raise an exception
        drawtext(context, "testfont", test_text, x, y, fg_color, bg_color)
        
        # Verify text was rendered (basic check)
        # In a real test, you might capture the screen and verify pixels
        
        pygame.quit()
    
    def test_screen_initialization(self):
        """Test screen initialization with different modes."""
        pygame.init()
        
        # Test different display modes
        modes = [
            (800, 600),
            (1024, 768),
            (1920, 1080)
        ]
        
        for width, height in modes:
            screen = pygame.display.set_mode((width, height))
            assert screen.get_size() == (width, height)
            pygame.display.quit()
        
        pygame.quit()
    
    def test_color_rendering(self):
        """Test color rendering on screen."""
        pygame.init()
        screen = pygame.display.set_mode((400, 300))
        
        # Test different colors
        colors = [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 255, 255), # White
            (0, 0, 0),      # Black
        ]
        
        for color in colors:
            # Fill screen with color
            screen.fill(color)
            
            # Update display
            pygame.display.flip()
            
            # Small delay to see the color (in real test, you'd verify pixels)
            pygame.time.wait(100)
        
        pygame.quit()


@pytest.mark.gui
class TestModalDialogs:
    """Test cases for modal dialog functionality."""
    
    def test_modal_rendering(self):
        """Test modal dialog rendering."""
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        
        # Test modal background rendering
        modal_rect = pygame.Rect(100, 100, 600, 400)
        
        # Draw modal background
        pygame.draw.rect(screen, (60, 60, 60), modal_rect)
        pygame.draw.rect(screen, (210, 0, 100), modal_rect, 3)
        
        # Update display
        pygame.display.flip()
        
        # Verify modal was drawn (basic check)
        # In a real test, you'd verify the pixels
        
        pygame.quit()


@pytest.mark.gui
class TestParticleRendering:
    """Test cases for particle system rendering."""
    
    def test_particle_creation(self):
        """Test particle creation and rendering."""
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        
        # Create particle group
        particle_group = pygame.sprite.Group()
        
        # Create a simple particle surface
        particle_surface = pygame.Surface((10, 10))
        particle_surface.fill((255, 255, 0))  # Yellow particle
        
        # Create sprite from surface
        particle_sprite = pygame.sprite.Sprite()
        particle_sprite.image = particle_surface
        particle_sprite.rect = particle_surface.get_rect()
        particle_sprite.rect.center = (400, 300)
        
        # Add to group
        particle_group.add(particle_sprite)
        
        # Draw particles
        particle_group.draw(screen)
        pygame.display.flip()
        
        # Verify particle was drawn
        # In a real test, you'd verify the pixels
        
        pygame.quit()


# Skip these tests if no display is available
@pytest.mark.skipif(
    not pygame.display.get_init(),
    reason="No display available for GUI tests"
)
class TestDisplayAvailability:
    """Test cases that require display availability."""
    
    def test_display_info(self):
        """Test display information retrieval."""
        pygame.init()
        
        # Get display info
        info = pygame.display.Info()
        
        # Verify we have valid display info
        assert info.current_w > 0
        assert info.current_h > 0
        
        pygame.quit() 