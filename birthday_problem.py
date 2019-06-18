## Author: Chen, Fei
## Date: July 12, 2018
## Project: EC541 lab
## the simulation for the birthday problem/coupon collection, based on the matlab script written by Professor Starobinski
## Python version: 3.6.3

from random import *
import numpy as np
import scipy.integrate.quadrature as quad

K = 365 # number of coupons (i.e., days of the year) 
iteration_num = 10**5 # number of independent iterations
T_sum = 0 #keeps track of sum of stopping times accross all iterations (to compute average)

for i in range(iteration_num):
    success = 0 #reset flag
    T = 0 #reset stopping time
    coupon_count = [0] * K # each entry i in the vector counts the number of coupons of type i that were collected 
    while success == 0:
        T = T + 1 #increases stopping time
        coupon_type = randint(0, K-1) #coupon collected uniformly at random
        coupon_count[coupon_type] += 1 #increment by 1 counter for collected coupon 
        if coupon_count[coupon_type] == 2: #end when two coupons of same type are collected
            success = 1 # change stopping criterion for other problems
    T_sum = T_sum + T
    
T_mean = T_sum/iteration_num #estimate of the mean of the stopping time

def funcX(x):
    return (np.exp(-x/K) + x/K*np.exp(-x/K))**K
T_mean_ana = quad(funcX, 0, 100)

print('the average time from simulation is', T_mean)
print('the numerical solution result is', T_mean_ana[0])
