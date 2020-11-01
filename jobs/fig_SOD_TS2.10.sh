#!/bin/bash

D=/home/ssenesi/CAMMAC

# Create a working directory specific to this figure. It will hold cached data
figname=$(basename $0)
figname=${figname/.sh/}
mkdir -p $figname
cd $figname

cat <<EOF >fig_SOD_TS2.10.yaml

do_test  : False

excluded_models :
   sos   : [ IPSL-CM6A-LR]   # Issue for CDO remap : ssp245,picontrol data have variable 'area' without coordinates
   P-E   : [ EC-Earth3-Veg ] # EC-Earth : Issue with evspsbl version latest for historical,r4i1p1f1 for tag 20200719d
   pr_day: [ EC-Earth3-Veg, EC-Earth3 ] # EC-Earth : Issue with mergetime 

variability_excluded_models :
   sos   : [ IPSL-CM6A-LR]   # Issue for CDO remap : ssp245,picontrol data have variable 'area' without coordinates
   P-E   : [ ACCESS-ESM1-5 ] # ACCESS-ESM1-5 : Pr and evspsbl don't have common period, as of 20200913
   pr_day: [ EC-Earth3-Veg, EC-Earth3 ] # EC-Earth : Issue with mergetime 

use_cached_proj_fields : True

version : "P_E_nr"

EOF

hours=23
export PBS_RESSOURCES="-l mem=64g -l vmem=64g -l walltime=${hours:-06}:00:00"
$D/jobs/job_pm.sh $D/notebooks/change_map_1SSP_9vars.ipynb fig_SOD_TS2.10.yaml $figname $figname
#$D/jobs/job_nb.sh $D/notebooks/change_map_1SSP_9vars.ipynb $figname $figname
