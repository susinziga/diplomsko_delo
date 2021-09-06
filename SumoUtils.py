from __future__ import absolute_import
from __future__ import print_function
from sumolib import checkBinary
import math
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
from collections import deque
from keras.layers import Input, Conv2D, Flatten, Dense
from keras.models import Model

class SumoUtils:
    def __init__(self):

        
       
        try:
            sys.path.append(os.path.join(os.path.dirname(
                __file__), '..', '..', '..', '..', "tools")) 
            sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(
                os.path.dirname(__file__), "..", "..", "..")), "tools"))  
            from sumolib import checkBinary  
        except ImportError:
            sys.exit()
   
    def generate_sumo(self):

        nrOfCars = 800
        random.seed(42) 
        N = 4500 

        timings = np.random.weibull(2, nrOfCars)
        timings = np.sort(timings)

        car_gen_steps = []
        min_old = math.floor(timings[1])
        max_old = math.ceil(timings[-1])
        min_new = 0
        max_new = N
        for value in timings:
            car_gen_steps = np.append(car_gen_steps, ((max_new - min_new) / (max_old - min_old)) * (value - max_old) + max_new)

        car_gen_steps = np.rint(car_gen_steps)  

        with open("intersection/episode_routes.rou.xml", "w") as routes:
            print("""<routes>
            <vType accel="1.0" decel="4.5" id="standard_car" length="5.0" minGap="2.5" maxSpeed="25" sigma="0.5" />

            <route id="W_N" edges="W2TL TL2N"/>
            <route id="W_E" edges="W2TL TL2E"/>
            <route id="W_S" edges="W2TL TL2S"/>
            <route id="N_W" edges="N2TL TL2W"/>
            <route id="N_E" edges="N2TL TL2E"/>
            <route id="N_S" edges="N2TL TL2S"/>
            <route id="E_W" edges="E2TL TL2W"/>
            <route id="E_N" edges="E2TL TL2N"/>
            <route id="E_S" edges="E2TL TL2S"/>
            <route id="S_W" edges="S2TL TL2W"/>
            <route id="S_N" edges="S2TL TL2N"/>
            <route id="S_E" edges="S2TL TL2E"/>""", file=routes)

            for car_counter, step in enumerate(car_gen_steps):
                straight_or_turn = np.random.uniform()
                if straight_or_turn < 0.75:  
                    route_straight = np.random.randint(1, 5)  
                    if route_straight == 1:
                        print('    <vehicle id="W_E_%i" type="standard_car" route="W_E" depart="%s" departLane="random" departSpeed="10" />' % (car_counter, step), file=routes)
                    elif route_straight == 2:
                        print('    <vehicle id="E_W_%i" type="standard_car" route="E_W" depart="%s" departLane="random" departSpeed="10" />' % (car_counter, step), file=routes)
                    elif route_straight == 3:
                        print('    <vehicle id="N_S_%i" type="standard_car" route="N_S" depart="%s" departLane="random" departSpeed="10" />' % (car_counter, step), file=routes)
                    else:
                        print('    <vehicle id="S_N_%i" type="standard_car" route="S_N" depart="%s" departLane="random" departSpeed="10" />' % (car_counter, step), file=routes)
                else:  
                    route_turn = np.random.randint(1, 9)  
                    if route_turn == 1:
                        print('    <vehicle id="W_N_%i" type="standard_car" route="W_N" depart="%s" departLane="random" departSpeed="10" />' % (car_counter, step), file=routes)
                    elif route_turn == 2:
                        print('    <vehicle id="W_S_%i" type="standard_car" route="W_S" depart="%s" departLane="random" departSpeed="10" />' % (car_counter, step), file=routes)
                    elif route_turn == 3:
                        print('    <vehicle id="N_W_%i" type="standard_car" route="N_W" depart="%s" departLane="random" departSpeed="10" />' % (car_counter, step), file=routes)
                    elif route_turn == 4:
                        print('    <vehicle id="N_E_%i" type="standard_car" route="N_E" depart="%s" departLane="random" departSpeed="10" />' % (car_counter, step), file=routes)
                    elif route_turn == 5:
                        print('    <vehicle id="E_N_%i" type="standard_car" route="E_N" depart="%s" departLane="random" departSpeed="10" />' % (car_counter, step), file=routes)
                    elif route_turn == 6:
                        print('    <vehicle id="E_S_%i" type="standard_car" route="E_S" depart="%s" departLane="random" departSpeed="10" />' % (car_counter, step), file=routes)
                    elif route_turn == 7:
                        print('    <vehicle id="S_W_%i" type="standard_car" route="S_W" depart="%s" departLane="random" departSpeed="10" />' % (car_counter, step), file=routes)
                    elif route_turn == 8:
                        print('    <vehicle id="S_E_%i" type="standard_car" route="S_E" depart="%s" departLane="random" departSpeed="10" />' % (car_counter, step), file=routes)

            print("</routes>", file=routes)


        return nrOfCars




    def get_options(self):
        optParser = optparse.OptionParser()

        optParser.add_option("--nogui", action="store_true",
                             default=False, help="true")
                             
        options, args = optParser.parse_args()
        return options

    def getState(self):
        positionMatrix = []
        velocityMatrix = []

        positionMatrix1 = []
        positionMatrix2 = []
        positionMatrix3 = []
        positionMatrix4 = []

        cellLength = 7
        offs = 11
        speedLimit = 14

        junctionPosition = traci.junction.getPosition('TL')[0]
        
        vehicles_road1 = traci.edge.getLastStepVehicleIDs('N2TL')   #ZGORNJA
        vehicles_road2 = traci.edge.getLastStepVehicleIDs('S2TL')   #SPODNJA
        vehicles_road3 = traci.edge.getLastStepVehicleIDs('E2TL')   #DESNA
        vehicles_road4 = traci.edge.getLastStepVehicleIDs('W2TL')   #LEVA
        #nastavimo 0 v vsa polja

        for i in range(4):
            positionMatrix1.append([])
            positionMatrix2.append([])
            positionMatrix3.append([])
            positionMatrix4.append([])
            
            for j in range(16):
                positionMatrix1[i].append(0)
                positionMatrix2[i].append(0)
                positionMatrix3[i].append(0)
                positionMatrix4[i].append(0)
                


        for i in range(16):
            positionMatrix.append([])
            velocityMatrix.append([])
            for j in range(8):
                positionMatrix[i].append(0)
                velocityMatrix[i].append(0)

        #za vse 4 ceste določimo pozicijo vozil in hitrosti v posameznih celicah
        for v in vehicles_road1:
            ind = int(
                abs((junctionPosition - traci.vehicle.getPosition(v)[1] - offs)) / cellLength)-4
            if(ind < 8):
                positionMatrix1[traci.vehicle.getLaneIndex(v)][ind] = 1

                if traci.vehicle.getAccumulatedWaitingTime(v) == 0:
                    t = 1
                else:
                    t = traci.vehicle.getAccumulatedWaitingTime(v)

                positionMatrix[traci.vehicle.getLaneIndex(v)][ind] = t
                velocityMatrix[traci.vehicle.getLaneIndex(v)][ind] = traci.vehicle.getSpeed(v) / speedLimit

        for v in vehicles_road2:
            ind = int(
                abs((junctionPosition - traci.vehicle.getPosition(v)[1] + offs)) / cellLength)-4
            if(ind < 8):
                positionMatrix2[traci.vehicle.getLaneIndex(v)][ind] = 1

                if traci.vehicle.getAccumulatedWaitingTime(v) == 0:
                    t = 1
                else:
                    t = traci.vehicle.getAccumulatedWaitingTime(v)

                positionMatrix[4 + traci.vehicle.getLaneIndex(v)][ind] = t
                velocityMatrix[4 + traci.vehicle.getLaneIndex(v)][ind] = traci.vehicle.getSpeed(v) / speedLimit

        junctionPosition = traci.junction.getPosition('TL')[1]
        for v in vehicles_road3:
            ind = int(
                abs((junctionPosition - traci.vehicle.getPosition(v)[0] - offs)) / cellLength)-4
            if(ind < 8):
                positionMatrix3[traci.vehicle.getLaneIndex(v)][ind] = 1

                if traci.vehicle.getAccumulatedWaitingTime(v) == 0:
                    t = 1
                else:
                    t = traci.vehicle.getAccumulatedWaitingTime(v)

                positionMatrix[8 + traci.vehicle.getLaneIndex(v)][ind] = t
                velocityMatrix[8 + traci.vehicle.getLaneIndex(v)][ind] = traci.vehicle.getSpeed(v) / speedLimit

        for v in vehicles_road4:
            ind = int(
                abs((junctionPosition - traci.vehicle.getPosition(v)[0] + offs)) / cellLength)-4
            if(ind < 8):
                positionMatrix4[traci.vehicle.getLaneIndex(v)][ind] = 1

                if traci.vehicle.getAccumulatedWaitingTime(v) == 0:
                    t = 1
                else:
                    t = traci.vehicle.getAccumulatedWaitingTime(v)

                positionMatrix[12 + traci.vehicle.getLaneIndex(v)][ind] = t
                velocityMatrix[12 + traci.vehicle.getLaneIndex(v)][ind] = traci.vehicle.getSpeed(v) / speedLimit

        light = []
        
        if(traci.trafficlight.getPhase('TL') == 4):
            light = [1, 0]
        else:
            light = [0, 1]

        position = np.array(positionMatrix)
        position = position.reshape(1,128)
        '''
        velocity = np.array(velocityMatrix)
        velocity = velocity.reshape(1, 16, 8, 1)

        '''
        '''
        lgts = np.array(light)
        lgts = lgts.reshape(1, 2, 1)
        '''

        

        return [position]
