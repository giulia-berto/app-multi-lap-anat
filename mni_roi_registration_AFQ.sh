#!/bin/bash

#-----------------------------------------------------------------------------
# ROI Enumeration
#-----------------------------------------------------------------------------

# The original labels of ROI from MNI JHU atlas
ROI_TRL1=ATR_roi1_L
ROI_TRL2=ATR_roi2_L
ROI_TRR1=ATR_roi1_R
ROI_TRR2=ATR_roi2_R
ROI_CSTL1=CST_roi1_L
ROI_CSTL2=CST_roi2_L
ROI_CSTR1=CST_roi1_R
ROI_CSTR2=CST_roi2_R
ROI_AFL1=SLF_roi1_L
ROI_AFL2=SLFt_roi2_L
ROI_AFR1=SLF_roi1_R
ROI_AFR2=SLFt_roi2_R
ROI_CGCL1=CGC_roi1_L
ROI_CGCL2=CGC_roi2_L
ROI_CGCR1=CGC_roi1_R
ROI_CGCR2=CGC_roi2_R
ROI_CGHL1=HCC_roi1_L
ROI_CGHL2=HCC_roi2_L
ROI_CGHR1=HCC_roi1_R
ROI_CGHR2=HCC_roi2_R
ROI_UFL1=UNC_roi1_L
ROI_UFL2=UNC_roi2_L
ROI_UFR1=UNC_roi1_R
ROI_UFR2=UNC_roi2_R

# The list of ROI to be registered from MNI JHU atlas
ROI_ALL="TRL1 TRL2 TRR1 TRR2 CSTL1 CSTL2 CSTR1 CSTR2 AFL1 AFL2 AFR1 AFR2 CGCL1 CGCL2 CGCR1 CGCR2 CGHL1 CGHL2 CGHR1 CGHR2 UFL1 UFL2 UFR1 UFR2"


#-----------------------------------------------------------------------------
# Setting Parameters
#-----------------------------------------------------------------------------

# Threshold value to binarize the roi mask after the warping
ROI_CUT=0.3

