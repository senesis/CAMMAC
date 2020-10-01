#!/bin/bash
# Idem 8.19 sauf retrait de deux modèles CanESM

D=/home/ssenesi/CAMMAC

# Create a working directory specific to this figure. It will hold cached data
figname=$(basename $0)
figname=${figname/.sh/}
mkdir -p $figname
cd $figname

cat <<EOF >fig_SOD_8.19.yaml

figure_name : Fig8-19
variable    : mrso
table       : Lmon
field_type  : mean_schange
custom_plot : {"colors": "-5 -2 -1 -0.5 -0.25 0. 0.25 0.5 1 2 5", "units":"-", "color":"AR6_Precip_12s"} 
do_test     : False 
use_cached_proj_fields : False
figure_mask : $D/data/mask_hide_antarctic_360x180.nc
excluded_models : [ CanESM5 , CanESM5-CanOE ]

plot_for_each_model : [ "reference", "projection", "change", "rchange", "schange", "variability" ]
plot_for_each_model : [  ]

ranges :  {
  "reference"  : { "min" : 0., "max" : 3000. , "delta" : 200. } ,
  "projection" : { "min" : 0., "max" : 3000. , "delta" : 200. } ,
  "change"     : { "min" :1000.,"max":-1000. , "delta":200.} , 
  "rchange"    : { "min" : -25., "max" : 25. , "delta" : 5. } ,
  "schange"    : { "colors": "-5 -2 -1 -0.5 -0.25 0. 0.25 0.5 1 2 5"  , "units":"-", "color":"AR6_Precip_12s" } , 
  "variability": { "min" : 0., "max" : 1. , "delta" : 0.1 } ,
  }


EOF

hours=06
export PBS_RESSOURCES="-l mem=64g -l vmem=64g -l walltime=${hours:-06}:00:00"
$D/jobs/job_pm.sh $D/notebooks/change_map_3SSPs_2seasons.ipynb fig_SOD_8.19.yaml $figname $figname
