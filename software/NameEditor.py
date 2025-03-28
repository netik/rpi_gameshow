import pygame
import ptext
import pygame_textinput  # from https://github.com/Nearoo/pygame-text-input

import config
from GameState import GameState
from drawutil import drawtext

class NameEditor:
    """
    NameEditor is a modal that allows the user to edit the player names.
    """
    input_height = None
    input_font_size = 60
    input_spacing = None # will compute after font loaded
    inputs_offset = 150  # offset from top of modal where inputs begin
    label_offset = 100  # offset from top of modal where labels begin
    
    def __init__(self, context):
        self.context = context
        self.width = context.screenInfo.current_w * 0.15  # 85% total
        self.height = context.screenInfo.current_h * 0.10  # 75% total
        
        # setup fonts
        self.context.load_font("namefont", "RobotoCondensed-Bold.ttf", self.input_font_size)    

        self.input_height = context.fonts["namefont"].get_height()
        self.input_spacing = self.input_height * 2  # spacing between inputs

    def draw_modal(self):
        pass

    def run(self):
        self.context.state = GameState.INPUT

        # which name we are editing
        editing = 0

        # draw a modal box at 85% of the screen. Stop the clock.
        self.context.state = GameState.SETUP

        # inside modal
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

        # outside edge
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

        # start a bit inset in the modal
        xpos = self.width + 60

        # Center the title
        ptext.draw(
            "Edit Player Names (ESC to exit)",
            centerx=self.context.screenInfo.current_w / 2,
            centery=self.height + self.input_height - 10,
            fontname="fonts/RobotoCondensed-Bold.ttf",
            fontsize=self.input_font_size - 20
        )

        for i in range(0, config.PLAYERS):
            # input box - grey until edit is active
            pygame.draw.rect(
                self.context.screen,
                config.THEME_COLORS["name_input_inactive_bg"],
                (
                    xpos - 4,
                    self.height + self.inputs_offset + (i * self.input_spacing),
                    self.context.screenInfo.current_w - (self.width * 2) - 120,
                    self.input_height,
                ),
            )

            # input label
            drawtext(
                self.context,
                "robo36",
                f"Player {(i+1)}",
                xpos,
                self.height + self.label_offset + (i * self.input_spacing),
                config.THEME_COLORS["name_input_modal_fg"],
                config.THEME_COLORS["name_input_modal_bg"],
            )

            # player name
            drawtext(
                self.context,
                "namefont",
                self.context.player_names[i],
                xpos,
                self.height + self.inputs_offset + (i * self.input_spacing),
                config.THEME_COLORS["name_input_inactive_fg"],
                config.THEME_COLORS["name_input_inactive_bg"]
            )

        # this manager allows 10 char names
        limit_10 = lambda x: len(x) <= 10  
        textmanager = pygame_textinput.TextInputManager(validator=limit_10)
        make_textinput = lambda: pygame_textinput.TextInputVisualizer(
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

            # clear the text input box, make it grey and put the text back.
            pygame.draw.rect(
                self.context.screen,
                config.THEME_COLORS["name_input_active_bg"],
                (
                    xpos - 4,
                    self.height + self.inputs_offset + (editing * self.input_spacing),
                    self.context.screenInfo.current_w - (self.width * 2) - 120,
                    self.input_height
                )
            )
            events = pygame.event.get()
            # pass all of the events to textinput for input handling
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
                    # store the old data
                    self.context.player_names[editing] = textinput.value.strip()
                    self.context.save()

                    # clear the text input box, make it grey and put the text back.
                    pygame.draw.rect(
                        self.context.screen,
                        config.THEME_COLORS["name_input_inactive_bg"],
                        (
                            xpos - 4,
                            self.height + self.inputs_offset + (editing * self.input_spacing),
                            self.context.screenInfo.current_w - (self.width * 2) - 120,
                            self.input_height
                        )
                    )

                    drawtext(
                        self.context,
                        "namefont",
                        self.context.player_names[editing],
                        xpos,
                        self.height + self.inputs_offset + (editing * self.input_spacing),
                        config.THEME_COLORS["name_input_inactive_fg"],
                        config.THEME_COLORS["name_input_inactive_bg"]
                    )

                    # move to the next row or go up if requested
                    if event.key == pygame.K_UP:
                        self.context.player_names[editing] = textinput.value.strip()
                        editing = editing - 1

                    if event.key in (pygame.K_DOWN, pygame.K_RETURN, pygame.K_TAB):
                        self.context.player_names[editing] = textinput.value.strip()
                        editing = editing + 1

                    if editing > 3:
                        editing = 0

                    if editing < 0:
                        editing = 3

                    # get us a new object for this row
                    del textinput

                    textinput = make_textinput()

                    textinput.value = self.context.player_names[editing]
                    textmanager.cursor_pos = len(self.context.player_names[editing])

                    # break so we don't overprocess events
                    break

                # clear the region
                pygame.draw.rect(
                    self.context.screen,
                    (30, 30, 30),
                    (
                        xpos-4,
                        self.height + self.inputs_offset + (editing * self.input_spacing),
                        self.context.screenInfo.current_w - (self.width * 2) - 120,
                        self.input_height,
                    ),
                )

            # Blit its surface onto the screen
            # thre is a slight problem here that the text drawing is off?
            self.context.screen.blit(
                textinput.surface,
                (xpos, self.height + self.inputs_offset + (editing * self.input_spacing)),
            )

            clock.tick(30)
            pygame.display.update()
