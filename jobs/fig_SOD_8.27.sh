#!/bin/bash

D=/home/ssenesi/CAMMAC

# Create a working directory specific to this figure, based on script name.
# It will hold cached data

figname=$(basename $0)
figname=${figname/.sh/}
mkdir -p $figname
cd $figname

cat <<EOF >fig_SOD_8.27.yaml

compute_basins : [ Amazon , Lena, Yangtze , Mississippi, Danube, Niger ]

variables: 
  - [ mrro , Lmon, mean ]
  - [ mrro , Lmon, std ]

do_test    : False
do_compute : false

do_plot : True
plot_basins : [ Amazon , Yangtze, Lena  ]


EOF


hours="23" $D/jobs/job_pm.sh $D/notebooks/change_rate_basins.ipynb fig_SOD_8.27.yaml $figname $figname
