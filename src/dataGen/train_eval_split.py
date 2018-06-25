import glob
import random
import os 
import errno
import ntpath
import argparse

def split_folder(folder, extension='dcm', split=.2):
	'''
	split a  dataset of training data into train and eval folders

	assumes file structure with one folder full of .dcms or .txts and .heas

	Params
	------
	folder : location of datafolder
	
	extension : extion of folder structure (0ch.txt for .txt files)

	split : what percentage of the files will be used for eval data 
	
	Returns
	-------
	None, saves folders to folder/train and folder/eval
	'''

	try:
		os.makedirs('{}/train'.format(folder))
		os.makedirs('{}/eval'.format(folder))
	except OSError as e:
		if e.errno != errno.EEXIST:
			raise


	
	files = glob.glob(r'{}/*.{}'.format(folder, extension))
	if extension == 'txt':
		files = glob.glob(r'{}/*-0ch.{}'.format(folder, extension))	
	n_files = len(files)
	n_eval = n_files * .2
	evals = 0
	#move random number of files to eval/
	while evals <= n_eval:
		file = random.choice(files)
		files.remove(file)
		hea = '{}.hea'.format(file[:-4])
		if extension == 'txt':
			hea = '{}.hea'.format(file[:-8])
		try:
			newfile = '{}/eval/{}'.format(folder, ntpath.basename(file))
			newhea = '{}/eval/{}'.format(folder, ntpath.basename(hea))
			print('file: {}'.format(file))
			print('newfile: {}'.format(newfile))
			print('newhea: {}'.format(newhea))
			os.rename(file, newfile)
			os.rename(hea, newhea)
			evals = evals+1
		except FileNotFoundError:
			print('MISSING FILE: {}'.format(hea))
			continue
		except FileExistsError:
			print('FILE ALREADY EXISTS {}'.format(newfile))
			continue


	#move the rest of the files to train/
	for file in files:
		hea = '{}.hea'.format(file[:-4])
		if extension == 'txt':
			hea = '{}.hea'.format(file[:-8])
		try:
			newfile = '{}/train/{}'.format(folder, ntpath.basename(file))
			newhea = '{}/train/{}'.format(folder, ntpath.basename(hea))
			print('file: {}'.format(file))
			print('newfile: {}'.format(newfile))
			print('newhea: {}'.format(newhea))
			os.rename(file, newfile)
			os.rename(hea, newhea)
		except FileNotFoundError:
			print('MISSING FILE: {}'.format(hea))
			continue
		except FileExistsError:
			print('FILE ALREADY EXISTS {}'.format(newdcm))
			continue

if __name__ == '__main__':
	parser = argparse.ArgumentParser()

	parser.add_argument('--datafolder',
			required=True,
			type=str,
			help='Folder of dicoms and .hea files to move to train/eval')
	parser.add_argument('--split', 
		type=float, 
		default=.2, 
		help='percentage of files that will go into eval/, decimal')
	parser.add_argument('--extension',
		type=str,
		default='dcm',
		help='extension of files in dataset (dcm or txt)')
	args = parser.parse_args()
	folder = str(args.datafolder)
	split = args.split	
	try:
		split_folder(folder, args.extension, split)
	except IndexError:
		print('no dicom files found in {}'.format(folder))
