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
import tensorflow as tf


tf.test.is_gpu_available()