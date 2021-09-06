from __future__ import absolute_import
from __future__ import print_function

from keras.backend import batch_dot
from matplotlib.pyplot import step
from sumolib import checkBinary
import os
import sys
import optparse
import subprocess
import random
import traci
import random
import numpy as np
import keras
import h5py
import timeit
from graphd import Visualization
from agentModel import agentModel
from SumoUtils import SumoUtils
from collections import deque
from keras.layers import Input, Conv2D, Flatten, Dense
from keras.models import Model

#           1, 4  -->  horizontala
"""
return: skupno stevilo kolone
"""

def _get_queue_length():
        
       
        queue_length = traci.edge.getLastStepHaltingNumber("N2TL") + traci.edge.getLastStepHaltingNumber("S2TL") + traci.edge.getLastStepHaltingNumber("E2TL") + traci.edge.getLastStepHaltingNumber("W2TL")

        
        return queue_length


'''
Parameter:  tabela s cakalnimi casi iz metode main


return:  nagrada,  cas cakanja vseh avtomobilov, ki so zaspustili simulacijo
'''
def getReward(wait_times):
        waited = 0.0
        
        car_list = traci.vehicle.getIDList()
        total_time = 0
        for car_id in car_list:
            wait_time = traci.vehicle.getAccumulatedWaitingTime(car_id)
            
            if traci.vehicle.getRoadID(car_id) in roads:
                wait_times[car_id] = wait_time

            else: 
                if car_id in wait_times:
                    waited += wait_times[car_id]
                    del wait_times[car_id]
  
        return sum(wait_times.values()),waited
       



if __name__ == '__main__':
    sumoInt = SumoUtils()
    options = sumoInt.get_options()
    sumoInt.generate_sumo()
    episodes  = 100
    agent = agentModel()
    agent.episodes = episodes
    path="P:\FERI\diploma\project\Graphs"
    Visualization = Visualization(
        path,
        dpi=96
    )

    try:
        agent.load('model/reinf_traf_control_35s.h5') 
        print("model loaded")
    except:
        print('No model')



    batch_size = 50
    sumoBinary = checkBinary('sumo')

  

    time_waited = 0
    cars = 800

    
    
    lane1 = 'E2TL'
    lane2 = 'N2TL'
    lane3 = 'S2TL'
    lane4 = 'W2TL'

    rewards_all = []
    waiting_all = []
    queue_all = []
    _waiting_times = {}
    roads = ["E2TL", "N2TL", "W2TL", "S2TL"]
    waiting_times_for_cars = []

    
    waiting_time = 0

    old_wait = 0
    sum_neg_reward = 0

    yellow_duration = 4 
    green_duration = 10

    for e in range(episodes):
        print("--------------------")
        print("episode - " + str(e)+ " -- epsilon: "+ str(agent.epsilon))
       
        start_time = timeit.default_timer()
        traci.start([sumoBinary, "-c", "intersection/sumo_config.sumocfg", '--start'])

        traci.trafficlight.setPhase("TL", 4)
        light_last = 0
        traci.trafficlight.setPhaseDuration("TL", 200)


        max_steps = 4500
        steps = 0
        sum_neg_reward = 0
        waiting_time_current = 0
        rwd1= 0
        queue_length = 0
        old_state = []
        time_waited = 0
        avg_time_Waited = 0

        sum_queue_length = 0
        sum_waiting_time = 0

        old_action = -1

        while traci.simulation.getMinExpectedNumber() > 0 and  steps < max_steps :
            
            

           

            

            state = sumoInt.getState()

            rwd1,waited = getReward(_waiting_times)
            time_waited += waited
            reward = old_wait - rwd1


            if(steps > 0):
                agent.remember(old_state, old_action, reward, state, False)


            action = agent.act(state)

           
            #print(waiting_time_current)


            if steps!= 0 and action != old_action:
                if old_action == 0:
                    traci.trafficlight.setPhase("TL", 1)
                elif old_action == 2:
                    traci.trafficlight.setPhase("TL", 5)
                elif old_action == 1:
                    traci.trafficlight.setPhase("TL", 7)
                elif old_action == 3:
                    traci.trafficlight.setPhase("TL", 3)
                yl = yellow_duration
                count = 0

                while count < yl:
                    traci.simulationStep()  
                    steps += 1 
                    
                    queue_length = _get_queue_length()
                    sum_queue_length += queue_length
                    sum_waiting_time += queue_length

                    count += 1


            if action == 0:
                traci.trafficlight.setPhase("TL", 0)
            elif action == 2:
                traci.trafficlight.setPhase("TL", 4)
            elif action == 1:
                traci.trafficlight.setPhase("TL", 6)
            elif action == 3:
                traci.trafficlight.setPhase("TL", 2)
            
            gl = green_duration
            
            if (steps + gl) >= max_steps:  
                steps_todo = max_steps - steps

            count = 0

            while count < gl:
                traci.simulationStep()  
                steps += 1
            
                queue_length = _get_queue_length()
                sum_queue_length += queue_length
                sum_waiting_time += queue_length 

                count += 1
            
           

            old_wait = rwd1
            old_state = state
            old_action = action

            
            
            if reward < 0:
                sum_neg_reward += reward
            
                

            steps += 1
                

        
        rewards_all.append(sum_neg_reward)
        avg_time_Waited = time_waited / cars
        waiting_all.append(avg_time_Waited)
        queue_all.append(sum_queue_length)

        print("Nagrada: "+str(sum_neg_reward)+", čas čakanja: "+str(avg_time_Waited)+" dolžina kolone: "+str(sum_queue_length)+"\n\r")
        traci.close(wait=False)
        simulation_time = round(timeit.default_timer() - start_time, 1)

        print("učenje......")
        start_time = timeit.default_timer()

        if(len(agent.memory) > batch_size):
            for _ in range(3):
                agent.lrn(batch_size)
        else:
            for _ in range(3):
                agent.lrn(len(agent.memory))



        agent.epsilon = 1 - ((e+1)/episodes)

        '''
        zmanjsevanje epsilona ko je dosezena nova najvecja nagrada
        '''


        '''
        if sum_neg_reward >= reward_threshhold:
            reward_threshhold += 5000
            agent.epsilon = agent.epsilon * 0.97
           
        else:
            agent.epsilon = agent.epsilon * 0.99
        '''
        
       
      

        training_time = round(timeit.default_timer() - start_time, 1)

        
       
       
        
        

        
      



        agent.save('model/model_' + str(e) + '.h5')

        
        print("Simulacija: "+str(simulation_time)+"........... Učenje: "+str(training_time))

        

    Visualization.save_data_and_plot(data=rewards_all, filename='reward', xlabel='Episode', ylabel='Skupna negativna nagrada')
    Visualization.save_data_and_plot(data=waiting_all, filename='wait', xlabel='Episode', ylabel='Povprečen čas čakanja')
    Visualization.save_data_and_plot(data=queue_all, filename='queue', xlabel='Episode', ylabel='Skupna dolžina kolone')