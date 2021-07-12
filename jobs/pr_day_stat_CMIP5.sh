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
cat <<-"EOF" >param.yaml
	
	do_test           : False
	project           : CMIP5
	data_versions_dir : /home/ssenesi/CAMMAC/select_data_versions
	data_versions_tag : CMIP5_20210626
	version           : ""
	output_option     : add_to_input
	output_pattern    : '/data/ssenesi/CMIP5_derived_variables/${variable}/${variable}_${table}_${model}_${experiment}_${realization}_${version}_${PERIOD}.nc'
	periods :
	    historical : "1850-2005"
	    rcp26     : "2006-2100"
	    rcp45     : "2006-2100"
	    rcp85     : "2006-2100"
	    piControl  : null

EOF

hours=60 $CAMMAC/jobs/job_pm.sh $CAMMAC/select_data_versions/create_derived_variable.ipynb param.yaml $jobname $output
