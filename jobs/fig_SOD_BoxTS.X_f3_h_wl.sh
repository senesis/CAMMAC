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

version         : tropics_ann_ssp5
do_test         : False
hybrid_seasons  : 
  tropics_annual : [  [ tropics , ANN ] ]  
scenarios       : [ ssp126, ssp245, ssp585 ]
excluded_models : {}
#  mrro : [ CAMS-CSM1-0 ]  # outlier

max_warming        : 5. # °C
min_warming        : 1.5
warming_step       : 0.25
proj_period        : 2000-2099 # period investigated for the warming
window_half_size   : 10  # (years) half-size of temperature running mean 

EOF

jobname=$figname
output=$figname
$D/jobs/job_pm.sh $D/notebooks/change_hybrid_seasons_dT.ipynb fig.yaml $jobname $output
