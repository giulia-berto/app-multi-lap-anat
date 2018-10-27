"""ROI-based distances.
"""

from __future__ import division, print_function, absolute_import
import numpy as np
import nibabel as nib
from nibabel.affines import apply_affine 
from scipy.spatial.distance import cdist


def bundle2roi_distance(bundle, roi_mask, distance='euclidean'):
	"""Compute the minimum euclidean distance between a
	   set of streamlines and a ROI nifti mask.
	"""
	data = roi_mask.get_data()
	affine = roi_mask.affine
	roi_coords = np.array(np.where(data)).T
	x_roi_coords = apply_affine(affine, roi_coords)
	result=[]
	for sl in bundle:                                                                                  
		d = cdist(sl, x_roi_coords, distance)
		result.append(np.min(d)) 
	return result


def bundles_distances_roi(bundle, superset, roi1, roi2):

    roi1_dist = bundle2roi_distance(superset, roi1)
    roi2_dist = bundle2roi_distance(superset, roi2)
    roi_vector = np.add(roi1_dist, roi2_dist)
    roi_matrix = np.zeros((len(bundle), len(superset)))
    roi1_ex_dist = bundle2roi_distance(bundle, roi1)
    roi2_ex_dist = bundle2roi_distance(bundle, roi2)
    roi_ex_vector = np.add(roi1_ex_dist, roi2_ex_dist)
    #subtraction
    for i in range(len(bundle)):
	for j in range(len(superset)):
            roi_matrix[i,j] = np.abs(np.subtract(roi_ex_vector[i], roi_vector[j]))
	
    return roi_matrix

