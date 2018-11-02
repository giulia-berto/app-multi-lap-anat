from __future__ import division, print_function, absolute_import
import os
import os.path
import nibabel as nib
import numpy as np
from dipy.tracking.streamline import set_number_of_points
from dipy.tracking.distances import bundles_distances_mam
from dissimilarity import compute_dissimilarity, dissimilarity
from dipy.tracking.utils import length
from sklearn.neighbors import KDTree


def resample_tractogram(tractogram, step_size):
    """Resample the tractogram with the given step size.
    """
    lengths=list(length(tractogram))
    tractogram_res = []
    for i, f in enumerate(tractogram):
	nb_res_points = np.int(np.floor(lengths[i]/step_size))
	tmp = set_number_of_points(f, nb_res_points)
	tractogram_res.append(tmp)
    tractogram_res = nib.streamlines.array_sequence.ArraySequence(tractogram_res)
    return tractogram_res


def compute_superset(true_tract, kdt, prototypes, k=1000, distance_func=bundles_distances_mam):
    """Compute a superset of the true target tract with k-NN.
    """
    true_tract = np.array(true_tract, dtype=np.object)
    dm_true_tract = distance_func(true_tract, prototypes)
    D, I = kdt.query(dm_true_tract, k=k)
    superset_idx = np.unique(I.flat)
    return superset_idx


def compute_kdtree_and_dr_tractogram(tractogram, num_prototypes=None):
    """Compute the dissimilarity representation of the target tractogram and 
    build the kd-tree.
    """
    tractogram = np.array(tractogram, dtype=np.object)
    print("Computing dissimilarity matrices...")
    if num_prototypes is None:
        num_prototypes = 40
        print("Using %s prototypes as in Olivetti et al. 2012."
              % num_prototypes)
    print("Using %s prototypes" % num_prototypes)
    dm_tractogram, prototype_idx = compute_dissimilarity(tractogram,
                                                         num_prototypes=num_prototypes,
                                                         distance=bundles_distances_mam,
                                                         prototype_policy='sff',
                                                         n_jobs=-1,
                                                         verbose=False)
    prototypes = tractogram[prototype_idx]
    print("Building the KD-tree of tractogram.")
    kdt = KDTree(dm_tractogram)
    return kdt, prototypes 


def save_bundle(estimated_bundle_idx, static_tractogram, step_size, out_filename):

	extension = os.path.splitext(out_filename)[1]
	static_tractogram = nib.streamlines.load(static_tractogram)
	aff_vox_to_ras = static_tractogram.affine
	voxel_sizes = static_tractogram.header['voxel_sizes']
	dimensions = static_tractogram.header['dimensions']
	static_tractogram = static_tractogram.streamlines
	static_tractogram_res = resample_tractogram(static_tractogram, step_size)
	static_tractogram = np.array(static_tractogram_res, dtype=np.object)
	estimated_bundle = static_tractogram[estimated_bundle_idx]
	
	if extension == '.trk':
		hdr = nib.streamlines.trk.TrkFile.create_empty_header()
		hdr['voxel_sizes'] = voxel_sizes
		hdr['dimensions'] = dimensions
		hdr['voxel_order'] = 'LAS'
		hdr['voxel_to_rasmm'] = aff_vox_to_ras 
	elif extension == '.tck':
		hdr = nib.streamlines.tck.TckFile.create_empty_header()
		hdr['voxel_sizes'] = voxel_sizes
		hdr['dimensions'] = dimensions
	else:
		print("%s format not supported." % extension)

	t = nib.streamlines.tractogram.Tractogram(estimated_bundle, affine_to_rasmm=np.eye(4))
	nib.streamlines.save(t, out_filename, header=hdr)
	print("Bundle saved in %s" % out_filename)

