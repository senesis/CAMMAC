#!/bin/bash

D=/home/ssenesi/CAMMAC

# Create a working sub-directory specific to this figure. It will hold cached data
figname=$(basename $0)
figname=${figname/.sh/}
wdir=${figname/_figure}
mkdir -p $wdir
cd $wdir


# Create input parameters file 
cat <<EOF >fig.yaml

#version         : land_ann_ssp5
version         : tropics_ann_ssp5
hybrid_seasons  : 
  tropics_annual : [  [ tropics , ANN ] ]  #land_annual : [  [ land , ANN ] ]
scenarios       : [ ssp585 ]
excluded_models : 
  mrro : [ CAMS-CSM1-0 ]  # outlier

EOF

jobname=$figname
output=$figname
$D/jobs/job_pm.sh $D/notebooks/change_hybrid_seasons.ipynb fig.yaml $jobname $output
