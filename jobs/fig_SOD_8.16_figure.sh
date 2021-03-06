#!/bin/bash

D=/home/ssenesi/CAMMAC

# Create a working sub-directory specific to this figure. It will hold cached data
figname=$(basename $0)
figname=${figname/.sh/}
wdir=${figname/_figure}
mkdir -p $wdir
cd $wdir


# Create input parameters file 
cat <<EOF >fig_SOD_8.16_figure.yaml
input_dir : /data/ssenesi/prod/fig_SOD_8.16/changes
EOF

jobname=$figname
output=$figname
$D/jobs/job_pm.sh $D/notebooks/change_hybrid_seasons_figure.ipynb fig_SOD_8.16_figure.yaml $jobname $output
