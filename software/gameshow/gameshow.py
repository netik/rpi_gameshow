#!/usr/bin/python
#
# Dirty Talk game show game show code, version 3, rPi and custom board
#

import os
import time
import pygame
import pygame_textinput    # from https://github.com/Nearoo/pygame-text-input
import ptext
import pygame.freetype
from pygame import Color
import RPi.GPIO as GPIO

# config
PLAYERS=4
MAXCLOCK=60000 # in microseconds!
CLOCK_STEP=250 # mS
CLOCKEVENT=pygame.USEREVENT + 1
SOUNDSET=2
TITLE="The Dirty Talk Game Show"
LOGO="images/logo.jpg"
SPLASH="images/dirtytalk-fs.jpg"

# GPIO Pinout
player_map = [ 16, 17, 18, 19 ]
reverse_map = { 16: 0, 17: 1, 18: 2, 19: 3 }
led_map = [ 20, 21, 22, 23 ]

player_names = []

# working dir
os.chdir("/home/pi/src/gameshow")

# can't hurt. 
os.system("/usr/bin/amixer set PCM -- 1000")

# force 1/8" output no matter what
os.system("/usr/bin/amixer cset numid-3 1")

class GameState:
    IDLE = 0,
    RUNNING = 1,
    BUZZIN = 2,
    TIMEUP = 3,
    INPUT = 4,
    HELP = 5,
    SETUP = 6
    SPLASH = 10
    
  # globals
clock = MAXCLOCK
fonts = {}
colors = {}
screen = None
scores = [0,0,0,0]

# "attract" mode, run when game idle
blinky = 0

# game state
buzzedin = -1
state = GameState.IDLE

# I have no idea where these warnings are coming from on pin 20, let's disable them.
# maybe it's complaining because pin 20 is MOSI/SPI but we're not using that and everything works fine.
GPIO.setwarnings(False)
                        
def button_event(channel):
    # remember the event, we will handle this on the next clock tick
    global buzzedin
    buzzedin = reverse_map[channel]
    
def clear_leds():
    for k in led_map:
        GPIO.output(k, False)
    
