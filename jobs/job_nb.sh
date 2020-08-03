#!/bin/bash

DEFAULT_PBS_RESSOURCES="-l mem=16g -l vmem=32g -l walltime=${hours:-06}:00:00"

notebook=$1
jobname=$2
output=$3

here=$(pwd)
nbdir=$(cd $(dirname $notebook) ; pwd)
notebook=$(basename $notebook)
this=$(cd $(dirname $0) ; pwd)

ENV_PM=${ENV_PM:-$this/job_env.sh}

# Use newest Notebook if none specified
if [ -z $notebook ] ; then
    notebook=$(ls -rt *pynb | tail -n 1)
    echo "Launching Notebook : $notebook"
fi
[ -z $jobname ] && jobname=${notebook/.ipynb/}
[ -z $output  ] && output=${notebook/.ipynb/.html}
# Remove ipynb extension for output (if any)
output=${output/.ipynb/}
					     
qsub -V ${PBS_RESSOURCES:-${DEFAULT_PBS_RESSOURCES}} -j eo -N $jobname <<-EOF
	cd $here
	export CAMMAC=$(dirname $this)
	. $ENV_PM
	jupyter nbconvert --to html $nbdir/${notebook} --output $output --execute \
		--ExecutePreprocessor.timeout=None --ExecutePreprocessor.startup_timeout=300
EOF
date

