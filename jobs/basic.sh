#!/bin/bash

CAMMAC=${CAMMAC:-/data/ssenesi/CAMMAC}
export CAMMAC=$(cd $CAMMAC; pwd)

ssp=${1:-ssp245}
season=${2:-DJF}
scheme=${3:-KS} # Can also be AR6S
threshold=${4:-0.9}
variable=${5:-pr}
		       

# Create a working directory specific to this figure. It will hold cached data and figures
figname=$(basename $0)
figname=${figname/.sh/}
figname=${figname}_${variable}_${ssp}_${season}_${scheme}_${threshold}
mkdir -p $figname
cd $figname

# Create input parameters file 
cat <<EOF >fig.yaml

do_test : False
scheme                 : ${scheme}
version                : ""
#
variable               : ${variable}
threshold              : ${threshold}
table                  : Amon
figure_mask            : null 

included_models        : null 
excluded_models        : [ ]
#
season                 : $season
experiment             : $ssp 
proj_period            : "2081-2100"
ref_experiment         : historical
ref_period             : "1995-2014"  
#
common_grid            : "r360x180"

EOF

# Launch a job in which papermill will execute the notebook, injecting above parameters
jobname=$figname
output=$figname

# Provide location for environment setting
export CAMMAC=$(cd $CAMMAC; pwd)
export ENV_PM=$CAMMAC/jobs/job_env.sh

# Tell job_pm.sh to use reference parameters file 
commons=$CAMMAC/jobs/common_parameters.yaml
[ ! -f $commons ] && $commons = ""

hours=2 $CAMMAC/jobs/job_pm.sh $CAMMAC/notebooks/basic.ipynb fig.yaml $jobname $output $commons
