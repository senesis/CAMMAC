#!/bin/bash

D=/home/ssenesi/CAMMAC

# Create a working directory specific to this figure, based on script name.
# It will hold cached data

figname=$(basename $0)
figname=${figname/.sh/}
mkdir -p $figname
cd $figname

cat <<EOF >fig_SOD_8.27.yaml

compute_basins : [ Amazon , Lena, Yangtze , Mississippi, Danube, Niger, Euphrates, Indus, Nile, Parana, Amu-Darya, Mackenzie, "Lake Eyre" ]

variables: 
  - [ mrro , Lmon, mean ]
  - [ mrro , Lmon, std ]

do_test    : False
do_compute : True

do_plot : True
#plot_basins : [ Amazon , Yangtze, Lena , Mississippi, Euphrates, Niger ] 
#plot_basins : [ Amazon , Yangtze, Euphrates  ] 

plot_basins : [ Indus, Nile, Parana, Amu-Darya, Mackenzie, "Lake Eyre" ]
version : 6more

EOF


hours="23" $D/jobs/job_pm.sh $D/notebooks/change_rate_basins.ipynb fig_SOD_8.27.yaml $figname $figname


#ncl -Q /home/ssenesi/CAMMAC/notebooks/change_rate_basins_6means.ncl ' input_file = "change_rate_basins_data.nc"' ' figfile    = "./figures/rate_of_change_per_basin_vs_1850-1900_20200918"' ' names = (/"mean",""/)' ' name  = "mean"' ' title = "Rate of change in basin-scale runoff mean "' ' xtitle = "Warming above 1850-1900, from 1901 to 2100"' ' ytitle = "Change in basin-averaged mean  of runoff, vs 1850-1900 (%) ~Z75~~C~(29 models ensemble mean, 5 and 95 percentiles)"' ' vars = (/"mrro_mean", "mrro_std"/)' ' var  = "mrro_mean"' ' basins = (/"Indus", "Nile", "Parana", "Amu-Darya", "Mackenzie", "Lake Eyre"/)' ' experiments_labels = (/"SSP5-8.5", "SSP2-4.5", "SSP1-2.6"/)' ' xmin = 0.0' ' xmax = 5.15' 'yminmax=(/(/-45,110/),(/-100,180/),(/-40.,70./),(/-40,80/),(/-10,50/),(/-90,170/) /) '
