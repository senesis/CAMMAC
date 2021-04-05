#!/bin/bash

D=${CAMMAC:-/home/ssenesi/CAMMAC}

# Create a working directory specific to this script. 
scriptname=$(basename $0)
scriptname=${scriptname/.sh/}

mkdir -p $scriptname
cd $scriptname

# Create input parameters file 
cat <<"EOF" >param.yaml

do_test             : False

data_versions_dir   : /home/ssenesi/CAMMAC/select_data_versions
data_versions_tag   : "20210201"

experiments         : [ piControl , historical , ssp126 , ssp245 , ssp585 , ssp119, ssp370 ]

variables           : 
     Amon : [ pr , tas , prw , evspsbl ]
     Lmon : [ mrro , mrso , mrsos ]
     Omon : [ sos ]
     day  : [ pr ]

#experiments         : [ piControl , historical , ssp370 ]
#variables           : 
#     Amon : [ pr  ]

piControl_minimum_duration : 200

preferred_grids  : 
  CESM2-WACCM     : gn 
  CESM2-WACCM-FV  : gn 
  CESM2-WACCM-FV2 : gn 
  CESM2-FV2       : gn 
  CESM2           : gn 
  CNRM-CM6-1      : gr1 
  CNRM-ESM2-1     : gr1 
  GFDL-ESM4       : gn 
  GFDL-CM4        : [ gn , gr1 ] 
  IPSL-CM6A-LR    : gr1 
  MIROC-ES2L      : gr1
  MRI-ESM2-0      : gn 

EOF

# Launch a job in which papermill will execute the notebook, injecting above parameters 
jobname=$scriptname
output=$scriptname
# Tell job_pm.sh to use co-located environment setting
export ENV_PM=$(cd $(dirname $0); pwd)/job_env.sh

# Tell job_pm.sh to use co-located parameters file 
commons=$(cd $(dirname $0); pwd)/common_parameters.yaml
[ ! -f $commons ] && $commons = ""

hours=23 $D/jobs/job_pm.sh $D/select_data_versions/data_selection.ipynb param.yaml $jobname $output $commons
