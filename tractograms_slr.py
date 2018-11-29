""" SLR (Streamline Linear Registration) of two tractograms.
    
	See Garyfallidis et. al, 'Robust and efficient linear registration 
	of white-matter fascicles in the space of streamlines', 
	Neuroimage, 117:124-140, 2015.
"""

import os
import sys
import argparse
import nibabel as nib
import numpy as np
import ntpath
from nibabel.streamlines import load
from dipy.segment.clustering import QuickBundles
from dipy.align.streamlinear import StreamlineLinearRegistration
from dipy.tracking.streamline import set_number_of_points


def tractograms_slr(moving_tractogram, static_tractogram):

	subjID = ntpath.basename(static_tractogram)[0:6]
	exID = ntpath.basename(moving_tractogram)[0:6]

	print("Loading tractograms...")
	moving_tractogram = nib.streamlines.load(moving_tractogram)
	moving_tractogram = moving_tractogram.streamlines
	static_tractogram = nib.streamlines.load(static_tractogram)
	static_tractogram = static_tractogram.streamlines     

	print("Set parameters as in Garyfallidis et al. 2015.") 
	threshold_length = 40.0 # 50mm / 1.25
	qb_threshold = 16.0  # 20mm / 1.25 
	nb_res_points = 20

	print("Performing QuickBundles of static tractogram and resampling...")
	st = np.array([s for s in static_tractogram if len(s) > threshold_length], dtype=np.object)
	qb = QuickBundles(threshold=qb_threshold)
	st_clusters = [cluster.centroid for cluster in qb.cluster(st)]
	st_clusters = set_number_of_points(st_clusters, nb_res_points)

	print("Performing QuickBundles of moving tractogram and resampling...")
	mt = np.array([s for s in moving_tractogram if len(s) > threshold_length], dtype=np.object)
	qb = QuickBundles(threshold=qb_threshold)
	mt_clusters = [cluster.centroid for cluster in qb.cluster(mt)]
	mt_clusters = set_number_of_points(mt_clusters, nb_res_points)

	print("Performing Linear Registration...")
	srr = StreamlineLinearRegistration()
	srm = srr.optimize(static=st_clusters, moving=mt_clusters)

	print("Affine transformation matrix with Streamline Linear Registration:")
	affine = srm.matrix
	print('%s' %affine)

	np.save('affine_m%s_s%s.npy' %(exID, subjID), affine)
	print("Affine for example %s and target %s saved." %(exID, subjID))


if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('-moving', nargs='?', const=1, default='',
	                    help='The moving tractogram filename')
	parser.add_argument('-static', nargs='?',  const=1, default='',
	                    help='The static tractogram filename')                 
	args = parser.parse_args()

	tractograms_slr(args.moving, args.static)	
	                            
	sys.exit()    
