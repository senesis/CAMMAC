#!/bin/bash

# For ploting other basins, assuming computation did occur upstream

D=/home/ssenesi/CAMMAC

# Create a working directory specific to this figure, based on script name.
# It will hold cached data

bname=$(basename $0)
bname=${bname/.sh/}
dname=${bname/_alt/}
mkdir -p $dname
cd $dname

cat <<EOF >fig_SOD_8.27.yaml

plot_version : alt

plot_basins : [ Mississippi, Danube, Niger ]

variables: 
  - [ mrro , Lmon, mean ]
  - [ mrro , Lmon, std ]

do_compute : False
do_plot    : True

EOF


hours="23" $D/jobs/job_pm.sh $D/notebooks/change_rate_basins.ipynb fig_SOD_8.27.yaml $bname $bname

# Pour ajuster les graphes : 
# ncl -Q /home/ssenesi/CAMMAC/notebooks/change_rate_basins.ncl ' input_file = "change_rate_basins_data.nc"' ' figfile    = "./figures/rate_of_change_per_basin_vs_1850-1900_20200918alt"' ' names = (/"mean","variability"/)' ' title = "Rate of change in basin-scale runoff mean and variability"' ' xtitle = "Warming above 1850-1900, from 1901 to 2100"' ' ytitle = "Change in basin-averaged mean and variability of runoff, vs 1850-1900 (%) ~Z75~~C~(19 models ensemble mean, 5 and 95 percentiles)"' ' vars = (/"mrro_mean", "mrro_std"/)' ' basins = (/"Danube", "Mississippi",  "Niger"/)' ' experiments_labels = (/"SSP5-8.5", "SSP2-4.5", "SSP1-2.6"/)' ' xmin = 0.0' ' xmax = 5.05' 'yminmax = (/(/(/-30,40/),(/-50.,80./)/), (/(/-40,30/),(/-50.,60./)/), (/(/-70,150/),(/-50.,130./)/)  /) '
