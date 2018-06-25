'''
Created on Jun 6, 2018

@author: jhealy
'''

import argparse
import pydicom
import glob
from pydicom import compat
from pydicom.tag import Tag
from EcgObject import EcgObject
import sys
import xmltodict
import json
import numpy as np 

def dcmReadChannels(dicomFile):
	ds = pydicom.dcmread(dicomFile)
	ds.decode()

	wfSeq = ds.data_element("WaveformSequence")

	for wf in wfSeq:
		channels = wf.data_element("NumberOfWaveformChannels").value
		samples = wf.data_element("NumberOfWaveformSamples").value
		data = wf.data_element("WaveformData").value
		wfData = []
	
		for i in range(int(len(data)/2)):
			b = [data[i*2], data[i*2+1]]
			wfData.append(int.from_bytes(b, byteorder='little', signed=True))
	
		wfDataSeq = []
		for i in range(channels):
			channel = []
			pos = i
			for j in range(samples):
				channel.append(wfData[pos])
				pos = pos + channels
			wfDataSeq.append(channel)
	
	return wfDataSeq

def getMarkersFromCardioPet(xmlData):
	'''
	Get markers from cardioPet data
	
	Params
	------
	xmlData : string
		cardiopet xml from vetdata DB

	Returns
	-------
	array
		array containing markers - each marker is indeck in signal 
		empty if no markers

	'''

	data = xmltodict.parse(xmlData)
	markers = []
	try: 
		if data['jetsonResult']['resultSummary']['morphology-other']['@result'] == 'fail':
			values = data['jetsonResult']['resultSummary']['trace-morph']['trace-beat']
			if len(values) == 1:
				markers.append(values['@pos'])
			else:
				for value in values:
					markers.append(value['@pos'])
	except TypeError:
		markers = []
	
	return markers

def dcm_process_abnormal(filename, markers, window_size):
	'''
	return list of dicts found from the file
	each dict in list follows format to be written to json file
	
	'''
	channels = dcmReadChannels(filename)
	n_beats = len(channels[0])
	if n_beats == 0:
		raise ValueError('Empty signal file: {}'.format(filename))
	oneSideSamples = int(window_size/2) 
	data = [] #list of dicts to be written to json 
	
	for marker in markers:
		signal_channels = []
		marker = int(marker)
		start = marker - oneSideSamples
		end = marker + oneSideSamples
		
		if (end) > n_beats:
			continue
		elif (start) < 0:
			continue
		else:
			signal_channels.append(channels[0][start:end])
			data.append(EcgObject(label=1, original_file=filename, signal_channels=channels[0][start:end], startIndex=start, endIndex=end, markerIndex=marker)) 
				
	return data

def dcm_process_normal(filename, window_size):
	
	channels = dcmReadChannels(filename)
	n_beats = len(channels[0])
	if n_beats == 0:
		raise ValueError('Empty signal file: {}'.format(filename))
	
	oneSideSamples = int(window_size/2)
	data = []
	point = oneSideSamples + 1
	
	while (point+oneSideSamples) <= n_beats:
		signal_channels = []
		start = point-oneSideSamples
		end = point+oneSideSamples	
		data.append(EcgObject(label=0, original_file=filename, signal_channels=channels[0][start:end], startIndex=start, endIndex=end))
		point = end

	return data

def dcm_datasetFromFolder(dataFolder, window_size, savePath):
	'''
	assumes datafolder with .dcms and a correlating .hea file in the same folder
	'''
	data = []
	normals = 0
	abnormals = 1
	fileGlob = glob.glob(r'{}/*.dcm'.format(dataFolder))
	n_files = len(fileGlob)
	cfile = 1
	for file in fileGlob:
		sys.stdout.write('\r{}/{}...'.format(cfile, n_files))
		sys.stdout.flush()
		cfile = cfile+1
		name = file[:-4]
		with open('{}.hea'.format(name), 'r') as hf:
			hf.readline()
			markers = getMarkersFromCardioPet(hf.readline())
			if len(markers) > 0:
				try:
					samples = dcm_process_abnormal(file, markers, window_size)
					if samples == None:
						continue
					for sample in samples:
						data.append(sample.jsonify())
						abnormals = abnormals + 1
				except ValueError:
					continue
				except pydicom.errors.InvalidDicomError:
					continue
			elif len(markers) == 0:
				try:
					samples = dcm_process_normal(file, window_size)
					if samples == None:
						continue
					for sample in samples:
						data.append(sample.jsonify())
						normals = normals + 1
						if normals > 10000:
							break
				except ValueError:
					continue
				except pydicom.errors.InvalidDicomError:
					continue
	print(savePath)
	
	with open(savePath, 'w+') as f:
		f.write(json.dumps(data, indent=4))	
	

def txt_datasetFromFolder(dataFolder, window_length, n_normals=None, n_abnormals=None):
	X = []
	Y = []

	segment_samples = int(window_length / 2)
	
	normals = 0
	abnormals = 0

	#create iterator for files
	files = glob.iglob(r'{}/*0ch.txt'.format(dataFolder))

	still_looking = True
	done_normals = False
	done_abnormals = False

	while still_looking:
		#do still_looking check

		if done_abnormals and done_normals:
			still_looking = False

		
		file = None 
		try:
			file = files.__next__()
		except StopIteration:
			still_looking = False
			break

		signal = np.loadtxt(file)
		n_samples = len(signal)
		if n_samples == 0:
			continue

		markers = []
		with open('{}.hea'.format(file[:-8])) as hf:
			hf.readline()
			try:
				markers = getMarkersFromCardioPet(hf.readline())
			except ValueError:
				markers = []
		hf.close()

		if len(markers) > 0:
			for marker in markers:
				marker = int(marker)
				if (marker + segment_samples) > n_samples:
					continue
				elif (marker - segment_samples) < 0:
					continue
				else:
					if not done_abnormals:
						X.append(signal[(marker-segment_samples):(marker+segment_samples)]) 
						Y.append([0, 1])
						abnormals = abnormals + 1

						if n_abnormals != None:
							if abnormals >= n_abnormals:
								done_abnormals = True
		elif len(markers) == 0:
			point = segment_samples + 1

			while (point+segment_samples) < n_samples:
				if not done_normals:
					X.append(signal[(point-segment_samples):point+segment_samples])
					Y.append([1,0])
					normals = normals+1
					if n_normals != None:
						if normals >= n_normals:
							done_normals = True
				point = point + segment_samples
	xFile = 'x.txt'
	yFile = 'y.txt'
	X = np.asarray(X)
	Y = np.asarray(Y)
	with open(xFile, 'wb+') as xf:
		X.dump(xf)
	with open(yFile, 'wb+') as yf:
		Y.dump(yf)

	return (X, Y)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--dataFolder', 
						required=True,
						type=str,
						help='Location of ecg files to be converted to json', nargs='+')
	parser.add_argument('--extension',
						required=True,
						type=str,
						help='file extension of signal files, supported: dcm, txt')
	parser.add_argument('--savePath',
						type=str,
						default='test_dataset.json',
						help='location of json file for dataset to be written to')	
	parser.add_argument('--window_size',
						type=int,
						default=600, help='size of sliding window over signals')
	
	args = parser.parse_args()
	folder = args.dataFolder[0]
	savePath = args.savePath
	window_size = args.window_size
	if args.extension == 'dcm':
		dcm_datasetFromFolder(folder, window_size, savePath)
	elif args.extension == 'txt':
		txt_datasetFromFolder(folder, window_size) 
	else:
		print('{} extension not supported yet'.format(args.extension))
	
