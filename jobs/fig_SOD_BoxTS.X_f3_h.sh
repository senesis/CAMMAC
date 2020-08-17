#!/bin/bash

D=/home/ssenesi/CAMMAC

# Create a working sub-directory specific to this figure. It will hold cached data
figname=$(basename $0)
figname=${figname/.sh/}
wdir=${figname/_figure}
mkdir -p $wdir
cd $wdir


# Create input parameters file 
cat <<EOF >fig.yaml
figure_name : fig_SOD_BoxTS.X_f3_h
input_dir : /data/ssenesi/prod/fig_SOD_8.16/changes

version         : "_without_CAMS-CSM1-0"
excluded_models : [ CAMS-CSM1-0 ]

EOF

jobname=$figname
output=$figname
$D/jobs/job_pm.sh $D/notebooks/change_hybrid_seasons_figure2.ipynb fig.yaml $jobname $output
