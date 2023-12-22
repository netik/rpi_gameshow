#!/usr/bin/env python
#
# Dirty Talk game show game show code, version 3, rPi and custom board
#

import os
import pygame
import pygame_textinput  # from https://github.com/Nearoo/pygame-text-input
import ptext
import math
import pickle
import time

# OFFLINE MODE if this is set to anything other than "rpi", we will never
# attempt to access the rPi GPIO pins and we will display a fake LED state on
# the screen
 
# numkey 1-4 on the keypad can be used to simulate buzzers
#PLATFORM = "rpi"  # Running the entire game on a raspberry pi using the onboard GPIO 
#PLATFORM = "pc"  # Running the game in dev mode on a computer, no GPIO
PLATFORM = "pcserial"  # Running on a computer with a serial connection to GPIO board (rev4)
SERIAL_DEVICE = "/dev/cu.usbserial-84440"

if PLATFORM == "rpi":
  import RPi.GPIO as GPIO

if PLATFORM == "pcserial": 
  import serial

# config
PLAYERS = 4
FPS=30
MAXCLOCK = 60000  # in microseconds!
CLOCK_STEP = 1000  # mS
CLOCKEVENT = pygame.USEREVENT + 1
SOUNDSET = 2
TITLE = "The Dirty Talk Game Show"
LOGO = "images/logo.jpg"
SPLASH = "images/dirtytalk-fs.jpg"
STATEFILE = "gamestate.pickle"

# GPIO Pinout
player_map = [16, 17, 18, 19]
reverse_map = {16: 0, 17: 1, 18: 2, 19: 3}
led_map = [20, 21, 22, 23]
led_state = [False, False, False, False]
player_names = []
sound_library = {}

# Serial port, if using one
SER = None

# set working dir
if PLATFORM == "rpi":
  os.chdir("/home/pi/src/gameshow")

    # can't hurt.
  os.system("/usr/bin/amixer set PCM -- 1000")

  # force 1/8" output no matter what
  os.system("/usr/bin/amixer cset numid-3 1")


# send a command to the serial port and wait for response
def sendSerial(cmd):
  global SER

  if PLATFORM == "pcserial":
    SER.write(cmd)
    SER.flush()
    print("sent: %s" % cmd)
    resp = SER.readline()
    print("recv: %s" % resp)
    return "OK"

#--------------------------------------
# ENUMS to represent the game state
class GameState:
    IDLE = (0,)
    RUNNING = (1,)
    BUZZIN = (2,)
    TIMEUP = (3,)
    INPUT = (4,)
    HELP = (5,)
    SETUP = 6
    SPLASH = 10

# globals
clock = MAXCLOCK
prevsec = 0
fonts = {}
colors = {}
screen = None
scores = [0, 0, 0, 0]
invert_display = True

# "attract" mode, run when game idle
blinky = 0

# game state
buzzedin = -1
state = GameState.IDLE

def button_event(channel):
    # remember the event, we will handle this on the next clock tick
    global buzzedin

    # if it's serial we can use it directly.
    if SER:
       buzzedin = channel-1
       return
    
    # if GPIO we have to map it back to the right player
    buzzedin = reverse_map[channel]

# display the LED state on the main screen for debugging
def draw_leds():
  if PLATFORM != "pc":
    return
  
  xpos = 20
  y = 250
  drawtext("robo36", "(debug) LEDs:", xpos, y-50, (255,255,255), (0,0,0))

  pygame.draw.rect(
    screen,
    (255,255,255),
    (xpos, y, PLAYERS * 85, 80),
    2
  )
    
  for k in range(0,PLAYERS):
    if led_state[k]:
        color = (0,0,255)
    else:
        color = (20,20,20)

    pygame.draw.circle(
      screen,
      color,
      (xpos + 50, y+40),
      30,
      0 # filled
    )
    xpos = xpos + 80

# set all of the LEDs to a state
def set_all_leds(state=False):
    for k in range(0,PLAYERS):
      if PLATFORM == "rpi":
        GPIO.output(led_map[k], state)

      if PLATFORM == "pcserial":
        sendSerial(b"LED %d %d\n" % ((k+1), state))

      led_state[k] = state
    
