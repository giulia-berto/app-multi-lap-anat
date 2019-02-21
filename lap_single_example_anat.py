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
from endpoints_distance import bundles_distances_endpoints_fastest
from waypoints_distance import bundles_distances_roi_fastest, bundles_distances_roi

try:
    from linear_assignment import LinearAssignment
except ImportError:
    print("WARNING: Cythonized LAPJV not available. Falling back to Python.")
    print("WARNING: See README.txt")
    from linear_assignment_numpy import LinearAssignment 

try:
    from joblib import Parallel, delayed, cpu_count
    joblib_available = True
except ImportError:
    joblib_available = False


def compute_lap_matrices(superset_idx, source_tract, tractogram, roi1, roi2, subjID, exID):
	"""Code for computing the inputs to the MODIFIED Rectangular Linear Assignment Problem.
	"""
	with open('config.json') as f:
		data = json.load(f)
	norm_mat = data["norm_mat"]
	distance = bundles_distances_mam
	tractogram = np.array(tractogram, dtype=np.object)
	
	if isfile('distance_matrix_m%s_s%s.npy' %(exID, subjID)):
		print("Retrieving distance matrix for example %s and target %s." %(exID, subjID))
		distance_matrix = np.load('distance_matrix_m%s_s%s.npy' %(exID, subjID))
	else:
		print("Computing the distance matrix (%s x %s) for RLAP with %s... " % (len(source_tract), len(superset_idx), distance))
		t0=time.time()
		distance_matrix = dissimilarity(source_tract, tractogram[superset_idx], distance)
		np.save('distance_matrix_m%s_s%s.npy' %(exID, subjID), distance_matrix)
		print("Time for computing the distance matrix = %s seconds" %(time.time()-t0))
	
	print("Computing the endpoint matrix (%s x %s) for RLAP... " % (len(source_tract), len(superset_idx)))
	t1=time.time()
	endpoint_matrix = bundles_distances_endpoints_fastest(source_tract, tractogram[superset_idx])
	endpoint_matrix = endpoint_matrix * 0.5
	print("Time for computing the endpoint matrix = %s seconds" %(time.time()-t1))

	print("Computing the waypoint matrix (%s x %s) for RLAP... " % (len(source_tract), len(superset_idx)))
	t2=time.time()
	if joblib_available:
		roi_matrix = bundles_distances_roi_fastest(source_tract, tractogram[superset_idx], roi1, roi2)
	else:
		roi_matrix = bundles_distances_roi(source_tract, tractogram[superset_idx], roi1, roi2)
	roi_matrix = roi_matrix * 0.5
	print("Time for computing the waypoint matrix = %s seconds" %(time.time()-t2))

	if norm_mat == True:
		#normalize matrices
		distance_matrix = (distance_matrix-np.min(distance_matrix))/(np.max(distance_matrix)-np.min(distance_matrix))
		endpoint_matrix = (endpoint_matrix-np.min(endpoint_matrix))/(np.max(endpoint_matrix)-np.min(endpoint_matrix))
		roi_matrix = (roi_matrix-np.min(roi_matrix))/(np.max(roi_matrix)-np.min(roi_matrix))

	return distance_matrix, endpoint_matrix, roi_matrix


def RLAP_modified(distance_matrix, endpoint_matrix, roi_matrix, superset_idx, lD, lE, lR):
    """Code for MODIFIED Rectangular Linear Assignment Problem.
    """
    lD = np.asarray(lD, dtype='float64')
    lE = np.asarray(lE, dtype='float64')
    lR = np.asarray(lR, dtype='float64')
    print("Computing cost matrix.")
    cost_matrix = lD * distance_matrix + lE * endpoint_matrix + lR * roi_matrix
    print("Computing RLAP with LAPJV...")
    t0=time.time()
    assignment = LinearAssignment(cost_matrix).solution
    estimated_bundle_idx = superset_idx[assignment]
    min_cost_values = cost_matrix[np.arange(len(cost_matrix)), assignment]
    print("Time for computing the solution to the assignment problem = %s seconds" %(time.time()-t0))

    return estimated_bundle_idx, min_cost_values


def lap_single_example(moving_tractogram, static_tractogram, example, lD, lE, lR):
	"""Code for LAP from a single example.
	"""
	np.random.seed(0)

	with open('config.json') as f:
	    data = json.load(f)
	    k = data["k"]
	    step_size = data["step_size"]
	    tag = data["_inputs"][2]["datatype_tags"][0].encode("utf-8")
	distance_func = bundles_distances_mam

	subjID = ntpath.basename(static_tractogram)[0:6]
	tract_name = ntpath.basename(example)[7:-10]
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

	print("Computing superset with k = %s" %k)
	superset_idx = compute_superset(example_bundle_aligned, kdt, prototypes, k=k)

	print("Loading the two-waypoint ROIs of the target...")
	table_filename = 'ROIs_labels_dictionary.pickle'
	table = pickle.load(open(table_filename))
	roi1_lab = table[tract_name].items()[0][1]
	roi2_lab = table[tract_name].items()[1][1]
	if tag == 'afq':
		roi1_filename = 'aligned_ROIs/sub-%s_var-AFQ_lab-%s_roi.nii.gz' %(subjID, roi1_lab)
		roi2_filename = 'aligned_ROIs/sub-%s_var-AFQ_lab-%s_roi.nii.gz' %(subjID, roi2_lab)
	elif tag == 'wmaSeg':
		roi1_filename = 'aligned_ROIs/%s.nii.gz' %roi1_lab
		roi2_filename = 'aligned_ROIs/%s.nii.gz' %roi2_lab
	roi1 = nib.load(roi1_filename)
	roi2 = nib.load(roi2_filename)
	
	print("Computing matrices for LAP...")
	distance_matrix, endpoint_matrix, roi_matrix = compute_lap_matrices(superset_idx, example_bundle_aligned, static_tractogram, roi1, roi2, subjID, exID)

	print("Using lambdaD = %s, lambdaE = %s and lambdaR = %s" %(lD,lE,lR))
	estimated_bundle_idx, min_cost_values = RLAP_modified(distance_matrix, endpoint_matrix, roi_matrix, superset_idx, lD, lE, lR)

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
	parser.add_argument('-lD', nargs='?',  const=1, default='',
	                    help='Weight of the distance matrix')
	parser.add_argument('-lE', nargs='?',  const=1, default='',
	                    help='Weight of the endpoint matrix')
	parser.add_argument('-lR', nargs='?',  const=1, default='',
	                    help='Weight of the waypoint matrix')
	parser.add_argument('-out', nargs='?',  const=1, default='',
	                    help='The output estimated bundle filename')                               
	args = parser.parse_args()

	result_lap = lap_single_example(args.moving, args.static, args.ex, args.lD, args.lE, args.lR)

	np.save('result_lap', result_lap)

	if args.out:
		estimated_bundle_idx = result_lap[0]
		with open('config.json') as f:
            		data = json.load(f)
	    		step_size = data["step_size"]
		save_bundle(estimated_bundle_idx, args.static, step_size, args.out)

	sys.exit()    
