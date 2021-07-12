#!/bin/bash

CAMMAC=${CAMMAC:-/data/ssenesi/CAMMAC}
export CAMMAC=$(cd $CAMMAC; pwd)

# Create a working directory specific to this script. 
scriptname=$(basename $0)
scriptname=${scriptname/.sh/}

mkdir -p $scriptname
cd $scriptname

# Create input parameters file 
cat <<"EOF" >param.yaml

do_test             : False

project             : CMIP5
data_versions_dir   : /home/ssenesi/CAMMAC/select_data_versions
data_versions_tag   : "CMIP5_20210626"

experiments         : [ piControl , historical , rcp26 , rcp45 , rcp85 ]

variables           : 
     Amon : [ pr , tas , prw , evspsbl ]
     Lmon : [ mrro , mrso , mrsos ]
     Omon : [ sos ]
     day  : [ pr ]

piControl_minimum_duration : 200

periods   :
    historical : "1850-2005"
    rcp26     : "2006-2099" 
    rcp45     : "2006-2099"  
    rcp85     : "2006-2099"  
    piControl  : "*"

preferred_grids  : null

EOF

# Launch a job in which papermill will execute the notebook, injecting above parameters 
jobname=$scriptname
output=$scriptname
# Tell job_pm.sh to use co-located environment setting
export ENV_PM=$(cd $(dirname $0); pwd)/job_env.sh

# Tell job_pm.sh to use co-located parameters file 
commons=$(cd $(dirname $0); pwd)/common_parameters.yaml
[ ! -f $commons ] && $commons = ""

hours=23 $CAMMAC/jobs/job_pm.sh $CAMMAC/select_data_versions/data_selection.ipynb param.yaml $jobname $output $commons
