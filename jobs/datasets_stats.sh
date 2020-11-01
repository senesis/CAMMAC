#!/bin/bash

D=/home/ssenesi/CAMMAC

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

EOF


hours="23" $D/jobs/job_pm.sh $D/select_data_versions/Chek_ESGF_lists_on_bdd.ipynb fig.yaml datasets_stats 
