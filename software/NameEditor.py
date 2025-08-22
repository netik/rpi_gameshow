"""
Player name editor modal for the game show application.

This module provides a modal dialog for editing player names during gameplay.
It allows users to navigate between different player name fields and save
changes to the game state.
"""

import pygame
import ptext
import pygame_textinput

import game_config as config
from GameState import GameState
from Context import Context
from drawutil import drawtext


class NameEditor:
    """
    Modal dialog for editing player names.
    
    This class provides a user interface for editing the names of all players
    in the game. It supports keyboard navigation between fields and saves
    changes to the game state.
    """
    
    # Class-level constants
    INPUT_FONT_SIZE: int = 60
    INPUTS_OFFSET: int = 150  # Offset from top of modal where inputs begin
    LABEL_OFFSET: int = 100   # Offset from top of modal where labels begin
    
    def __init__(self, context: Context) -> None:
        """
        Initialize the name editor modal.
        
        Args:
            context: Game context containing screen and player data
        """
        self.context = context
        
        # Ensure screenInfo is initialized
        if self.context.screenInfo is None:
            self.context.screenInfo = pygame.display.Info()
            
        self.width = context.screenInfo.current_w * 0.15  # 85% total
        self.height = context.screenInfo.current_h * 0.10  # 75% total
        
        # Setup fonts
        self.context.load_font("namefont", "RobotoCondensed-Bold.ttf", self.INPUT_FONT_SIZE)    

        self.input_height = context.fonts["namefont"].get_height()
        self.input_spacing = self.input_height * 2  # Spacing between inputs

    def draw_modal(self) -> None:
        """Draw the modal background and structure."""
        # TODO: Implement modal drawing if needed

    def run(self) -> None:
        """
        Run the name editor modal.
        
        This method handles the main interaction loop for editing player names.
        It processes keyboard input, manages navigation between fields, and
        saves changes to the game state.
        """
        self.context.state = GameState.INPUT

        # Which name we are editing (0-3 for 4 players)
        editing = 0

        # Draw a modal box at 85% of the screen. Stop the clock.
        self.context.state = GameState.SETUP

        # Inside modal
        pygame.draw.rect(
            self.context.screen,
            (60, 60, 60),
            (
                self.width,
                self.height,
                self.context.screenInfo.current_w - (self.width * 2),
                self.context.screenInfo.current_h - (self.height * 2),
            ),
        )

        # Outside edge
        pygame.draw.rect(
            self.context.screen,
            (210, 0, 100),
            (
                self.width,
                self.height,
                self.context.screenInfo.current_w - (self.width * 2),
                self.context.screenInfo.current_h - self.height * 2,
            ),
        )

        # Start a bit inset in the modal
        xpos = self.width + 60

        # Center the title
        ptext.draw(
            "Edit Player Names (ESC to exit)",
            centerx=self.context.screenInfo.current_w / 2,
            centery=self.height + self.input_height - 10,
            fontname="fonts/RobotoCondensed-Bold.ttf",
            fontsize=self.INPUT_FONT_SIZE - 20
        )

        for i in range(0, config.PLAYERS):
            # Input box - grey until edit is active
            pygame.draw.rect(
                self.context.screen,
                config.THEME_COLORS["name_input_inactive_bg"],
                (
                    xpos - 4,
                    self.height + self.INPUTS_OFFSET + (i * self.input_spacing),
                    self.context.screenInfo.current_w - (self.width * 2) - 120,
                    self.input_height,
                ),
            )

            # Input label
            drawtext(
                self.context,
                "robo36",
                f"Player {(i+1)}",
                xpos,
                self.height + self.LABEL_OFFSET + (i * self.input_spacing),
                config.THEME_COLORS["name_input_modal_fg"],
                config.THEME_COLORS["name_input_modal_bg"],
            )

            # Player name
            drawtext(
                self.context,
                "namefont",
                self.context.player_names[i],
                xpos,
                self.height + self.INPUTS_OFFSET + (i * self.input_spacing),
                config.THEME_COLORS["name_input_inactive_fg"],
                config.THEME_COLORS["name_input_inactive_bg"]
            )

        # This manager allows 10 char names
        limit_10 = lambda x: len(x) <= 10  
        textmanager = pygame_textinput.TextInputManager(validator=limit_10)
        
        def make_textinput() -> pygame_textinput.TextInputVisualizer:
            """Create a new text input visualizer with current settings."""
            return pygame_textinput.TextInputVisualizer(
                manager=textmanager,
                font_color=config.THEME_COLORS["name_input_active_fg"],
                cursor_color=config.THEME_COLORS["name_input_cursor"],
                cursor_blink_interval=500,
                font_object=self.context.fonts["namefont"],
            )

        textinput = make_textinput()

        textinput.value = self.context.player_names[editing]
        textmanager.cursor_pos = len(self.context.player_names[editing])

        pygame.key.set_repeat(200, 25)
        clock = pygame.time.Clock()
        
        while True:
            # Clear the text input box, make it grey and put the text back.
            pygame.draw.rect(
                self.context.screen,
                config.THEME_COLORS["name_input_active_bg"],
                (
                    xpos - 4,
                    self.height + self.INPUTS_OFFSET + (editing * self.input_spacing),
                    self.context.screenInfo.current_w - (self.width * 2) - 120,
                    self.input_height
                )
            )
            
            events = pygame.event.get()
            # Pass all of the events to textinput for input handling
            textinput.update(events)

            # See if we care about any of the events that just fired
            for event in events:
                if event.type == pygame.QUIT:
                    print("Quitting..")
                    if self.context.serial_port:
                        print("Closing serial port")
                        self.context.serial_port.close()
                    pygame.quit()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.context.state = GameState.IDLE
                    self.context.player_names[editing] = textinput.value.strip()
                    self.context.save()
                    return
                
                if event.type == pygame.KEYDOWN and (
                    event.key
                    in (pygame.K_UP, pygame.K_DOWN, pygame.K_RETURN, pygame.K_TAB)
                ):
                    # Store the old data
                    self.context.player_names[editing] = textinput.value.strip()
                    self.context.save()

                    # Clear the text input box, make it grey and put the text back.
                    pygame.draw.rect(
                        self.context.screen,
                        config.THEME_COLORS["name_input_inactive_bg"],
                        (
                            xpos - 4,
                            self.height + self.INPUTS_OFFSET + (editing * self.input_spacing),
                            self.context.screenInfo.current_w - (self.width * 2) - 120,
                            self.input_height
                        )
                    )

                    drawtext(
                        self.context,
                        "namefont",
                        self.context.player_names[editing],
                        xpos,
                        self.height + self.INPUTS_OFFSET + (editing * self.input_spacing),
                        config.THEME_COLORS["name_input_inactive_fg"],
                        config.THEME_COLORS["name_input_inactive_bg"]
                    )

                    # Move to the next row or go up if requested
                    if event.key == pygame.K_UP:
                        self.context.player_names[editing] = textinput.value.strip()
                        editing = editing - 1

                    if event.key in (pygame.K_DOWN, pygame.K_RETURN, pygame.K_TAB):
                        self.context.player_names[editing] = textinput.value.strip()
                        editing = editing + 1

                    # Wrap around player indices
                    if editing > 3:
                        editing = 0

                    if editing < 0:
                        editing = 3

                    # Get us a new object for this row
                    del textinput
                    textinput = make_textinput()

                    textinput.value = self.context.player_names[editing]
                    textmanager.cursor_pos = len(self.context.player_names[editing])

                    # Break so we don't overprocess events
                    break

                # Clear the region
                pygame.draw.rect(
                    self.context.screen,
                    (30, 30, 30),
                    (
                        xpos-4,
                        self.height + self.INPUTS_OFFSET + (editing * self.input_spacing),
                        self.context.screenInfo.current_w - (self.width * 2) - 120,
                        self.input_height,
                    ),
                )

            # Blit its surface onto the screen
            # Use the original positioning to maintain compatibility
            self.context.screen.blit(
                textinput.surface,
                (xpos, self.height + self.INPUTS_OFFSET + (editing * self.input_spacing)),
            )

            clock.tick(30)
            pygame.display.update()
