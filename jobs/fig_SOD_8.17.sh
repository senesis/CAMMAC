#!/bin/bash

D=/home/ssenesi/CAMMAC

# Create a working directory specific to this figure. It will hold cached data
figname=$(basename $0)
figname=${figname/.sh/}
mkdir -p $figname
cd $figname

# Create input parameters file 
cat <<EOF >fig_SOD_8.17.yaml
excluded_models        : [ EC-Earth3 , EC-Earth3-Veg ]  # Issue with mergetime
variability_excluded_models : [ EC-Earth3 , EC-Earth3-Veg ]  # Issue with mergetime
use_cached_proj_fields : False
print_statistics       : False
do_test                : False

EOF


hours=36 $D/jobs/job_pm.sh $D/notebooks/change_map_3SSPs_2vars.ipynb fig_SOD_8.17.yaml $figname $figname
