#!/bin/bash

D=/home/ssenesi/CAMMAC

# Create a working directory specific to this figure. It will hold cached data
figname=$(basename $0)
figname=${figname/.sh/}
mkdir -p $figname
cd $figname

cat <<EOF >fig_SOD_TS2.10.yaml

excluded_models :
   sos   : [ IPSL-CM6A-LR]   # Issue for CDO remap : ssp245 data have variable 'area' without coordinates
   E-P   : [ EC-Earth3-Veg ] # Issue with evspsbl version latest for historical,r4i1p1f1 for tag 20200719d

EOF

hours=18
export PBS_RESSOURCES="-l mem=64g -l vmem=64g -l walltime=${hours:-06}:00:00"
$D/jobs/job_pm.sh $D/notebooks/change_map_1SSP_9vars.ipynb fig_SOD_TS2.10.yaml $figname $figname
#$D/jobs/job_nb.sh $D/notebooks/change_map_1SSP_9vars.ipynb $figname $figname