# Some hardware abstractions here so we can debug w/o the hardware
# LED abstraction
def set_led(led, state, exclusive = False):
    # print("set_led(%d, %s)" % (led, state))
    
    if exclusive:
      set_all_leds(False)

    if PLATFORM == "rpi":
      GPIO.output(led_map[led], state)

    if PLATFORM == "pcserial":
       sendSerial(b"LED %d %d\n" % ((led+1), state))

    led_state[led] = state

def setup_serial(device):
  if PLATFORM != "pcserial":
    return

  SER = serial.Serial(device, 115200, bytesize=8, parity=serial.PARITY_NONE, stopbits=1)  # open serial port
  while not SER.isOpen():
    pass
  
  print("Serial port open")
  # sleep for board to reset as it resets on open
  print("Waiting for board to reset...")

  while True:
    line = SER.readline()
    print("recv: %s" % line)
    if line == b"RESET OK\r\n":
      break

  print("Board reset")
  return SER

def setup_gpio():
    if PLATFORM != "rpi":
        return

    # Setup the GPIOs as inputs with Pull Ups since the buttons are connected to GND
    GPIO.setmode(GPIO.BCM)
    for k in player_map:
        GPIO.setup(k, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(k, GPIO.FALLING, button_event, bouncetime=50)

    for k in led_map:
        GPIO.setup(k, GPIO.OUT)

    # I have no idea where these warnings are coming from on pin 20, let's disable them.
    # maybe it's complaining because pin 20 is MOSI/SPI but we're not using that and everything works fine.
    GPIO.setwarnings(False)

    set_all_leds()

def loadfont(shortname, filename, size):
    fonts[shortname] = pygame.font.Font(os.path.join("fonts", filename), size)

def drawtext(fontshortname, text, x, y, fg, bg):
    text_surface = fonts[fontshortname].render(text, True, fg, bg)

    screen.blit(text_surface, (x, y))

def cleardisplay():
    screen.fill((0, 0, 0))

def initgame():
    global screen, screenInfo

    # init the system, get screen metrics
    # enable sound
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.mixer.init()
    pygame.init()

    screenInfo = pygame.display.Info()
    print(screenInfo)

    screen = pygame.display.set_mode(
        (screenInfo.current_w, screenInfo.current_h), pygame.FULLSCREEN
    )

    # hide mouse
    pygame.mouse.set_visible(False)

    cleardisplay

    # load fonts
    loadfont("bebas40", "BebasKai-Regular.otf", 40)
    loadfont("robo36", "RobotoCondensed-Bold.ttf", 36)
    loadfont("robo50", "RobotoCondensed-Bold.ttf", 50)
    loadfont("robo90", "RobotoCondensed-Bold.ttf", 90)
    loadfont("robo250", "RobotoCondensed-Bold.ttf", 250)

    # set player names
    for i in range(0, PLAYERS):
        player_names.append("Player %d" % (i + 1))


def initpalette():
  colors["black"] = pygame.Color(0, 0, 0)
  colors["white"] = pygame.Color(255, 255, 255)
  colors["grey"] = pygame.Color(164, 164, 164, 255)
  colors["blue"] = pygame.Color(0, 0, 200, 255)
  colors["green"] = pygame.Color(0, 200, 0, 255)
  colors["grey"] = pygame.Color(164, 164, 164, 255)
  colors["lightgrey"] = pygame.Color(200, 200, 200, 255)
  colors["pink"] = pygame.Color(255, 0, 255, 255)

def buzz_in_alert():
    global state

    # stop the clock by changing state.
    state = GameState.BUZZIN

    # play sound
    sound_library['BUZZ'].play()

    # light only that player
    set_led(buzzedin, True, True)

def draw_scores():
    i = 1
    
    while i < PLAYERS + 1:
      bgcolor = colors["black"] # black

      if buzzedin == (i-1):
        bgcolor=colors["blue"]

      if invert_display:  
        pygame.draw.rect(
          screen,
          bgcolor,
          (
            (i - 1) * screenInfo.current_w / PLAYERS,
            0,
            (screenInfo.current_w / PLAYERS),
            240,
          ),
        )

        # player name
        ptext.draw(
            player_names[i - 1],
            centerx=(screenInfo.current_w / 8 * ((i * 2) - 1)),
            centery=60,
            color=colors["lightgrey"],
            fontname="fonts/RobotoCondensed-Bold.ttf",
            fontsize=80,
        )

        # score
        ptext.draw(
            "%d" % scores[i - 1],
            centerx=(screenInfo.current_w / 8 * ((i * 2) - 1)),
            centery=170,
            color=colors["white"],
            fontname="fonts/RobotoCondensed-Bold.ttf",
            fontsize=120,
        )

        # divider
        if i < PLAYERS:
            pygame.draw.line(
                screen,
                colors["grey"],
                ((screenInfo.current_w / 4 * i - 2), 0),
                ((screenInfo.current_w / 4 * i - 2), 240),
                width = 2
            )

      else:  
        pygame.draw.rect(
          screen,
          bgcolor,
          (
            (i - 1) * screenInfo.current_w / 4,
            screenInfo.current_h / 2 + 150,
            (screenInfo.current_w / 4),
              screenInfo.current_h,
          ),
        )

        ptext.draw(
            player_names[i - 1],
            centerx=(screenInfo.current_w / 8 * ((i * 2) - 1)),
            centery=screenInfo.current_h / 2 + 200,
            color=colors["lightgrey"],
            fontname="fonts/RobotoCondensed-Bold.ttf",
            fontsize=80,
        )

        ptext.draw(
            "%d" % scores[i - 1],
            centerx=(screenInfo.current_w / 8 * ((i * 2) - 1)),
            centery=(screenInfo.current_h / 2) + 350,
            color=colors["white"],
            fontname="fonts/RobotoCondensed-Bold.ttf",
            fontsize=120,
        )
        pygame.draw.line(
            screen,
            colors["grey"],
            ((screenInfo.current_w / 4 * i - 2), screenInfo.current_h / 2 + 150),
            ((screenInfo.current_w / 4 * i - 2), screenInfo.current_h),
            width = 2
        )

      i += 1

    if invert_display:
      # draw separator under scores
      pygame.draw.line(
        screen,
        colors["grey"],
        (0, 240),
        (screenInfo.current_w, 240),
        width = 2
      )

def reset_game():
    global scores, clock, state, buzzedin
    i = 0
    while i < 4:
        scores[i] = 0
        i = i + 1
    clock = MAXCLOCK
    prevsec = 0
    state = GameState.IDLE
    buzzedin = -1

    draw_clock()

def reset_clock():
    global scores, clock, state, buzzedin
    clock = MAXCLOCK
    prevsec = 0
    state = GameState.IDLE
    buzzedin = -1

    draw_clock()


def draw_title():
    img = pygame.image.load(LOGO)
    PADDING=60

    if invert_display:
        # logo left and right
        screen.blit(img, (PADDING, screenInfo.current_h - img.get_height() - PADDING))
        screen.blit(img, (screenInfo.current_w - img.get_width() - PADDING, screenInfo.current_h - img.get_height() - PADDING))
        # title
        ptext.draw(
            TITLE,
            centerx=screenInfo.current_w / 2,
            centery=screenInfo.current_h  - (img.get_height()/2) - PADDING,
            color="pink",
            gcolor="red",
            fontname="fonts/RobotoCondensed-Bold.ttf",
            fontsize=80,
        )
    else:
        screen.blit(img, (PADDING, PADDING))
        screen.blit(img, (screenInfo.current_w - img.get_width() - PADDING, PADDING))

        ptext.draw(
            TITLE,
            centerx=screenInfo.current_w / 2,
            centery=50 + img.get_height()/2,
            color="pink",
            gcolor="red",
            fontname="fonts/RobotoCondensed-Bold.ttf",
            fontsize=80,
        )

def draw_splash():
    state = GameState.SPLASH
    cleardisplay()

    img = pygame.image.load(SPLASH)
    screen.blit(
        img,
        (
            screenInfo.current_w / 2 - img.get_width() / 2,
            screenInfo.current_h / 2 - img.get_width() / 2,
        ),
    )
    pygame.display.flip()

    # block for keypress
    waiting = True
    while waiting:
        e = pygame.event.wait()
        if e.type == pygame.KEYDOWN:
            waiting = False

    pygame.display.flip()

    state = GameState.IDLE
    render_all()

def nameedit_modal():
    global state
    state = GameState.INPUT

    # which name we are editing
    editing = 0

    # draw a modal box at 85% of the screen. Stop the clock.
    state = GameState.SETUP

    # black out the modal
    width = screenInfo.current_w * 0.15  # 85% total
    height = screenInfo.current_h * 0.10  # 75% total
    
    input_height = 80
    input_spacing = 200 # spacing between inputs
    inputs_offset = 150 # offset from top of modal where inputs begin
    label_offset = 100 # offset from top of modal where labels begin

    # inside modal
    pygame.draw.rect(
        screen,
        (60, 60, 60),
        (
            width,
            height,
            screenInfo.current_w - (width * 2),
            screenInfo.current_h - (height * 2),
        ),
    )

    # outside edge
    pygame.draw.rect(
        screen,
        (210, 0, 100),
        (
            width,
            height,
            screenInfo.current_w - (width * 2),
            screenInfo.current_h - height * 2,
        ),
    )

    # start a bit inset in the modal
    xpos = width + 60

    # Center the title
    ptext.draw(
        "Edit Player Names (ESC to exit)",
        centerx=screenInfo.current_w / 2,
        centery=height+50,
        fontname="fonts/RobotoCondensed-Bold.ttf",
        fontsize=50,
    )

    for i in range(0, PLAYERS):
        # input box - grey until edit is active
        pygame.draw.rect(
            screen,
            (60, 60, 60),
            (
                xpos - 4,
                height + inputs_offset + (i * input_spacing),
                screenInfo.current_w - (width * 2) - 120,
                input_height,
            ),
        )

        # input label
        drawtext(
            "robo36", 
            "Player %d" % (i + 1), 
            xpos, height + label_offset + (i * input_spacing), 
            (255, 255, 255), 
            (210, 0, 100) 
        )
        
        # player name
        drawtext(
            "robo50",
            player_names[i],
            xpos,
            height + inputs_offset + (i * input_spacing),
            (255, 255, 0),
            (60, 60, 60),
        )

    clock = pygame.time.Clock()

    textmanager = pygame_textinput.TextInputManager()
    input_font = pygame.font.Font("fonts/RobotoCondensed-Bold.ttf", 50)

    textinput = pygame_textinput.TextInputVisualizer(
        manager=textmanager,
        font_color=(255, 255, 0),
        cursor_color=(255, 255, 255),
        font_object=input_font
    )
  
    textinput.value = player_names[editing]
    textmanager.cursor_pos = len(player_names[editing])
  
    pygame.key.set_repeat(200, 25)
    
    while True:
        events = pygame.event.get()
        # pass all of the events to textinput for input handling
        textinput.update(events)

        # See if we care about any of the events that just fired
        for event in events:
            if event.type == pygame.QUIT:
                print("Quitting..")
                if SER:
                  print("Closing serial port")
                  SER.close()
                pygame.quit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state = GameState.IDLE
                player_names[editing] = textinput.value
                store_state()
                render_all()
                return

            # Feed it with events every frame
            if (
                event.type == pygame.KEYUP
                and (event.key == pygame.K_UP or event.key == pygame.K_DOWN or event.key == pygame.K_RETURN)
            ):
                # store the old data
                player_names[editing] = textinput.value
                store_state()

                # clear the text input box, make it grey and put the text back.
                pygame.draw.rect(
                    screen,
                    (60, 60, 60),
                    (
                        xpos - 4,
                        height + inputs_offset + (editing * input_spacing),
                        screenInfo.current_w - (width * 2) - 120,
                        input_height,
                    ),
                )

                drawtext(
                    "robo50",
                    player_names[editing],
                    xpos,
                    height + inputs_offset + (editing * input_spacing),
                    (255, 255, 0),
                    (60, 60, 60),
                )

                # move to the next row or go up if requested
                if event.key == pygame.K_UP:
                    player_names[editing] = textinput.value
                    editing = editing - 1

                if event.key == pygame.K_DOWN or event.key == pygame.K_RETURN:
                    player_names[editing] = textinput.value
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
                    font_object=input_font
                )
                
                textinput.value = player_names[editing]            
                textmanager.cursor_pos = len(player_names[editing])

                # break so we don't overprocess events
                break

            # clear the region
            pygame.draw.rect(
                screen,
                (30, 30, 30),
                (
                    xpos - 4,
                    height + inputs_offset + (editing * input_spacing),
                    screenInfo.current_w - (width * 2) - 120,
                    input_height,
                ),
            )

            # Blit its surface onto the screen
            # thre is a slight problem here that the text drawing is off?
            screen.blit(textinput.surface, (xpos, height + inputs_offset + (editing * input_spacing)))

        pygame.display.update()
        clock.tick(FPS)

