""" Bundle segmentation with Rectangular Linear Assignment Problem.
"""

import os
import sys
import argparse
import os.path
import nibabel as nib
import numpy as np
import pickle
import json
import time
import ntpath
from os.path import isfile
from tractograms_slr import tractograms_slr
from dipy.tracking.streamline import apply_affine
from dissimilarity import compute_dissimilarity, dissimilarity
from dipy.tracking.distances import bundles_distances_mam
from utils import resample_tractogram, compute_superset, compute_kdtree_and_dr_tractogram, save_bundle


try:
    from linear_assignment import LinearAssignment
except ImportError:
    print("WARNING: Cythonized LAPJV not available. Falling back to Python.")
    print("WARNING: See README.txt")
    from linear_assignment_numpy import LinearAssignment 


def RLAP(kdt, k, dm_source_tract, source_tract, tractogram, distance, exID, subjID):
    """Code for Rectangular Linear Assignment Problem.
    """
    tractogram = np.array(tractogram, dtype=np.object)
    D, I = kdt.query(dm_source_tract, k=k)
    superset = np.unique(I.flat)

    if isfile('distance_matrix_m%s_s%s.npy' %(exID, subjID)):
	print("Retrieving distance matrix for example %s and target %s." %(exID, subjID))
	cost_matrix = np.load('distance_matrix_m%s_s%s.npy' %(exID, subjID))
    else:
    	print("Computing the cost matrix (%s x %s) for RLAP... " % (len(source_tract), len(superset)))
    	cost_matrix = dissimilarity(source_tract, tractogram[superset], distance)

    print("Computing RLAP with LAPJV...")
    assignment = LinearAssignment(cost_matrix).solution
    estimated_bundle_idx = superset[assignment]
    min_cost_values = cost_matrix[np.arange(len(cost_matrix)), assignment]

    return estimated_bundle_idx, min_cost_values


def lap_single_example(moving_tractogram, static_tractogram, example):
	"""Code for LAP from a single example.
	"""
	np.random.seed(0)

	with open('config.json') as f:
	    data = json.load(f)
	    k = data["k"]
	    step_size = data["step_size"]
	distance_func = bundles_distances_mam

	subjID = ntpath.basename(static_tractogram)[0:6]
	exID = ntpath.basename(example)[0:6]

	example_bundle = nib.streamlines.load(example)
	example_bundle = example_bundle.streamlines
	example_bundle_res = resample_tractogram(example_bundle, step_size)
	
	print("Retrieving the affine slr transformation for example %s and target %s." %(exID, subjID))
	affine = np.load('affine_m%s_s%s.npy' %(exID, subjID))
	print("Applying the affine to the example bundle.")
	example_bundle_aligned = np.array([apply_affine(affine, s) for s in example_bundle_res])
	
	print("Compute the dissimilarity representation of the target tractogram and build the kd-tree.")
	static_tractogram = nib.streamlines.load(static_tractogram)
	static_tractogram = static_tractogram.streamlines
	static_tractogram_res = resample_tractogram(static_tractogram, step_size)	
	static_tractogram = static_tractogram_res
	if isfile('prototypes.npy') & isfile('kdt'):
		print("Retrieving past results for kdt and prototypes.")
		kdt_filename='kdt'
		kdt = pickle.load(open(kdt_filename))
		prototypes = np.load('prototypes.npy')
	else:
		kdt, prototypes = compute_kdtree_and_dr_tractogram(static_tractogram)
		#Saving files
		kdt_filename='kdt'
		pickle.dump(kdt, open(kdt_filename, 'w'), protocol=pickle.HIGHEST_PROTOCOL)
		np.save('prototypes', prototypes)

	print("Compute the dissimilarity of the aligned example bundle with the prototypes of target tractogram.")
	example_bundle_aligned = np.array(example_bundle_aligned, dtype=np.object)
	dm_example_bundle_aligned = distance_func(example_bundle_aligned, prototypes)

	print("Segmentation as Rectangular linear Assignment Problem (RLAP).")
	estimated_bundle_idx, min_cost_values = RLAP(kdt, k, dm_example_bundle_aligned, example_bundle_aligned, static_tractogram, distance_func, exID, subjID)
	estimated_bundle = static_tractogram[estimated_bundle_idx]

	return estimated_bundle_idx, min_cost_values, len(example_bundle)
	


if __name__ == '__main__':

	np.random.seed(0) 

	parser = argparse.ArgumentParser()
	parser.add_argument('-moving', nargs='?', const=1, default='',
	                    help='The moving tractogram filename')
	parser.add_argument('-static', nargs='?',  const=1, default='',
	                    help='The static tractogram filename')
	parser.add_argument('-ex', nargs='?',  const=1, default='',
	                    help='The example (moving) bundle filename')  
	parser.add_argument('-out', nargs='?',  const=1, default='',
	                    help='The output estimated bundle filename')                               
	args = parser.parse_args()

	result_lap = lap_single_example(args.moving, args.static, args.ex)

	np.save('result_lap', result_lap)

	if args.out:
		estimated_bundle_idx = result_lap[0]
		with open('config.json') as f:
            		data = json.load(f)
	    		step_size = data["step_size"]
		save_bundle(estimated_bundle_idx, args.static, step_size, args.out)

	sys.exit()    
