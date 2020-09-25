#!/bin/bash

t1=`jq -r '.t1_static' config.json`
fsDir=`jq -r '.fsDir' config.json`
fsImg=./aparc.a2009s+aseg_1.25mm.nii.gz

echo "Convert the parcellation mgz file into nii format."
mgzfile=$fsDir/mri/aparc.a2009s+aseg.mgz
niifile=./aparc.a2009s+aseg.nii.gz
mri_convert $mgzfile $niifile

echo "Downsample the file nii file as the reference image."
flirt -in $niifile -ref $t1 -out $fsImg -interp nearestneighbour
