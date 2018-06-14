import glob
import random
import os 
import errno
import ntpath
import argparse

def split_dcm_folder(folder, split=.2):
	'''
	split a dicom dataset of training data into train and eval folders

	assumes file structure with one folder full of .dcms and .heas

	Params
	------
	folder : location of datafolder
		
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

	dcms = glob.glob(r'{}/*.dcm'.format(folder))
	n_files = len(dcms)
	n_eval = n_files * .2
	evals = 0
	print('total_files: {}'.format(n_files))
	#move random number of files to eval/
	while evals <= n_eval:
		dcm = random.choice(dcms)
		dcms.remove(dcm)
		hea = '{}.hea'.format(dcm[:-4])
		bn = ntpath.basename(dcm)
		try:
			newdcm = '{}/eval/{}'.format(folder, bn)
			newhea = '{}/eval/{}'.format(folder, ntpath.basename(hea))
			os.rename(dcm, newdcm)
			os.rename(hea, newhea)
			evals = evals+1
		except FileNotFoundError:
			print('MISSING FILE: {}'.format(hea))
			continue
		except FileExistsError:
			print('FILE ALREADY EXISTS {}'.format(newdcm))
			continue


	#move the rest of the files to train/
	for file in dcms:
		hea = '{}.hea'.format(file[:-4])
		bn = ntpath.basename(file)
		try:
			newdcm = '{}/train/{}'.format(folder, bn)
			newhea = '{}/train/{}'.format(folder, ntpath.basename(hea))
			os.rename(file, newdcm)
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

	args = parser.parse_args()
	folder = str(args.datafolder)
	split = args.split	
	try:
		split_dcm_folder(folder, split)
	except IndexError:
		print('no dicom files found in {}'.format(folder))
