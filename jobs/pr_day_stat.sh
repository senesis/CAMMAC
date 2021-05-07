#!/bin/bash

CAMMAC=${CAMMAC:-/data/ssenesi/CAMMAC}
export CAMMAC=$(cd $CAMMAC; pwd)

# Create a working directory specific to this job
bname=$(basename $0)
bname=${bname/.sh/}
dirname=$bname
mkdir -p $dirname
cd $dirname

jobname=$bname
output=$bname


# Create input parameters file 
cat <<-EOF >param.yaml
	
	do_test         : False 
	data_versions_tag : "20210201"
	version         : "_derived"
	output_option   : "add_to_input"
	
#	included_models : { "ssp126" : "KACE-1-0-G",  "ssp245" : "KACE-1-0-G",  "ssp585" : "KACE-1-0-G",  "historical" : "KACE-1-0-G" }
#	excluded_models : { "ssp585" : "EC-Earth3-Veg" }
#	periods         : { "historical" : "1850-2014", "ssp126" : "2015-2100", "ssp245" : "2015-2100", "ssp585" : "2015-2100" }


EOF

hours=70 $CAMMAC/jobs/job_pm.sh $CAMMAC/select_data_versions/create_derived_variable.ipynb param.yaml $jobname $output
