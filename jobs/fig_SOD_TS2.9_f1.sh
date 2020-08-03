#!/bin/bash

D=/home/ssenesi/CAMMAC

# Create a working directory specific to this figure. It will hold cached data
figname=$(basename $0)
figname=${figname/.sh/}
mkdir -p $figname
cd $figname


# No need to change nb parameters 


hours=12
export PBS_RESSOURCES="-l mem=64g -l vmem=64g -l walltime=${hours:-06}:00:00"
$D/jobs/job_pm.sh $D/notebooks/change_map_3SSPs_3horizons.ipynb "" $figname $figname
