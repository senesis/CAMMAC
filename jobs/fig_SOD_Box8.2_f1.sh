#!/bin/bash

D=/home/ssenesi/CAMMAC

# Create a working directory specific to this figure. It will hold cached data
figname=$(basename $0)
figname=${figname/.sh/}
mkdir -p $figname
cd $figname


cat <<EOF >fig_SOD_Box8.2_f1.yaml

use_cached_proj_fields : False
use_cached_ref_field   : False
print_statistics       : False
plot_for_each_model : [ "reference", "projection", "change", "rchange", "variability" ]

ranges :  {
  "reference"  : { "min" : 0., "max" : 3000. , "delta" : 200. } ,
  "projection" : { "min" : 0., "max" : 3000. , "delta" : 200. } ,
  "rchange"    : { "min" : -25., "max" : 25. , "delta" : 5. } ,
  "variability": { "min" : 0., "max" : 1. , "delta" : 0.1 } ,
  }

ranges : {
  "change"     : {"min":-0.2,"max":0.2, "delta":0.04, "color":"AR6_Temp_12s"}
  }

EOF

#PBS_RESSOURCES="-l mem=16g -l vmem=48g -l walltime=12:00:00"
$D/jobs/job_pm.sh $D/notebooks/change_map_3SSPs_plus_ref.ipynb fig_SOD_Box8.2_f1.yaml $figname $figname

