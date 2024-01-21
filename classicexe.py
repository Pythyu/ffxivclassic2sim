from tkinter import *
import math
import random

from datetime import datetime
random.seed(datetime.now().timestamp())

REFRESH_RATE = 50

import sys
from os import path

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    return "img/" + relative_path
   # base_path = getattr(sys, '_MEIPASS', path.dirname(path.abspath(__file__)))
   # return path.join(base_path, relative_path)

class Node:
    def __init__(self, x, y, size, nodeType):
        self.x = x
        self.y = y
        self.size = size
        self.nodeType = nodeType # 0 : penta 1 : tri 2 : square
        self.drawFunc = [self.draw_penta, self.draw_triangle, self.draw_square]

    def rotate_180(self, center_x, center_y):
        vectx = self.x - center_x
        vecty = self.y - center_y
        self.x = center_x + -1 * vectx
        self.y = center_y + -1 * vecty

    def draw(self, canvas):
        self.drawFunc[self.nodeType](canvas)

    def draw_square(self, canvas):
        canvas.create_rectangle(self.x - self.size,
                                self.y - self.size,
                                self.x + self.size,
                                self.y + self.size, fill = "yellow")

    def draw_triangle(self, canvas):
        tetha1 = -math.pi / 6
        tetha2 = math.pi / 2
        tetha3 = math.pi + math.pi / 6
        pos = [self.x + math.cos(tetha1)*self.size, self.y + math.sin(tetha1)*self.size,
               self.x + math.cos(tetha2)*self.size, self.y + math.sin(tetha2)*self.size,
               self.x + math.cos(tetha3)*self.size, self.y + math.sin(tetha3)*self.size]
        canvas.create_polygon(pos, fill = "red")

    def draw_penta(self, canvas):
        tetha1 = math.pi / 10
        tetha2 = math.pi / 2
        pos = [self.x + math.cos(tetha1)*self.size, self.y + math.sin(tetha1)*self.size,
               self.x + math.cos(tetha2)*self.size, self.y + math.sin(tetha2)*self.size]
        for k in range(1,4):
            pos.append(self.x + math.cos(tetha2 + k * (2*math.pi/5)) * self.size)
            pos.append(self.y + math.sin(tetha2 + k * (2*math.pi/5)) * self.size)
        canvas.create_polygon(pos, fill = "blue")

class CastBar:
    def __init__(self,xa, ya, xb, yb):
        self.text = "Panta Rhei"
        self.cast_time = 15
        self.progress = 0
        self.xa = xa
        self.ya = ya
        self.xb = xb
        self.yb = yb
        self.instep = 5

    def tick(self, can):
        if self.progress >= 1:
            return True
        REFRESH_STEP = 1000 / REFRESH_RATE
        self.progress += 1 / (self.cast_time * REFRESH_STEP)
        can.create_text((self.xb + self.xa) / 2, self.ya - self.instep*4, text=self.text, 
                fill="black", font="Arial 28 italic")
        # outline
        can.create_rectangle(self.xa, self.ya, self.xb, self.yb, outline = "black")
        # fill
        new_xa = self.xa + (self.xb - self.xa) * self.progress
        can.create_rectangle(self.xa + self.instep, self.ya + self.instep,
                                new_xa, self.yb - self.instep, fill = "black")
        return False

