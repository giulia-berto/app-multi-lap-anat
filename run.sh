#!/bin/bash

echo "copying moving and static tractograms"
subjID=`jq -r '._inputs[0].meta.subject' config.json`
static=`jq -r '.tractogram_static' config.json`
t1_static=`jq -r '.t1_static' config.json`
segmentations=`jq -r '.segmentations' config.json`
movings=`jq -r '.tractograms_moving' config.json`
t1s=`jq -r '.t1s_moving' config.json`
lambdaD=`jq -r '.lambdaD' config.json`
lambdaE=`jq -r '.lambdaE' config.json`
lambdaR=`jq -r '.lambdaR' config.json`

# Building arrays
arr_seg=()
arr_seg+=(${segmentations})
arr_mov=()
arr_mov+=(${movings})
arr_t1s=()
arr_t1s+=(${t1s})

echo "Check the inputs subject id"
num_ex=$((${#arr_seg[@]} - 2))
if [ ! $subjID == `jq -r '._inputs[1].meta.subject' config.json` ]; then
echo "Inputs subject id incorrectly inserted. Check them again."
	exit 1
fi
for i in `seq 1 $num_ex`; 
do 
	id_seg=$(jq -r "._inputs[1+$i].meta.subject" config.json | tr -d "_")
	id_mov=$(jq -r "._inputs[1+$i+$num_ex].meta.subject" config.json | tr -d "_")
	id_t1=$(jq -r "._inputs[1+$i+$num_ex+$num_ex].meta.subject" config.json | tr -d "_")	
	if [ $id_seg == $id_mov -a $id_seg == $id_t1 ]; then
	echo "Inputs subject id correctly inserted"
else
	echo "Inputs subject id incorrectly inserted. Check them again."
	exit 1
fi
done

echo "Building LAP environment"
if [ -f "linear_assignment.c" ];then
	echo "LAP already built. Skipping"
else
	cython linear_assignment.pyx;
	python setup_lapjv.py build_ext --inplace;

	ret=$?
	if [ ! $ret -eq 0 ]; then
		echo "LAP environment build failed"
		echo $ret > finished
		exit $ret
	fi
fi

echo "Tractogram conversion to trk"
mkdir tractograms_directory;
if [[ $static == *.tck ]];then
	echo "Input in tck format. Convert it to trk."
	cp $static ./tractogram_static.tck;
	python tck2trk.py $t1_static tractogram_static.tck -f;
	cp tractogram_static.trk $subjID'_track.trk';
	for i in `seq 1 $num_ex`; 
	do 
		t1_moving=${arr_t1s[i]//[,\"]}
		id_mov=$(jq -r "._inputs[1+$i+$num_ex].meta.subject" config.json | tr -d "_")
		cp ${arr_mov[i]//[,\"]} ./${id_mov}_tractogram_moving.tck;
		python tck2trk.py $t1_moving ${id_mov}_tractogram_moving.tck -f;
		cp ${id_mov}_tractogram_moving.trk tractograms_directory/$id_mov'_track.trk';
	done
fi

if [ -z "$(ls -A -- "tractograms_directory")" ]; then    
	echo "tractograms_directory is empty."; 
	exit 1;
else    
	echo "tractograms_directory created."; 
fi

echo "SLR registration"
for i in `seq 1 $num_ex`; 
do
	id_mov=$(jq -r "._inputs[1+$i+$num_ex].meta.subject" config.json | tr -d "_")
	tractogram_moving=tractograms_directory/$id_mov'_track.trk'
	python tractograms_slr.py -moving $tractogram_moving -static $subjID'_track.trk'
done

echo "AFQ conversion to trk"
for i in `seq 1 $num_ex`; 
do
	t1_moving=${arr_t1s[i]//[,\"]}
	id_mov=$(jq -r "._inputs[1+$i+$num_ex].meta.subject" config.json | tr -d "_")		
	matlab -nosplash -nodisplay -r "afqConverterMulti(${arr_seg[i]//,}, ${arr_t1s[i]//,})";
	while read tract_name; do
		echo "Tract name: $tract_name";
		if [ ! -d "examples_directory_$tract_name" ]; then
  			mkdir examples_directory_$tract_name;
		fi
		mv $tract_name'_tract.trk' examples_directory_$tract_name/$id_mov'_'$tract_name'_tract.trk';

		if [ -z "$(ls -A -- "examples_directory_$tract_name")" ]; then    
			echo "examples_directory is empty."; 
			exit 1;
		else    
			echo "examples_directory created."; 
		fi	
	done < tract_name_list.txt

done

wmc_tag=`jq -r '._inputs[2].datatype_tags[0]' config.json` 
if [ $wmc_tag == 'afq' ]; then
	echo "Coregistering ROIs on the target subject space"
	./mni_roi_registration.sh ${subjID} ${t1_static} AFQ
elif [ $wmc_tag == 'wmaSeg' ]; then
	echo "Extracting endROIs of the minor tracts"
	mkdir aligned_ROIs;
	fsDir=`jq -r '.fsDir' config.json`
	python extract_endrois_minor.py -region 'parietal' -fsDir ${fsDir} -t1 ${t1_static} -out_dir aligned_ROIs
	python extract_endrois_minor.py -region 'temporal' -fsDir ${fsDir} -t1 ${t1_static} -out_dir aligned_ROIs
	python extract_endrois_minor.py -region 'LatTemp' -fsDir ${fsDir} -t1 ${t1_static} -out_dir aligned_ROIs
fi

echo "Running anatomically-informed multi-LAP"
mkdir tracts_tck;
run=multi-LAPanat	

while read tract_name; do
	echo "Tract name: $tract_name"; 
	base_name=$tract_name'_tract'
	output_filename=tracts_tck/${subjID}_${base_name}_${run}.tck
	python lap_multiple_examples_anat.py -moving_dir tractograms_directory -static $subjID'_track.trk' -ex_dir examples_directory_$tract_name -lD $lD -lE $lE -lR $lR -out $output_filename;

done < tract_name_list.txt

if [ -z "$(ls -A -- "tracts_tck")" ]; then    
	echo "multi-LAPanat failed."
	exit 1
else    
	echo "multi-LAPanat done."
fi

echo "Build partial tractogram"
output_filename=${subjID}'_var-partial_tract_'${run}'.tck';
python build_partial_tractogram.py -tracts_tck_dir 'tracts_tck' -out ${output_filename};
if [ -f ${output_filename} ]; then 
    echo "Partial tractogram built."
else 
	echo "Partial tractogram missing."
	exit 1
fi

echo "Build a wmc structure"
stat_sub=\'$subjID\'
tag=\'$run\'
matlab -nosplash -nodisplay -r "build_wmc_structure($stat_sub, $tag)";
if [ -f 'output.mat' ]; then 
    echo "WMC structure created."
else 
	echo "WMC structure missing."
	exit 1
fi

echo "Complete"
