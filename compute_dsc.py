"""Compute the following voxel measures:
DSC, wDSC, J, sensitivity, vol_A, vol_B. 
"""

from __future__ import print_function
import os
import sys
import argparse
import os.path
import nibabel as nib
import numpy as np
import dipy
import json
from nibabel.streamlines import load
from dipy.tracking.vox2track import streamline_mapping
from dipy.tracking.streamline import set_number_of_points
from dipy.tracking.utils import length


def resample_tractogram(tractogram, step_size):
    """Resample the tractogram with the given step size.
    """
    lengths=list(length(tractogram))
    tractogram_res = []
    for i, f in enumerate(tractogram):
	nb_res_points = np.int(np.floor(lengths[i]/step_size))
	tmp = set_number_of_points(f, nb_res_points)
	tractogram_res.append(tmp)
    return tractogram_res


def compute_voxel_measures(estimated_tract, true_tract, aff):

    #aff=np.array([[-1.25, 0, 0, 90],[0, 1.25, 0, -126],[0, 0, 1.25, -72],[0, 0, 0, 1]])
    voxel_list_estimated_tract = streamline_mapping(estimated_tract, affine=aff).keys()
    voxel_list_true_tract = streamline_mapping(true_tract, affine=aff).keys()

    n_ET = len(estimated_tract)
    n_TT = len(true_tract)	
    dictionary_ET = streamline_mapping(estimated_tract, affine=aff)
    dictionary_TT = streamline_mapping(true_tract, affine=aff)
    voxel_list_intersection = set(voxel_list_estimated_tract).intersection(set(voxel_list_true_tract))

    sum_int_ET = 0
    sum_int_TT = 0
    for k in voxel_list_intersection:
	sum_int_ET = sum_int_ET + len(dictionary_ET[k])
	sum_int_TT = sum_int_TT + len(dictionary_TT[k])
    sum_int_ET = sum_int_ET/n_ET
    sum_int_TT = sum_int_TT/n_TT

    sum_ET = 0
    for k in voxel_list_estimated_tract:
	sum_ET = sum_ET + len(dictionary_ET[k])
    sum_ET = sum_ET/n_ET

    sum_TT = 0
    for k in voxel_list_true_tract:
	sum_TT = sum_TT + len(dictionary_TT[k])
    sum_TT = sum_TT/n_TT
    
    TP = len(set(voxel_list_estimated_tract).intersection(set(voxel_list_true_tract)))
    vol_A = len(set(voxel_list_estimated_tract))
    vol_B = len(set(voxel_list_true_tract))
    FP = vol_B-TP
    FN = vol_A-TP
    sensitivity = float(TP) / float(TP + FN) 
    DSC = 2.0 * float(TP) / float(vol_A + vol_B)
    wDSC = float(sum_int_ET + sum_int_TT) / float(sum_ET + sum_TT)
    J = float(TP) / float(TP + FN + FP)

    return DSC, wDSC, J, sensitivity, vol_A, vol_B



if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('-sub', nargs='?', const=1, default='',
	                    help='Subject ID')
	parser.add_argument('-list', nargs='?',  const=1, default='',
	                    help='The tract name list file .txt')                               
	args = parser.parse_args()

	#retrieve tract name
	with open(args.list) as fid:
	    content = fid.read().splitlines()

	with open('config.json') as f:
            data = json.load(f)
	    step_size = data["step_size"]
	    multi_LAP = data["multi_LAP"]

	tract_name = content[0]

	if multi_LAP == True:
		run_list = ['multi-LAP', 'multi-LAPanat']
		results_matrix = np.zeros((2, 6))
	else:
		run_list = ['multi-LAPanat']
		results_matrix = np.zeros((1, 6))

	#Write results on a file
	results = 'sub-%s_results_%s.txt' %(args.sub, tract_name)
	with open(results, "a") as myfile:
            myfile.write("DSC\twDSC\tJ\tsens\tvol_A\tvol_B\n")

        for r, run in enumerate(run_list):
		estimated_tract_filename = 'tracts_tck/%s_%s_tract_%s.tck' %(args.sub, tract_name, run)
		estimated_tract = nib.streamlines.load(estimated_tract_filename)
		estimated_tract = estimated_tract.streamlines
		true_tract_filename = '%s_tract.trk' %(tract_name)
		true_tract = nib.streamlines.load(true_tract_filename)
		affine = true_tract.affine
		true_tract = true_tract.streamlines
		print("Resampling with step size = %s mm" %step_size)
		true_tract_res = resample_tractogram(true_tract, step_size)
		true_tract = true_tract_res
		DSC, wDSC, J, sensitivity, vol_A, vol_B = compute_voxel_measures(estimated_tract, true_tract, affine)
		print("The DSC of the tract %s with %s is %s" %(tract_name, run, DSC))
		results_matrix[r] = [DSC, wDSC, J, sensitivity, vol_A, vol_B] 
		with open(results, "a") as myfile:
			myfile.write("%0.3f\t%0.3f\t%0.3f\t%0.3f\t%s\t%s\n" %(DSC, wDSC, J, sensitivity, vol_A, vol_B))
	
	np.save('sub-%s_results_%s_%s' %(args.sub, run, tract_name), results_matrix)

sys.exit()