class TerrainLoader:
    def __init__(self, path="data.terrain"):
        self.path = resource_path(path)
        self.fd = open(self.path, "r")
        self.terrains = []
        self.gen_terrains()
        random.shuffle(self.terrains)
    
    def __destroy__(self):
        self.fd.close()

    def reset_terrain(self, newpath=None):
        if newpath is None:
            newpath = self.path
        else:
            newpath = resource_path(newpath)
        self.fd.close()
        self.fd = open(newpath, "r")
        self.terrains = []
        self.gen_terrains()
        random.shuffle(self.terrains)
    
    def look_for(self, x, y, alpha=True, ignore=[]):
        potential = []
        for yi in [-1,0,1]:
            for xi in [-1,0,1]:
                nx = x + xi
                ny = y + yi
                if abs(xi) == abs(yi) or (nx,ny) in ignore:
                    continue
                if 0 <= nx <= 3 and 0 <= ny <= 2:
                    if alpha is None: # looking for blue
                        if self.terrain[nx][ny].nodeType == 0:
                            return (nx, ny)
                    elif (nx,ny) not in self.taken:
                        if alpha: # Alpha debuff
                            if self.terrain[nx][ny].nodeType == 1:
                                potential.append((nx,ny))
                        else: # Beta debuff
                            if self.terrain[nx][ny].nodeType == 2:
                                potential.append((nx,ny))
        if len(potential) == 1:
            self.taken.append(potential[0])
            return potential[0]
        for pos in potential:
            found = self.look_for(pos[0], pos[1], alpha=None, ignore=[(x,y)])
            if not found:
                self.taken.append(pos)
                return pos
        return None
    
    def solve_terrain(self):
        self.taken = []
        origin_map = {}
        soluce = [[None, None] for _ in range(4)] # [alpha, beta] for bpog
        for x in range(4):
            for y in range(3):
                if self.terrain[x][y].nodeType == 0:
                    alpha_out = self.look_for(x,y)
                    beta_out = self.look_for(x,y,alpha=False)
                    if not (alpha_out and beta_out):
                        return None, None
                    else:
                        soluce[x][0] = alpha_out
                        soluce[x][1] = beta_out
                        origin_map[alpha_out] = (x,y)
                        origin_map[beta_out] = (x,y)
        return soluce, origin_map

    def gen_terrains(self):
        while True:
            mapping = {"B":0,"R":1,"Y":2}
            terrain = [[None for _ in range(3)] for _ in range(4)]
            step_x = 1024/4
            step_y = 760/3
            for y in range(3):
                startx = step_x / 2
                starty = step_y / 2
                line = self.fd.readline()
                if not line:
                    return
                for x,char in enumerate(line):
                    if char == "\n":
                        continue
                    terrain[x][y] = Node(startx + x*step_x,
                            starty + y*step_y,30,mapping[char])
            self.terrains.append(terrain)
            line = self.fd.readline()
            if not line:
                return

    def rotate_terrain(self):
        self.terrain = [list(reversed(elem)) for elem in reversed(self.terrain)]

    def get_one(self, ishard=False):
        if not self.terrains:
            if ishard:
                self.reset_terrain("hardmode.data")
            else:
                self.reset_terrain("data.terrain")

        self.terrain = self.terrains.pop()
        return self.terrain
 
class Player:
    def __init__(self, x, y):
        self.BLUE = PhotoImage(file=resource_path("./Blue.png"))
        self.PURPLE = PhotoImage(file=resource_path("./Purple.png"))
        self.GREEN = PhotoImage(file=resource_path("./Green.png"))
        self.ORANGE = PhotoImage(file=resource_path("./Orange.png"))
        self.x = x
        self.y = y
        self.target = None
        self.speed = 25
        self.marker = random.choice(["B","P","G","O"])
        self.markerMap = {"B":self.BLUE,"P":self.PURPLE,
                "G":self.GREEN,"O":self.ORANGE}

    def move(self):
        if not self.target:
            return
        
        diffx = (self.target[0] - self.x)
        diffy = (self.target[1] - self.y)
        norm = math.sqrt(diffx**2 + diffy**2)
        if norm == 0:
            norm = 1
        diffx /= norm
        diffy /= norm
        self.x += diffx * self.speed
        self.y += diffy * self.speed
        if norm <= self.speed:
            self.x = self.target[0]
            self.y = self.target[1]
            self.target = None

    def draw(self, can):
        self.move()
        if self.marker:
            can.create_image(self.x, self.y-40, image=self.markerMap[self.marker])
        can.create_oval(self.x-10,self.y-10,self.x+10,self.y+10, fill="black")

