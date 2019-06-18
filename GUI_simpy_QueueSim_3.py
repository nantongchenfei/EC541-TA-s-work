## Author: Chen, Fei
## Date: July 22, 2018
## Project: EC541 lab
## A simulation model for MMxx or MDxx queues, show the waiting time animation and reports average waiting time, utilization, number of customers in queue. Run on Python 3.6 with simpy as simulation core lib.
## new features added, jackson network, new drawing for that.
## SimPy version: 3.010
## Python version: 3.6.3

from tkinter import *
from tkinter import ttk
import time

import numpy as np
import simpy as sp
import scipy.stats
import math


class Queue_sim:
    def __init__(self, queueType, N_arrivals, mean_arrival, mean_service):
        self.N_arrivals = N_arrivals
        self.L_arrivals = [] #the information list of the arrivals of [ID, arrivalTime, serviceTime, waitTime]
        self.mean_arrival = mean_arrival
        self.mean_service = mean_service
        self.env = sp.Environment()
        self.customerProcess = self.env.process(self.arrivals())
        self.queue_Len = 0
        self.queue_T = [] 
        self.queueType = queueType
        self.res = sp.Resource(self.env, capacity=int(queueType[2]))  
        self.res_count_l = []   

    def arrivals(self):
        for i in range(self.N_arrivals):
            T_interArrival = np.random.exponential(self.mean_arrival)
            if self.queueType[1] == 'M': #service time uniformly distributed
                T_service = np.random.exponential(self.mean_service)
            elif self.queueType[1] == 'D': #service time determined
                T_service = self.mean_service
            elif self.queueType[1] == 'G': #service time uniformly distributed
                T_service = np.random.exponential(self.mean_service) # now the parameter is a list; [low, high]
            else:              
                print('unsupported queue type, only MMx or MDx')
                exit()
            T_wait = math.inf
            self.L_arrivals.append([i, self.env.now, T_service, T_wait])
            self.queue_Len += 1
            self.queue_T.append([self.env.now, self.queue_Len])
            self.env.process(self.service(i, T_service))
            yield self.env.timeout(T_interArrival)

    def service(self, i, T_service):
        # print(str(i) + ' joined the queue at: ' + str(self.env.now))
        with self.res.request() as req:
            yield req
            self.res_count_l.append([self.env.now, self.res.count])
            self.queue_Len -= 1
            self.queue_T.append([self.env.now, self.queue_Len])
            # print(str(i) + ' left the queue at: ' + str(self.env.now))
            self.L_arrivals[i][3] = self.env.now - self.L_arrivals[i][1]
            yield self.env.timeout(self.L_arrivals[i][2])
            self.res.release(req)
            self.res_count_l.append([self.env.now, self.res.count])
            
