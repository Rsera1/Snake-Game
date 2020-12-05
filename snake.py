#!/usr/bin/env python
from direct.showbase.Transitions import Transitions
from panda3d.core import TransparencyAttrib
from panda3d.core import *
# Tell Panda3D to use OpenAL, not FMOD
loadPrcFileData("", "audio-library-name p3openal_audio")
from direct.task import Task
from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
import soundcard as sc
import random
import time, sys, os, json

if os.environ.get('OS','') == 'Windows_NT':            # Checks if the computer running the program is Windows
    try:                                               # Tries to import the joycon dependency
        from pyjoycon import JoyCon, get_R_id
    except:
        print("hidapi libraries not found")

try:                                                   # Tries to establish a connection to a joycon
    joycon_id = get_R_id()
    joycon = JoyCon(*joycon_id)
except:
    print("JoyCon can't connect")


with open('placement.txt') as f:                       # Opens a preset json file for coordinates the snake can move to
    data = f.read() 
  
d = json.loads(data) 

food_pos = '0 4 4'                                     # Placement of the snake food in the game area
food_flag = 0                                          # A flag to allow the food to spawn when the game starts
scrn = 1                                               # Lets the program know what screen it needs to be on. 1:Menu, 2:Options, 3:Game, 4:Try Again
cycle = 0                                              # Lets the program know what option the selector bar should be at
vid = 0                                                # Controls when the menu background audio and video plays 

snks = []                                              # Array to hold all the snake models gained by eating food
var = 0                                                # Temporal variable when switching between snake models
snk_length = 0                                         # Keeps track of snake length
snk_history = ['0']                                    # Keeps track of the snake placement
snk_dir = '0 0 0'                                      # Keeps track of the direction of the snake.
capture = 0                                            # Used for boundary marking


snake = [0,0,0]                                        # Array holding the x, y, z coordinates of the snakes location       

flag = [0,0,0,0]                                       # Array of flags so the program knows what direction the snake needs to go next

speaker = 0                                            # Flag to know when onscreen text for audio checker can be deleted to avoid crashing


ent = [[0 for c in range(22)] for r in range(22)]      # Array of all placements the snake can be


def addInstructions(pos, msg):                                                          # Displays text
    return OnscreenText(text=msg, style=1, fg=(0, 0, 0, 1), shadow=(1, 1, 1, 1),
                        parent=base.a2dTopLeft, align=TextNode.ALeft,
                        pos=(0.08, -pos - 0.04), scale=.09)

# Function to put title on the screen.
def addTitle(pos, text):                                                                # Displays text
    return OnscreenText(text=text, style=1, pos=(0.36, -pos - 0.04), scale=0.6,         
                        parent=base.a2dTopLeft, align=TextNode.ALeft,
                        fg=(1, 1, 1, 1), shadow=(0, 0, 0, 1))

scr = 0                                                # Score counter
hscr = 0                                               # Highscore counter
ct,ct2= 0,0                                            # Counters for timing tasks

new = 0                                                # Previous button position of 'a' on the joycon
rs_down = 0                                            # Previous button position of right stick on the joycon
rs_up = 0                                              # Previous button position of right stick on the joycon
rs_left = 0                                            # Previous button position of right stick on the joycon
rs_right = 0                                           # Previous button position of right stick on the joycon
snk_list = []                                          # Used for boundary identification
pos_arr = []                                           # Array to keep track of snake position history
dir_arr = []                                           # Array to keep track of snake direction history

