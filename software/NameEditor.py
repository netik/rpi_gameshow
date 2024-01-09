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
    input_height = 80
    input_spacing = 200  # spacing between inputs
    inputs_offset = 150  # offset from top of modal where inputs begin
    label_offset = 100  # offset from top of modal where labels begin

    def __init__(self, context):
        self.context = context
        self.width = context.screenInfo.current_w * 0.15  # 85% total
        self.height = context.screenInfo.current_h * 0.10  # 75% total

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
            centery=self.height + 50,
            fontname="fonts/RobotoCondensed-Bold.ttf",
            fontsize=50,
        )

        for i in range(0, config.PLAYERS):
            # input box - grey until edit is active
            pygame.draw.rect(
                self.context.screen,
                (60, 60, 60),
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
                (255, 255, 255),
                (210, 0, 100),
            )

            # player name
            drawtext(
                self.context,
                "robo50",
                self.context.player_names[i],
                xpos,
                self.height + self.inputs_offset + (i * self.input_spacing),
                (255, 255, 0),
                (60, 60, 60),
            )

        textmanager = pygame_textinput.TextInputManager()
        input_font = pygame.font.Font("fonts/RobotoCondensed-Bold.ttf", 50)

        textinput = pygame_textinput.TextInputVisualizer(
            manager=textmanager,
            font_color=(255, 255, 0),
            cursor_color=(255, 255, 255),
            font_object=input_font,
        )

        textinput.value = self.context.player_names[editing]
        textmanager.cursor_pos = len(self.context.player_names[editing])

        pygame.key.set_repeat(200, 25)

        while True:
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

                # Feed it with events every frame
                if event.type == pygame.KEYUP and (
                    event.key
                    in (pygame.K_UP, pygame.K_DOWN, pygame.K_RETURN, pygame.K_TAB)
                ):
                    # store the old data
                    self.context.player_names[editing] = textinput.value.strip()
                    self.context.save()

                    # clear the text input box, make it grey and put the text back.
                    pygame.draw.rect(
                        self.context.screen,
                        (60, 60, 60),
                        (
                            xpos - 4,
                            self.height + self.inputs_offset + (editing * self.input_spacing),
                            self.context.screenInfo.current_w - (self.width * 2) - 120,
                            self.input_height,
                        ),
                    )

                    drawtext(
                        self.context,
                        "robo50",
                        self.context.player_names[editing],
                        xpos,
                        self.height + self.inputs_offset + (editing * self.input_spacing),
                        (255, 255, 0),
                        (60, 60, 60),
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

                    textinput = pygame_textinput.TextInputVisualizer(
                        manager=textmanager,
                        font_color=(255, 255, 0),
                        cursor_color=(255, 255, 255),
                        font_object=input_font,
                    )

                    textinput.value = self.context.player_names[editing]
                    textmanager.cursor_pos = len(self.context.player_names[editing])

                    # break so we don't overprocess events
                    break

                # clear the region
                pygame.draw.rect(
                    self.context.screen,
                    (30, 30, 30),
                    (
                        xpos - 4,
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

            pygame.display.update()
