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

        
        # we need to import python modules from the $SUMO_HOME/tools directory
        try:
            sys.path.append(os.path.join(os.path.dirname(
                __file__), '..', '..', '..', '..', "tools"))  # tutorial in tests
            sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(
                os.path.dirname(__file__), "..", "..", "..")), "tools"))  # tutorial in docs
            from sumolib import checkBinary  # noqa
        except ImportError:
            sys.exit()
   
    def generate_sumo(self):

        nrOfCars = 800
        random.seed(42)  # make tests reproducible
        N = 4500  # number of time steps
        # demand per second from different directions
        

        # the generation of cars is distributed according to a weibull distribution
        timings = np.random.weibull(2, nrOfCars)
        timings = np.sort(timings)

        # reshape the distribution to fit the interval 0:max_steps
        car_gen_steps = []
        min_old = math.floor(timings[1])
        max_old = math.ceil(timings[-1])
        min_new = 0
        max_new = nrOfCars
        for value in timings:
            car_gen_steps = np.append(car_gen_steps, ((max_new - min_new) / (max_old - min_old)) * (value - max_old) + max_new)

        car_gen_steps = np.rint(car_gen_steps)  # round every value to int -> effective steps when a car will be generated

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
                if straight_or_turn < 0.75:  # choose direction: straight or turn - 75% of times the car goes straight
                    route_straight = np.random.randint(1, 5)  # choose a random source & destination
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
                             default=False, help="run the commandline version of sumo")
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
        offset = 11
        speedLimit = 14

        junctionPosition = traci.junction.getPosition('TL')[0]
        vehicles_road1 = traci.edge.getLastStepVehicleIDs('E2TL')   #DESNA
        vehicles_road2 = traci.edge.getLastStepVehicleIDs('N2TL')   #ZGORNJA
        vehicles_road3 = traci.edge.getLastStepVehicleIDs('S2TL')   #SPODNJA
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
            for j in range(16):
                positionMatrix[i].append(0)
                velocityMatrix[i].append(0)

        #za vse 4 ceste določimo pozicijo vozil in hitrosti v posameznih celicah
        for v in vehicles_road1:
            ind = int(
                abs((junctionPosition - traci.vehicle.getPosition(v)[0] - offset)) / cellLength)
            if(ind < 16):
                positionMatrix1[traci.vehicle.getLaneIndex(v)][ind]
                positionMatrix[traci.vehicle.getLaneIndex(v)][ind -4] = 1
                velocityMatrix[traci.vehicle.getLaneIndex(v)][ind] = traci.vehicle.getSpeed(v) / speedLimit

        for v in vehicles_road2:
            ind = int(
                abs((junctionPosition - traci.vehicle.getPosition(v)[1] + offset)) / cellLength)
            if(ind < 16):
                positionMatrix2[traci.vehicle.getLaneIndex(v)][ind]
                positionMatrix[4 + traci.vehicle.getLaneIndex(v)][ind] = 1
                velocityMatrix[4 + traci.vehicle.getLaneIndex(v)][ind] = traci.vehicle.getSpeed(v) / speedLimit

        junctionPosition = traci.junction.getPosition('TL')[1]
        for v in vehicles_road3:
            ind = int(
                abs((junctionPosition - traci.vehicle.getPosition(v)[1] - offset)) / cellLength)
            if(ind < 16):
                positionMatrix3[traci.vehicle.getLaneIndex(v)][ind]
                positionMatrix[8 + traci.vehicle.getLaneIndex(v)][ind] = 1
                velocityMatrix[8 + traci.vehicle.getLaneIndex(v)][ind] = traci.vehicle.getSpeed(v) / speedLimit

        for v in vehicles_road4:
            ind = int(
                abs((junctionPosition - traci.vehicle.getPosition(v)[0] + offset)) / cellLength)-4
            if(ind < 16):
                positionMatrix4[traci.vehicle.getLaneIndex(v)][ind]
                positionMatrix[12 + traci.vehicle.getLaneIndex(v)][ind] = 1
                velocityMatrix[12 + traci.vehicle.getLaneIndex(v)][ind] = traci.vehicle.getSpeed(v) / speedLimit

        light = []
        if(traci.trafficlight.getPhase('TL') == 4):
            light = [1, 0]
        else:
            light = [0, 1]

        position = np.array(positionMatrix)
        position = position.reshape(4,4,16)

        velocity = np.array(velocityMatrix)
        velocity = velocity.reshape(1, 16, 16, 1)

        lgts = np.array(light)
        lgts = lgts.reshape(1, 2, 1)


        position1 = np.array(positionMatrix1)
        position1 = position1.reshape(1,4,16)

        position2 = np.array(positionMatrix2)
        position2 = position2.reshape(1,4,16)

        position3 = np.array(positionMatrix3)
        position3 = position3.reshape(1,4,16)

        position4 = np.array(positionMatrix4)
        position4 = position4.reshape(1,4,16)

        return [position1,position2,position3,position4]
