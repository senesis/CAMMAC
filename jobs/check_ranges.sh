#!/bin/bash

CAMMAC=${CAMMAC:-/data/ssenesi/CAMMAC}
export CAMMAC=$(cd $CAMMAC; pwd)

# Create a working directory specific to this figure. It will hold cached data and figures
bname=$(basename $0)
bname=${bname/.sh/}
dirname=$bname
mkdir -p $dirname
cd $dirname

jobname=$bname
output=$bname


# Create input parameters file 
cat <<-EOF >param.yaml
	
experiments : [ historical, ssp126, ssp245, ssp585 ] 

variables : 
    Amon: [ pr, tas, prw, evspsbl ]
    Lmon: [ mrro, mrso, mrsos ]
    Omon: [ sos ]

fld_stats : [ "fldpctl,5", "fldpctl,50", "fldpctl,95" ]
tim_stats : [ timmean ]

excluded_models     : []
included_models     : null   

data_versions_tag  : 20210201

do_test : False

EOF
hours=23 $CAMMAC/jobs/job_pm.sh $CAMMAC/select_data_versions/Check_ranges.ipynb param.yaml $jobname $output
