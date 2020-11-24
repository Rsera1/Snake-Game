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

import time, sys, os

if os.environ.get('OS','') == 'Windows_NT':
    try:
        from pyjoycon import JoyCon, get_R_id
    except:
        print("hidapi libraries not found")




try:
    joycon_id = get_R_id()
    joycon = JoyCon(*joycon_id)
except:
    print("JoyCon can't connect")



scrn = 1
vid = 0

snake_x = 0
snake_y = 0
snake_z = 0

flag = [0,0,0,0]
# flag = [up, down, left, right]

# Function to put instructions on the screen.
def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(0, 0, 0, 1), shadow=(1, 1, 1, 1),
                        parent=base.a2dTopLeft, align=TextNode.ALeft,
                        pos=(0.08, -pos - 0.04), scale=.09)

# Function to put title on the screen.
def addTitle(pos, text):
    return OnscreenText(text=text, style=1, pos=(0.36, -pos - 0.04), scale=0.6,
                        parent=base.a2dTopLeft, align=TextNode.ALeft,
                        fg=(1, 1, 1, 1), shadow=(0, 0, 0, 1))

def addSelector(pos):
    return OnscreenImage(image='Selector1.png', pos=(-1.05,0,0), scale=(0.2,1,0.05))

ct,ct2= 0,0
cycle = 0
new = 0
rs_down = 0
rs_up = 0
rs_left = 0
rs_right = 0
class MediaPlayer(ShowBase):
    
    def __init__(self):
        ShowBase.__init__(self)

        self.title_screen()

        #self.video()
        self.videoTask = taskMgr.add(self.video, "video")
        self.gameTask = taskMgr.add(self.gameLoop, "gameLoop")
        self.butTask = taskMgr.add(self.butLoop, "butLoop")


        self.selectCycle()
        
    def snake_screen(self):
        self.m = self.loader.loadModel("snake_game.egg")
        self.m.reparentTo(self.render)
        self.m.setPosHpr(0, 45, 0, 0, 45, 0)
        self.snake = Actor("python.egg")
        self.snake.reparentTo(self.render)
        self.snake.setPosHpr(0.2, 46, -1, 0, 45, 0)

    def title_screen(self):
        self.t1 = addTitle(0.5, "PYTHO")
        self.t2 = addInstructions(1, "START")
        self.t3 = addInstructions(1.12, "OPTIONS")
        self.t4 = addInstructions(1.24, "QUIT")

    def del_title_screen(self):
        self.t1.destroy()
        self.t2.destroy()
        self.t3.destroy()
        self.t4.destroy()

    def options_screen(self): 
        self.opt = OnscreenImage(image='options.png', pos=(0,0,0), scale=(1,1,1))
        self.opt.setTransparency(1)

    def del_options_screen(self):
        self.opt.destroy()

    def title_to_option(self):
        self.options_screen()

    def option_to_title(self):
        self.del_options_screen()
        
    def enter_button(self):
        global cycle, scrn, vid
        
        if cycle == 2 and scrn == 1:     
            scrn = 2
            self.del_title_screen()
            self.options_screen()

        elif cycle == 1 and scrn == 1:
            scrn = 3
            vid = 2
            self.selector.destroy()
            self.del_title_screen()
            self.snake_screen()
                     
        elif cycle == 2 and scrn == 2:
            scrn = 1
            self.del_options_screen()
            self.title_screen()

        elif cycle == 3 and scrn == 1:
            sys.exit()

        cycle = 1
        self.selectCycle()

    def butLoop(self, task):
        global new,rs_down,rs_up,rs_left,rs_right
        global cycle, scrn
        global snake_x, snake_y
        try:
            arr = joycon.get_status()
            arr2 = arr['buttons']['right']
            arr3 = arr['analog-sticks']['right']
            #print(arr3)

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
                        self.keyboard_down(2)
                    rs_down = down
                    
                elif up + rs_up == 1:
                    if up:
                        self.keyboard_up(1)
                    rs_up = up

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
            print("JoyCon Status Denied")

        #self.joy(arr)

        return Task.cont

    def gameLoop(self, task):
        global cycle, scrn, ct2

        if scrn == 1:
            self.accept('arrow_down', self.keyboard_down, [3])
            self.accept('arrow_up', self.keyboard_up, [1])


        elif scrn == 2:
            self.accept('arrow_down', self.keyboard_down, [2])
            self.accept('arrow_up', self.keyboard_up, [1])

        elif scrn == 3:
            if ct2 == 5:
                self.direction()
                ct2 = 0
            else:
                ct2 += 1

            self.accept('arrow_down', self.dn_flag)
            self.accept('arrow_up', self.up_flag)
            self.accept('arrow_left', self.lt_flag)
            self.accept('arrow_right', self.rt_flag)

        self.accept('enter', self.enter_button) 

        return Task.cont

    def keyboard_up(self, mn):
        global cycle
        if cycle > mn:
            cycle -= 1
            self.selectCycle()

    def keyboard_down(self, mx):
        global cycle
        if cycle < mx:
            cycle += 1
            self.selectCycle()



    def dn_flag(self):
        global flag
        flag = [1,0,0,0]
    def up_flag(self):
        global flag
        flag = [0,1,0,0]
    def lt_flag(self):
        global flag
        flag = [0,0,1,0]
    def rt_flag(self):
        global flag
        flag = [0,0,0,1]



    def direction(self):
        global flag
        if flag[0] == 1:
            self.snake_dn()
        elif flag[1] == 1:
            self.snake_up()
        elif flag[2] == 1:
            self.snake_lt()
        elif flag[3] == 1:
            self.snake_rt()


    def snake_up(self):
        global snake_x, snake_y
        if snake_x <= 6.5 and snake_y <= 6.5:
            snake_x += 0.65
            snake_y += 0.65
            self.snake.setPosHpr(0.2+snake_z, 46+snake_x, -1+snake_y, 0, 45, 0)
                
            
    def snake_dn(self):
        global snake_x, snake_y
        if snake_x >= -7.0 and snake_y >= -7.0:
            snake_x -= 0.65
            snake_y -= 0.65
            self.snake.setPosHpr(0.2+snake_z, 46+snake_x, -1+snake_y, -180, -45, 0)
            
           
    def snake_lt(self):
        global snake_x, snake_y, snake_z
        if snake_z >= -10.5:
            snake_z -= 1
            self.snake.setPosHpr(0.2+snake_z, 46+snake_x-0.7, -1+snake_y-0.7, 90, 0, 0)
            
            

    def snake_rt(self):
        global snake_x, snake_y, snake_z
        if snake_z <= 9.5:
            snake_z += 1
            self.snake.setPosHpr(0.2+snake_z, 46+snake_x-0.7, -1+snake_y-0.7, -90, 0, 0)

    

    def selectCycle(self):
        global cycle,scrn
        
        if cycle == 1:
            if scrn == 1:
                self.selector.destroy()
                self.selector = OnscreenImage(image='Selector.png', pos=(-1.05,1,-0.01), scale=(0.2,1,0.05))
                self.selector.setTransparency(TransparencyAttrib.MAlpha)
                self.selector.setDepthWrite(False)
                self.selector.setBin('fixed', 0)
            elif scrn == 2:
                self.selector.destroy()
                self.selector = OnscreenImage(image='Selector.png', pos=(-.5,0,0.15), scale=(0.2,1,0.05))
                self.selector.setTransparency(TransparencyAttrib.MAlpha)
                self.selector.setDepthWrite(False)
                self.selector.setBin('fixed', 0)

        elif cycle == 2:
            if scrn == 1:
                self.selector.destroy()
                self.selector = OnscreenImage(image='Selector.png', pos=(-1.05,1,-0.13), scale=(0.2,1,0.05))
                self.selector.setTransparency(TransparencyAttrib.MAlpha)
                self.selector.setDepthWrite(False)
                self.selector.setBin('fixed', 0)
            elif scrn == 2:
                self.selector.destroy()
                self.selector = OnscreenImage(image='Selector.png', pos=(-.5,0,-0.47), scale=(0.2,1,0.05))
                self.selector.setTransparency(TransparencyAttrib.MAlpha)
                self.selector.setDepthWrite(False)
                self.selector.setBin('fixed', 0)
            
        elif cycle == 3:
            self.selector.destroy()
            self.selector = OnscreenImage(image='Selector.png', pos=(-1.05,1,-0.25), scale=(0.2,1,0.05))
            self.selector.setTransparency(TransparencyAttrib.MAlpha)
            self.selector.setDepthWrite(False)
            self.selector.setBin('fixed', 0)
            

        if cycle == 0:
            self.selector = OnscreenImage(image='Selector.png', pos=(-1.05,1,-0.01), scale=(0.2,1,0.05))
            self.selector.setTransparency(TransparencyAttrib.MAlpha)
            self.selector.setDepthWrite(False)
            self.selector.setBin('fixed', 0)
            cycle = 1
            
        

    def video(self,task):
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
        

player = MediaPlayer()
player.run()