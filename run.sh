#!/bin/bash

echo "copying moving and static tractograms"
subjID=`jq -r '._inputs[0].meta.subject' config.json`
static=`jq -r '.tractogram_static' config.json`
t1_static=`jq -r '.t1_static' config.json`
segmentations=`jq -r '.segmentations' config.json`
movings=`jq -r '.tractograms_moving' config.json`
t1s=`jq -r '.t1s_moving' config.json`
slr=`jq -r '.slr' config.json`
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
id_fs=$(jq -r "._inputs[2+$num_ex+$num_ex+$num_ex].meta.subject" config.json | tr -d "_")
if [ ! $subjID == $id_fs ]; then
echo "Inputs subject id incorrectly inserted. Check them again."
	exit 1
fi

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
mkdir -p tractograms_directory;
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
		mv ${id_mov}_tractogram_moving.trk tractograms_directory/$id_mov'_track.trk';
	done
else
	echo "Tractogram already in .trk format"
	cp $static $subjID'_track.trk';
	for i in `seq 1 $num_ex`; 
	do 
		id_mov=$(jq -r "._inputs[1+$i+$num_ex].meta.subject" config.json | tr -d "_")
		cp ${arr_mov[i]//[,\"]} tractograms_directory/$id_mov'_track.trk';
	done
fi

if [ -z "$(ls -A -- "tractograms_directory")" ]; then    
	echo "tractograms_directory is empty."; 
	exit 1;
else    
	echo "tractograms_directory created."; 
fi

if [[ $slr == true ]];then
	echo "SLR registration"
	for i in `seq 1 $num_ex`; 
	do
		id_mov=$(jq -r "._inputs[1+$i+$num_ex].meta.subject" config.json | tr -d "_")
		tractogram_moving=tractograms_directory/$id_mov'_track.trk'
		python tractograms_slr.py -moving $tractogram_moving -movID $id_mov -static $subjID'_track.trk' -statID $subjID
	done
else
	echo "Assuming subjects already co-registered in the same space."
fi

echo "Create examples directory"
if [[ ${arr_seg[1]//[,\"]} == *.trk ]];then
	echo "Tracts already in .trk format"
	tract_name=$(jq -r "._inputs[2].tags[0]" config.json | tr -d "_")
	echo $tract_name > tract_name_list.txt
	mkdir -p examples_directory_$tract_name;
	for i in `seq 1 $num_ex`; 
	do
		id_mov=$(jq -r "._inputs[1+$i+$num_ex].meta.subject" config.json | tr -d "_")
		cp ${arr_seg[i]//[,\"]} examples_directory_$tract_name/$id_mov'_'$tract_name'_tract.trk';
	done
else
	echo "Tracts conversion to trk"
	for i in `seq 1 $num_ex`; 
	do
		t1_moving=${arr_t1s[i]//[,\"]}
		id_mov=$(jq -r "._inputs[1+$i+$num_ex].meta.subject" config.json | tr -d "_")
		tractogram_moving=tractograms_directory/$id_mov'_track.trk'		
		seg_file=${arr_seg[i]//[,\"]}
		rm -f tract_name_list.txt;
		python wmc2trk.py -tractogram $tractogram_moving -classification $seg_file
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
fi

#wmc_tag=`jq -r '._inputs[2].datatype_tags[0]' config.json` 
tractID_list=`jq -r '.tractID_list' config.json`
arr=()
arr+=(${tractID_list})
tractID=${arr[0]//[,\"]}

if [[ $tractID < 30 ]]; then #afq
	echo "Coregistering ROIs on the target subject space"
	./mni_roi_registration.sh ${subjID} ${t1_static} AFQ
else #wmaSeg
	echo "Extracting endROIs of the minor tracts"
	mkdir -p aligned_ROIs;
	fsDir=`jq -r '.fsDir' config.json`
	python extract_endrois_minor.py -region 'parietal' -fsDir ${fsDir} -t1 ${t1_static} -out_dir aligned_ROIs
	python extract_endrois_minor.py -region 'temporal' -fsDir ${fsDir} -t1 ${t1_static} -out_dir aligned_ROIs
	python extract_endrois_minor.py -region 'LatTemp' -fsDir ${fsDir} -t1 ${t1_static} -out_dir aligned_ROIs
fi

echo "Running anatomically-informed multi-LAP"
mkdir -p tracts_tck;
run=multi-LAPanat	

while read tract_name; do
	echo "Tract name: $tract_name"; 
	base_name=$tract_name'_tract'
	output_filename=tracts_tck/${subjID}_${base_name}_${run}.tck
	python lap_multiple_examples_anat.py -moving_dir tractograms_directory -static $subjID'_track.trk' -ex_dir examples_directory_$tract_name -lD $lD -lE $lE -lR $lR -out $output_filename;
	mv estimated_bundle_idx_lap.npy estimated_bundle_idx_lap_${tract_name}.npy

done < tract_name_list.txt

if [ -z "$(ls -A -- "tracts_tck")" ]; then    
	echo "multi-LAPanat failed."
	exit 1
else    
	echo "multi-LAPanat done."
fi

echo "Building the wmc structure"
python build_wmc.py -tractogram $static
if [ -f 'classification.mat' ]; then 
    echo "WMC structure created."
else 
	echo "WMC structure missing."
	exit 1
fi

mkdir -p output_wmc
mv tracts output_wmc
cp classification.mat output_wmc

if [[ ${arr_seg[1]//[,\"]} == *.trk ]];then
	echo "Saving the tract also in .trk format"
	est_tck=$(ls tracts_tck)
	echo "${est_tck}"
	python tck2trk.py $t1_static tracts_tck/${est_tck}
	mv tracts_tck/*.trk track.trk
fi

