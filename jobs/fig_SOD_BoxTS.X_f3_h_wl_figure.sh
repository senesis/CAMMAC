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

input_dir : /data/ssenesi/prod/fig_SOD_BoxTS.X_f3_h_wl/changes

version             : tropics_ann_ssp5
title               : "Hydrological variables change over tropical land"
figure_name         : fig_SOD_BoxTS.X_f3_h_tropics_5vars

#combined_seasons    : [ land_annual ]
combined_seasons    : [ tropics_annual ]
max_warming_level   : 5.
min_models_nb       : 7
scenarios           : [ ssp585 ]
excluded_models     : [ CAMS-CSM1-0 ]

only_warmer_CI      : True  
show_variability_CI : True
show_mean_CI        : True
show_tas_CI         : False
plot_intermediate_CIs : False

variables   : [  [pr,mean],  [mrro,mean], [pr,std], [mrro,std], [prw,mean]]
xy_ranges   : [ 1.5, 6.9, -9.0, 40.0 ]
yaxis_title : "% change"

EOF

jobname=$figname
output=$figname
$D/jobs/job_pm.sh $D/notebooks/change_hybrid_seasons_dT_figure.ipynb fig.yaml $jobname $output
