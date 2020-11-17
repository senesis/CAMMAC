#!/bin/bash

# Setting up CAMMAC environment on Ciclad for using CliMAF, IPython NoteBooks
# and colormaps used in CAMMAClib.

# Environment variable CAMMAC must be set to the CAMMAC location
# It allows to reach some Ncl colormaps

module load ncl/6.6.2 cdo/1.9 netcdf4/4.3.3.1-gfortran 
#
conda_env=/modfs/modtools/miniconda2
CLIMAF=/home/ssenesi/climaf_installs/climaf_running
#
export PATH=${conda_env}/envs/analyse_2.7/bin:${conda_env}/bin:$CLIMAF/bin:$PATH 
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
# -- For conversion of Notebooks to PDF
module load TeX-live

# Where to find Ncl AR6 colormaps
export NCARG_COLORMAP_PATH=${CAMMAC?}/data/colormaps:$NCARG_ROOT/lib/ncarg/colormaps

