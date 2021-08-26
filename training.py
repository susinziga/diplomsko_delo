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


def _get_queue_length():
        """
        stevilo avtomobilov ki stojijo za semaforjem na posameznih cestah
        """
        halt_N = traci.edge.getLastStepHaltingNumber("N2TL")
        halt_S = traci.edge.getLastStepHaltingNumber("S2TL")
        halt_E = traci.edge.getLastStepHaltingNumber("E2TL")
        halt_W = traci.edge.getLastStepHaltingNumber("W2TL")
        queue_length = halt_N + halt_S + halt_E + halt_W

        
        return queue_length

def getWaitTime(wait_times):
        reward1 = 0
        car_list = traci.vehicle.getIDList()
        total_time = 0
        for car_id in car_list:
            wait_time = traci.vehicle.getAccumulatedWaitingTime(car_id)
            road_id = traci.vehicle.getRoadID(car_id)

            if road_id in incoming_roads:
                wait_times[car_id] = wait_time
            else:
                if car_id in wait_times: # a car that was tracked has cleared the intersection
                    reward1 += wait_times[car_id]
                    del wait_times[car_id]
        
        total_time = sum(wait_times.values())

       
        return reward1 - total_time


def _simulate( step , steps_todo, max_steps):
       
        if (step + steps_todo) >= max_steps:  # do not do more steps than the maximum allowed number of steps
            steps_todo = steps - step

        sum_queue_length = 0
        waiting_time = 0

        while steps_todo > 0:
            traci.simulationStep()  # simulate 1 step in sumo
            step += 1 # update the step counter
            steps_todo -= 1
            queue_length = _get_queue_length()
            
            sum_queue_length += queue_length
            waiting_time += queue_length # 1 step while wating in queue means 1 second waited, for each car, therefore queue_lenght == waited_seconds
       
        return step,sum_queue_length,waiting_time


''' 
Ta funkcija se trenutno ne uporablja
'''
def _simulate_0(step , steps_todo, max_steps):
        traci.trafficlight.setPhase('TL', 5)
        steps, queue_length_current, waiting_time_current = _simulate(steps , yellow_duration, max_steps)
    
        traci.trafficlight.setPhase('TL', 6)
        steps, queue_length_current, waiting_time_current = _simulate(steps , green_duration, max_steps)

        traci.trafficlight.setPhase('TL', 7)
        steps, queue_length_current, waiting_time_current = _simulate(steps , yellow_duration, max_steps)

        traci.trafficlight.setPhase ('TL', 0)
        steps, queue_length_current, waiting_time_current = _simulate(steps , green_duration, max_steps)

        if (step + steps_todo) >= max_steps:  # do not do more steps than the maximum allowed number of steps
            steps_todo = steps - step

        sum_queue_length = 0
        waiting_time = 0

        while steps_todo > 0:
            traci.simulationStep()  # simulate 1 step in sumo
            step += 1 # update the step counter
            steps_todo -= 1
            queue_length = _get_queue_length()
            
            sum_queue_length += queue_length
            waiting_time += queue_length # 1 step while wating in queue means 1 second waited, for each car, therefore queue_lenght == waited_seconds
       
        return step,sum_queue_length,waiting_time



