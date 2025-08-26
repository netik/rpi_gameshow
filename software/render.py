# render.py

import math
import pygame
import pygame.gfxdraw
import ptext
import game_config as config
from drawutil import drawtext
from particleutil import spawn_exploding_particles
from GameState import GameState
from helpinfo import HELP_KEYS

def clear_display(context):
    context.screen.fill((0, 0, 0))


def draw_leds(context):
    """
    Draw debug LED indicators on screen for development and testing.
    
    This function renders visual representations of the physical LED states
    on the screen when DEBUG_LEDS is enabled. It shows the current state
    of each player's LED indicator with colored circles.

    Args:
        context (Context): Current game context containing LED state information

    Note:
        - Only renders when config.DEBUG_LEDS is True
        - Shows LED states as colored circles (blue for on, dark gray for off)
        - Positioned on the left side of the screen for easy visibility
        - Useful for debugging when running without physical hardware
    """
    if config.DEBUG_LEDS is False:
        return

    xpos = 20
    ypos = 300
    drawtext(
        context, "robo36", "(debug) LEDs:", xpos, ypos - 50, (255, 255, 255), (0, 0, 0)
    )

    pygame.draw.rect(
        context.screen, (255, 255, 255), (xpos, ypos, config.PLAYERS * 85, 80), 2
    )

    for k in range(0, config.PLAYERS):
        if context.led_state[k]:
            color = (0, 0, 255)
        else:
            color = (20, 20, 20)

        pygame.draw.circle(
            context.screen, color, (xpos + 50, ypos + 40), 30, 0
        )  # filled
        xpos = xpos + 80


