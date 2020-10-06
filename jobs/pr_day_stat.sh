#!/bin/bash

D=/home/ssenesi/CAMMAC

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
	
	do_test         : False 
	version         : "_plus_derived"
	output_option   : "add_to_input"
	
	excluded_models : {}
	#periods : {"ssp126" : "2015-2016" }
EOF

hours=70 $D/jobs/job_pm.sh $D/select_data_versions/create_yearly_stat_of_daily_pr.ipynb param.yaml $jobname $output