def setup_gpio():
    #Setup the GPIOs as inputs with Pull Ups since the buttons are connected to GND
    GPIO.setmode(GPIO.BCM)
    for k in player_map:
        GPIO.setup(k, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(k, GPIO.FALLING, button_event, bouncetime=50)

    for k in led_map:
        GPIO.setup(k, GPIO.OUT)

    clear_leds()
    
def loadfont(shortname, filename, size):
    fonts[shortname] = pygame.freetype.Font(os.path.join("fonts",filename),size)

def drawtext(fontshortname, text, x, y, fg, bg):
    fonts[fontshortname].render_to(screen, (x,y), text, fg, bg, True)
    
def cleardisplay():
    screen.fill((0, 0, 0))
    pygame.display.flip()

def initgame():
    global screen,screenInfo
    # init the system, get screen metrics
    # enable sound
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.mixer.init()
    pygame.init()

    screenInfo = pygame.display.Info()
    screen = pygame.display.set_mode((screenInfo.current_w, screenInfo.current_h), pygame.FULLSCREEN)

    # hide mouse
    pygame.mouse.set_visible(False)

    cleardisplay
    
    # load fonts
    loadfont("bebas40", "BebasKai-Regular.otf", 40)
    loadfont("robo36", "RobotoCondensed-Bold.ttf", 36)

    # set player names
    for i in range(0,PLAYERS):
        player_names.append("Player %d" % (i+1))

        
def initpalette():
    colors['white'] = pygame.Color(255,255,255)
    colors['grey'] = pygame.Color(164, 164, 164, 255)

def buzzin(playerno):
    global state, screenInfo

    # stop the clock
    state = GameState.BUZZIN

    # draw their name 
    pygame.draw.rect(screen, (0,0,0),
                     (0, screenInfo.current_h/3+100, screenInfo.current_w, 200))
    msg = "--- Player %d: %s ---" % (playerno + 1, player_names[playerno])
    ptext.draw(msg,
               centerx=screenInfo.current_w/2,
               centery=screenInfo.current_h/3+160,
               owidth=1, ocolor=(180,0,0), color=(255,255,255),
               fontname="fonts/RobotoCondensed-Bold.ttf", fontsize=90)

    pygame.display.flip()

    # play sound
    pygame.mixer.music.load("sounds/Soundsets/%d/BUZZ.mp3" % SOUNDSET)
    pygame.mixer.music.play()

    # light player buzzer
    i = 0
    for k in led_map:
        if i == playerno:
            GPIO.output(k, True)
        else:
            GPIO.output(k, False)
        i = i + 1
    
def draw_scores(): 
    i=1

    pygame.draw.rect(screen, (0,0,0),
                     (0, screenInfo.current_h/2+150, screenInfo.current_w, screenInfo.current_h));

    while i<5:
        if buzzedin == (i-1):
            # make blue if they are buzzed in 
            pygame.draw.rect(screen, (0,0,200),
                             ((i-1) * screenInfo.current_w/4, screenInfo.current_h/2+150, (screenInfo.current_w/4), screenInfo.current_h));
            
        ptext.draw(player_names[i-1],
                   centerx=(screenInfo.current_w/8 * ((i*2)-1)),
                   centery=screenInfo.current_h/2+200,
                   color=(180,180,180),
                   fontname="fonts/RobotoCondensed-Bold.ttf",
                   fontsize=80)
        
        ptext.draw("%d" % scores[i - 1],
                   centerx=(screenInfo.current_w/8 * ((i*2)-1)),
                   centery=(screenInfo.current_h/2)+350,
                   color="white",
                   fontname="fonts/RobotoCondensed-Bold.ttf",
                   fontsize=120)
        
        pygame.draw.line(screen, colors['grey'],
                         ((screenInfo.current_w/4 * i+1), screenInfo.current_h/2+150),
                         ((screenInfo.current_w/4 * i+1), screenInfo.current_h));
        
        i += 1
    
    pygame.display.flip()

def reset_game():
    global scores, clock, state, buzzedin
    i = 0
    while i < 4:
        scores[i] = 0
        i = i + 1
    clock = MAXCLOCK
    state = GameState.IDLE
    buzzedin = -1

    draw_clock()
    
def reset_clock():
    global scores, clock, state, buzzedin
    clock = MAXCLOCK
    state = GameState.IDLE
    buzzedin = -1

    draw_clock()
        
def draw_title():
    img = pygame.image.load(LOGO)
    screen.blit(img,(0,0))
    screen.blit(img,(screenInfo.current_w - img.get_width(),0))
    ptext.draw(TITLE,
               centerx=screenInfo.current_w/2, centery=50,
               color="pink", gcolor="red",
               fontname="fonts/RobotoCondensed-Bold.ttf", fontsize=80)
    pygame.display.flip()

def draw_splash():
    state = GameState.SPLASH
    cleardisplay()

    img = pygame.image.load(SPLASH)
    screen.blit(img,(screenInfo.current_w/2 - img.get_width()/2,
                     screenInfo.current_w/2 - img.get_width()/2))
    pygame.display.flip()

    # block for keypress
    waiting = True
    while waiting: 
        e = pygame.event.wait()
        if e.type == pygame.KEYDOWN:
            waiting = False

    pygame.display.flip()
    
    state = GameState.IDLE
    cleardisplay()
    draw_title()
    draw_clock()
    draw_scores()
    
def nameedit_modal():
    global state
    state = GameState.INPUT

    # which name we are editing
    editing = 0
    
    # draw a modal box at 85% of the screen. Stop the clock.
    state = GameState.SETUP

    # black out the modal
    width = screenInfo.current_w * .15  # 85% total
    height = screenInfo.current_h * .10 # 75% total

    # inside modal
    pygame.draw.rect(screen, (60,60,60),
                     (width, height, screenInfo.current_w - (width * 2), screenInfo.current_h - (height*2)))
                                                                                   # outside edge
    pygame.draw.rect(screen, (210,0,100),
                     (width, height, screenInfo.current_w - (width * 2), screenInfo.current_h - height*2))

    xpos = width + 60
    ypos = height + 30

    # Draw Names
    ptext.draw("Edit Player Names (ESC to exit)",
               centerx=screenInfo.current_w/2,
               centery=ypos,
               fontname="fonts/RobotoCondensed-Bold.ttf", fontsize=50)

    ypos = ypos + 60

    for i in range(0, PLAYERS):
        drawtext("robo36", "Player %d" % (i + 1), xpos, ypos, (255,255,255), (60,60,60))
        drawtext("robo36", player_names[i], xpos, height + 140 + (120 * i), (255,255,0), (60,60,60))
        ypos = ypos + 120 

    clock = pygame.time.Clock()
    textinput = pygame_textinput.TextInput(text_color=(255,255,0),
                                           cursor_color=(255,255,255),
                                           font_size=50,
                                           value=player_names[editing])
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state = GameState.IDLE
                cleardisplay()
                draw_title()
                draw_clock()
                draw_scores()
                return

                
            # Feed it with events every frame
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_UP or event.key == pygame.K_DOWN) or textinput.update(events):
                # store the old data
                player_names[editing] = textinput.get_text()
                pygame.draw.rect(screen, (60,60,60),
                             (xpos-4, height+136 + (editing * 120), screenInfo.current_w - (width * 2) - 120,46))
                
                drawtext("robo36", player_names[editing], xpos, height + 140 + (120 * editing), (255,255,0), (60,60,60))            
                
                # move to the next row or go up if requested
                if (event.type == pygame.KEYDOWN and event.key == pygame.K_UP):
                    editing = editing - 1
                else:
                    editing = editing + 1

                if editing > 3:
                    editing = 0

                if editing < 0:
                    editing = 3
                # get us a new object for this row
                del textinput
                textinput = pygame_textinput.TextInput(text_color=(255,255,0),
                                                       cursor_color=(255,255,255),
                                                       font_size=50,
                                                       value=player_names[editing])
                # break so we don't overprocess events
                break
            
            # clear the region
            pygame.draw.rect(screen, (30,30,30),
                             (xpos-4, height+136 + (editing * 120), screenInfo.current_w - (width * 2) - 120,46))
            # Blit its surface onto the screen
            screen.blit(textinput.get_surface(), (xpos, height+140 + (editing * 120)))
            
        pygame.display.update()
        clock.tick(60)
    