class JacksonQueue_2_sim:
    def __init__(self, queueType, N_arrivals, mean_arrival, mean_service, P_backin = 0.5):
        self.N_arrivals = N_arrivals
        self.L_arrivals = [] #the information list of the arrivals of [ID, arrivalTime, serviceTime, waitTime]
        self.mean_arrival = mean_arrival
        self.mean_service = mean_service
        self.env = sp.Environment()
        self.customerProcess = self.env.process(self.arrivals_outside())
        self.queue1_Len = 0
        self.queue1_T = []
        self.queue2_Len = 0
        self.queue2_T = []
        self.queueType = queueType
        self.res1 = sp.Resource(self.env, capacity=int(queueType[2])) 
        self.res2 = sp.Resource(self.env, capacity=int(queueType[2]))  
        self.res1_count_l = [] 
        self.res2_count_l = []
        self.P_backin = P_backin

    def arrivals_outside(self):
        for i in range(self.N_arrivals):
            T_interArrival = np.random.exponential(self.mean_arrival)
            if self.queueType[1] == 'M': #service time uniformly distributed
                T_service = np.random.exponential(self.mean_service)
            elif self.queueType[1] == 'D': #service time determined
                T_service = self.mean_service
            elif self.queueType[1] == 'G': #service time uniformly distributed
                T_service = np.random.exponential(self.mean_service) # now the parameter is a list; [low, high]
            else:              
                print('unsupported queue type, only MMx or MDx')
                exit()
            T_wait = math.inf
            self.L_arrivals.append([i, self.env.now, T_service, T_wait])

            self.env.process(self.service_1(i, T_service))
            yield self.env.timeout(T_interArrival)

    def service_1(self, i, T_service):
        # print(str(i) + ' joined the queue at: ' + str(self.env.now))
        self.queue1_Len += 1
        self.queue1_T.append([self.env.now, self.queue1_Len])
        with self.res1.request() as req:
            yield req
            self.res1_count_l.append([self.env.now, self.res1.count])
            self.queue1_Len -= 1
            self.queue1_T.append([self.env.now, self.queue1_Len])
            # print(str(i) + ' left the queue at: ' + str(self.env.now))
            self.L_arrivals[i][3] = self.env.now - self.L_arrivals[i][1]
            yield self.env.timeout(self.L_arrivals[i][2])
            self.res1.release(req)
            self.res1_count_l.append([self.env.now, self.res1.count])
            if np.random.uniform(0, 1) > self.P_backin:
                self.env.process(self.service_2(i, T_service))

            
    def service_2(self, i, T_service):
        # print(str(i) + ' joined the queue at: ' + str(self.env.now))
        self.queue2_Len += 1
        self.queue2_T.append([self.env.now, self.queue2_Len])
        with self.res2.request() as req:
            yield req
            self.res2_count_l.append([self.env.now, self.res2.count])
            self.queue2_Len -= 1
            self.queue2_T.append([self.env.now, self.queue2_Len])
            # print(str(i) + ' left the queue at: ' + str(self.env.now))
            self.L_arrivals[i][3] = self.env.now - self.L_arrivals[i][1]
            yield self.env.timeout(self.L_arrivals[i][2])
            self.res2.release(req)
            self.res2_count_l.append([self.env.now, self.res2.count])
            self.env.process(self.service_1(i, T_service))

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
        Height = 400
        self.root = Tk()
        self.anima = ttk.Frame(self.root, borderwidth=5) 
        self.anima.grid(column=0, row=0, columnspan=1, rowspan=2) 
        self.canvas = Canvas(self.anima, width = Width, height = Height)
        self.canvas.pack() 
        self.draw_net_demo()
        self.root.title("random walk demo")
        self.root.mainloop()

        
    def draw_net_demo(self):
        global stop_signal
        global show_delay
        mat_demo = [[0, 1, 0, 1, 1, 0, 0, 0, 0],
                    [1, 0, 1, 1, 1, 1, 0, 0, 0],
                    [0, 1, 0, 0, 1, 1, 0, 0, 0],
                    [1, 1, 0, 0, 1, 0, 1, 1, 0],
                    [1, 1, 1, 1, 0, 1, 1, 1, 1],
                    [0, 1, 1, 0, 1, 0, 0, 1, 1],
                    [0, 0, 0, 1, 1, 0, 0, 1, 0],
                    [0, 0, 0, 1, 1, 1, 1, 0, 1],
                    [0, 0, 0, 0, 1, 1, 0, 1, 0]]
        N_walk = 800
        g = Graph_randomWalk(mat_demo)
        g.randomWalk(N_walk)
        start_pos = [100, 100]
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
        DELAY = show_delay
        self.canvas.itemconfig(g.nodes[n_pre].draw, fill='red')
        self.anima.update()
        time.sleep(DELAY)
        self.canvas.itemconfig(g.nodes[n_pre].draw, fill='white')
        self.anima.update()
        for i in range(1, N_walk):
            if stop_signal==1:
                break
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
            
## initialize the queue on canvas
def initialize_Queue_show(tk, qx=100, qy=50, qw=10, qh=50, qn=10, s_size = 30):
    canvas.delete("all")
    arrival = canvas.create_polygon(qx-50, qy+qh/2-5, qx-30, qy+qh/2-5, qx-30, qy+qh/2-10, qx-10, qy+qh/2, qx-30, qy+qh/2+10, qx-30, qy+qh/2+5, qx-50, qy+qh/2+5, fill = 'white', outline = 'black')
    queue_slots = []
    slot_x = qx
    slot_y = qy
    slot_width = qw
    slot_height = qh
    slot_num = qn
    for i in range(slot_num):
        queue_slots.append(canvas.create_rectangle(slot_x, slot_y, slot_x+slot_width, slot_y+slot_height, fill = 'white'))
        slot_x = slot_x + slot_width
    server_size = s_size
    server = canvas.create_oval(slot_x,slot_y, slot_x+server_size,slot_y+slot_height,fill='white')
    qx = qx + 200
    left = canvas.create_polygon(qx-50, qy+qh/2-5, qx-30, qy+qh/2-5, qx-30, qy+qh/2-10, qx-10, qy+qh/2, qx-30, qy+qh/2+10, qx-30, qy+qh/2+5, qx-50, qy+qh/2+5, fill = 'white', outline = 'black')
    return (arrival, queue_slots, server, left)
    