def draw_scores(context):
    """
    Draw player scores and names in the score display area.
    
    This function renders the player score display showing each player's name
    and current score. The display adapts to the invert_display setting,
    positioning scores either at the top or bottom of the screen.

    Args:
        context (Context): Current game context containing player scores and names

    Note:
        - Supports both normal and inverted display modes
        - Shows player names and scores in themed colors
        - Highlights the currently buzzing player with different colors
        - Draws separators between player areas
        - Uses theme colors for consistent visual appearance
        - Responsive layout that adapts to screen dimensions
    """
    i = 1

    if context.invert_display:
        top_y = 0
    else:
        top_y = context.screen_info.current_h - 240

    while i < config.PLAYERS + 1:
        if context.invert_display:
            # background
            pygame.draw.rect(
                context.screen,
                config.THEME_COLORS["buzzed_in_bg"] if context.player_buzzed_in == (i - 1) else config.THEME_COLORS["player_area_bg"],
                (
                    (i - 1) * context.screen_info.current_w / config.PLAYERS,
                    0,
                    (context.screen_info.current_w / config.PLAYERS),
                    240,
                ),
            )

            # player name
            ptext.draw(
                context.player_names[i - 1],
                centerx=(context.screen_info.current_w / 8 * ((i * 2) - 1)),
                centery=60,
                color=config.THEME_COLORS["buzzed_in_fg"] if context.player_buzzed_in == (i - 1) else config.THEME_COLORS["player_name_fg"],
                fontname="fonts/RobotoCondensed-Bold.ttf",
                fontsize=70,
                shadow=(1,1) if context.player_buzzed_in != (i - 1) else None 
            )

            # score
            ptext.draw(
                f"{context.scores[i - 1]:d}",
                centerx=(context.screen_info.current_w / 8 * ((i * 2) - 1)),
                centery=170,
                color=config.THEME_COLORS["buzzed_in_fg"] if context.player_buzzed_in == (i - 1) else config.THEME_COLORS["player_score_fg"],
                fontname="fonts/RobotoCondensed-Bold.ttf",
                fontsize=120,
                shadow=(1,1) if context.player_buzzed_in != (i - 1) else None
            )

            # divider
            if i < config.PLAYERS:
                pygame.draw.line(
                    context.screen,
                    config.THEME_COLORS["separator"],
                    ((context.screen_info.current_w / 4 * i - 2), 0),
                    ((context.screen_info.current_w / 4 * i - 2), 240),
                    width=3,
                )
        else:
            # background
            pygame.draw.rect(
                context.screen,
                config.THEME_COLORS["buzzed_in_bg"] if context.player_buzzed_in == (i - 1) else config.THEME_COLORS["player_area_bg"],
                (
                    (i - 1) * context.screen_info.current_w / 4,
                    top_y,
                    (context.screen_info.current_w / 4),
                    context.screen_info.current_h,
                ),
            )

            # player name
            ptext.draw(
                context.player_names[i - 1],
                centerx=(context.screen_info.current_w / 8 * ((i * 2) - 1)),
                centery=top_y + 50,
                color=config.THEME_COLORS["buzzed_in_fg"] if context.player_buzzed_in == (i - 1) else config.THEME_COLORS["player_name_fg"],
                fontname="fonts/RobotoCondensed-Bold.ttf",
                fontsize=70,
                shadow=(1,1) if context.player_buzzed_in != (i - 1) else None
            )

            # score
            ptext.draw(
                f"{context.scores[i - 1]:d}",
                centerx=(context.screen_info.current_w / 8 * ((i * 2) - 1)),
                centery=top_y + 170,
                color=config.THEME_COLORS["buzzed_in_fg"] if context.player_buzzed_in == (i - 1) else config.THEME_COLORS["player_score_fg"],
                fontname="fonts/RobotoCondensed-Bold.ttf",
                fontsize=120,
                shadow=(1,1) if context.player_buzzed_in != (i - 1) else None
            )

            # divider
            if i < config.PLAYERS:
                pygame.draw.line(
                    context.screen,
                    config.THEME_COLORS["separator"],
                    (
                        (context.screen_info.current_w / 4 * i - 2),
                        top_y,
                    ),
                    (
                        (context.screen_info.current_w / 4 * i - 2),
                        context.screen_info.current_h,
                    ),
                    width=3,
                )

        i += 1

    if context.invert_display:
        # draw separator under scores
        pygame.draw.line(
            context.screen,
            config.THEME_COLORS["separator"],
            (0, 240),
            (context.screen_info.current_w, 240),
            width=2,
        )
    else:
        # draw separateor above scores
        pygame.draw.line(
            context.screen,
            config.THEME_COLORS["separator"],
            (0, top_y),
            (context.screen_info.current_w, top_y),
            width=2,
        )

def draw_title(context):
    """
    Draw the game title and logo.
    
    This function renders the game title text and logo images. The layout
    adapts to the invert_display setting, positioning elements either at
    the top or bottom of the screen.

    Args:
        context (Context): Current game context containing display information

    Note:
        - Loads and scales logo image based on LOGO_RESIZE_FACTOR
        - Supports both normal and inverted display modes
        - Logo is drawn on both left and right sides for symmetry
        - Title text is centered between the logos
        - Uses theme colors for consistent appearance
        - Only draws logo when DRAW_LOGO is enabled
    """
    img = pygame.image.load(config.LOGO).convert_alpha()
    line_padding = 60
    resized_img = pygame.transform.scale(img, (int(img.get_width() * config.LOGO_RESIZE_FACTOR), int(img.get_height() * config.LOGO_RESIZE_FACTOR)))

    if context.invert_display:
        # logo left and right on bottom
        if config.DRAW_LOGO:
            context.screen.blit(
                resized_img,
                (
                    line_padding,
                    context.screen_info.current_h - resized_img.get_height() - line_padding,
                ),
            )
            context.screen.blit(
                resized_img,
                (
                    context.screen_info.current_w - resized_img.get_width() - line_padding,
                    context.screen_info.current_h - resized_img.get_height() - line_padding,
                ),
            )
        # title
        ptext.draw(
            config.TITLE,
            centerx=context.screen_info.current_w / 2,
            # 35 here is a guess, given the font is 80 pixels(?) high
            centery=context.screen_info.current_h - (resized_img.get_height() / 2) - line_padding,
            color=config.THEME_COLORS["title_text"],
            fontname="fonts/RobotoCondensed-Bold.ttf",
            fontsize=70,
            shadow=(1,1),
            scolor="black"
        )
    else:
        # logo left and right on top
        if config.DRAW_LOGO:
            context.screen.blit(resized_img, (line_padding, line_padding))
            context.screen.blit(
                resized_img,
                (   
                    context.screen_info.current_w - resized_img.get_width() - line_padding,
                    line_padding,
                ),
            )

        ptext.draw(
            config.TITLE,
            centerx=context.screen_info.current_w / 2,
            centery=line_padding + (resized_img.get_height() / 2),
            color=config.THEME_COLORS["title_text"],
            fontname="fonts/RobotoCondensed-Bold.ttf",
            fontsize=70,
            shadow=(1,1),
            scolor="black"
        )


