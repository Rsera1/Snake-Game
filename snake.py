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
import random
import time, sys, os, json

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


with open('placement.txt') as f: 
    data = f.read() 
  
d = json.loads(data) 

food_pos = '0 4 4'
food_flag = 0
scrn = 1
vid = 0

snks = []
var = 0
snk_length = 0
snk_history = ['0']
snk_dir = '0 0 0'
capture = 0


snake = [0,0,0]

flag = [0,0,0,0]


ent = [[0 for c in range(22)] for r in range(22)]


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
scr = 0
hscr = 0
ct,ct2= 0,0
cycle = 0
new = 0
rs_down = 0
rs_up = 0
rs_left = 0
rs_right = 0
snk_list = []
pos_arr = []
dir_arr = []
class MediaPlayer(ShowBase):
    
    def __init__(self):
        ShowBase.__init__(self)

        self.title_screen()

        #self.video()
        self.videoTask = taskMgr.add(self.video, "video")
        self.gameTask = taskMgr.add(self.gameLoop, "gameLoop")
        self.butTask = taskMgr.add(self.butLoop, "butLoop")
        self.entTask = taskMgr.add(self.entLoop, "entLoop")

        self.selectCycle()
        
    def snake_screen(self):
        global d
        self.m = self.loader.loadModel("snake_game.egg")
        self.m.reparentTo(self.render)
        self.m.setPosHpr(0, 45, 0, 0, 45, 0)
        self.food = self.loader.loadModel("Food.egg")
        self.food.reparentTo(self.render)
        self.food.setPosHpr(0.2+d[food_pos][2], 46+d[food_pos][0], -1+d[food_pos][1], 0, 0, 0)

    def add_snake(self):
        global snks, var, ct
        snks.append(self.loader.loadModel("python.egg"))
        for i in range(len(snks)):
            var = snks[i]
            var.reparentTo(self.render)
            if ct == 0:
                var.setPosHpr(0.2, 46, -1, 0, 45, 0)
            
    def update_snake(self):
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
            
    def reset(self):
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
        global cycle, scrn, vid, food_flag, ct, scr, hscr
        
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
            pass

        return Task.cont

    def gameLoop(self, task):
        global cycle, scrn, ct2, snake, d, food_pos, snk_list, capture, snk_length

        if scrn == 1:
            self.accept('arrow_down', self.keyboard_down, [3])
            self.accept('arrow_up', self.keyboard_up, [1])


        elif scrn == 2:
            self.accept('arrow_down', self.keyboard_down, [2])
            self.accept('arrow_up', self.keyboard_up, [1])

        elif scrn == 3:
            if ct2 == 5:
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
                    self.reset()

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
        global snake, var, snk_dir
        if snake[0] <= 6.5 and snake[1] <= 6.5:
            snake[0] += 0.65
            snake[1] += 0.65
            var.setPosHpr(0.2+snake[2], 46+snake[0], -1+snake[1], 0, 45, 0)
            snk_dir = '0 45 0'
                    
            
    def snake_dn(self):
        global snake, var, snk_dir
        if snake[0] >= -7.0 and snake[1] >= -7.0:
            snake[0] -= 0.65
            snake[1] -= 0.65
            var.setPosHpr(0.2+snake[2], 46+snake[0], -1+snake[1], -180, -45, 0)
            snk_dir = '-180 -45 0'
                 
           
    def snake_lt(self):
        global snake, var, snk_dir
        if snake[2] >= -10.5:
            snake[2] -= 1
            var.setPosHpr(0.2+snake[2], 46+snake[0]-0.7, -1+snake[1]-0.7, 90, 0, 0)
            snk_dir = '90 0 0'
            

    def snake_rt(self):
        global snake, var, snk_dir
        if snake[2] <= 9.5:
            snake[2] += 1
            var.setPosHpr(0.2+snake[2], 46+snake[0]-0.7, -1+snake[1]-0.7, -90, 0, 0)
            snk_dir = '-90 0 0'
            

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

    def fod(self):
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

    def entLoop(self,task):
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