def draw_help():
    global state

    helpstr = [
        {"key": "SPACE", "text": "Stop/Start clock"},
        {"key": "SHIFT-ESC", "text": "Quit"},
        {"key": "H or ?", "text": "HELP"},
        {"key": "1", "text": "+1 point Player 1"},
        {"key": "2", "text": "+1 point Player 2"},
        {"key": "3", "text": "+1 point Player 3"},
        {"key": "4", "text": "+1 point Player 4"},
        {"key": "Q", "text": "-1 point Player 1"},
        {"key": "W", "text": "-1 point Player 2"},
        {"key": "E", "text": "-1 point Player 3"},
        {"key": "R", "text": "-1 point Player 4"},
        {"key": "P", "text": "Clock: +5 seconds"},
        {"key": "L", "text": "Clock: -5 seconds"},
        {"key": "T", "text": 'Play a "time\'s up" sound'},
        {"key": "B", "text": "Play a buzzer sound"},
        {"key": "N", "text": "Name Players"},
        {"key": "I", "text": "Invert Display (toggle)"},
        {"key": "S", "text": "Draw Splash Screen"},
        {"key": "SHIFT-A", "text": "Reset game"},
        {"key": "SHIFT-Z", "text": "Reset Clock"},
    ]

    # draw a modal box at 85% of the screen. Stop the clock.
    state = GameState.HELP

    # black out that box
    width = screenInfo.current_w * 0.15  # 85% total
    height = 10

    # inside box
    pygame.draw.rect(
        screen,
        (60, 60, 60),
        (
            width,
            height,
            screenInfo.current_w - (width * 2),
            screenInfo.current_h - (height * 2),
        ),
    )
    # outside perimeter
    pygame.draw.rect(
        screen,
        (210, 0, 100),
        (
            width,
            height,
            screenInfo.current_w - (width * 2),
            screenInfo.current_h - (height * 2),
        ),
        2,
    )

    xpos = width + 60
    ypos = height + 30

    # draw help text
    ptext.draw(
        "HELP",
        centerx=screenInfo.current_w / 2,
        centery=ypos,
        fontname="fonts/RobotoCondensed-Bold.ttf",
        fontsize=50,
    )

    ypos = ypos + 60

    for k in helpstr:
        drawtext("robo36", k["key"], xpos, ypos, (255, 255, 255), (60, 60, 60))
        drawtext(
            "robo36",
            k["text"],
            screenInfo.current_w / 2,
            ypos,
            (255, 255, 255),
            (60, 60, 60),
        )
        ypos = ypos + fonts["robo36"].get_height()

    pygame.display.flip()

    # block for keypress
    waiting = True
    while waiting:
        e = pygame.event.wait()
        if e.type == pygame.KEYDOWN:
            waiting = False

    pygame.display.flip()

    state = GameState.IDLE
    render_all()

