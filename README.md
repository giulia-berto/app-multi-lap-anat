[![Abcdspec-compliant](https://img.shields.io/badge/ABCD_Spec-v1.1-green.svg)](https://github.com/brain-life/abcd-spec)
[![Run on Brainlife.io](https://img.shields.io/badge/Brainlife-bl.app.227-blue.svg)](https://doi.org/10.25663/brainlife.app.227)

# app-multi-lap-anat

<!-- brainlife-app:begin (generated from the App manifest; edit the manifest, not this block) -->

> **Segments white matter bundles in a target tractogram by anatomically-informed multiple Linear Assignment Problems (multi-LAP-anat), learning from WMC segmentations of example subjects, and outputs a WMC.**

Supervised example-based bundle segmentation: example bundles from several subjects (AFQ or WMA WMC segmentations with their tractograms and T1s) are optionally aligned to the target with streamline linear registration (SLR), and for each requested bundle the target streamlines are selected by solving linear assignment problems that combine streamline distance, endpoint distance and ROI terms. Use it to transfer bundle definitions from example subjects to a new subject. Several bundles can be segmented in one run; WMA minor tracts (IDs 38-45) need the target FreeSurfer input. All example inputs must be given in the same subject order.

| | |
|---|---|
| 📥 **Inputs** | `neuro/track/tck` ×2 · `neuro/anat/t1w` ×2 · `neuro/wmc` · `neuro/freesurfer` (optional) |
| 📤 **Outputs** | `neuro/wmc` |
| 🐳 **Container** | `brainlife/connectome_workbench:1.4.2b` |
| ⚙️ **Resources** | 16 CPUs · 31 GB memory · 12 h walltime |
| 🔑 **Requires** | `FREESURFER_LICENSE` |
| 🔗 **Run it** | [doi.org/10.25663/brainlife.app.227](https://doi.org/10.25663/brainlife.app.227) |

#### 📥 Inputs

| Input | Datatype | Required | Description |
|---|---|---|---|
| `0` | `neuro/track/tck` | yes | Tractogram of static (target) subject. Same subject as the static T1. |
| `1` | `neuro/anat/t1w` (acpc_aligned) | yes | T1 of static (target) subject |
| `2` | `neuro/wmc` | yes | Segmentations of moving (examples) subjects (they should be extracted from the tractogram provided). One per example subject, in the same order as the moving tractograms and T1s. |
| `3` | `neuro/track/tck` | yes | Tractograms of moving (example) subjects |
| `4` | `neuro/anat/t1w` (acpc_aligned) | yes | Ts1 of moving (example) subjects |
| `5` | `neuro/freesurfer` | no | FreeSurfer parcellation of static (target) subject (not used in version 1.0, needed for tractID from 38 to 45) |

#### 📤 Outputs

| Output | Datatype | Description |
|---|---|---|
| `output_wmc` | `neuro/wmc` | segmented bundles |

<details>
<summary><b>⚙️ Parameters</b> (8)</summary>

| Parameter | Type | Default | Description |
|---|---|---|---|
| `k` | number | `2000` | value for k-NN to compute the superset |
| `step_size` | number | `0.625` | step size for resampling |
| `slr` | boolean | `true` | If false, assuming subjects already co-registered in the same space |
| `lambdaD` | number | `1` | weight for the distance matrix |
| `lambdaE` | number | `1` | weight for the endpoint-based distance matrix |
| `lambdaR` | number | `1` | weight for the ROI-based distance matrix |
| `norm_mat` | boolean | `true` | matrices normalization |
| `tractID_list` | string |  | ID list of the bundles of interest, separated by commas (refer to the README.md for the mapping) |

</details>

📚 **References used by this App:**
- Bertò G., Avesani P., Pestilli F., Bullock D., Caron B., Olivetti E. Anatomically-Informed Multiple Linear Assignment Problems for White Matter Bundle Segmentation. ISBI 2019. [doi:10.1109/ISBI.2019.8759174](https://doi.org/10.1109/ISBI.2019.8759174)
- Avesani P. et al. The open diffusion data derivatives, brain data upcycling via integrated publishing of derivatives and reproducible open cloud services. Sci Data 6, 69 (2019). [doi:10.1038/s41597-019-0073-y](https://doi.org/10.1038/s41597-019-0073-y)

<!-- brainlife-app:end -->

This App segments white matter bundles by solving Anatomically-Informed multiple Linear Assignment Problems (multi-LAP-anat). The method is a supervised example-based segmentation method, and thus requires multiple bundles as examples to learn from. The segmentation is performed by means of fiber correspondence across subjects by considering both the shape of the fibers and their relative anatomical position.

![](app-lap-anat-avatar.png)

### Authors
- Giulia Bertò (giulia.berto.4@gmail.com)

### Contributors
- Emanuele Olivetti (olivetti@fbk.eu)
- Paolo Avesani (avesani@fbk.eu)

### Funding Acknowledgement
brainlife.io is publicly funded and for the sustainability of the project it is helpful to Acknowledge the use of the platform. We kindly ask that you acknowledge the funding below in your publications and code reusing this code.

[![NSF-BCS-1734853](https://img.shields.io/badge/NSF_BCS-1734853-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1734853)
[![NSF-BCS-1636893](https://img.shields.io/badge/NSF_BCS-1636893-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1636893)
[![NSF-ACI-1916518](https://img.shields.io/badge/NSF_ACI-1916518-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1916518)
[![NSF-IIS-1912270](https://img.shields.io/badge/NSF_IIS-1912270-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1912270)
[![NIH-NIBIB-R01EB029272](https://img.shields.io/badge/NIH_NIBIB-R01EB029272-green.svg)](https://grantome.com/grant/NIH/R01-EB029272-01)

### Citation
We kindly ask that you cite the following article when publishing papers and code using this code: 
1. ["Anatomically-Informed Multiple Linear Assignment Problems for White Matter Bundle Segmentation."](https://doi.org/10.1109/ISBI.2019.8759174), Bertò, G., Avesani, P., Pestilli, F., Bullock, D., Caron, B. and Olivetti, E., 2019, April. Anatomically-Informed Multiple Linear Assignment Problems for White Matter Bundle Segmentation. In 2019 IEEE 16th International Symposium on Biomedical Imaging (ISBI 2019) (pp. 135-138). IEEE.
2. Avesani, P., McPherson, B., Hayashi, S. et al. The open diffusion data derivatives, brain data upcycling via integrated publishing of derivatives and reproducible open cloud services. Sci Data 6, 69 (2019). [https://doi.org/10.1038/s41597-019-0073-y](https://doi.org/10.1038/s41597-019-0073-y)

### Running the app
### On [Brainlife.io](http://brainlife.io/) 
You can submit this App online at https://doi.org/10.25663/brainlife.app.227 via the “Execute” tab.

Inputs: \
To perform the bundle segmentation, you need two key elements: (i) the tractogram of the (target) subject you want to extract the bundle from and (ii) the wmc segmentations of multiple (example) subjects you want to learn from. Moreover, you have to provide the anatomical T1s and the tractograms of the (example) subjects (which are used to apply an initial Streamline Linear Registration (SLR) between tractograms).  

Output: \
You will get the wmc segmentation of the (single) bundle of interest in the target subject.

#### Branch 1.0:
The wmc segmentation files you have to provide as examples should be obtained using the AFQ algorithm (https://doi.org/10.25663/bl.app.13). \
You can choose the bundle to be segmented (one at the time) by providing the id related to the AFQ segmentation as follows: \
1 - Left Thalamic Radiation \
2 - Right Thalamic Radiation \
3 - Left Corticospinal \
4 - Right Corticospinal \
5 - Left Cingulum Cingulate \
6 - Right Cingulum Cingulate \
7 - Left Cingulum Hippocampus \
8 - Right Cingulum Hippocampus \
9 - Callosum Forceps Major \
10 - Callosum Forceps Minor \
11 - Left IFOF \
12 - Right IFOF \
13 - Left ILF \
14 - Right ILF \
15 - Left SLF \
16 - Right SLF \
17 - Left Uncinate \
18 - Right Uncinate \
19 - Left Arcuate \
20 - Right Arcuate \
This branch is associated with the App https://doi.org/10.25663/brainlife.app.122 (deprecated).

#### Branch 1.1:
In addition to use as examples AFQ wmc segmentations, you may also provide as examples the wmc segmentation obtained using the WMA algorithm (https://doi.org/10.25663/bl.app.41). In this case you have also to provide the freesufer parcellation file, which can be obtained by running the app https://doi.org/10.25663/bl.app.0. \
You can choose the bundle to be segmented (one at the time) by providing the id related to the WMA segmentation as follows: \
38 - Left pArc \
39 - Right pArc \
40 - Left TPC \
41 - Right TPC \
42 - Left MdLF-SPL \
43 - Right MdLF-SPL \
44 - Left MdLF-Ang \
45 - Right MdLF-Ang \
This branch is associated with the App https://doi.org/10.25663/brainlife.app.122 (deprecated).

#### Branch 2.0:
This branch implements the same functionalities of the branch 1.1 but with the following changes: 
- uses the new wmc input 
- SLR registration is optional
- can run multiple bundles at the same time 

You may provide as examples AFQ segmentations obtained by the app https://doi.org/10.25663/brainlife.app.207 or WMA segmentations obtained by the app https://doi.org/10.25663/brainlife.app.188.

### Running locally
1. git clone this repo.
2. Inside the cloned directory, create `config.json` with something like the following content with paths to your input files:
```
{
    "tractogram_static": "./track.tck",
    "t1_static": "./t1.nii.gz",
    "segmentations": [
        "./sub-1/classification.mat",           
        "./sub-2/classification.mat"
    ],
    "tracts": [
        "./sub-1/tracts",
        "./sub-2/tracts"
    ],
    "tractograms_moving": [
        "./sub-1/track.tck",
        "./sub-2/track.tck"
    ],
    "t1s_moving": [
        "./sub-1/t1.nii.gz",
        "./sub-2/t1.nii.gz"
    ],
    "tractID_list": "11, 12, 19, 20"
}
```
3. Launch the App by executing `main`.
```
./main
```

### Output
The output is a wmc file containing the specified bundles segmented by multi-LAP-anat.

#### Dependencies
This App only requires [singularity](https://sylabs.io/singularity/) to run.

#### MIT Copyright (c) 2019 Bruno Kessler Foundation (FBK)
