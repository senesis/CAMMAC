#!/bin/bash

DEFAULT_PBS_RESSOURCES="--mem-per-cpu=32G  --time=240 "

usage="""
  $(basename $0) NOTEBOOK PARAMETERS_FILE JOBNAME OUTPUT COMMON_PARAMS

  Launch with 'sbatch' a job which executes NOTEBOOK using 'papermill' 
  (https://papermill.readthedocs.io). 

  Thanks to papermill, the executed notebook will take into account the settings read 
  in PARAMETERS_FILE (which must be in Yaml syntax). This file is optional. An example 
  of parameter file content shows below (after 'exit'). 

  Another parametesr setting file is pre-pended :
  common_parameters.yaml, either the one in the current working
  directory, or if missing the one designated by 5th arg
  COMMON_PARAMS, or if missing the one colocated with this script.

  Environement variable CAMMAC_USER_PYTHON_CODE_DIR is set to this
  script's directory if not already set

  Default value for JOBNAME is notebook's basename. Job submission uses environment 
  variable PBS_RESSOURCES, which defaults to :
          $DEFAULT_PBS_RESSOURCES

  The result of execution is shown in notebook OUTPUT, which name defaults to a combination
  of args NOTEBOOK and PARAMETERS_FILE

  Execution occurs in current directory, its environment is set by sourcing the file
  designated by environment variable ENV_PM (please provide a full path), or by default 
  colocated file job_env.sh

"""

#set -x
notebook=$1  
params=$2
jobname=$3
output=$4
commons=$5

# Current directory
here=$(pwd)

# Directory for the notebook to execute
nbdir=$(cd $(dirname $notebook) ; pwd)
notebook=$(basename $notebook)

# Directory of this script
this_script_dir=$(cd $(dirname $0) ; pwd)

# Unless set, assume CAMMAC top is parent dir
CAMMAC=${CAMMAC:-$(dirname $this_script_dir)}

[ -z $jobname ] && jobname=${notebook/.ipynb/}

if [ "$params" ];
then bparams=$(basename $params)
else bparams=noparams ; fi

[ -z $output ]   && output=${notebook/.ipynb}_${bparams/.yaml/}.ipynb
# Remove ipynb extension for output (if any)
output=${output/.ipynb/}

# Use local file common_parameters if it exists, otherwise colocated one
if [ -f commons_parameters.yaml ] ; then
    commons=commons_parameters.yaml
else
    if [ -z $commons ] ; then 
	commons=$this_script_dir/common_parameters.yaml
    fi
fi

fparams=$here/tmp_${bparams}_common.yaml
cat $commons $params > $fparams
params="--parameters_file $fparams"

ENV_PM=${ENV_PM:-$this_script_dir/job_env.sh}

# Launch  job
sbatch --export=ALL ${PBS_RESSOURCES:-${DEFAULT_PBS_RESSOURCES}} --job_name $jobname <<-EOF
	cd $here
	export CAMMAC=$CAMMAC
	KERNEL=
	. $ENV_PM  # this sets KERNEL
	echo KERNEL=\$KERNEL
	export CAMMAC_USER_PYTHON_CODE_DIR=${CAMMAC_USER_PYTHON_CODE_DIR:-$this_script_dir}
	papermill $params $nbdir/$notebook ${output}_\${PBS_JOBID}.ipynb -k \$KERNEL
	rm $fparams
	EOF

date
echo "Execution flow will show in $here/${output}_<jobid>.ipynb"



exit



# Example of Yaml-syntax for a parameter file content
#####################################################

# Commented lines show Python equivalent for the yaml syntax that follows immediately

# experiments = ["ssp126", "ssp245", "ssp585"]
experiments: [ssp126, ssp245, ssp585]

# variability_sampling_args= { "house_keeping": True, "compute": True, "detrend": True, "shift": 100 }
variability_sampling_args:
   house_keeping: True
   compute: True
   detrend: True
   shift: 100

# a_string="a_string"
a_string: string

# If you want a number as a string
another_string: "1"

# excluded_modles=None
excluded_models : null 