class MediaPlayer(ShowBase):                                          # Class for the game
    
    def __init__(self):                                               # Performs initial task when the game start up
        ShowBase.__init__(self)

        self.title_screen()                                          

        # Panda3d has a task manager system to have multiple loops running
        self.videoTask = taskMgr.add(self.video, "video")             
        self.gameTask = taskMgr.add(self.gameLoop, "gameLoop")
        self.butTask = taskMgr.add(self.butLoop, "butLoop")
        self.entTask = taskMgr.add(self.entLoop, "entLoop")

        self.selectCycle()                                           
        
    def snake_screen(self):                                           # Displays all initial graphics for in-game play
        global d
        self.m = self.loader.loadModel("snake_game_2.0.egg")
        self.m.reparentTo(self.render)
        self.m.setPosHpr(0, 45, 0, 0, 45, 0)
        self.food = self.loader.loadModel("Food.egg")
        self.food.reparentTo(self.render)
        self.food.setPosHpr(0.2+d[food_pos][2], 46+d[food_pos][0], -1+d[food_pos][1], 0, 0, 0)

    def add_snake(self):                                              # Adds another snake model to game area
        global snks, var, ct
        snks.append(self.loader.loadModel("python.egg"))
        for i in range(len(snks)):
            var = snks[i]
            var.reparentTo(self.render)
            if ct == 0:
                var.setPosHpr(0.2, 46, -1, 0, 45, 0)
            
    def update_snake(self):                                           # Updates the position and direction of all snake models in the game area
        global snks, snk_history, pos_arr, dir_arr
        
        for j in snk_history:
            history = j.split()
            pos = '{} {} {}'.format(history[0],history[1],history[2])
            drt = '{} {} {}'.format(history[3],history[4],history[5])
            pos_arr.append(pos)
            dir_arr.append(drt)


        for i in range(len(snks)-1):
            t = snks[i]
            direct = dir_arr[-i-1].split()
            if int(direct[0]) == 90 or int(direct[0]) == -90:
                t.setPosHpr(0.2+d[pos_arr[-i-1]][2], 46+d[pos_arr[-i-1]][0]-0.7, -1+d[pos_arr[-i-1]][1]-0.7, int(direct[0]), int(direct[1]), int(direct[2]))
            else:
                t.setPosHpr(0.2+d[pos_arr[-i-1]][2], 46+d[pos_arr[-i-1]][0], -1+d[pos_arr[-i-1]][1], int(direct[0]), int(direct[1]), int(direct[2]))
            
    def reset(self):                                                 # Resets the game area
        global food_pos, snks, var, snk_length, snk_history, snk_dir, snake, flag, ent, ct, pos_arr, dir_arr, scr
        for i in range(len(snks)):
            snks[i].removeNode()

        food_pos = '0 4 4'
        snks = []
        var = 0
        snk_length = 0
        snk_history = ['0']
        snk_dir = '0 0 0'
        snake = [0,0,0]
        flag = [0,0,0,0]
        ent = [[0 for c in range(22)] for r in range(22)]
        ct = 0
        pos_arr = []
        dir_arr = []
        scr = 0

        self.s_ct.destroy()

        self.s_ct = OnscreenText(text=str(scr), style=1, fg=(0, 0, 0, 1), shadow=(1, 1, 1, 1),
                                 parent=base.a2dTopLeft, align=TextNode.ALeft,
                                 pos=(0.4, -0.2 - 0.04), scale=.09)

        self.food.setPosHpr(0.2+d[food_pos][2], 46+d[food_pos][0], -1+d[food_pos][1], 0, 0, 0)

        self.add_snake()
        ct += 1



    def title_screen(self):                                                                    # Displays Menu
        self.t1 = addTitle(0.5, "PYTHO")
        self.t2 = addInstructions(1, "START")
        self.t3 = addInstructions(1.12, "OPTIONS")
        self.t4 = addInstructions(1.24, "QUIT")

    def del_title_screen(self):                                                                # Deletes Menu
        self.t1.destroy()
        self.t2.destroy()
        self.t3.destroy()
        self.t4.destroy()

    def options_screen(self, op):                                                              # Displays option screen
        if op == 1:
            self.opt = OnscreenImage(image='1.PNG', pos=(0,0,0), scale=(1.1,1,1))
            self.opt.setTransparency(1)
        elif op == 2:
            self.opt = OnscreenImage(image='2.PNG', pos=(0,0,0), scale=(1.1,1,1))
            self.opt.setTransparency(1)
        elif op == 3:
            self.opt = OnscreenImage(image='3.PNG', pos=(0,0,0), scale=(1.1,1,1))
            self.opt.setTransparency(1)


    def del_options_screen(self):                                                              # Deletes option screen
        self.opt.destroy()

    def title_to_option(self):                                                                 # Tranfer from menu to option screen
        self.options_screen()

    def option_to_title(self):                                                                 # Transfer from option to menu screen
        self.del_options_screen()

    def continue_screen(self):                                                                 # Displays "Try again" screen
        self.contin = OnscreenImage(image='continue.PNG', pos=(0,0,0), scale=(0.5,1,0.1))
        self.contin.setTransparency(1)
        
    def enter_button(self):                                                                    # Keeps track of what screen and option the selector is on to determine outcome of enter key
        global cycle, scrn, vid, food_flag, ct, scr, hscr, speaker
        
        if cycle == 1 and scrn == 1:
            scrn = 3
            vid = 2

            self.selector.destroy()
            self.del_title_screen()
            self.snake_screen()

            self.highscore = addInstructions(0.1, 'HIGHSCORE:')
            self.score = addInstructions(0.2, 'SCORE:')

            self.hs_ct = OnscreenText(text=str(hscr), style=1, fg=(0, 0, 0, 1), shadow=(1, 1, 1, 1), 
                                      parent=base.a2dTopLeft, align=TextNode.ALeft, 
                                      pos=(0.6, -0.1 - 0.04), scale=.09)
            self.s_ct = OnscreenText(text=str(scr), style=1, fg=(0, 0, 0, 1), shadow=(1, 1, 1, 1), 
                                     parent=base.a2dTopLeft, align=TextNode.ALeft, 
                                     pos=(0.4, -0.2 - 0.04), scale=.09)

            self.add_snake()
            ct += 1
            food_flag = 1


        elif cycle == 2 and scrn == 1:     
            scrn = 2
            self.del_title_screen()
            self.options_screen(1)
            cycle = 1

        elif cycle == 3 and scrn == 1 or cycle == 2 and scrn == 4:
            sys.exit()

        elif cycle == 1 and scrn == 2:
            if speaker == 1:
                self.speaker.destroy()
                speaker = 0
            self.del_options_screen()
            self.options_screen(1)

        elif cycle == 2 and scrn == 2:
            if speaker == 1:
                self.speaker.destroy()
                speaker = 0
            self.del_options_screen()
            self.options_screen(2)

        elif cycle == 3 and scrn == 2:
            self.del_options_screen()
            self.options_screen(3)

            try:
                aud = sc.default_speaker()
            except:
                aud = "Speaker not found"

            if speaker == 1:
                self.speaker.destroy()

            self.speaker = OnscreenText(text=str(aud), style=2, fg=(1, 0, 0, 1), shadow=(0, 0, 0, 1), 
                                        parent=base.a2dTopLeft, align=TextNode.ALeft, 
                                        pos=(1, -0.8), scale=.08, wordwrap=10)
            speaker = 1
                     
        elif cycle == 4 and scrn == 2:
            scrn = 1
            if speaker == 1:
                self.speaker.destroy()
                speaker = 0

            self.del_options_screen()
            self.title_screen()
            cycle = 1

        elif cycle == 1 and scrn == 4:
            self.contin.destroy()
            self.selector.destroy()
            self.reset()
            scrn = 3

        self.selectCycle()

    def butLoop(self, task):                                 # A task loop for outcomes of the joycon based on what screen and selector option
        global new,rs_down,rs_up,rs_left,rs_right
        global cycle, scrn
        try:
            arr = joycon.get_status()
            arr2 = arr['buttons']['right']
            arr3 = arr['analog-sticks']['right']
            
            if arr2['a'] + new == 1:
                if arr2['a'] == 1:
                    self.enter_button()
                new = arr2['a']

            down = int((3000 < arr3['horizontal'] < 3400) and (1200 < arr3['vertical'] < 2300))
            up = int((800 < arr3['horizontal'] < 1200) and (1200 < arr3['vertical'] < 2300))
            left = int((1300 < arr3['horizontal'] < 2800) and (700 < arr3['vertical'] < 1000))
            right = int((1300 < arr3['horizontal'] < 2800) and (2500 < arr3['vertical'] < 2900))

            if scrn == 1:
                if down + rs_down == 1:
                    if down:
                        self.keyboard_down(3)
                    rs_down = down
                    
                elif up + rs_up == 1:
                    if up:
                        self.keyboard_up(1)
                    rs_up = up

            elif scrn == 2:
                if down + rs_down == 1:
                    if down:
                        self.keyboard_down(4)
                    rs_down = down
                    
                elif up + rs_up == 1:
                    if up:
                        self.keyboard_up(1)
                    rs_up = up

            elif scrn == 4:
                if right + rs_right == 1:
                    if right:
                        self.keyboard_down(2)
                    rs_right = right
                    
                elif left + rs_left == 1:
                    if left:
                        self.keyboard_up(1)
                    rs_left = left

            elif scrn == 3:
                if down + rs_down == 1:
                    if down:
                        self.dn_flag()
                    rs_down = down

                elif up + rs_up == 1:
                    if up:
                        self.up_flag()
                    rs_up = up

                elif left + rs_left == 1:
                    if left:
                        self.lt_flag()
                    rs_left = left

                elif right + rs_right == 1:
                    if right:
                        self.rt_flag()
                    rs_right = right

        except NameError:
            pass

        return Task.cont

    def gameLoop(self, task):                                                       #Main game task loop for keyboard presses based on screen and selector option. Also determines when boundaries are hit.
        global cycle, scrn, ct2, snake, d, food_pos, snk_list, capture, snk_length

        if scrn == 1:
            self.accept('arrow_down', self.keyboard_down, [3])
            self.accept('arrow_up', self.keyboard_up, [1])
            self.accept('s', self.keyboard_down, [3])
            self.accept('w', self.keyboard_up, [1])

        elif scrn == 2:
            self.accept('arrow_down', self.keyboard_down, [4])
            self.accept('arrow_up', self.keyboard_up, [1])
            self.accept('s', self.keyboard_down, [4])
            self.accept('w', self.keyboard_up, [1])

        elif scrn == 4:
            self.accept('arrow_right', self.keyboard_down, [2])
            self.accept('arrow_left', self.keyboard_up, [1])
            self.accept('d', self.keyboard_down, [2])
            self.accept('a', self.keyboard_up, [1])


        elif scrn == 3:
            if ct2 == 4:
                self.hs_ct.destroy()
                self.s_ct.destroy()
                self.hs_ct = OnscreenText(text=str(hscr), style=1, fg=(0, 0, 0, 1), shadow=(1, 1, 1, 1),
                                          parent=base.a2dTopLeft, align=TextNode.ALeft,
                                          pos=(0.6, -0.1 - 0.04), scale=.09)

                self.s_ct = OnscreenText(text=str(scr), style=1, fg=(0, 0, 0, 1), shadow=(1, 1, 1, 1),
                                         parent=base.a2dTopLeft, align=TextNode.ALeft,
                                         pos=(0.4, -0.2 - 0.04), scale=.09)

                self.direction()
                ss = list(d.keys())[list(d.values()).index(snake)]
                spl = ss.split()
                his = ss + " " + snk_dir
                snk_history.append(his)
                snk_history.pop(0)
                
                spl2 = '{} {}'.format(spl[1],spl[2])
                
                ps = []
                for i in snk_history:
                    p = i.split()
                    pp = '{} {}'.format(p[1],p[2])
                    ps.append(pp)
                
                counts = dict()
                for j in ps:
                    counts[j] = counts.get(j, 0) + 1

                snk_list = list(counts.values())
                self.update_snake()
                
                if capture <= snk_length:
                    capture += 1

                boundary = snk_history[-1].split()
                if boundary[1] == '0' or boundary[2] == '0' or boundary[1] == '21' or boundary[2] == '21' or ((len(snk_list) <= snk_length) and capture-1 == snk_length) or counts[spl2] == 2:
                    self.continue_screen()
                    cycle = 1
                    scrn = 4
                    self.selectCycle()

                ct2 = 0
            else:
                ct2 += 1

            self.accept('arrow_down', self.dn_flag)
            self.accept('arrow_up', self.up_flag)
            self.accept('arrow_left', self.lt_flag)
            self.accept('arrow_right', self.rt_flag)
            self.accept('s', self.dn_flag)
            self.accept('w', self.up_flag)
            self.accept('a', self.lt_flag)
            self.accept('d', self.rt_flag)

        self.accept('enter', self.enter_button) 

        return Task.cont

    def keyboard_up(self, mn):      # Moves selector position up 1
        global cycle
        if cycle > mn:
            cycle -= 1
            self.selectCycle()

    def keyboard_down(self, mx):    # Moves selector position down 1
        global cycle
        if cycle < mx:
            cycle += 1
            self.selectCycle()

    # These 4 function determine if the snake is in the correct direction before changing the state of the snakes direction flags.
    def dn_flag(self):
        global flag, snk_dir
        if snk_dir != '0 45 0':
            flag = [1,0,0,0]
    def up_flag(self):
        global flag, snk_dir
        if snk_dir != '-180 -45 0':
            flag = [0,1,0,0]
    def lt_flag(self):
        global flag, snk_dir
        if snk_dir != '-90 0 0':
            flag = [0,0,1,0]
    def rt_flag(self):
        global flag, snk_dir
        if snk_dir != '90 0 0':
            flag = [0,0,0,1]



    def direction(self):          # Determines which direction function should be called based on snake direction flags.
        global flag
        if flag[0] == 1:
            self.snake_dn()
        elif flag[1] == 1:
            self.snake_up()
        elif flag[2] == 1:
            self.snake_lt()
        elif flag[3] == 1:
            self.snake_rt()


    def snake_up(self):                                                                 # Moves the position/direction of the snake up
        global snake, var, snk_dir
        if snake[0] <= 6.5 and snake[1] <= 6.5:
            snake[0] += 0.65
            snake[1] += 0.65
            var.setPosHpr(0.2+snake[2], 46+snake[0], -1+snake[1], 0, 45, 0)
            snk_dir = '0 45 0'
                    
            
    def snake_dn(self):                                                                 # Moves the position/direction of the snake down
        global snake, var, snk_dir
        if snake[0] >= -7.0 and snake[1] >= -7.0:
            snake[0] -= 0.65
            snake[1] -= 0.65
            var.setPosHpr(0.2+snake[2], 46+snake[0], -1+snake[1], -180, -45, 0)
            snk_dir = '-180 -45 0'
                 
           
    def snake_lt(self):                                                                 # Moves the position/direction of the snake left
        global snake, var, snk_dir
        if snake[2] >= -10.5:
            snake[2] -= 1
            var.setPosHpr(0.2+snake[2], 46+snake[0]-0.7, -1+snake[1]-0.7, 90, 0, 0)
            snk_dir = '90 0 0'
            

    def snake_rt(self):                                                                 # Moves the position/direction of the snake right
        global snake, var, snk_dir
        if snake[2] <= 9.5:
            snake[2] += 1
            var.setPosHpr(0.2+snake[2], 46+snake[0]-0.7, -1+snake[1]-0.7, -90, 0, 0)
            snk_dir = '-90 0 0'
    
    def select(self,px,py,pz,sx,sy,sz):                                                 # Displays selector on screen with user selectable options
        global scrn
        self.selector.destroy()
        if scrn == 4:
            self.selector = OnscreenImage(image='Selector2.png', pos=(px,py,pz), scale=(sx,sy,sz))
        else:
            self.selector = OnscreenImage(image='Selector.png', pos=(px,py,pz), scale=(sx,sy,sz))
        self.selector.setTransparency(TransparencyAttrib.MAlpha)
        self.selector.setDepthWrite(False)
        self.selector.setBin('fixed', 0)       

    def selectCycle(self):                                                              # Displays selector at certain positions based on which screen and selector option comes next
        global cycle,scrn
        
        if cycle == 1:
            if scrn == 1:
                self.select(-1.05,1,-0.01,0.2,1,0.05)
            elif scrn == 2:
                self.select(-0.82,0,0.51,0.26,1,0.07)
            elif scrn == 4:
                self.select(-0.33,0,-0.04,-0.1,1,0.01)

        elif cycle == 2:
            if scrn == 1:
                self.select(-1.05,1,-0.13,0.2,1,0.05)
            elif scrn == 2:
                self.select(-0.82,0,0.13,0.26,1,0.07)
            elif scrn == 4:
                self.select(0.31,0,-0.04,-0.1,1,0.01)
            
        elif cycle == 3:
            if scrn == 1:
                self.select(-1.05,1,-0.25,0.2,1,0.05)
            elif scrn == 2:
                self.select(-0.82,0,-0.25,0.26,1,0.07)
            
        elif cycle == 4:
            if scrn == 2:
                self.select(-0.82,0,-0.63,0.26,1,0.07)

        if cycle == 0:
            self.selector = OnscreenImage(image='Selector.png', pos=(-1.05,1,-0.01), scale=(0.2,1,0.05))
            self.selector.setTransparency(TransparencyAttrib.MAlpha)
            self.selector.setDepthWrite(False)
            self.selector.setBin('fixed', 0)
            cycle = 1
            
        

    def video(self,task):                               # Displays the background audio and video for the menu
        global vid, card

        if vid == 0:
            self.tex = MovieTexture("name")
            success = self.tex.read("Intro.avi")
            assert success, "Failed to load video!"
            cm = CardMaker("My Fullscreen Card")
            cm.setFrameFullscreenQuad()
            cm.setUvRange(self.tex)
            card = NodePath(cm.generate())
            card.reparentTo(self.render2d)
            card.setTexture(self.tex)
            self.sound = loader.loadSfx("Aesir.avi")
            self.sound.setLoop(True)
            self.sound.play()
            self.tex.setLoop(True)
            self.tex.play()
            vid = 1;
            return Task.cont
        elif vid == 2:
            self.tex.stop()
            self.sound.stop()
            card.removeNode()
            return Task.done
        else:
            return Task.cont

    def fod(self):                                     # Updates scores, randomizes food position and updates snake placement history based on its length
        global food_pos, snake, snk_length, capture, scr, hscr
        ss = list(d.keys())[list(d.values()).index(snake)]
        fd1 = ss.split()
        fd2 =food_pos.split()
        if int(fd1[1])+1 == int(fd2[1]) and int(fd1[2]) == int(fd2[2]):
            x = random.randint(2, 20)
            y = random.randint(2, 20)


            snk_length += 1
            his = ss + " " + snk_dir
            snk_history.append(his)
            capture = 0

            scr += 1
            if hscr < scr:
                hscr += 1
            
            if ent[x][y] != 1:
                self.add_snake()
                food_pos = '0 {} {}'.format(x,y)
        self.food.setPosHpr(0.2+d[food_pos][2], 46+d[food_pos][0], -1+d[food_pos][1], 0, 0, 0)

    def entLoop(self,task):                                    # Task loop for identifying snake placement for future food to spawn
        global ent, snake, food_flag
        if food_flag == 1:
            self.fod()
        ent = [[0 for c in range(22)] for r in range(22)]
        lst = list(d.keys())[list(d.values()).index(snake)]
        key = lst.split()
        ent[int(key[1])][int(key[2])] = 1
        return Task.cont 

player = MediaPlayer()
player.run()