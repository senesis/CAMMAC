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
	data_versions_tag : 20200918_plus_derived
#	version         : "_plus_KACE"
	output_option   : "add_to_input"
	
#	included_models : { "ssp126" : "KACE-1-0-G",  "ssp245" : "KACE-1-0-G",  "ssp585" : "KACE-1-0-G",  "historical" : "KACE-1-0-G" }
#	excluded_models : {}
#	periods         : { "historical" : "1850-2014", "ssp126" : "2015-2100", "ssp245" : "2015-2100", "ssp585" : "2015-2100" }


EOF

hours=70 $D/jobs/job_pm.sh $D/select_data_versions/create_yearly_stat_of_daily_pr.ipynb param.yaml $jobname $output