def initialize_JacksonQueue_show(tk, qx=100, qy=50, qw=10, qh=50, qn=10, s_size = 30):
    canvas.delete("all")
    queue_slots1 = []
    queue_slots2 = []
    slot_x = qx
    slot_y = qy
    slot_width = qw
    slot_height = qh
    slot_num = qn
    server_size = s_size
    ### the first queue
    arrival1 = canvas.create_polygon(qx-50, qy+qh/2-25, qx-30, qy+qh/2-25, qx-30, qy+qh/2-30, qx-10, qy+qh/2-20, qx-30, qy+qh/2-10, qx-30, qy+qh/2-15, qx-50, qy+qh/2-15, fill = 'white', outline = 'black')
    for i in range(slot_num):
        queue_slots1.append(canvas.create_rectangle(slot_x, slot_y, slot_x+slot_width, slot_y+slot_height, fill = 'white'))
        slot_x = slot_x + slot_width
    server1 = canvas.create_oval(slot_x,slot_y, slot_x+server_size,slot_y+slot_height,fill='white')
    qx = qx + 195
    left1 = canvas.create_polygon(qx-50, qy+qh/2-25, qx-30, qy+qh/2-25, qx-30, qy+qh/2-30, qx-10, qy+qh/2-20, qx-30, qy+qh/2-10, qx-30, qy+qh/2-15, qx-50, qy+qh/2-15, fill = 'white', outline = 'black')
    ### the second queue
    qy = qy + 30
    arrival2 = canvas.create_polygon(qx-50, qy, qx-10, qy, qx-10, qy+2*slot_height, qx-40, qy+2*slot_height, qx-40, qy+2*slot_height+5, qx-60, qy+2*slot_height-5, qx-40, qy+2*slot_height-15, qx-40, qy+2*slot_height-10, qx-20, qy+2*slot_height-10, qx-20, qy+10, qx-50, qy+10, fill = 'white', outline = 'black')
    slot_x = slot_x + server_size
    slot_y = slot_y + 2 * slot_height
    for i in range(slot_num):
        queue_slots2.append(canvas.create_rectangle(slot_x, slot_y, slot_x-slot_width, slot_y+slot_height, fill = 'white'))
        slot_x = slot_x - slot_width       
    server2 = canvas.create_oval(slot_x,slot_y, slot_x-server_size,slot_y+slot_height,fill='white')
    qx = slot_x-server_size - 15
    qy = qy+2*slot_height
    left2 = canvas.create_polygon(qx, qy, qx-40, qy, qx-40, qy-2*slot_height, qx-10, qy-2*slot_height, qx-10, qy-2*slot_height-5,qx+10, qy-2*slot_height+5, qx-10, qy-2*slot_height+15, qx-10, qy-2*slot_height+10, qx-30, qy-2*slot_height+10, qx-30, qy-10, qx, qy-10, fill = 'white', outline = 'black')
    return (arrival1, queue_slots1, server1, left1, arrival2, queue_slots2, server2, left2)

# show the average waiting time, 
def initialize_results_text(tk):
    l1 = Label(tk, text = 'Results:')
    l1.grid(sticky="W", column=0,row=0)
    data = Text(tk, width=50, height=10)
    data.grid(column=0, row=1)
    return data

    
#initialize the window and three frames    
root = Tk()

# split the window into three parts, for nimation, configuration and results
content = ttk.Frame(root, borderwidth=5)
anima = ttk.Frame(content, borderwidth=5)
config = ttk.Frame(content, borderwidth=5)
report = ttk.Frame(content, borderwidth=5)
content.grid(column=0, row=0,columnspan=2, rowspan=2)
anima.grid(column=0, row=0, columnspan=1, rowspan=2)
config.grid(column=1, row=0,columnspan=1, rowspan=1)
report.grid(column=1, row=1,columnspan=1, rowspan=1)
Width = 400
Height = 400
canvas = Canvas(anima, width = Width, height = Height)
canvas.pack()



