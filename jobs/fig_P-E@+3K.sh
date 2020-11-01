#!/bin/bash

D=/home/ssenesi/CAMMAC

# Create a working directory specific to this figure. It will hold cached data
figname=$(basename $0)
figname=${figname/.sh/}
mkdir -p $figname
cd $figname


cat <<EOF >fig.yaml
do_test : False
excluded_models : [ ACCESS-ESM1-5, EC-Earth3-Veg, EC-Earth3 ]
field_type : mean

season : ANN
version : ""
figure_name : Fig_P-E@+3C

plot_args : 
  color : AR6_Precip_12s 
  min   : -1
  max   : 1 
  delta : 0.2 
  
  aux_options : "|cnLineThicknessF=5.|cnLineColor=black|gsnContourZeroLineThicknessF=9."

clim_contours : [ -2, 0 , 2 ] # mm/day
clim_contours : [ 0 ] 

warming : 1.5
figure_name : "FigP-E@1.5K"
EOF

$D/jobs/job_pm.sh $D/notebooks/change_map_1var_at_WL_1SSP_with_clim.ipynb fig.yaml $figname $figname

