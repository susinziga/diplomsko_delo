from __future__ import absolute_import
from __future__ import print_function
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
from collections import deque
from keras.layers import Input, Conv2D, Flatten, Dense
from keras.models import Model
from tensorflow.keras import losses
from tensorflow.keras.optimizers import Adam



class agentModel:
    def __init__(self):
        self.gamma = 0.95   # gamma  0,95
        self.epsilon = 1  # raziskovanje   
        self.learning_rate = 0.0003
        self.allActions = 2  # stevilo moznih akcij
        self.episodes = 0
        self.epsilon_decay = 0.98



        self.memory = deque(maxlen=256)
        self.model = self.build_model()


        


    def build_model(self):
		# CSS   inputi    16x16,   16x16,    2x1


        inp_1 = Input(shape=(4,16))
        xx1 = Flatten()(inp_1)

        inp_2 = Input(shape=(4,16))
        xx2 = Flatten()(inp_2)

        inp_3 = Input(shape=(4,16))
        xx3 = Flatten()(inp_3)
        
        inp_4 = Input(shape=(4,16))
        xx4 = Flatten()(inp_4)

        input_1 = Input(shape=(256,))
        x1 = Dense(128, activation='relu')(input_1)
        '''
        input_1 = Input(shape=(16, 16, 1))
        x1 = Conv2D(16, (4, 4), strides=(2, 2), activation='relu')(input_1)
        x1 = Conv2D(32, (2, 2), strides=(1, 1), activation='relu')(x1)
        x1 = Flatten()(input_1)
        '''
        input_2 = Input(shape=(16, 16, 1))
        x2 = Conv2D(16, (4, 4), strides=(4, 4), activation='relu')(input_2)
        x2 = Conv2D(64, (2, 2), strides=(2, 2), activation='relu')(x2)
        x2 = Flatten()(x2)

        input_3 = Input(shape=(2, 1))
        x3 = Flatten()(input_3)
        x = keras.layers.concatenate([xx1,xx2,xx3,xx4])
        xf = keras.layers.concatenate([x1])

       
        x = Dense(64, activation='relu')(x)

        x = Dense(2, activation='linear')(x)

        model = Model(inputs=[inp_1,inp_2,inp_3,inp_4], outputs=[x])

        model.compile(loss=losses.mean_squared_error, optimizer=Adam(learning_rate=self.learning_rate))
    

        return model


    def save(self, name):
        
        self.model.save_weights(name)
   

    
    def setEpsilon(self):
        self.epsilon = self.epsilon - 1/self.episodes
        #self.epsilon = self.epsilon * self.epsilon_decay

   

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.allActions)
        else:
            
            tmp = self.model.predict(state)
            a = np.argmax(tmp[0])           
        return a

    def lrn(self, batch_size):
        temp = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in temp:
            rwd = reward
            if not done:
                next_rwd_temp = self.model.predict(next_state)
                next_rwd = np.amax(next_rwd_temp[0])
                rwd = ( reward +  (self.gamma * next_rwd))
            q_v = self.model.predict(state)
            q_v[0][action] = rwd
            
            self.model.fit(state, q_v, epochs=1, verbose=0)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def load(self, name):
        
        self.model.load_weights(name)
        

        