#simulation configuration
v0 = IntVar(config) 
v0.set(0)
v1 = IntVar(config)
v1.set(1)
queueTypes = [
"MM1",
"MD1",
"MM2",
"jacksonNetwork",
"randomWalkDemo"
] # the function for choosing the queuetype from the dropdown optionMenu
speedSim = [
"fast",
"medium",
"slow"
]
v2 = StringVar(config)
v2.set(queueTypes[0]) # default value
v3 = StringVar(config)
v3.set('')
v4 = StringVar(config)
v4.set('')    
v5 = StringVar(config)
v5.set('')
v6 = StringVar(config)
v6.set(speedSim[1])
v7 = IntVar(config) 
v7.set(0)
v8 = IntVar(config) 
v8.set(0)
# time_sim = StringVar()
# name = ttk.Entry(config, textvariable=time_sim)
l0 = Checkbutton(config, text = 'stepmode', variable=v0)
l0.grid(sticky="W",column=2, row=0)

l1 = Checkbutton(config, text = 'show_animation', variable=v1)
l1.grid(sticky="W",column=0, row=0)
# w1 = OptionMenu(config, v1, *N_queues)
# w1.grid(sticky="W",column=2, row=0)

l2 = Label(config, text = 'Q1 type:')
l2.grid(sticky="W",column=0, row=1)
w2 = OptionMenu(config, v2, *queueTypes)
w2.grid(sticky="W",column=2, row=1)

l3 = Label(config, text = 'simulation arrivals')
l3.grid(sticky="W",column=0, row=2)
w3 = ttk.Entry(config, textvariable=v3)
w3.insert(END, '10000')
w3.grid(sticky="W",column=2, row=2)

l4 = Label(config, text = 'arrival rate')
l4.grid(sticky="W",column=0, row=3)
w4 = ttk.Entry(config, textvariable=v4)
w4.insert(END, '0.8')
w4.grid(sticky="W",column=2, row=3)

l5 = Label(config, text = 'service rate')
l5.grid(sticky="W",column=0, row=4)
w5 = ttk.Entry(config, textvariable=v5)
w5.insert(END, '1')
w5.grid(sticky="W",column=2, row=4)

l6 = Label(config, text = 'animation speed:')
l6.grid(sticky="W",column=0, row=5)
w6 = OptionMenu(config, v6, *speedSim)
w6.grid(sticky="W",column=2, row=5)

#initialize the results text box
Result_text = initialize_results_text(report)


show_animation = 0
step_mode = 0
sim_arrivals = 1000
queue_type = 'MM1'
arrival_rate = 0.5
service_rate = 1
stop_signal = 0
show_delay = 0.2

def get_config():
    global show_animation
    global step_mode
    global queue_type
    global sim_arrivals
    global arrival_rate
    global service_rate
    global show_delay
    global Queue_info
    step_mode = v0.get()
    show_animation = v1.get()
    queue_type = v2.get()
    sim_arrivals = v3.get()
    arrival_rate = v4.get()
    service_rate = v5.get()
    if v6.get() == "fast":
        show_delay = 0.05
    if v6.get() == "medium":
        show_delay = 0.1
    if v6.get() == "slow":
        show_delay = 0.2
    print('parameters:')
    print(show_animation, sim_arrivals, queue_type, arrival_rate, service_rate, show_delay)
    #initialize the animation of queue
    if queue_type == 'jacksonNetwork':
        Queue_info = initialize_JacksonQueue_show(anima)
    else:
        Queue_info = initialize_Queue_show(anima)

def type_change(*args):
    if v2.get() == 'jacksonNetwork':
        Queue_info = initialize_JacksonQueue_show(anima)
    elif v2.get() == 'randomWalkDemo':
        app = appGUI()
    else:
        Queue_info = initialize_Queue_show(anima)
# change the canvas when choose different queue type:
v2.trace('w', type_change)
#initialize the config GUI
get_config()



