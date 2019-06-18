## Author: Chen, Fei
## Date: July 2, 2018
## Project: EC541 lab
## A simulation model for simulation Bitcoint mining

# from tkinter import *
# from tkinter import ttk
import time
import random
from copy import deepcopy
import numpy as np
import simpy as sp
import scipy
import scipy.stats
import math
import sys, os

minining_mean_time = 10 #
gamma = 0.5 #percentage of hoest miners who are "closer" to selfish miners = 0
N_rounds = 10
##############  print disable ############### 
# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__
##############  print disable ############### 

class Block:
    def __init__(self, ownerName, time):
        self.owner = ownerName
        self.time  = time
        self.pre = None
        self.next = None
        
# class BlockChain:
#     def __init__(self):
#         self.len = 0
#         self.chain = []
#         self.next = None
    
class Miner:
    def __init__(self, env, NameID, Power = 1, Type = 'honest' , Group = None, gamma = 0.5):
        self.env = env
        self.name = NameID
        self.power = Power
        self.type = Type
        self.group = Group
        # self.Bchain = []
        self.privateBchain = []
        self.money = 0
        self.action  = None
        self.announceStatus = False
        self.privateBranchchainLen = 0
    
    def mining(self, env, announce, publicChain, chainSplits, powerChange = 0):
        self.announceStatus = False
        print(self.name + ' starts at: ' + str(self.env.now))
        print('power changed by: ', str(powerChange))
        N_lead = 0
        # w  = env.process(self.wait)
        while True:
            yield self.env.timeout(np.random.exponential(minining_mean_time / (self.power + powerChange))) | announce
            if self.type == 'honest':
                if announce.triggered:# when the others find a block
                    print(self.name + ' interrupt at: ' + str(self.env.now))
                else: # when the honest find a block
                    print(self.name + ' finishes at: ' + str(self.env.now))
                    publicChain.append(Block(self.name, str(env.now)))
                    self.announceStatus = True
                    announce.succeed()
                break
            else: 
                delta = len(self.privateBchain) - len(publicChain)
                if announce.triggered: # if the others find a block
                    print(self.name + ' interrupt at: ' + str(self.env.now))
                    print(self.name, ' now delta is ' + str(delta))
                    if delta == -1: # the others win, transfer to the public chain
                        print(self.name, ' lost, change to public chain')
                        self.privateBchain = list(publicChain)
                        self.privateBranchchainLen = 0
                    elif delta == 0: # now we are even, announce my block and try the luck
                        print('chainSplits')
                        if not chainSplits.triggered:
                            chainSplits.succeed()
                        self.announceStatus = True
                    elif delta == 1: # others wasted their time, anounce the private chain to substitude the public chain
                        print(self.name, ' chainSplits winned by one')
                        publicChain.clear()
                        publicChain.extend(self.privateBchain)
                        self.privateBranchchainLen = 0
                        self.announceStatus = True
                    else:
                        print(self.name, ' chainSplits winned a lot')
                        l = len(publicChain)
                        publicChain.clear()
                        publicChain.extend(self.privateBchain[:l+1])
                    break
                else: # if the selfish find a block
                    print(self.name + ' finishes at: ' + str(self.env.now))
                    print(self.name, ' now delta is ' + str(delta+1))
                    # announce.succeed()
                    if random.random() <= self.power / (self.power + powerChange):
                        self.privateBchain.append(Block(self.name, str(env.now)))
                    else:
                        print('lost one to honest on the private chain')
                        self.privateBchain.append(Block('Miner0', str(env.now)))
                    self.privateBranchchainLen +=  1      
                    print(self.name, ' privatebranch is ', self.privateBranchchainLen)         
                    if delta == 0 and self.privateBranchchainLen == 2: # under chainSplits
                        print(self.name, 'chainSplits winned by one')
                        publicChain.clear()
                        publicChain.extend(self.privateBchain) # win the chainSplits,  put the money into pocket
                        self.privateBranchchainLen = 0
                        self.announceStatus = True
                        announce.succeed()
                        break
                    else:
                        continue                  

class mining_sim:
    def __init__(self, N_miners, power , typeList):
        self.env = sp.Environment()
        self.miners = []
        self.Bchain = []
        self.N_miners = N_miners #there should be only one honest miner
        self.powerlist = [i / sum(power) for i in power] #nomalization of mining power of each miners      
        self.announce = self.env.event()   
        self.chainSplits = self.env.event()         
        for i in range(self.N_miners):
            self.miners.append(Miner(self.env, 'Miner'+str(i), self.powerlist[i], typeList[i]))
        self.action = self.env.process(self.sim())
        
    def sim(self):
        print('\n\n\n')
        print('Simulation starts:')
        n = 0
        powerFromHonest = 0
        powerChange = 0
        while n < N_rounds:
            print('\nRound' + str(n)+'...')
            Event = self.announce
            for m in self.miners:
                if m.type == 'selfish' and m.announceStatus == True:
                    p = powerChange
                elif m.type == 'honest':
                    p = - powerFromHonest
                else:
                    p = 0
                Event = Event & self.env.process(m.mining(self.env, self.announce, self.Bchain, self.chainSplits, p))
            yield Event
            if self.chainSplits.triggered:
                powerFromHonest = self.miners[0].power * gamma
                k = len([m for m in self.miners if m.type == 'selfish' and m.announceStatus == True]) #how many braches splitted
                powerChange = powerFromHonest / k
                self.chainSplits = self.env.event()
            else:
                powerChange = 0
                powerFromHonest = 0
            self.announce = self.env.event()
            n += 1
            self.ChainPrint()
            
    def ChainPrint(self):
        print ('******Public chain is: ')
        for m in self.Bchain:
            print ('owner: ', m.owner)
            print ('time at: ', m.time)

#simulation input
sim = mining_sim(2, [1,1], ['honest', 'selfish']) 

# sim = mining_sim(3, [1,1,1], ['honest', 'selfish', 'selfish']) # Miner[0] is always honest
# sim.sim()
# blockPrint()
sim.env.run()
enablePrint()
print('total result:')
for b in sim.Bchain:
    for m in sim.miners:
        if b.owner == m.name:
            m.money += 1
for m in sim.miners:
    print(m.name + ' won: ' + str(m.money) + ' blocks')
# for n in sim.Bchain:
#     print(n.time)
#     print(n.owner)

        
        
            
