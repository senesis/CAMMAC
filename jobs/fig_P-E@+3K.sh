#!/bin/bash

D=/home/ssenesi/CAMMAC

# Create a working directory specific to this figure. It will hold cached data
figname=$(basename $0)
figname=${figname/.sh/}
mkdir -p $figname
cd $figname


cat <<EOF >fig.yaml
do_test : False
excluded_models : [ ACCESS-ESM1-5, EC-Earth3-Veg, EC-Earth3 ]
season : DJF
EOF

$D/jobs/job_pm.sh $D/notebooks/change_map_1var_at_WL_1SSP_with_clim.ipynb fig.yaml $figname $figname

