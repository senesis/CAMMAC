#!/bin/bash

# Setting up the environment on Ciclad for using CliMAF, IPython NoteBooks
# and colormaps used in CAMMAClib. Environment variable CAMMAC must be set to the CAMMAC location
# It allows to reach some Ncl colormaps

module load ncl/6.6.2 cdo/1.9 netcdf4/4.3.3.1-gfortran TeX-live
#
conda_env=/modfs/ipslfs/dods/jservon/miniconda
CLIMAF=/home/ssenesi/climaf_installs/climaf_running
#CLIMAF=/home/ssenesi/climaf_installs/climaf_V2.0.0
#
export PATH=${conda_env}/envs/analyse_env_2.7/bin:${conda_env}/bin:$CLIMAF/bin:$PATH 
export LD_LIBRARY_PATH=${conda_env}/lib:$LD_LIBRARY_PATH
export PYTHONPATH=$CLIMAF:$PYTHONPATH
#
# Set CliMAF cache
if [[ $HOSTNAME == ciclad*  ]]  
  then export CLIMAF_CACHE=/data/$USER/climafcache
  else export CLIMAF_CACHE=/homedata/$USER/climafcache # e.g. on Camelot
fi
export TMPDIR=$CLIMAF_CACHE
#
# Speed-up Climaf setup (at the expense of not identifying the version of external tools)
#export CLIMAF_CHECK_DEPENDENCIES=no   #no more possible since CliMAF V2

# -- For conversion of Notebooks to PDF
module load TeX-live

# Where to find Ncl AR6 colormaps
export NCARG_COLORMAP_PATH=${CAMMAC?}/data/colormaps:$NCARG_ROOT/lib/ncarg/colormaps

