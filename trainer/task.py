'''
Created on Jun 6, 2018

@author: jhealy
'''

import trainer.model as model
import numpy as np
import os
import errno
from sklearn.model_selection import train_test_split
from keras.callbacks import TensorBoard, ModelCheckpoint, EarlyStopping
from numpy.f2py.crackfortran import verbose
import argparse

def train_main(data, output_dir, tboard_dir, batch_size, n_epochs=200, window_size=600):
    
    X, Y = model.generate_inputs(data)
    X = np.asarray(X)
    X = model.normalize(X)
    
    x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, shuffle=True)
    
    fc_model = model.create_model(input_dim=(window_size, ), n_classes=2)
    
    epoch_savename = '{epoch:02d}-fc_model.hdf5'
    epochs_dir = '{}/epochs'.format(output_dir)
    try:
        os.makedirs(epochs_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    
    model_savename = 'best-fc_model.hdf5'
    
    epochs = ModelCheckpoint('{}/{}'.format(epoch_savename, epochs_dir))
    bestModel = ModelCheckpoint('{}/{}'.format(output_dir, model_savename), monitor='val_acc', verbose=1, save_best_only=True, mode='max')
    tb = TensorBoard(log_dir=tboard_dir)
    earlystop = EarlyStopping(monitor='acc', patience=20)
    
    callbacks = [epochs, bestModel, tb, earlystop]
    fc_model.fit(x_train, y_train, verbose=1, 
              validation_data=(x_test, y_test), 
              callbacks=callbacks, 
              batch_size=batch_size, epochs=n_epochs)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--train-files',
                      required=True,
                      type=str,
                      help='Training files', nargs='+')
    parser.add_argument('--job-dir',
                        required=True,
                        type=str,
                        help='output_dir')
    parser.add_argument('--batch-size',
                        type=int,
                        default=64,
                        help='batch size')
    args = parser.parse_args()
    train_data = str(args.train-files)
    output_dir = str(args.job-dir)
    train_main(train_data, output_dir, 'tensorboard/{}'.format(output_dir), args.batch-size)

