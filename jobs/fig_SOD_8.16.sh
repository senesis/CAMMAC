#!/bin/bash

D=/home/ssenesi/CAMMAC

# Create a working directory specific to this figure. It will hold cached data
figname=$(basename $0)
figname=${figname/.sh/}
mkdir -p $figname
cd $figname


# Create input parameters file 
cat <<EOF >fig_SOD_8.16.yaml
dummy : dummy
excluded_models : 
  mrro : [ CAMS-CSM1-0 ]  # outlier
#version : _no_Antarctic

EOF

PBS_RESSOURCES="-l mem=32g -l vmem=48g -l walltime=23:59:00" $D/jobs/job_pm.sh $D/notebooks/change_hybrid_seasons.ipynb fig_SOD_8.16.yaml $figname $figname