def draw_splash(context):
    """
    Display splash screen and wait for user input.
    
    This function shows a splash screen image and pauses the game until
    the user presses any key. It's used for game startup and can be
    triggered manually during gameplay.

    Args:
        context (Context): Current game context containing display information

    Note:
        - Loads and displays splash image from config.SPLASH
        - Centers the image on screen
        - Blocks execution until any key is pressed
        - Transitions game state to SPLASH during display
        - Returns to IDLE state after keypress
        - Calls render_all() to refresh the display
        - Uses pygame.display.flip() for immediate visual feedback
    """
    print("Drawing splash screen and pausing. Press any key to resume.")
    context.state = GameState.SPLASH
    clear_display(context)

    img = pygame.image.load(config.SPLASH)
    context.screen.blit(
        img,
        (
            context.screen_info.current_w / 2 - img.get_width() / 2,
            context.screen_info.current_h / 2 - img.get_width() / 2,
        ),
    )
    pygame.display.flip()

    # block for keypress
    waiting = True
    while waiting:
        event = pygame.event.wait()
        if event.type == pygame.KEYDOWN:
            waiting = False

    pygame.display.flip()

    context.state = GameState.IDLE
    render_all(context)


def draw_help(context):
    """
    Display help screen with game controls and instructions.
    
    This function renders a modal help screen showing all available
    keyboard shortcuts and their functions. It pauses the game until
    the user dismisses it with any keypress.

    Args:
        context (Context): Current game context containing display information

    Note:
        - Creates a modal dialog box centered on screen
        - Lists all keyboard shortcuts with descriptions
        - Uses theme colors for consistent appearance
        - Blocks execution until any key is pressed
        - Transitions game state to HELP during display
        - Returns to IDLE state after dismissal
        - Calls render_all() to refresh the display
        - Help text includes scoring, timing, and game control shortcuts
    """

    # draw a modal box at 85% of the screen. Stop the clock.
    context.state = GameState.HELP

    width = context.screen_info.current_w * 0.30
    height = context.screen_info.current_h * 0.75

    xtop = (context.screen_info.current_w - width)  / 2
    ytop = (context.screen_info.current_h - height)  / 2
    
    # inside box (fill)
    pygame.draw.rect(
        context.screen,
        config.THEME_COLORS['help_bg'],
        (
            xtop,
            ytop,
            width,
            height
        ),
    )

    # outside perimeter (line)
    pygame.draw.rect(
        context.screen,
        config.THEME_COLORS['help_border'],
        (
            xtop,
            ytop,
            width,
            height
        ),
        2,
    )

    xpos = xtop + 60
    ypos = ytop + 30

    # draw help text
    ptext.draw(
        "HELP",
        color=config.THEME_COLORS["help_title"],
        centerx=(xtop + (width/2)),
        centery=ypos,
        fontname="fonts/RobotoCondensed-Bold.ttf",
        fontsize=50,
    )

    ypos = ypos + 60

    for k in HELP_KEYS:
        drawtext(context, 
                 "robo24", 
                 k["key"], 
                 xpos, 
                 ypos,             
                 config.THEME_COLORS["help_fg"],
                 config.THEME_COLORS["help_bg"])

        drawtext(
            context,
            "robo24",
            k["text"],
            xpos + 200,
            ypos,
            config.THEME_COLORS["help_fg"],
            config.THEME_COLORS["help_bg"]
        )
        ypos = ypos + context.fonts["robo24"].get_height()

    ypos = ypos + context.fonts["robo24"].get_height()

    ptext.draw(
        "Hit any Key to continue",
        color=config.THEME_COLORS["help_title"],
        centerx=(xtop + (width/2)),
        centery=ypos,
        fontname="fonts/RobotoCondensed-Bold.ttf",
        fontsize=16,
    )

    pygame.display.flip()

    # block for keypress
    waiting = True
    while waiting:
        event = pygame.event.wait()
        if event.type == pygame.KEYDOWN:
            waiting = False

    pygame.display.flip()

    context.state = GameState.IDLE
    render_all(context)


