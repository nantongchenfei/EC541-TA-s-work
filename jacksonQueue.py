# test jacksonNetwork without GUI
import numpy as np
import simpy as sp
import scipy.stats
import math

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
                print('join queue2')
                print(self.queue2_T)
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
            
Q1 = JacksonQueue_2_sim('MM1', 10, 0.5, 1)
Q1.env.run()
print(Q1.queue1_T)
print(Q1.queue2_T)
print(Q1.res1_count_l)
print(Q1.res2_count_l)