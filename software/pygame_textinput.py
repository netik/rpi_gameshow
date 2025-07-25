"""
Text input management for pygame applications.

Copyright 2021, Silas Gyger, silasgyger@gmail.com, All rights reserved.
Borrowed from https://github.com/Nearoo/pygame-text-input under the MIT license.

This module provides text input functionality for pygame applications,
including cursor management, text validation, and visual rendering.
"""

from typing import List, Callable, Optional
import pygame
import pygame.locals as pl

pygame.font.init()


class TextInputManager:
    """
    Manages text input state including cursor position and validation.
    
    This class keeps track of text input, cursor position, and provides
    validation capabilities. Pass a validator function to restrict input.
    
    Example:
        # Limit input to 5 characters
        limit_5 = lambda x: len(x) <= 5
        manager = TextInputManager(validator=limit_5)
    """
    
    def __init__(
        self,
        initial: str = "",
        validator: Callable[[str], bool] = lambda x: True
    ) -> None:
        """
        Initialize the text input manager.
        
        Args:
            initial: Initial text string
            validator: Function that takes a string and returns True if valid
        """
        self.left = initial  # String to the left of the cursor
        self.right = ""      # String to the right of the cursor
        self.validator = validator

    @property
    def value(self) -> str:
        """Get the current input value."""
        return self.left + self.right
    
    @value.setter
    def value(self, value: str) -> None:
        """Set the current input value while preserving cursor position if possible."""
        cursor_pos = self.cursor_pos
        self.left = value[:cursor_pos]
        self.right = value[cursor_pos:]
    
    @property
    def cursor_pos(self) -> int:
        """Get the current cursor position."""
        return len(self.left)

    @cursor_pos.setter
    def cursor_pos(self, value: int) -> None:
        """Set the cursor position, clamping to valid range."""
        complete = self.value
        self.left = complete[:value]
        self.right = complete[value:]
    
    def update(self, events: List[pygame.event.Event]) -> None:
        """
        Update internal state with fresh pygame events.
        
        Call this every frame with all events returned by pygame.event.get().
        
        Args:
            events: List of pygame events to process
        """
        for event in events:
            if event.type == pl.KEYDOWN:
                v_before = self.value
                c_before = self.cursor_pos
                self._process_keydown(event)
                if not self.validator(self.value):
                    self.value = v_before
                    self.cursor_pos = c_before

    def _process_keydown(self, ev: pygame.event.Event) -> None:
        """Process a keydown event."""
        attrname = f"_process_{pygame.key.name(ev.key)}"
        if hasattr(self, attrname):
            getattr(self, attrname)()
        else:
            self._process_other(ev)

    def _process_delete(self) -> None:
        """Process delete key press."""
        self.right = self.right[1:]
    
    def _process_backspace(self) -> None:
        """Process backspace key press."""
        self.left = self.left[:-1]
    
    def _process_right(self) -> None:
        """Process right arrow key press."""
        self.cursor_pos += 1
    
    def _process_left(self) -> None:
        """Process left arrow key press."""
        self.cursor_pos -= 1

    def _process_end(self) -> None:
        """Process end key press."""
        self.cursor_pos = len(self.value)
    
    def _process_home(self) -> None:
        """Process home key press."""
        self.cursor_pos = 0
    
    def _process_return(self) -> None:
        """Process return key press."""
        pass  # Override in subclass if needed
    
    def _process_other(self, event: pygame.event.Event) -> None:
        """Process other key presses by adding the character."""
        if event.unicode.isprintable():
            self.left += event.unicode


