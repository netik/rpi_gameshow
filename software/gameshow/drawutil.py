
def drawtext(context, font_name, text, xpos, ypos, fg_color, bg_color):
    """blit a string of text to the screen at a specific location and with a specific font

    Args:
        context (GameContext): Game Context
        font_name (str): name of font to use
        text (str): text to display
        xpos (number): xpos coordinate
        ypos (number): ypos coordinate
        fg_color (color): foreground color
        bg_color (color): background color
    """
    text_surface = context.fonts[font_name].render(text, True, fg_color, bg_color)

    context.screen.blit(text_surface, (xpos, ypos))