def draw_state():
  statestr = ""

  if state == GameState.TIMEUP:
      statestr = "TIME'S UP!"

  if state == GameState.IDLE:
      statestr = "STOPPED"

  if state == GameState.RUNNING:
      statestr = ""

  if invert_display:
    message_y = 320
  else:
    message_y = screenInfo.current_h / 3 + 250

  ptext.draw(
      statestr,
      centerx=screenInfo.current_w / 2,
      centery=message_y,
      color="purple",
      fontname="fonts/RobotoCondensed-Bold.ttf",
      fontsize=90,
  )

def draw_clock():
    minutes = math.floor(clock / 60000)
    sec = int((clock - (minutes * 60000)) / 1000)

    # blank out the area the clock will occupy
    fontheight = fonts["robo250"].get_height()
    
    ptext.draw(
        "%d:%02d" % (minutes, sec),
        centerx=screenInfo.current_w / 2,
        centery=screenInfo.current_h / 3 + 100,
        background="black",
        color="pink",
        gcolor="red",
        fontname="fonts/RobotoCondensed-Bold.ttf",
        fontsize=250,
    )

    draw_state()

def do_beep():
  # make a beep
  sound_library['BEEP'].play()



def draw_gamestate():
  if state == GameState.BUZZIN:
    # draw their name    
    msg = "--- Player %d: %s ---" % (buzzedin + 1, player_names[buzzedin])

    message_y = 180
    if invert_display:
      message_y = 300
        
    ptext.draw(
        msg,
        centerx=screenInfo.current_w / 2,
        centery=message_y,
        owidth=1,
        ocolor=(180, 0, 0),
        color=colors["white"],
        fontname="fonts/RobotoCondensed-Bold.ttf",
        fontsize=90,
    )

