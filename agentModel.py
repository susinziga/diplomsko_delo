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
import tensorflow as tf



class agentModel:
    def __init__(self):
        self.gamma = 0.85   # gamma 
        self.epsilon = 1  # raziskovanje   
        self.learning_rate = 0.0003
        self.allActions = 4  # stevilo moznih akcij
        self.episodes = 0
        self.epsilon_decay = 0.98



        self.memory = deque(maxlen=256)
        self.model = self.build_model()


        


    def build_model(self):

        input_1 = Input(shape=(128,))
        x1 = Flatten()(input_1)

        x = Dense(64, activation='relu')(x1)
        x = Dense(32, activation='relu')(x)

        x = Dense(4, activation='linear')(x)

        model = Model(inputs=[input_1], outputs=[x])

        model.compile(loss=losses.mean_squared_error, optimizer=Adam(learning_rate=self.learning_rate))
    
        return model
    


    def save(self, name):
        
        self.model.save_weights(name)
   

    
    def setEpsilon(self,epsilon):
        self.epsilon = epsilon
        #self.epsilon = self.epsilon * self.epsilon_decay

   

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.allActions)
        else:
            with tf.device("/device:GPU:0"):
                tmp = self.model.predict(state)
            a = np.argmax(tmp[0])           
        return a

    def lrn(self, batch_size):
        temp = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in temp:
            rwd = reward
            if not done:
                with tf.device("/device:GPU:0"):
                    next_rwd_temp = self.model.predict(next_state)
                next_rwd = np.amax(next_rwd_temp[0])
                rwd = ( reward +  (self.gamma * next_rwd))
            with tf.device("/device:GPU:0"):
                q_v = self.model.predict(state)
            q_v[0][action] = rwd
            with tf.device("/device:GPU:0"):
                self.model.fit(state, q_v, epochs=1, verbose=0)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def load(self, name):
        
        self.model.load_weights(name)
        

        