class OptionPanel:
    def __init__(self, tk, app):
        self.tk = tk
        self.app = app
        self.pausevalue = False
        self.singleplayer = True
        self.hard = False
        self.terobj = None

        self.frame = Frame(self.tk, width=200,height=760)
        self.frame.pack_propagate(0)
        self.frame.pack(side="right")

        self.pause = Button(self.frame, text="Pause", command=self.pausegame)
        self.pause.pack(side="top")

        self.lab = Label(self.frame, text="Cast Speed :")
        self.lab.pack(side="top")
        self.spinvar = DoubleVar()
        self.spinvar.set(1)
        self.spin = Spinbox(self.frame, from_=0.1, to=5, increment=0.1, format="%.1f", textvariable=self.spinvar)
        self.spin.pack(side="top")

        self.singlemode = Checkbutton(self.frame, text="Control two player ?", 
                command=self.switch_single)
        self.singlemode.pack(side="top")

        self.hardb = Checkbutton(self.frame, text="Hard pattern only", 
                command=self.hardmode)
        self.hardb.pack(side="top")

        self.blueVar = BooleanVar()
        self.blueVar.set(True)
        self.greenVar = BooleanVar()
        self.greenVar.set(True)
        self.purpleVar = BooleanVar()
        self.purpleVar.set(True)
        self.orangeVar = BooleanVar()
        self.orangeVar.set(True)

        self.internalFrame = Frame(self.frame)
        self.internalFrame.pack(side="top")
        
        self.blueSymb = Checkbutton(self.internalFrame, image=self.app.player.BLUE, variable=self.blueVar)
        self.blueSymb.pack()
        self.greenSymb = Checkbutton(self.internalFrame, image=self.app.player.GREEN, variable=self.greenVar)
        self.greenSymb.pack()
        self.purpleSymb = Checkbutton(self.internalFrame, image=self.app.player.PURPLE, variable=self.purpleVar)
        self.purpleSymb.pack()
        self.orangeSymb = Checkbutton(self.internalFrame, image=self.app.player.ORANGE, variable=self.orangeVar)
        self.orangeSymb.pack()

        self.skip = Button(self.frame, text="Finish CastBar", command=self.skip_castbar)
        self.skip.pack(side="top")


    def hardmode(self):
        self.hard = not self.hard
        if self.hard:
            self.terobj.reset_terrain("hardmode.data")
        else:
            self.terobj.reset_terrain("data.terrain")

    def pausegame(self):
        self.pausevalue = not self.pausevalue

    def switch_single(self):
        self.singleplayer = not self.singleplayer

    def skip_castbar(self):
        self.app.castbar.progress = 0.99

    def get_marker_possibilities(self):
        markers = ["B","G","P","O"]
        output = []
        for k,var in enumerate([self.blueVar, self.greenVar, self.purpleVar, self.orangeVar]):
            if var.get():
                output.append(markers[k])
        return output