def restore_state():
    global scores, clock, state, buzzedin
    if os.path.exists(STATEFILE):
      filehandler = open(STATEFILE, "rb")
      saved_object = pickle.load(filehandler)
      filehandler.close()

      player_names = saved_object["player_names"]
      scores = saved_object["scores"]
      invert_display = saved_object["invert_display"]

def store_state():
    global scores, clock, state, buzzedin
    saved_object = {
        "player_names": player_names,
        "scores": scores,
        "invert_display": invert_display
    }

    filehandler = open(STATEFILE, "wb")
    pickle.dump(saved_object, filehandler)
    filehandler.close()

def render_all():
  '''Render the entire screen'''
  cleardisplay()
  draw_title()
  draw_clock()
  draw_scores()
  draw_gamestate()

  # draw LED and debugging if platform is not rpi
  draw_leds()
  
  pygame.display.flip()

def load_sounds():
  """Load all sounds from subdirectories in a dictionary"""
  global sound_library
  print("Loading sounds...")
  sound_path = "sounds/Soundsets/%d" % SOUNDSET
  for dirpath, dirnames, filenames in os.walk(sound_path):
    print ("Found directory: %s" % dirpath)
    print ("Files: %s" % filenames)

    for name in filenames:
      if name.endswith('.mp3'):
          key = name[:-4]
          sound_library[key] = pygame.mixer.Sound(os.path.join(sound_path,name))
          print ("Loaded sound %s" % key)

