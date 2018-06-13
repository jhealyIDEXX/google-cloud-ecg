'''
Created on Jun 6, 2018

@author: jhealy

implements a fully-connected keras sequential model for ecgs
'''

from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import Adam
import json
import numpy as np

LABEL_DICT = {0: 'normal', 1: 'abnormal'}

def create_model(input_shape, n_classes, lr=0.001, loss='binary_crossentropy'):
	'''
	TODO: Unit Test
	creates keras sequential model, compiles it and returns it
	'''
	
	model = Sequential()
	model.add(Dense(1024, activation='relu', input_shape=input_shape))
	model.add(Dropout(0.2))

	model.add(Dense(1024, activation='relu'))
	model.add(Dropout(0.2))

	model.add(Dense(512, activation='relu'))
	model.add(Dropout(0.2))

	model.add(Dense(512, activation='relu'))


	model.add(Dense(n_classes, activation='softmax'))
	model = compile_model(model, lr, loss=loss)
	
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
	n_classes = len(LABEL_DICT)
	with open(dataFile, 'r') as df:
		data = df.read()
		data = json.loads(data)
		for obj in data:
			channels = obj['channels']
			signal = channels[str(channel_used)]
			signal_len = len(signal)
			if  signal_len < window_size:
				continue
			if signal_len > window_size:
				signal = signal[:600]
			signal = np.asarray(signal)	
			onehot_label = []
			for i in range(0, n_classes):
				onehot_label.append(i)
			label = int(obj['label'])
			onehot_label[label] = 1
			X.append(signal)
			Y.append(onehot_label)
	
	if len(X) != len(Y):
		raise ValueError('ERROR: mismatch in data and labels')
	
	return (X, Y)
	