class TextInputVisualizer:
    """
    Visual representation of text input with cursor and styling.
    
    This class handles the visual rendering of text input, including
    cursor blinking, text rendering, and surface management.
    """
    
    def __init__(
        self,
        manager: Optional[TextInputManager] = None,
        font_object: Optional[pygame.font.Font] = None,
        antialias: bool = True,
        font_color: pygame.Color = pygame.Color(0, 0, 0),
        cursor_blink_interval: int = 300,
        cursor_width: int = 3,
        cursor_color: pygame.Color = pygame.Color(0, 0, 0)
    ) -> None:
        """
        Initialize the text input visualizer.
        
        Args:
            manager: Text input manager to visualize
            font_object: Font to use for rendering
            antialias: Whether to use antialiasing
            font_color: Color of the text
            cursor_blink_interval: Cursor blink interval in milliseconds
            cursor_width: Width of the cursor in pixels
            cursor_color: Color of the cursor
        """
        self._manager = manager or TextInputManager()
        self._font_object = font_object or pygame.font.Font(None, 20)
        self._antialias = antialias
        self._font_color = font_color
        self._cursor_width = cursor_width
        self._cursor_color = cursor_color
        self._cursor_blink_interval = cursor_blink_interval
        self._cursor_visible = True
        self._last_cursor_switch = pygame.time.get_ticks()
        self._surface = pygame.Surface((0, 0))
        self._rerender()

    @property
    def value(self) -> str:
        """Get the current input value."""
        return self._manager.value
    
    @value.setter
    def value(self, v: str) -> None:
        """Set the current input value."""
        self._manager.value = v
        self._rerender()

    @property
    def manager(self) -> TextInputManager:
        """Get the text input manager."""
        return self._manager
    
    @manager.setter
    def manager(self, v: TextInputManager) -> None:
        """Set the text input manager."""
        self._manager = v
        self._rerender()

    @property
    def surface(self) -> pygame.Surface:
        """Get the rendered surface."""
        self._rerender()
        return self._surface

    @property
    def antialias(self) -> bool:
        """Get antialiasing setting."""
        return self._antialias
    
    @antialias.setter
    def antialias(self, v: bool) -> None:
        """Set antialiasing setting."""
        self._antialias = v
        self._require_rerender()

    @property
    def font_color(self) -> pygame.Color:
        """Get font color."""
        return self._font_color
    
    @font_color.setter
    def font_color(self, v: pygame.Color) -> None:
        """Set font color."""
        self._font_color = v
        self._require_rerender()

    @property
    def font_object(self) -> pygame.font.Font:
        """Get font object."""
        return self._font_object
    
    @font_object.setter
    def font_object(self, v: pygame.font.Font) -> None:
        """Set font object."""
        self._font_object = v
        self._require_rerender()

    @property
    def cursor_visible(self) -> bool:
        """Get cursor visibility."""
        return self._cursor_visible
    
    @cursor_visible.setter
    def cursor_visible(self, v: bool) -> None:
        """Set cursor visibility."""
        self._cursor_visible = v
        self._rerender()

    @property
    def cursor_width(self) -> int:
        """Get cursor width."""
        return self._cursor_width
    
    @cursor_width.setter
    def cursor_width(self, v: int) -> None:
        """Set cursor width."""
        self._cursor_width = v
        self._require_rerender()

    @property
    def cursor_color(self) -> pygame.Color:
        """Get cursor color."""
        return self._cursor_color
    
    @cursor_color.setter
    def cursor_color(self, v: pygame.Color) -> None:
        """Set cursor color."""
        self._cursor_color = v
        self._require_rerender()

    @property
    def cursor_blink_interval(self) -> int:
        """Get cursor blink interval."""
        return self._cursor_blink_interval
    
    @cursor_blink_interval.setter
    def cursor_blink_interval(self, v: int) -> None:
        """Set cursor blink interval."""
        self._cursor_blink_interval = v

    def update(self, events: List[pygame.event.Event]) -> None:
        """
        Update the visualizer with new events.
        
        Args:
            events: List of pygame events to process
        """
        self._manager.update(events)
        self._rerender()

    def _require_rerender(self) -> None:
        """Mark that a rerender is required."""
        self._surface = pygame.Surface((0, 0))

    def _rerender(self) -> None:
        """Rerender the text input surface."""
        if self._surface.get_size() == (0, 0):
            text_surface = self._font_object.render(
                self._manager.value,
                self._antialias,
                self._font_color
            )
            self._surface = pygame.Surface(
                (text_surface.get_width() + self._cursor_width, text_surface.get_height())
            )
            self._surface.fill((255, 255, 255))
            self._surface.blit(text_surface, (0, 0))
            
            if self._cursor_visible:
                cursor_y = text_surface.get_height() // 2 - self._cursor_width // 2
                pygame.draw.rect(
                    self._surface,
                    self._cursor_color,
                    (text_surface.get_width(), cursor_y, self._cursor_width, self._cursor_width)
                )


######################################
#  The example from the repo README: #
######################################

if __name__ == "__main__":
    pygame.init()

    # No arguments needed to get started
    textinput = TextInputVisualizer()

    # But more customization possible: Pass your own font object
    font = pygame.font.SysFont("Consolas", 55)
    # Create own manager with custom input validator
    manager = TextInputManager(validator = lambda input: len(input) <= 5)
    # Pass these to constructor
    textinput_custom = TextInputVisualizer(manager=manager, font_object=font)
    # Customize much more
    textinput_custom.cursor_width = 4
    textinput_custom.cursor_blink_interval = 400 # blinking interval in ms
    textinput_custom.antialias = False
    textinput_custom.font_color = (0, 85, 170)

    screen = pygame.display.set_mode((1000, 200))
    clock = pygame.time.Clock()

    # Pygame now allows natively to enable key repeat:
    pygame.key.set_repeat(200, 25)

    while True:
        screen.fill((225, 225, 225))

        events = pygame.event.get()

        # Feed it with events every frame
        textinput.update(events)
        textinput_custom.update(events)

        # Get its surface to blit onto the screen
        screen.blit(textinput.surface, (10, 10))
        screen.blit(textinput_custom.surface, (10, 50))

        # Modify attributes on the fly - the surface is only rerendered when .surface is accessed & if values changed
        textinput_custom.font_color = [(c+10)%255 for c in textinput_custom.font_color]

        # Check if user is exiting or pressed return
        for event in events:
            if event.type == pygame.QUIT:
                exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                print(f"User pressed enter! Input so far: {textinput.value}")

        pygame.display.update()
        clock.tick(30)