def draw_help():
    global state

    helpstr = [ { "key": "SPACE", "text": "Stop/Start clock" },
                { "key": "SHIFT-ESC" , "text": "Quit" },
                { "key": "H or ?" , "text": "HELP" },
                { "key": "1" , "text": "+1 point Player 1" },
                { "key": "2" , "text": "+1 point Player 2" },
                { "key": "3" , "text": "+1 point Player 3" },
                { "key": "4" , "text": "+1 point Player 4" },
                { "key": "Q" , "text": "-1 point Player 1" },
                { "key": "W" , "text": "-1 point Player 2" },
                { "key": "E" , "text": "-1 point Player 3" },
                { "key": "R" , "text": "-1 point Player 4" },
                { "key": "P" , "text": "Clock: +5 seconds" },
                { "key": "L" , "text": "Clock: -5 seconds" },
                { "key": "T" , "text": "Play a \"time's up\" sound" },
                { "key": "B" , "text": "Play a buzzer sound" },
                { "key": "N" , "text": "Name Players" },
                { "key": "S" , "text": "Draw Splash Screen" },
                { "key": "SHIFT-A" , "text": "Reset game" },
                { "key": "SHIFT-Z" , "text": "Reset Clock" },                    ]

    # draw a modal box at 85% of the screen. Stop the clock.
    state = GameState.HELP

    # black out that box
    width = screenInfo.current_w * .15  # 85% total
    height = 10

    # inside box
    pygame.draw.rect(screen, (60,60,60),
                     (width, height, screenInfo.current_w - (width * 2), screenInfo.current_h - (height*2)));
    # outside perimeter
    pygame.draw.rect(screen, (210,0,100),
                     (width, height, screenInfo.current_w - (width * 2), screenInfo.current_h - (height*2)), 2);

    xpos = width + 60
    ypos = height + 30

    # draw help text
    ptext.draw("HELP",
               centerx=screenInfo.current_w/2,
               centery=ypos,
               fontname="fonts/RobotoCondensed-Bold.ttf", fontsize=50)

    ypos = ypos + 60

    for k in helpstr:
        drawtext("robo36", k["key"], xpos, ypos, (255,255,255), (60,60,60))
        drawtext("robo36", k["text"], screenInfo.current_w/2, ypos, (255,255,255), (60,60,60))
        ypos = ypos + fonts["robo36"].get_sized_height()
        
    pygame.display.flip()

    # block for keypress
    waiting = True
    while waiting: 
        e = pygame.event.wait()
        if e.type == pygame.KEYDOWN:
            waiting = False

    pygame.display.flip()
    
    state = GameState.IDLE
    cleardisplay()
    draw_title()
    draw_clock()
    draw_scores()

        
def draw_clock():
    minutes = (clock / 60000)
    sec = (clock - (minutes * 60000) ) / 1000
    pygame.draw.rect(screen, (0,0,0),
                     (0, screenInfo.current_h/3-90, screenInfo.current_w, screenInfo.current_h/3+90));

    ptext.draw("%d:%02d" % (minutes, sec), centerx=screenInfo.current_w/2, centery=screenInfo.current_h/3, color="pink", gcolor="red", fontname="fonts/RobotoCondensed-Bold.ttf", fontsize=250)
    statestr = ""

    if state == GameState.TIMEUP:
        statestr = "TIME'S UP!"
        
    if state == GameState.IDLE:
        statestr = "STOPPED"

    if state == GameState.RUNNING:
        statestr = ""
        
    ptext.draw(statestr,
               centerx=screenInfo.current_w/2, centery=screenInfo.current_h/3+160,
               color="purple",
               fontname="fonts/RobotoCondensed-Bold.ttf", fontsize=90)
    
    pygame.display.flip()
    
