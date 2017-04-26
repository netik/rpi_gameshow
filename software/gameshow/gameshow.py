#!/usr/bin/python
#
# Dirty Talk game show game show code, version 3, rPi and custom board
#

import pygame
import ptext
import pygame.freetype
import os
from pygame import Color
import RPi.GPIO as GPIO

# config
PLAYERS=4
MAXCLOCK=60000 # in microseconds!
CLOCKEVENT=pygame.USEREVENT + 1
SOUNDSET=2

# GPIO Pinout
player_map = [ 16, 17, 18, 19 ]
reverse_map = { 16: 0, 17: 1, 18: 2, 19: 3 }
led_map = [ 20, 21, 22, 23 ]
buzzedin = -1

# working dir
os.chdir("/home/pi/src/gameshow")

class GameState:
    IDLE = 0,
    RUNNING = 1,
    BUZZIN = 2,
    TIMEUP = 3,
    SETUP = 4

# globals
clock = MAXCLOCK
fonts = {}
colors = {}
screen = None
scores = [0,0,0,0]
state = GameState.IDLE
blinky = 0

# I have no idea where these warnings are coming from on pin 20, let's disable them.
GPIO.setwarnings(False)

def button_event(channel):
    global buzzedin

    print "button"
    buzzedin = reverse_map[channel]
    print "channel %d set to %d" % (channel, buzzedin)
    
def clear_leds():
    for k in led_map:
        GPIO.output(k, False)
    
def setup_gpio():
    #Setup the GPIOs as inputs with Pull Ups since the buttons are connected to GND
    GPIO.setmode(GPIO.BCM)
    for k in player_map:
        GPIO.setup(k, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(k, GPIO.RISING, button_event, bouncetime=50)

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
    # init the system
    pygame.init()
    screenInfo = pygame.display.Info()

    screen = pygame.display.set_mode((screenInfo.current_w, screenInfo.current_h), pygame.FULLSCREEN)

    # hide mouse
    pygame.mouse.set_visible(False)

    # enable sound
    pygame.mixer.init()
     
    cleardisplay
    
    # load fonts
    loadfont("bebas40", "BebasKai-Regular.otf", 40)
    loadfont("robo36", "RobotoCondensed-Bold.ttf", 36)

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
    msg = "--- Player %d ---" % (playerno + 1)
    ptext.draw(msg,
               centerx=screenInfo.current_w/2,
               centery=screenInfo.current_h/3+140,
               owidth=1, ocolor=(255,255,255), color=(255,0,0),
               fontname="fonts/RobotoCondensed-Bold.ttf", fontsize=90)

    pygame.display.flip()

    # play sound
    pygame.mixer.music.load("sounds/Soundsets/2/BUZZ.mp3")
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
        ptext.draw("Player %d" % i,
                   centerx=(screenInfo.current_w/8 * ((i*2)-1)),
                   centery=screenInfo.current_h/2+200,
                   color="white",
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
    global scores
    global clock
    
    i = 0
    while i < 4:
        scores[i] = 0
        i = i + 1
    clock = MAXCLOCK

def draw_title():
    img = pygame.image.load('images/logo.jpg')
    screen.blit(img,(0,0))
    screen.blit(img,(screenInfo.current_w - img.get_width(),0))
    ptext.draw("The Dirty Talk Game Show",
               centerx=screenInfo.current_w/2, centery=50,
               color="pink", gcolor="red",
               fontname="fonts/RobotoCondensed-Bold.ttf", fontsize=80)
    pygame.display.flip()

def draw_clock():
    minutes = (clock / 60000)
    sec = (clock - (minutes * 60000) ) / 1000
    pygame.draw.rect(screen, (0,0,0),
                     (0, screenInfo.current_h/3-80, screenInfo.current_w, screenInfo.current_h/3+80));

    ptext.draw("%d:%02d" % (minutes, sec), centerx=screenInfo.current_w/2, centery=screenInfo.current_h/3, color="pink", gcolor="red", fontname="fonts/RobotoCondensed-Bold.ttf", fontsize=200)
    statestr = ""

    if state == GameState.TIMEUP:
        statestr = "TIME'S UP!"
        
    if state == GameState.IDLE:
        statestr = "STOPPED"

    if state == GameState.RUNNING:
        statestr = ""
        
    ptext.draw(statestr,
               centerx=screenInfo.current_w/2, centery=screenInfo.current_h/3+140,
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
pygame.time.set_timer(CLOCKEVENT, 250)

while running:
    # we do not poll here because it will induce very high cpu.
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = 0

        # player scores
        if (event.type == pygame.KEYDOWN):
            # MC Controls
            #
            # 1,2,3,4 = Adds a point to that player 1,2,3,4
            # q,w,e,r = Deduct a point from player 1,2,3,4
            # z = reset round
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

            # clock changes
            if event.key == pygame.K_p:
                clock = clock + 5000
                draw_clock()
                
            if event.key == pygame.K_l:
                clock = clock - 5000
                if clock < 0:
                    clock = 0
                draw_clock()

            # zero
            if event.key == pygame.K_z:
                reset_game()
            
            draw_scores()

            # space -- transitions state 
            if event.key == pygame.K_SPACE:
                clear_leds()
                if (state == GameState.BUZZIN):
                    state = GameState.RUNNING
                else:
                    if (state == GameState.IDLE):
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
                
        if event.type == CLOCKEVENT:
            if clock > 0:
                if state == GameState.RUNNING: 
                    clock = clock - 250
                    # handle timeout
                    if clock == 0:
                        # play sound
                        for i in range(0, PLAYERS-1):
                            GPIO.output(led_map[i],True)

                        pygame.mixer.music.load("sounds/Soundsets/2/TIMESUP.mp3")
                        pygame.mixer.music.play()
                        state = GameState.TIMEUP
                        
                    draw_clock()

            if state == GameState.IDLE:
                # in idle state, walk the LEDs. 
                blinky += 1
                if blinky > PLAYERS-1:
                    blinky = 0

                for i in range(0, PLAYERS-1):
                    GPIO.output(led_map[i],False)

                GPIO.output(led_map[blinky], True)

        if buzzedin > -1:
            # now handle player buzz-in
            if state == GameState.RUNNING:
                buzzin(buzzedin)
            buzzedin = -1