if __name__ == '__main__':
    sumoInt = SumoUtils()
    options = sumoInt.get_options()
    sumoInt.generate_sumo()
    episodes  = 200
    agent = agentModel()
    agent.episodes = episodes
    path="P:\FERI\diploma\project\Graphs"
    Visualization = Visualization(
        path,
        dpi=96
    )

    try:
        agent.load('model/reinf_traf_control_79a.h5')
        print("model loaded")
    except:
        print('No model')



    batch_size = 100
    sumoBinary = checkBinary('sumo')

  

    


    
    
    lane1 = 'E2TL'
    lane2 = 'N2TL'
    lane3 = 'S2TL'
    lane4 = 'TL2E'

    rewards_all = []
    waiting_all = []
    queue_all = []
    _waiting_times = {}

    incoming_roads = ['E2TL','N2TL','S2TL','TL2E']
    waiting_times_for_cars = []

    
    waiting_time = 0

    old_wait = 0
    sum_neg_reward = 0

    yellow_duration = 6
    green_duration = 25

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
        queue_length = 0
        old_state = []

        sum_queue_length = 0
        sum_waiting_time = 0

        old_action = -1

        while traci.simulation.getMinExpectedNumber() > 0 and  steps < max_steps :
            
            

           

            

            state = sumoInt.getState()

            #waiting_time_current = getWaitTime(_waiting_times)
            #reward = old_wait - waiting_time_current

            reward = getWaitTime(_waiting_times)

            if(steps > 0):
                agent.remember(old_state, old_action, reward, state, False)


            action = agent.act(state)

            

            #print(waiting_time_current)

            if(action == old_action):
                if(action == 1):
                    traci.trafficlight.setPhase ('TL', 1)
                    steps, queue_length_current, waiting_time_current = _simulate(steps , green_duration, max_steps)
                    sum_waiting_time += waiting_time_current
                    sum_queue_length += queue_length_current
                if(action == 0):
                    traci.trafficlight.setPhase ('TL', 0)
                    steps, queue_length_current, waiting_time_current = _simulate(steps , green_duration, max_steps)
                    sum_waiting_time += waiting_time_current
                    sum_queue_length += queue_length_current
            
            
            if(action == 0 and action != old_action):
                traci.trafficlight.setPhase('TL', 5)
                steps, queue_length_current, waiting_time_current = _simulate(steps , yellow_duration, max_steps)
                sum_waiting_time += waiting_time_current
                sum_queue_length += queue_length_current
                traci.trafficlight.setPhase('TL', 6)
                steps, queue_length_current, waiting_time_current = _simulate(steps , green_duration, max_steps)
                sum_waiting_time += waiting_time_current
                sum_queue_length += queue_length_current
                traci.trafficlight.setPhase('TL', 7)
                steps, queue_length_current, waiting_time_current = _simulate(steps , yellow_duration, max_steps)
                sum_waiting_time += waiting_time_current
                sum_queue_length += queue_length_current
                traci.trafficlight.setPhase ('TL', 0)
                steps, queue_length_current, waiting_time_current = _simulate(steps , green_duration, max_steps)
                sum_waiting_time += waiting_time_current
                sum_queue_length += queue_length_current
                


            if(action == 1 and action != old_action):
                traci.trafficlight.setPhase('TL', 1)
                steps, queue_length_current, waiting_time_current = _simulate(steps , yellow_duration, max_steps)
                sum_waiting_time += waiting_time_current
                sum_queue_length += queue_length_current
                traci.trafficlight.setPhase('TL', 2)
                steps, queue_length_current, waiting_time_current = _simulate(steps , green_duration, max_steps)
                sum_waiting_time += waiting_time_current
                sum_queue_length += queue_length_current
                traci.trafficlight.setPhase('TL', 3)
                steps, queue_length_current, waiting_time_current = _simulate(steps , yellow_duration, max_steps)
                sum_waiting_time += waiting_time_current
                sum_queue_length += queue_length_current
                traci.trafficlight.setPhase ('TL', 4)
                steps, queue_length_current, waiting_time_current = _simulate(steps , green_duration, max_steps)
                sum_waiting_time += waiting_time_current
                sum_queue_length += queue_length_current
            
           

            old_wait = waiting_time_current
            old_state = state
            old_action = action
            
            


            if reward < 0:
                sum_neg_reward += reward

            steps += 1
                    # Randomly Draw 32 samples and train the neural network by RMS Prop algorithm
        rewards_all.append(sum_neg_reward)
        waiting_all.append(sum_waiting_time)
        queue_all.append(sum_queue_length)

        print("reward: "+str(sum_neg_reward)+", waiting time: "+str(sum_waiting_time)+" queue length: "+str(sum_queue_length))
        traci.close(wait=False)
        simulation_time = round(timeit.default_timer() - start_time, 1)

        print("training...")
        start_time = timeit.default_timer()
        if(len(agent.memory) > batch_size):
            agent.lrn(batch_size)
        else:
            agent.lrn(len(agent.memory))
        
        if e!=0 and e % 50 == 0 :
            batch_size = (int)(batch_size * 0.95)


        training_time = round(timeit.default_timer() - start_time, 1)
        agent.setEpsilon()

        
      



        agent.save('model/reinf_traf_control_' + str(e) + '.h5')

        
        print("Simulation time: "+str(simulation_time)+" ----- Training time: "+str(training_time))

        

    Visualization.save_data_and_plot(data=rewards_all, filename='reward', xlabel='Episode', ylabel='Cumulative negative reward')
    Visualization.save_data_and_plot(data=waiting_all, filename='wait', xlabel='Episode', ylabel='waiting time')
    Visualization.save_data_and_plot(data=queue_all, filename='queue', xlabel='Episode', ylabel='queue')