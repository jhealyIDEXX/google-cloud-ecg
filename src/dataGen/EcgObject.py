'''
Created on Jun 6, 2018

@author: jhealy
'''


LABEL_DICT = {0: 'normal', 1: 'abnormal'}

class EcgObject(object):
    '''
    classdocs
    '''

    def __init__(self, label, original_file, signal_channels, startIndex, endIndex, markerIndex=None):
        '''
        Constructor
        
        label : int
            label for classifier
        orifinal_file: str
            str location of original file before sliding window
        signal_channels : list
            list of signal channels
        startIndex: int
            index of the start position of this segment
        endIndex: int
            index of the end position of this segment
        mak
        '''
        self.labelName = LABEL_DICT.get(label)
        if self.labelName == None:
            raise ValueError('Incorrect Label passed to EcgObject')
        self.label = label
        self.original_file = original_file, 
        self.signal_channels = signal_channels
        self.startIndex = startIndex
        self.endIndex = endIndex
        if markerIndex == None:
            markerIndex = 0
        self.markerIndex = markerIndex
    
    def jsonify(self):
        '''
        returns object in dict form 
        '''
        
        signal_dict = {}
        data_dict = {}

        for i in range(0,len(self.signal_channels)):
            signal_dict[i] = self.signal_channels[i]

        data_dict['channels'] = signal_dict
        data_dict['label'] = self.label
        data_dict['labelname'] = self.labelName
        data_dict['original_file'] = self.original_file
        data_dict['startIndex'] = self.startIndex
        data_dict['endIndex'] = self.endIndex
        
        return data_dict