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


def queue_length_funct():
        
       
        queue = traci.edge.getLastStepHaltingNumber("N2TL") + traci.edge.getLastStepHaltingNumber("S2TL") + traci.edge.getLastStepHaltingNumber("E2TL") + traci.edge.getLastStepHaltingNumber("W2TL")

        return queue

def getWaitTime(wait_times):
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
  
        return waited





if __name__ == '__main__':
    sumoInt = SumoUtils()
    options = sumoInt.get_options()
    #sumoInt.generate_sumo()
 
   
    path="P:\FERI\diploma\project\GraphsTest"
    Visualization = Visualization(
        path,
        dpi=96
    )

  

    batch_size = 50
    sumoBinary = checkBinary('sumo-gui')

  


 

    
    
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
    cars = 800

    old_wait = 0
    sum_neg_reward = 0

    yellow_duration = 4
    green_duration = 10

    
    print("--------------------")
    print("TEST INITIATING")
 
    
    start_time = timeit.default_timer()
    traci.start([sumoBinary, "-c", "intersection/test1/sumo_config.sumocfg", '--start'])

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

    sum_queue_length = 0
    sum_waiting_time = 0

    old_action = -1
    action = 0
    time_waited = 0

    while traci.simulation.getMinExpectedNumber() > 0 and  steps < max_steps :
        
        
        waited = getWaitTime(_waiting_times)
        time_waited += waited

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
    
        old_action = action

        
        action += 1
        if action == 4:
            action = 0

        steps += 1
                

                
 
    avg_time_Waited = time_waited / cars

    

    print("Nagrada: "+str(sum_neg_reward)+", čas čakanja: "+str(avg_time_Waited)+" dolžina kolone: "+str(sum_queue_length)+"\n\r")
    traci.close(wait=False)
    simulation_time = round(timeit.default_timer() - start_time, 1)


    print("Simulacija: "+str(simulation_time))
