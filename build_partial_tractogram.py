""" Build a partial tck tractogram, composed of only some tracts.
"""

from __future__ import print_function
import os
import sys
import argparse
import os.path
import nibabel as nib
import numpy as np
from nibabel.streamlines import load, save
import scipy.io


def build_partial_tractogram(tracts_tck_dir, out_filename):
	
	tracts_tck = os.listdir(tracts_tck_dir)
	n = len(tracts_tck)
	
	some_tracts = []
	for i in range(n):
		tract_filename = '%s/%s' %(tracts_tck_dir, tracts_tck[i])
		tract = nib.streamlines.load(tract_filename)
		tract = tract.streamlines
		some_tracts.append(tract)

	# Concatenate streamlines
	st=nib.streamlines.array_sequence.concatenate(some_tracts[:], axis=0)

	# Retreiving header
	tract = nib.streamlines.load(tract_filename)
	aff_vox_to_ras = tract.affine
	nb_streamlines = tract.header['nb_streamlines']
	#voxel_sizes = tract.header['voxel_sizes']
	#dimensions = tract.header['dimensions']

	# Creating new header
	hdr = nib.streamlines.tck.TckFile.create_empty_header()
	#hdr['voxel_sizes'] = voxel_sizes
	#hdr['dimensions'] = dimensions
	hdr['voxel_to_rasmm'] = aff_vox_to_ras
	hdr['nb_streamlines'] = nb_streamlines

	# Saving partial tractogram
	stt = nib.streamlines.tractogram.Tractogram(st, affine_to_rasmm=np.eye(4))
	nib.streamlines.save(stt, out_filename, header=hdr)
	print("Partial tractogram saved in %s" % out_filename)

	# Create matlab structure
	a = np.array([len(some_tracts[j]) for j in range(n)])
	idx = np.zeros(np.sum(a))
	tmp = 0
	for j in range(n):
		idx[tmp:tmp+a[j]] = j+1 
		tmp += a[j]
	scipy.io.savemat('index', mdict={'idx':idx})


if __name__ == '__main__':

	np.random.seed(0) 

	parser = argparse.ArgumentParser()
	parser.add_argument('-tracts_tck_dir', nargs='?', const=1, default='',
	                    help='The tck tracts directory')
	parser.add_argument('-out', nargs='?',  const=1, default='default',
	                    help='The output partial tractogram filename')                   
	args = parser.parse_args()

	some_tracts = build_partial_tractogram(args.tracts_tck_dir, args.out)

	sys.exit()