# init
setup_gpio()
initgame()
initpalette()
draw_title()
draw_clock()
draw_scores()

# main event loop
i = 0
running = 1
pygame.time.set_timer(CLOCKEVENT, CLOCK_STEP)

while running:
    # we do not poll here because it will induce very high cpu.
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and pygame.key.get_mods() & pygame.KMOD_SHIFT):
            running = 0

        # player scores
        if (event.type == pygame.KEYDOWN):
            # MC Controls
            #
            # 1,2,3,4 = Adds a point to that player 1,2,3,4
            # q,w,e,r = Deduct a point from player 1,2,3,4
            # shift-a = reset all
            # shift-z = reset round
            #
            if event.key == pygame.K_1:
                scores[0] += 1

            if event.key == pygame.K_2:
                scores[1] += 1

            if event.key == pygame.K_3:
                scores[2] += 1

            if event.key == pygame.K_4:
                scores[3] += 1

            if event.key == pygame.K_q:
                scores[0] -= 1

            if event.key == pygame.K_w:
                scores[1] -= 1

            if event.key == pygame.K_e:
                scores[2] -= 1

            if event.key == pygame.K_r:
                scores[3] -= 1

            # sounds
            if event.key == pygame.K_b:
                pygame.mixer.music.load("sounds/misc/buzzer.mp3")
                pygame.mixer.music.play()

            if event.key == pygame.K_t:
                pygame.mixer.music.load("sounds/misc/timesup.mp3")
                pygame.mixer.music.play()

                
            # clock changes
            if event.key == pygame.K_p:
                clock = clock + 5000
                draw_clock()
                
            if event.key == pygame.K_l:
                clock = clock - 5000
                if clock < 0:
                    clock = 0
                draw_clock()

            # reset all 
            if event.key == pygame.K_a and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                reset_game()

            # reset round
            if event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                reset_clock()

            if event.key == pygame.K_h:
                draw_help()

            if event.key == pygame.K_n:
                nameedit_modal()

            if event.key == pygame.K_s and state == GameState.IDLE:
                draw_splash()
                
            if state != GameState.HELP: 
                draw_scores()

            # space -- transitions state 
            if event.key == pygame.K_SPACE:
                clear_leds()
                buzzedin=-1
                if (state == GameState.BUZZIN):
                    state = GameState.RUNNING
                    pygame.mixer.music.load("sounds/Soundsets/%d/TIMESUP.mp3" % SOUNDSET)
                else:
                    if (state == GameState.IDLE):
                        # make a beep
                        pygame.mixer.music.load("sounds/Soundsets/%d/BEEP.mp3" % SOUNDSET)
                        pygame.mixer.music.play()

                        # let the sound finish
                        while (pygame.mixer.music.get_busy() == True): 
                          time.sleep(.25)

                        # preload audio
                        pygame.mixer.music.load("sounds/Soundsets/%d/TIMESUP.mp3" % SOUNDSET)
                        state = GameState.RUNNING
                    else:
                        if (state == GameState.TIMEUP):
                            # you can either add time here, or if we
                            # are at zero we will start at zero
                            if clock == 0:
                                clock = MAXCLOCK
                            state = GameState.RUNNING
                        else:
                            state = GameState.IDLE
                draw_clock()
                            
        if event.type == CLOCKEVENT:
            if clock > 0:
                if state == GameState.RUNNING: 
                    clock = clock - CLOCK_STEP
                    # handle timeout
                    if clock == 0:
                        # play sound
                        for i in range(0, PLAYERS):
                            GPIO.output(led_map[i],True)
                        pygame.mixer.music.load("sounds/Soundsets/%d/TIMESUP.mp3" % SOUNDSET)
                        pygame.mixer.music.play()
                        state = GameState.TIMEUP
                        
                    draw_clock()

            if state == GameState.IDLE:
                # in idle state, walk the LEDs. 
                blinky += 1
                if blinky > PLAYERS-1:
                    blinky = 0

                for i in range(0, PLAYERS):
                    GPIO.output(led_map[i],False)

                GPIO.output(led_map[blinky], True)

        if buzzedin > -1:
            # now handle player buzz-in
            if state == GameState.RUNNING:
                buzzin(buzzedin)
                draw_scores()
            buzzedin = -1

    pygame.time.Clock().tick(20)
    