def start_sim():
    get_config()
    print("Simulation running...")
    print('step mode: ', step_mode)
    global stop_signal
    stop_signal = 0
    if v2.get() == 'randomWalkDemo':
        app = appGUI()
    if queue_type != 'jacksonNetwork': # single queue simulation
        Q1 = Queue_sim(queue_type, int(sim_arrivals), 1/float(arrival_rate), 1/float(service_rate)) 
        Q1.env.run()
        wait_l = [a[3] for a in Q1.L_arrivals]
        N_mean = 0
        Utility_mean = 0
        for i in range(len(Q1.queue_T)-1):
            N_mean += Q1.queue_T[i][1] * (Q1.queue_T[i+1][0] - Q1.queue_T[i][0])
        N_mean = N_mean/Q1.queue_T[-1][0]
        for i in range(len(Q1.res_count_l)-1):
            Utility_mean += Q1.res_count_l[i][1] * (Q1.res_count_l[i+1][0] - Q1.res_count_l[i][0])
        Utility_mean = Utility_mean/Q1.res_count_l[-1][0]
        ## get rid of the first unstable data(90% for default)
        n_arrive = len(wait_l) # actual sim number of arrivals
        N_pre_test = int(len(wait_l) * 0.1)
        wait_l = wait_l[N_pre_test:]
        confidence = 0.95 #defuat confidence level
        m, se = np.mean(wait_l), scipy.stats.sem(wait_l)
        h = se * scipy.stats.norm.ppf((1+confidence)/2)

        #show animation
        # D_queue = {}
        # D_server = {}
        # for i in Q1.queue_T:
        #     D_queue[i[0]] = i[1]
        # for i in Q1.res_count_l:
        #     D_server[i[0]] = i[1]
        if show_animation == 1:
            n_arrive_show = 0 # actual sim number of arrivals
            print('show animation')
            Q_queue = Q1.queue_T
            Q_server = Q1.res_count_l
            n_pre1 = 0
            n_pre2 = 0
            t_pre = 0
            real_dalay = show_delay / 2
            i = 0
            j = 0
            t = 0
            while i < Q1.N_arrivals or j < Q1.N_arrivals:            
                if stop_signal == 1:
                    break
                if step_mode == 1:
                    b4.wait_variable(v7)
                t1, n1 = Q_queue[i]
                t2, n2 = Q_server[j]
                t = min(t1, t2)
                time.sleep(real_dalay * (t - t_pre))
                # there are three conditions to show
                # the first : one joined the queue   
                if t1 <= t2 and n1 - n_pre1 == 1:
                    n_arrive_show += 1
                    canvas.itemconfig(Queue_info[0], fill='red')
                    anima.update()
                    time.sleep(show_delay)
                    canvas.itemconfig(Queue_info[0], fill='white')
                    if n1 <= 10:
                        canvas.itemconfig(Queue_info[1][-n1], fill='red')
                        anima.update()
                        time.sleep(show_delay)
                    n_pre1 = n1
                    i += 1
                    t_pre = t1
                # the second: one left queue and join the server
                elif t1 == t2 and n2 - n_pre2 == 1:  
                    if n1 < 10:
                        canvas.itemconfig(Queue_info[1][-n1-1], fill='white') #queue pop one customer
                    canvas.itemconfig(Queue_info[2], fill='red')   #server red     
                    anima.update()
                    n_pre1 = n1 
                    n_pre2 = n2
                    i += 1
                    j += 1
                    t_pre = t1
                # the third: one left the server and queue pop out one
                elif t1 == t2 and n1 - n_pre1 == -1 and n2 - n_pre2 == -1:
                    canvas.itemconfig(Queue_info[2], fill='white')   #server blank            
                    canvas.itemconfig(Queue_info[3], fill='red') #customer left
                    anima.update()
                    canvas.itemconfig(Queue_info[3], fill='white') #customer left
                    if n1 < 10:
                        canvas.itemconfig(Queue_info[1][-n1-1], fill='white') #queue pop one customer
                    canvas.itemconfig(Queue_info[2], fill='red')   #server blank            
                    anima.update()
                    n_pre1 = n1 
                    n_pre2 = 1
                    i += 1
                    j += 2
                    t_pre = t1
                  # the forth: one left the server and no one in the queue
                elif t1 > t2:
                    canvas.itemconfig(Queue_info[2], fill='white')   #server blank            
                    canvas.itemconfig(Queue_info[3], fill='red') #customer left
                    anima.update()
                    time.sleep(show_delay)
                    canvas.itemconfig(Queue_info[3], fill='white') #customer left 
                    n_pre2 = 0
                    j += 1
            n_arrive = n_arrive_show
        # print(Q1.res_count_l)
        result = str(n_arrive) + " arrivals has been showed." + '\n' + 'total statistics:' +  '\n' + 'average waiting time: ' + str(np.mean(np.array(wait_l))) + '\n' + "average utilization is: " + (str(Utility_mean))[:6] + '\n' + 'average number in the queue: ' + str(N_mean) + '\n' + "confidence interval of average waiting time is: " + (str(m-h))[:6] + " to " + (str(m+h))[:6] + '\n\n'               
        Result_text.insert(INSERT, result)
        
    else: # the jackson network simulation
        Q1 = JacksonQueue_2_sim('MM1', int(sim_arrivals), 1/float(arrival_rate), 1/float(service_rate))
        Q1.env.run()
        wait_l = [a[3] for a in Q1.L_arrivals]
        N_mean1 = 0
        N_mean2 = 0
        Utility_mean1 = 0
        Utility_mean2 = 0
        for i in range(len(Q1.queue1_T)-1):
            N_mean1 += Q1.queue1_T[i][1] * (Q1.queue1_T[i+1][0] - Q1.queue1_T[i][0])
        N_mean1 = N_mean1/Q1.queue1_T[-1][0]
        
        for i in range(len(Q1.queue2_T)-1):
            N_mean2 += Q1.queue2_T[i][1] * (Q1.queue2_T[i+1][0] - Q1.queue2_T[i][0])
        N_mean2 = N_mean2/Q1.queue2_T[-1][0]
        
        for i in range(len(Q1.res1_count_l)-1):
            Utility_mean1 += Q1.res1_count_l[i][1] * (Q1.res1_count_l[i+1][0] - Q1.res1_count_l[i][0])
        Utility_mean1 = Utility_mean1/Q1.res1_count_l[-1][0]
        
        for i in range(len(Q1.res2_count_l)-1):
            Utility_mean2 += Q1.res2_count_l[i][1] * (Q1.res2_count_l[i+1][0] - Q1.res2_count_l[i][0])
        Utility_mean2 = Utility_mean2/Q1.res2_count_l[-1][0]
        ## get rid of the first unstable data(90% for default)
        n_arrive = len(wait_l) # actual sim number of arrivals
        # N_pre_test = int(len(wait_l) * 0.1)
        # wait_l = wait_l[N_pre_test:]
        # confidence = 0.95 #defuat confidence level
        # m, se = np.mean(wait_l), scipy.stats.sem(wait_l)
        # h = se * scipy.stats.norm.ppf((1+confidence)/2)
        
        if show_animation == 1:
            n_arrive_show = 0 # actual sim number of arrivals
            print('show animation')
            Q_queue1 = Q1.queue1_T
            Q_server1 = Q1.res1_count_l
            Q_queue2 = Q1.queue2_T
            Q_server2 = Q1.res2_count_l
            n_pre1 = 0
            n_pre2 = 0
            n_pre3 = 0
            n_pre4 = 0
            t_pre = 0
            real_dalay = show_delay / 2
            i = 0
            j = 0
            m = 0
            n = 0
            t = 0
            while i < Q1.N_arrivals or j < Q1.N_arrivals or m < Q1.N_arrivals or n < Q1.N_arrivals:            
                if stop_signal == 1:
                    break
                t1, n1 = Q_queue1[i]
                t2, n2 = Q_server1[j]
                t3, n3 = Q_queue2[m]
                t4, n4 = Q_server2[n]
                l =[t1, t2, t3, t4]
                t = min(l)
                item_triggered = l.index(t)
                time.sleep(real_dalay * (t - t_pre))
                if step_mode == 1:
                    b4.wait_variable(v7)
                if item_triggered == 0: # queue 1 changed        
                    if n1 - n_pre1 == 1:# queue 1 adds one
                        n_arrive_show += 1
                        canvas.itemconfig(Queue_info[0], fill='red') #Queue_info[0] is the arrival arrow of queue 1
                        anima.update()
                        time.sleep(show_delay)
                        canvas.itemconfig(Queue_info[0], fill='white')
                        if n1 <= 10:
                            canvas.itemconfig(Queue_info[1][-n1], fill='red')
                            anima.update()
                            time.sleep(show_delay)
                    elif n1 - n_pre1 == -1:# queue 1 pops out one
                        if n1 < 10:
                            canvas.itemconfig(Queue_info[1][-n1-1], fill='white') #queue pop one customer
                        anima.update()
                        time.sleep(show_delay)
                    n_pre1 = n1
                    i += 1
                    t_pre = t1
                elif item_triggered == 1: #server 1 changed #Queue_info[2] is the server Queue_info[3] is the left arrow of queue 1
                    if n2 == 0:
                        canvas.itemconfig(Queue_info[2], fill='white')   #server blank
                        time.sleep(show_delay)
                        anima.update()
                    else:
                        canvas.itemconfig(Queue_info[2], fill='red')   #server blank
                        time.sleep(show_delay)
                        anima.update()                   
                    if n2 - n_pre2 == -1:
                        canvas.itemconfig(Queue_info[3], fill='red') #customer left
                        anima.update()
                        time.sleep(show_delay)
                        canvas.itemconfig(Queue_info[3], fill='white') #customer left
                        anima.update()  
                    n_pre2 = n2
                    j += 1  
                    t_pre = t2 
                elif item_triggered == 2:
                     if n3 - n_pre3 == 1:
                         n_arrive_show += 1
                         canvas.itemconfig(Queue_info[4], fill='red') #Queue_info[4] is the arrival arrow of queue 2
                         anima.update()
                         time.sleep(show_delay)
                         canvas.itemconfig(Queue_info[4], fill='white')
                         if n3 <= 10:
                             canvas.itemconfig(Queue_info[5][-n3], fill='red')
                             anima.update()
                             time.sleep(show_delay)
                     elif n3 - n_pre3 == -1:
                         if n1 < 10:
                             canvas.itemconfig(Queue_info[5][-n3-1], fill='white') #queue pop one customer
                         anima.update()
                         time.sleep(show_delay)
                     n_pre3 = n3
                     m += 1
                     t_pre = t3  
                else:
                    if n4 == 0:
                        canvas.itemconfig(Queue_info[6], fill='white')   #server blank
                        time.sleep(show_delay)
                        anima.update()
                    else:
                        canvas.itemconfig(Queue_info[6], fill='red')   #server blank
                        time.sleep(show_delay)
                        anima.update()                   
                    if n4 - n_pre4 == -1:
                        canvas.itemconfig(Queue_info[7], fill='red') #customer left
                        anima.update()
                        time.sleep(show_delay)
                        canvas.itemconfig(Queue_info[7], fill='white') #customer left
                        anima.update()  
                    n_pre4 = n4
                    n += 1  
                    t_pre = t4                              
            n_arrive = n_arrive_show
        result = str(n_arrive) + " arrivals has been showed." + '\n' +  'total statistics:' +  '\n' + 'average waiting time: ' + str(np.mean(np.array(wait_l))) + '\n' + "Queue1 average utilization is: " + (str(Utility_mean1))[:6] + '\n' + "Queue2 average utilization is: " + (str(Utility_mean2))[:6] + '\n' + 'average number in the queue1: ' + str(N_mean1) + '\n' + 'average number in the queue2: ' + str(N_mean2) + '\n\n'               
        Result_text.insert(INSERT, result)
       
def stop_sim():
    global stop_signal
    stop_signal = 1

def reset_sim():
    get_config()
    global Result_text
    Result_text.delete('1.0', END)
    canvas.itemconfig(Queue_info[0], fill='white')
    for i in range(10):
        canvas.itemconfig(Queue_info[1][i], fill='white')
    canvas.itemconfig(Queue_info[2], fill='white')
    canvas.itemconfig(Queue_info[3], fill='white')
       

b1 = Button(config, text = 'start', command=start_sim)
b1.grid(sticky="W", column=0, row=6)

b2 = Button(config, text = 'stop', command=stop_sim)
b2.grid(sticky="W",column=1, row=6)

b3 = Button(config, text = 'reset', command=reset_sim)
b3.grid(sticky="W",column=2, row=6)

b4 = Button(config, text = 'next_step', command = lambda: v7.set(1))
b4.grid(sticky="W",column=3, row=0)

# b5 = Button(config, text = 'pause', command = lambda: v8.set(0))
# b5.grid(sticky="W",column=3, row=6)

root.title("Queuing system simulation for EC541 lab")
root.mainloop()