def draw_state(context):
    """
    Draw the current game state text on screen.
    
    This function displays text indicating the current game state
    (e.g., "TIME'S UP!", "STOPPED", or nothing for running games).
    The text is positioned below the clock display.

    Args:
        context (Context): Current game context containing game state

    Note:
        - Shows different text based on current GameState
        - TIMEUP state displays "TIME'S UP!"
        - IDLE state displays "STOPPED"
        - RUNNING state shows no text
        - Uses theme colors for consistent appearance
        - Positioned below the clock display area
        - Text includes shadow effects for better visibility
    """
    statestr = ""

    if context.state == GameState.TIMEUP:
        statestr = "TIME'S UP!"

    if context.state == GameState.IDLE:
        statestr = "STOPPED"

    if context.state == GameState.RUNNING:
        statestr = ""

    message_y = context.screen_info.current_h / 3 + 260

    ptext.draw(
        statestr,
        centerx=context.screen_info.current_w / 2,
        centery=message_y,
        color=config.THEME_COLORS["state_text"],
        fontname="fonts/RobotoCondensed-Bold.ttf",
        fontsize=90,
        shadow=(1,1),
        scolor="black"
    )


def draw_clock(context):
    """
    Draw the large countdown clock in the center of the screen.
    
    This function renders the main game timer display showing minutes and seconds
    remaining. It also calls draw_state() to show the current game state below
    the clock. The clock is only displayed when CLOCK_ENABLED is True.

    Args:
        context (Context): Current game context containing clock and game state

    Note:
        - Converts milliseconds to minutes:seconds format
        - Centers the clock on screen
        - Uses large font (200pt) for visibility
        - Includes shadow effects for better readability
        - Only renders when CLOCK_ENABLED is True
        - Calls draw_state() to show game state below clock
        - Positioned in the upper third of the screen
    """
    minutes = math.floor(context.clock / 60000)
    sec = int((context.clock - (minutes * 60000)) / 1000)

    draw_state(context)

    if config.CLOCK_ENABLED == False:
        return

    # draw clock
    ptext.draw(
        f"{minutes:d}:{sec:02d}",
        centerx=context.screen_info.current_w / 2,
        centery=context.screen_info.current_h / 3 + 100,
        color=config.THEME_COLORS["clock_text"],
        fontname="fonts/RobotoCondensed-Bold.ttf",
        fontsize=200,
        shadow=(1,1),
        scolor="black"
    )


