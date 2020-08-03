#!/bin/bash

D=/home/ssenesi/CAMMAC

# Create a working directory specific to this figure. It will hold cached data
figname=$(basename $0)
figname=${figname/.sh/}
mkdir -p $figname
cd $figname

# Create input parameters file 
cat <<EOF >fig_SOD_8.17.yaml
use_cached_proj_fields : True
print_statistics       : False

EOF


hours=36 $D/jobs/job_pm.sh $D/notebooks/change_map_3SSPs_2vars.ipynb fig_SOD_8.17.yaml $figname $figname
