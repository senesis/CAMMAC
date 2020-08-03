#!/bin/bash

D=/home/ssenesi/CAMMAC

# Create a working directory specific to this figure. It will hold cached data
figname=$(basename $0)
figname=${figname/.sh/}
mkdir -p $figname
cd $figname


# Create input parameters file 
cat <<EOF >fig_SOD_8.18.yaml
variable : evspsbl
table    : Amon
field_type : mean_rchange
custom_plot :
  units: "%"
use_cached_proj_fields : False
print_statistics       : False

plot_for_each_model : [ "reference", "projection", "change", "rchange",  "variability" ]
ranges : 
  reference   : { scale : 24*3600 , units : mm/d, min : 0 , max : 5 , delta : 0.5 }
  projection  : { scale : 24*3600 , units : mm/d, min : 0 , max : 5 , delta : 0.5 }
  change      : { scale : 24*3600 , units : mm/d, min : -2.5 , max : 2.5 , delta : 0.5 }
  rchange     : { min : -100. , max : 100., delta : 10. }
  variability : { scale : 24*3600 , units : mm/d, min : 0 , max : 0.25 , delta : 0.2 }

EOF

export PBS_RESSOURCES="-l mem=64g -l vmem=64g -l walltime=${hours:-12}:00:00"
$D/jobs/job_pm.sh $D/notebooks/change_map_3SSPs_2seasons.ipynb fig_SOD_8.18.yaml $figname $figname