def draw_gamestate(context):
    """
    Draw game state-specific information on screen.
    
    This function renders information that changes based on the current
    game state. Currently, it shows the "buzzed in" message when a
    player has successfully buzzed in.

    Args:
        context (Context): Current game context containing player and game state

    Note:
        - Only renders content when state is BUZZIN
        - Shows player name with "Buzzed in!" message
        - Message position adapts to invert_display setting
        - Uses large font (150pt) for visibility
        - Includes shadow effects for better readability
        - Positioned either at top or bottom based on display orientation
    """
    if context.state == GameState.BUZZIN:
        # draw their name
        msg = f"{context.player_names[context.player_buzzed_in]} Buzzed in!"

        if context.invert_display:
            message_y = 125
        else:
            message_y = context.screen_info.current_h - 125
      
        ptext.draw(
            msg,
            centerx=context.screen_info.current_w / 2,
            centery=message_y,
            shadow=(1,1),
            color=config.THEME_COLORS["buzzed_in_message_fg"],
            fontname="fonts/RobotoCondensed-Bold.ttf",
            fontsize=150
        )


def draw_radial(context, color1, color2, width=40):
    """
    Draw a radial circus-tent like animated background.
    
    This function creates an animated radial background effect using
    triangular segments that rotate around a center point. It's used
    to create visual interest when RENDER_BACKGROUND is enabled.

    Args:
        context (Context): Current game context containing display information
        color1 (pygame.Color): First color for alternating segments
        color2 (pygame.Color): Second color for alternating segments
        width (int, optional): Width of each radial segment. Defaults to 40.

    Note:
        - Creates animated effect by rotating segments over time
        - Uses pygame.gfxdraw.filled_polygon for smooth rendering
        - Segments extend beyond screen boundaries for full coverage
        - Colors alternate between segments for visual variety
        - Animation speed is tied to pygame time for consistent motion
        - Creates a circus-tent or sunburst visual effect
    """
    center = [context.screen_info.current_w/2, context.screen_info.current_h+100]
    w = context.screen_info.current_w
    h = context.screen_info.current_h
    # radius = math.sqrt((w/2)**2 + (h/2)**2)  # maximum distance to the window boundary
    radius = w * 3
    i = 0
    color_flip=False
    while i < max(w, h):
        if color_flip:
            color = color1
        else:
            color = color2
        
        # gradient
        #color = (
        #    color1[0] * (1 - r) + color2[0] * r,
        #    color1[1] * (1 - r) + color2[1] * r,
        #    color1[2] * (1 - r) + color2[2] * r
        #)

        angle = 2 * math.pi * i / max(w, h) + pygame.time.get_ticks() / 100 / 360
        end_pos = (center[0] + radius * math.cos(angle), center[1] + radius * math.sin(angle))

        next_angle = 2 * math.pi * (i+width) / max(w, h) + pygame.time.get_ticks() / 100 / 360
        next_end_pos = (center[0] + radius * math.cos(next_angle + 0.1), center[1] + radius * math.sin(next_angle + 0.1))

        # draw a triangle that ends outside the viewport to get a sort of circus-tent look
        pygame.gfxdraw.filled_polygon(context.screen, [center, end_pos, next_end_pos], color)
        color_flip = not color_flip
        i = i + width


def render_background(context):
    """
    Render the animated background if enabled.
    
    This function conditionally renders the radial background effect
    based on the RENDER_BACKGROUND configuration setting.

    Args:
        context (Context): Current game context containing display information

    Note:
        - Only renders when config.RENDER_BACKGROUND is True
        - Uses theme colors bg_one and bg_two for the effect
        - Calls draw_radial() to create the animated background
        - Background provides visual interest without interfering with gameplay
    """
    if not config.RENDER_BACKGROUND:
        return

    color1 = config.THEME_COLORS["bg_one"]
    color2 = config.THEME_COLORS["bg_two"]    
    draw_radial(context, color1, color2)


def draw_particles(context):
    """
    Draw and update particle effects on screen.
    
    This function renders all active particle effects and updates their
    physics simulation. Particles are used for visual feedback during
    game events like player buzz-ins.

    Args:
        context (Context): Current game context containing particle group

    Note:
        - Draws all particles in the particle group
        - Updates particle physics with delta time
        - Particles are used for explosion effects and visual feedback
        - Delta time is calculated from pygame clock for smooth animation
        - Particle system is managed by the particleutil module
    """
    context.particle_group.draw(context.screen)

    # update
    dt = context.pyclock.tick() / 1000
    context.particle_group.update(dt)

