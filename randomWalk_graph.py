from tkinter import *
from tkinter import ttk
import time

import numpy as np
import simpy as sp
import scipy.stats
from math import sin, cos, inf

class Node:
    def __init__(self, i):
        self.touch = 0
        self.ID = i
        self.neighbors = []
        self.pos = []
        self.draw = None
        self.color = (255,255,255)
    
class Graph_randomWalk:
    def __init__(self, matrix):
        self.mat = matrix
        self.nodes = []
        self.trace = []
        for i, line in enumerate(matrix):
            self.nodes.append(Node(i))
            for j ,path in enumerate(line):
                if path != 0:
                    self.nodes[i].neighbors.append(j)
                            
    def randomWalk(self, N_steps):
        p = np.random.randint(0, len(self.nodes))
        startNode = self.nodes[p]
        self.trace.append(p)
        for i in range(N_steps):
            startNode.touch += 1
            if startNode.neighbors != []:
                p = np.random.randint(len(startNode.neighbors))
                nextNode = self.nodes[startNode.neighbors[p]]
                self.trace.append(startNode.neighbors[p])
                startNode = nextNode
        for n in self.nodes:
            print('node', n.ID)
            print('neighbors:', n.neighbors)
            print('touched:', n.touch)
            n.touch = 0

class appGUI:
    def __init__(self):
        Width = 400
        Height = 500
        self.root = Tk()
        self.anima = ttk.Frame(self.root, borderwidth=5) 
        self.anima.grid(column=0, row=0, columnspan=1, rowspan=2) 
        self.canvas = Canvas(self.anima, width = Width, height = Height)
        self.canvas.pack() 
        self.draw_net_demo()
        self.root.title("random walk demo")
        self.root.mainloop()

        
    def draw_net_demo(self):
        mat_demo = [[0, 1, 0, 1, 1, 0, 0, 0, 0],
                    [1, 0, 1, 1, 1, 1, 0, 0, 0],
                    [0, 1, 0, 0, 1, 1, 0, 0, 0],
                    [1, 1, 0, 0, 1, 0, 1, 1, 0],
                    [1, 1, 1, 1, 0, 1, 1, 1, 1],
                    [0, 1, 1, 0, 1, 0, 0, 1, 1],
                    [0, 0, 0, 1, 1, 0, 0, 1, 0],
                    [0, 0, 0, 1, 1, 1, 1, 0, 1],
                    [0, 0, 0, 0, 1, 1, 0, 1, 0]]
        N_walk = 1000
        g = Graph_randomWalk(mat_demo)
        g.randomWalk(N_walk)
        start_pos = [20, 20]
        x, y = start_pos
        step_len = 80
        l = 10
        i = 0
        edge_list = {}
        for i in range(3):
            for j in range(3):
                g.nodes[i*3+j].draw = self.canvas.create_oval(x-l, y-l, x+l, y+l, fill= 'white')
                g.nodes[i*3+j].pos = [x,y]
                x += step_len
            x = start_pos[0]
            y += step_len
        for i in range(9):
            for j in range(i+1, 10):
                if j in g.nodes[i].neighbors:
                    edge_list[(i,j)] = self.canvas.create_line(g.nodes[i].pos, g.nodes[j].pos, fill= 'blue')

        n_pre = g.trace[0]
        DELAY = 0.0000
        self.canvas.itemconfig(g.nodes[n_pre].draw, fill='red')
        self.anima.update()
        time.sleep(DELAY)
        self.canvas.itemconfig(g.nodes[n_pre].draw, fill='white')
        self.anima.update()
        for i in range(1, N_walk):
            n = g.trace[i]
            #edge color change
            a,b = min(n_pre, n), max(n_pre, n)
            self.canvas.itemconfig(edge_list[(a,b)], fill='yellow')
            #node color change
            self.canvas.itemconfig(g.nodes[n].draw, fill='red')
            self.anima.update()
            time.sleep(DELAY)
            self.canvas.itemconfig(edge_list[(a,b)], fill='blue')
            g.nodes[n].touch += 1
            c = max(0, 255-int(255*g.nodes[n].touch/N_walk*5))
            g.nodes[n].color = (255, c, c)
            newcolor = '#%02x%02x%02x' % g.nodes[n].color
            self.canvas.itemconfig(g.nodes[n].draw, fill=newcolor)
            self.anima.update()
            n_pre = n       
app = appGUI()                
                
                
        
        
        
                    
# g = Graph_randomWalk([[0, 1, 1, 1],
#                       [1, 0, 1, 1],
#                       [1, 1, 0, 1],
#                       [1, 1, 1, 0]])
# g.randomWalk(100000)
#
# for n in g.nodes:
#     print('node', n.ID)
#     print('neighbors:', n.neighbors)
#     print('touched:', n.touch)