#!/bin/bash

CAMMAC=${CAMMAC:-/data/ssenesi/CAMMAC}
export CAMMAC=$(cd $CAMMAC; pwd)

# Create a working directory specific to this job
dir=$(basename $0)
dir=${dir/.sh/}
mkdir -p $dir
cd $dir

cat <<EOF >fig.yaml
do_test : False

experiments  :  [ piControl, historical,ssp126, ssp245, ssp585, ssp119 ]

variables    :
    Amon: [ pr, tas, prw, evspsbl ]
    Lmon: [ mrro, mrso, mrsos ]
    Omon: [ sos ]
    day : [ pr ]

node : esgf-node.ipsl.upmc.fr
#esgf-node.jpl.nasa.gov

EOF


hours="23" $CAMMAC/jobs/job_pm.sh $CAMMAC/select_data_versions/Chek_ESGF_lists_on_bdd.ipynb fig.yaml datasets_stats 
