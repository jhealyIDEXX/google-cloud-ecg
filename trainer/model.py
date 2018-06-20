# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Implements the Keras Sequential model."""

import keras
from keras import backend as K
from keras import layers, models
from keras.utils import np_utils
from keras.backend import relu, softmax

#Python2/3 compatibility imports
from six.moves.urllib import parse as urlparse
from builtins import range

import tensorflow as tf
from tensorflow.python.saved_model import builder as saved_model_builder
from tensorflow.python.saved_model import tag_constants, signature_constants
from tensorflow.python.saved_model.signature_def_utils_impl import predict_signature_def

def model_fn(input_shape, 
	labels_dim,
	learning_rate=0.001, 
	loss='binary_crossentropy', 
	n_classes=2):
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

def compile_model(model, learning_rate):
  model.compile(loss='categorical_crossentropy',
                optimizer=keras.optimizers.Adam(lr=learning_rate),
                metrics=['accuracy'])
  return model

def to_savedmodel(model, export_path):
  """Convert the Keras HDF5 model into TensorFlow SavedModel."""

  builder = saved_model_builder.SavedModelBuilder(export_path)

  signature = predict_signature_def(inputs={'input': model.inputs[0]},
                                    outputs={'income': model.outputs[0]})

  with K.get_session() as sess:
    builder.add_meta_graph_and_variables(
        sess=sess,
        tags=[tag_constants.SERVING],
        signature_def_map={
            signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY: signature}
    )
    builder.save()

def generator_input(input_file, chunk_size, batch_size=64):
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
	with tf.gfile.Open(dataFile) as df:
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
				onehot_label.append(0)
			label = int(obj['label'])
			onehot_label[label] = 1
			X.append(signal)
			Y.append(onehot_label)
	
	if len(X) != len(Y):
		raise ValueError('ERROR: mismatch in data and labels')
	
	return (X, Y)