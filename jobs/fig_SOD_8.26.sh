#!/bin/bash

D=/home/ssenesi/CAMMAC

# Create a working directory specific to this figure. It will hold cached data
figname=$(basename $0)
figname=${figname/.sh/}
mkdir -p $figname
cd $figname


cat <<EOF >fig_SOD_8.26.yaml
dummy : dummy
#excluded_models : [ EC-Earth3-Veg, EC-Earth3 ]
EOF

$D/jobs/job_pm.sh $D/notebooks/change_map_path_dependance.ipynb fig_SOD_8.26.yaml $figname $figname

