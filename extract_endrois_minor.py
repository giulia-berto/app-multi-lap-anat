from __future__ import division, print_function, absolute_import
import os
import sys
import os.path
import argparse
import nibabel as nib
import numpy as np
import subprocess


def nifti_from_FSlabels(labels, fsImg, out_name):
	"""converts FreeSurfer labels into a unique ROI 
	in Nifti format for both the hemispheres.
	"""
	img = nib.load(fsImg)
	data = img.get_data()
	hdr = img.header
	affine = img.affine 

	for s in [1,2]:
	    sidenum = 10000 + s*1000
	    roi = np.zeros(data.shape)
	    for label in labels:
		label = label + sidenum
	        i,j,k = np.array(np.where(data==label))
	        roi[i,j,k] = 1

	    roi = nib.Nifti1Image(roi, affine, hdr)
	    if s==1:
	        roi_name = '%s_left.nii.gz' %out_name
	    elif s==2:
	        roi_name = '%s_right.nii.gz' %out_name
	    nib.save(roi, roi_name)
	    print("ROI saved in %s." %roi_name)	


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-region', nargs='?', const=1, default='',
	                    help='Region to extract the endrois from (available options are: parietal, temporal and LatTemp')
    parser.add_argument('-fsDir', nargs='?', const=1, default='',
	                    help='Freesurfer directory')   
    parser.add_argument('-t1', nargs='?', const=1, default='',
	                    help='T1 filename') 
    parser.add_argument('-out_dir', nargs='?', const=1, default='',
	                    help='The output directory')                         
    args = parser.parse_args()

    print("Convert the parcellation mgz file into nii format.")
    mgzfile = '%s/mri/aparc.a2009s+aseg.mgz' %(args.fsDir)
    niifile = '%s/mri/aparc.a2009s+aseg.nii.gz' %(args.fsDir)
    subprocess.check_call(['mri_convert', mgzfile, niifile])

    print("Downsample the file nii file as the reference image.")
    fsImg = 'aparc.a2009s+aseg_1.25mm.nii.gz' %(args.fsDir)
    cmd = 'flirt -in %s -ref %s -out %s -interp nearestneighbour' %(niifile, args.t1, fsImg)
    os.system(cmd)

    if args.region == 'parietal':
	labels = [157, 127, 168, 136, 126, 125]
    elif args.region == 'temporal':
	labels = [121, 161, 137, 162, 138, 173]
    elif args.region == 'LatTemp':
	labels = [134, 144, 174, 135]
    else:
	print("Region not supported.")

    out_name = '%s/%s_ROI' %(args.out_dir, args.region)
    nifti_from_FSlabels(labels, fsImg, out_name)
    
    sys.exit()
