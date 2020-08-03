#!/bin/bash

D=/home/ssenesi/CAMMAC

# Create a working directory specific to this figure. It will hold cached data
figname=$(basename $0)
figname=${figname/.sh/}
mkdir -p $figname
cd $figname


# Create input parameters file 
cat <<EOF >fig_SOD_8.14.yaml
dummy : dummy
use_cached_proj_fields : False
do_test : False
EOF

PBS_RESSOURCES="-l mem=16g -l vmem=48g -l walltime=12:00:00" $D/jobs/job_pm.sh $D/notebooks/change_zonal_mean.ipynb fig_SOD_8.14.yaml $figname $figname
