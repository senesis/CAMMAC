#!/bin/bash

# Setting up CAMMAC environment on Ciclad for using CliMAF, IPython NoteBooks
# and colormaps used in CAMMAClib.

# Environment variable CAMMAC should be set; it allows to reach some
# Ncl AR6 colormaps
export NCARG_COLORMAP_PATH=${CAMMAC?}/data/colormaps:$NCARG_ROOT/lib/ncarg/colormaps

# A given level is needed for some utilities
module load ncl/6.6.2 cdo/1.9 netcdf4/4.3.3.1-gfortran 
#
# Set the PATH for Jupyter, and its Python, and other required softwares
conda_env=/modfs/modtools/miniconda2
export PATH=${conda_env}/envs/analyse_2.7/bin:${conda_env}/bin:$PATH

# Prepend library path similarly for that Python
export LD_LIBRARY_PATH=${conda_env}/lib:$LD_LIBRARY_PATH

# Handle CLIMAF
export CLIMAF=${CLIMAF?"Must set it to a directory holding CLiMAF > 2.0.0"}
PYTHONPATH=$CLIMAF:$PYTHONPATH

# Set CliMAF cache to  a location with large (unsaved) disk space
if [[ $HOSTNAME == ciclad*  ]]  
  then export CLIMAF_CACHE=/data/$USER/climafcache
  else export CLIMAF_CACHE=/homedata/$USER/climafcache # e.g. on Camelot
fi
export TMPDIR=$CLIMAF_CACHE
#
# -- For conversion of Notebooks to PDF
module load TeX-live