def draw_testmode(context):
    """
    Draws the test mode indicators on the screen.

    Args:
        context (Context): The game context containing display information.
    """
    if not context.button_test:
        return

    xpos = 20
    drawtext(
        context, "robo36", "Button Test ON", xpos, 400, (255, 255, 255), (0, 0, 0)
    )

def render_all(context):
    """
    Render the complete game screen for one frame.
    
    This function orchestrates the rendering of all game elements in
    the correct order. It clears the screen, draws background, UI elements,
    game state, particles, and debug information, then updates the display.

    Args:
        context (Context): Current game context containing all game state and display info

    Note:
        - Clears the screen at the start of each frame
        - Renders elements in back-to-front order: background, title, clock, scores, game state, particles, debug LEDs
        - Only shows scores when not in BUZZIN state
        - Debug LEDs are drawn last for visibility
        - Calls pygame.display.flip() once at the end for efficient rendering
        - This is the main rendering pipeline called each frame
    """
    clear_display(context)
    render_background(context)
    draw_title(context)
    draw_clock(context)
    if context.state != GameState.BUZZIN:
        draw_scores(context)

    draw_gamestate(context)

    draw_particles(context)
    # draw LED and debugging if config.PLATFORM is not rpi
    draw_testmode(context)
    draw_leds(context)

    pygame.display.flip()


def init_game(context):
    """
    Initialize the game display, fonts, and basic game state.
    
    This function sets up the Pygame display surface based on configuration,
    loads all required fonts, and prepares the game for rendering. It handles
    different display modes (windowed, borderless, fullscreen) and platform-specific
    initialization.

    Args:
        context (Context): Game context to initialize with display and font information

    Note:
        - Creates display surface based on DISPLAY_STYLE configuration
        - Supports multiple display modes: windowed, borderless, fullscreen
        - Can target specific display monitors using DISPLAY_ID
        - Hides the mouse cursor for cleaner game appearance
        - Loads multiple font sizes for different UI elements
        - Fonts are loaded from the fonts/ directory
        - Clears the display after initialization
        - Platform-specific working directory changes for Raspberry Pi
    """
    # set display ID here via display = 1 if needed.
    context.screen = None
   
    if config.DISPLAY_STYLE == "windowed":
        # uses default display
        context.screen = pygame.display.set_mode(
            (config.DISPLAY_WINDOW_HEIGHT, config.DISPLAY_WINDOW_WIDTH), pygame.SHOWN)
        context.screen_info = pygame.display.Info()
    elif config.DISPLAY_STYLE == "borderless":
        # now let's see how big our screen is
        # and create a borderless window that's as big as the entire screen
        context.screen = pygame.display.set_mode(
            (0,0), 
            pygame.NOFRAME,
            display=config.DISPLAY_ID)
        context.screen_info = pygame.display.Info()
    elif config.DISPLAY_STYLE == "fullscreen":
        context.screen = pygame.display.set_mode(
            (0, 0), 
            pygame.FULLSCREEN, 
            display=config.DISPLAY_ID)
        context.screen_info = pygame.display.Info()
    
    print("Screen Info: ")
    print(context.screen_info)

    # hide mouse
    pygame.mouse.set_visible(False)

    clear_display(context)

    # load fonts
    context.load_font("bebas40", "BebasKai-Regular.otf", 40)
    context.load_font("robo24", "RobotoCondensed-Bold.ttf", 24)
    context.load_font("robo36", "RobotoCondensed-Bold.ttf", 36)
    context.load_font("robo50", "RobotoCondensed-Bold.ttf", 50)
    context.load_font("robo90", "RobotoCondensed-Bold.ttf", 90)
    context.load_font("robo250", "RobotoCondensed-Bold.ttf", 250)

