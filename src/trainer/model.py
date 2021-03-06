'''
Created on Jun 6, 2018

@author: jhealy

implements a fully-connected keras sequential model for ecgs
'''

from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
import json
import numpy as np

LABEL_DICT = {0: 'normal', 1: 'abnormal'}

def create_model(input_dim, n_classes, units_arr=[1024, 1024, 512, 512], lr=0.001, loss='binary_crossentropy'):
    '''
    TODO: Unit Test
    creates keras sequential model, compiles it and returns it
    '''
    
    model = Sequential()
    for units in units_arr:
        model.add(Dense(units, input_dim=input_dim, activation='relu'))
        
        input_dim=units
    
    model.add(Dense(n_classes, activation='softmax'))
    compile_model(model, lr)
    return model

def compile_model(model, lr, loss='binary_crossentropy'):
    '''
    TODO: Unit Test
    Compiles the model with the Adam optimizer and specified learning rate and returns it
    '''
    
    model.compile(loss=loss, optimizer=Adam(lr=lr), metrics=['accuracy'])
    return model

def normalize(data, mean=None, stdev=None):
    if mean == None:
        mean = np.mean(data, axis=0)
    if stdev == None:
        stdev = np.mean(data, axis=0)
        
    return (data - mean) / stdev

def generate_inputs(dataFile, channel_used=0, window_size=600):
    '''
    TODO: Unit Test
    generate input arrays
    
    datafile - location of json file for each signal, 
        TODO: doc with json design
        
    returns tuple of two lists (data, labels)
    '''
    
    X = []
    Y = []
    
    with open(dataFile, 'r') as df:
        data = df.read()
        data = json.loads(data)
        for obj in data:
            obj = json.loads(obj)
            channels = obj['channels']
            signal = channels[channel_used]
            if  signal < window_size:
                continue
            if signal > window_size:
                signal = signal[:600]
            signal = np.asarray(signal)    
            label = int(obj['label'])
            X.append(signal)
            Y.append(label)
    
    if len(X) != len(Y):
        raise ValueError('ERROR: mismatch in data and labels')
    
    return (X, Y)
    