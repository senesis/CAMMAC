#!/bin/bash

D=/home/ssenesi/CAMMAC

# Create a working directory specific to this figure. It will hold cached data and figures
figname=$(basename $0)
figname=${figname/.sh/}
mkdir -p $figname
cd $figname


# Create input parameters file 
cat <<EOF >fig_SOD_8.15s.yaml
do_test : False
figure_name : Fig8-15s
variable    : pr
table       : Amon
field_type  : mean_rchange
custom_plot :
  units: "%"
plot_for_each_model    : [ "reference", "projection", "change", "rchange", "variability" ]
#plot_for_each_model    : [ "reference", "change", "rchange" ]
#ranges : {}
ranges : 
  reference   : { scale : 24*3600 , units : mm/d, min : 0 , max : 10 , delta : 0.5 }
  projection  : { scale : 24*3600 , units : mm/d, min : 0 , max : 10 , delta : 0.5 }
  change      : { scale : 24*3600 , units : mm/d, min : -10 , max : 10 , delta : 1 }
  rchange     : { min : -100. , max : 100., delta : 10. }
  #rchange     : { colors : "-10000 -1000 -100 -50 -20 -10 0 10 20 50 100 1000 10000" , units : "%" }
  variability : { scale : 24*3600 , units : mm/d, min : 0 , max : 1 , delta : 0.05 }

use_cached_proj_fields   : True
write_cached_proj_fields : True
print_statistics         : True

EOF

export hours=06
export PBS_RESSOURCES="-l mem=64g -l vmem=64g -l walltime=${hours:-06}:00:00"
$D/jobs/job_pm.sh $D/notebooks/change_map_4seasons.ipynb fig_SOD_8.15s.yaml $figname $figname