for sound in sound_library:
    print(sound)

# init
setup_gpio()
SER = setup_serial(SERIAL_DEVICE)
restore_state()
initgame()
initpalette()
load_sounds()
render_all()

# ------------------ main event loop ------------------
i = 0
running = 1
pygame.time.set_timer(CLOCKEVENT, CLOCK_STEP)

# flush the serial buffers at the start of the game
if SER:
    SER.reset_input_buffer()
    SER.reset_output_buffer()

print("\nStarting main loop...\n")

while running:
    # do we have serial data?
    if SER:
        if SER.inWaiting() > 0:
            received_data = SER.read(SER.inWaiting())
            print("recv: %s" % received_data)
            parts = received_data.split()
            if parts[0] == b"SWITCH" and parts[2] == b"PRESSED":
                button_event(int(parts[1]))

    # we do not poll here because it will induce very high cpu.
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_ESCAPE
            and pygame.key.get_mods() & pygame.KMOD_SHIFT
        ):
            running = 0

        # player scores
        if event.type == pygame.KEYDOWN:
            # MC Controls
            #
            # 1,2,3,4 = Adds a point to that player 1,2,3,4
            # q,w,e,r = Deduct a point from player 1,2,3,4
            # shift-a = reset all
            # shift-z = reset round
            # (see help for the rest)
            #
            if event.key == pygame.K_1:
                scores[0] += 1
                store_state()

            if event.key == pygame.K_2:
                scores[1] += 1
                store_state()

            if event.key == pygame.K_3:
                scores[2] += 1
                store_state()

            if event.key == pygame.K_4:
                scores[3] += 1
                store_state()

            if event.key == pygame.K_q:
                scores[0] -= 1
                store_state()

            if event.key == pygame.K_w:
                scores[1] -= 1
                store_state()

            if event.key == pygame.K_e:
                scores[2] -= 1
                store_state()

            if event.key == pygame.K_r:
                scores[3] -= 1
                store_state()

            # if we are not running in debug mode we can emulate the buttons
            # with the keypad
            if PLATFORM != 'rpi' and state == GameState.RUNNING:
                if event.key == pygame.K_KP1:
                  button_event(player_map[0])

                if event.key == pygame.K_KP2:
                  button_event(player_map[1])
                
                if event.key == pygame.K_KP3:
                  button_event(player_map[2])

                if event.key == pygame.K_KP4:
                  button_event(player_map[3])
                  
            # sounds
            if event.key == pygame.K_b:
                sound_library['BUZZ'].play()

            if event.key == pygame.K_t:
                sound_library['TIMESUP'].play()
                
            # clock changes
            if event.key == pygame.K_p:
                clock = clock + 5000

            if event.key == pygame.K_l:
                clock = clock - 5000
                if clock < 0:
                    clock = 0

            # reset all
            if event.key == pygame.K_a and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                reset_game()
                store_state()

            # reset round
            if event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                reset_clock()

            if event.key == pygame.K_h:
                draw_help()

            if event.key == pygame.K_i:
                invert_display = not invert_display

            if event.key == pygame.K_n:
                nameedit_modal()

            if event.key == pygame.K_s and state == GameState.IDLE:
                draw_splash()

            # space -- transitions state
            if event.key == pygame.K_SPACE:
                set_all_leds(False)
                buzzedin = -1
                if state == GameState.BUZZIN:
                    do_beep()
                    state = GameState.RUNNING
                    pygame.mixer.music.load(
                        "sounds/Soundsets/%d/TIMESUP.mp3" % SOUNDSET
                    )
                else:
                    if state == GameState.IDLE:
                        do_beep()
                        # preload audio for time up
                        pygame.mixer.music.load(
                            "sounds/Soundsets/%d/TIMESUP.mp3" % SOUNDSET
                        )
                        state = GameState.RUNNING
                    else:
                        if state == GameState.TIMEUP:
                            # you can either add time here, or if we
                            # are at zero we will start at zero
                            if clock == 0:
                                clock = MAXCLOCK
                            state = GameState.RUNNING
                        else:
                            state = GameState.IDLE

        if event.type == CLOCKEVENT:
            if clock > 0:
                if state == GameState.RUNNING:
                  clock = clock - CLOCK_STEP
                  minutes = math.floor(clock / 60000)
                  sec = int((clock - (minutes * 60000)) / 1000)

                  if prevsec != sec:
                      prevsec = sec
                      if prevsec <= 4:
                          do_beep()

                  # handle timeout
                  if clock == 0:
                      # play sound
                      for i in range(0, PLAYERS):
                          set_all_leds(True)

                      pygame.mixer.music.load(
                          "sounds/Soundsets/%d/TIMESUP.mp3" % SOUNDSET
                      )
                      pygame.mixer.music.play()
                      state = GameState.TIMEUP

            if state == GameState.IDLE:
                # in idle state, walk the LEDs.
                blinky += 1
                if blinky > PLAYERS - 1:
                    blinky = 0
                set_all_leds(False)
                set_led(blinky, True)
                
        if buzzedin > -1:
            # now handle player buzz-in. The player number will have been set via
            # button_event()
            if state == GameState.RUNNING:
                # advance to next state, let render figure it out
                # make some blinking lights and sound
                buzz_in_alert()
                state = GameState.BUZZIN

    # the pattern here is to set the state of the game and then render
    # no rendering should happen before this line.
    render_all()
    pygame.display.flip()
    pygame.time.Clock().tick(FPS)