class App:
    def __init__(self):
        self.width = 1024
        self.height = 760
        self.mecha = False
        self.soluce = None
        self.eventTurn = False
        self.tk = Tk()
        self.can = Canvas(width=self.width, height=self.height+100)
        self.can.pack(side="left")

        self.player = Player(self.width/2, self.height/2)
        self.panel = OptionPanel(self.tk, self)

        self.bg = PhotoImage(file=resource_path("p2-waymarks.png"))
        self.can.create_image(0,0, image=self.bg, anchor="nw")
        
        self.loader = TerrainLoader()
        self.panel.terobj = self.loader
        self.terrain = self.loader.get_one()
        self.castbar = CastBar(100, self.height + 30, self.width - 100, self.height + 90)
        self.player2 = Player(self.width/2, self.height/2)
        self.player2.marker = self.player.marker

        self.update()

        self.can.bind("<Button-1>", self.motion)
        self.tk.mainloop()

    def update(self):
        self.tk.after(REFRESH_RATE, self.update)
        self.can.delete("all")
        self.can.create_image(0,0, image=self.bg, anchor="nw")
        if not self.panel.singleplayer and self.player2.marker != self.player.marker:
            self.player2.marker = self.player.marker
        if not self.panel.pausevalue:
            barprog = self.castbar.tick(self.can)
            if barprog and not self.mecha:
                self.mecha = True
                self.castbar.cast_time = 5 / self.panel.spinvar.get()
                self.castbar.progress = 0
                self.castbar.text = "Reset Time"
                self.player.marker = None
                if not self.panel.singleplayer:
                    self.player2.marker = None
                self.show(True)
            elif barprog and self.mecha:
                self.mecha = False
                self.soluce = None
                self.castbar.cast_time = 15 / self.panel.spinvar.get()
                self.castbar.progress = 0
                self.castbar.text = "Panta Rhei"
                self.terrain = self.loader.get_one(self.panel.hard)
                self.player.marker = random.choice(self.panel.get_marker_possibilities())
                if not self.panel.singleplayer:
                    self.player2.marker = self.player.marker
                self.show()
            else:
                self.show()
        else:
            self.show()
        self.player.draw(self.can)
        
        if not self.panel.singleplayer:
            self.player2.draw(self.can)
        
        
    def motion(self, event):
        playerObject = self.player
        if not self.panel.singleplayer:
            if self.eventTurn:
                playerObject = self.player2
            self.eventTurn = not self.eventTurn

        if 0 <= event.x <= self.width and 0 <= event.y <= self.height:
            playerObject.target = [event.x, event.y]

    def generate_terrain(self, width=1024, height=760):
        terrain = [[None for _ in range(3)] for _ in range(4)]
        step_y = height / 3
        step_x = width / 4
        types = [1,2] * 4 
        for x in range(4):
            ystart = step_y / 2
            xstart = step_x / 2
            random.shuffle(types)
            count = 0
            for y in range(3):
                if count >= 0 and (random.randint(1,3) == 3 or count >= 2):
                    count = -1
                    terrain[x][y] = Node(xstart + x * step_x, ystart + y * step_y, 30, 0)
                else:
                    if count >= 0:
                        count += 1
                    terrain[x][y] = Node(xstart + x * step_x, ystart + y * step_y, 30, types.pop())
        return terrain
    
   # def check_players_mech(self):
   #     patterns = ["B","P","O","G"]
   #     idx = patterns.index(self.player.marker)
   #     step_y = self.height / 3
   #     step_x = self.width / 4
   #     col = self.soluce[idx]
   #     for role in col:
   #         x,y = role
   #         bluepos = self.blue_origin[(x,y)]
   #         xa, xb = step_x/2 + x*step_x, step_x/2 + bluepos[0]*step_x
   #         if xa > xb:
   #             xa, xb = xb, xa
   #         ya, yb = step_y/2 + y*step_y, step_y/2 + bluepos[1]*step_y
   #         if ya > yb:
   #             ya, yb = yb, ya
   #         if xa <= self.player.x <= xb 
   #         self.can.create_line(step_x/2 + x*step_x,
   #                             step_y/2 + y*step_y,
   #                             step_x/2 + bluepos[0]*step_x,
   #                             step_y/2 + bluepos[1]*step_y, width=5)
   #         self.can.create_image(step_x/2 + x*step_x,
   #                 step_y/2 + y*step_y, image=markerMap[k])


    
    def show(self, rotate=False):
        for column in self.terrain:
            for node in column:
                if rotate:
                    node.rotate_180(self.width/2, self.height/2)
                node.draw(self.can)
        if rotate:
            self.loader.rotate_terrain()
            self.soluce, self.blue_origin = self.loader.solve_terrain()
        if self.soluce:
            markerMap = [self.player.BLUE,self.player.PURPLE,
            self.player.ORANGE,self.player.GREEN]
            step_y = self.height / 3
            step_x = self.width / 4
            for k,col in enumerate(self.soluce):
                for role in col:
                    x,y = role
                    bluepos = self.blue_origin[(x,y)]
                    self.can.create_line(step_x/2 + x*step_x,
                                        step_y/2 + y*step_y,
                                        step_x/2 + bluepos[0]*step_x,
                                        step_y/2 + bluepos[1]*step_y, width=5)
                    self.can.create_image(step_x/2 + x*step_x,
                            step_y/2 + y*step_y, image=markerMap[k])

                



if __name__ == "__main__":
    App()
