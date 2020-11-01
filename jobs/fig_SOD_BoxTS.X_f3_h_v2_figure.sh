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
figure_name : fig_SOD_BoxTS.X_f3_h_v2

input_dir : /data/ssenesi/prod/fig_SOD_BoxTS.X_f3_h_v2/changes

version             : land_ann_ssp5
combined_seasons    : [ land_annual ]
scenario            :  ssp585 
excluded_models     : [ CAMS-CSM1-0 ]
only_warmer_CI      : True  
show_variability_CI : False

variables : [  [pr,mean],  [mrro,mean], [pr,std], [mrro,std], [prw,mean]]
xy_ranges : [ 1.5 ,5.8,-5.,45. ]

EOF

jobname=$figname
output=$figname
$D/jobs/job_pm.sh $D/notebooks/change_hybrid_seasons_figure2.ipynb fig.yaml $jobname $output
