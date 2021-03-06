#!/bin/bash

D=/home/ssenesi/CAMMAC

# Create a working directory specific to this figure. It will hold cached data and figures
figname=$(basename $0)
figname=${figname/.sh/}
mkdir -p $figname
cd $figname


# Create input parameters file 
cat <<EOF >fig_SOD_8.15.yaml
figure_name : Fig8-mrro
version     : means_rchange
variable    : mrro
table       : Lmon
field_type  : means_rchange
custom_plot :
  units: "%"
  focus: land
figure_mask : $D/data/mask_hide_antarctic_360x180.nc

#plot_for_each_model    : [ "reference", "projection", "change", "rchange", "variability" ]
plot_for_each_model    : [ ]
ranges : 
  reference   : { scale : 24*3600 , units : mm/d, min : 0 , max : 10 , delta : 0.5 }
  projection  : { scale : 24*3600 , units : mm/d, min : 0 , max : 10 , delta : 0.5 }
  change      : { scale : 24*3600 , units : mm/d, min : -10 , max : 10 , delta : 1 }
  rchange     : { min : -100. , max : 100., delta : 10. }
  variability : { scale : 24*3600 , units : mm/d, min : 0 , max : 1 , delta : 0.05 }


use_cached_proj_fields : False
print_statistics       : False

EOF

export PBS_RESSOURCES="-l mem=64g -l vmem=64g -l walltime=${hours:-06}:00:00"
hours=18 $D/jobs/job_pm.sh $D/notebooks/change_map_3SSPs_2seasons.ipynb fig_SOD_8.15.yaml $figname $figname
