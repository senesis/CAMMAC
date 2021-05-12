#!/bin/bash

# Setting up CAMMAC environment on Ciclad for using CliMAF, IPython
# NoteBooks and colormaps used in CAMMAClib.

# Environment variable CAMMAC should be set; it allows to reach some
# Ncl AR6 colormaps and additionnal user code for notebooks
export NCARG_COLORMAP_PATH=${CAMMAC?}/data/colormaps:$NCARG_ROOT/lib/ncarg/colormaps
export CAMMAC_USER_PYTHON_CODE_DIR=${CAMMAC_USER_PYTHON_CODE_DIR:-$CAMMAC/jobs}

# A given level is needed for some utilities
module load ncl/6.6.2 cdo/1.9 netcdf4/4.3.3.1-gfortran 
#
# Set the PATH for Jupyter, and its Python, and other required softwares
conda_env=/modfs/modtools/miniconda2
export PATH=${conda_env}/envs/analyse_2.7/bin:${conda_env}/bin:$PATH

# Tell which Python kernel to use (this because some notebooks may have a
# metadata quoting another version, which mislead Papermill)
KERNEL=python2

# Prepend library path similarly for Python 
export LD_LIBRARY_PATH=${conda_env}/lib:$LD_LIBRARY_PATH

# Handle CLIMAF and CAMMAC in PYTHONPATH 
export CLIMAF=${CLIMAF?"Must set it to a directory holding CLiMAF > 2.0.0"}
# Putting CLIMAF in PYTHONPATH is superfluous if CLIMAF has been set using 'load module'
PYTHONPATH=$CLIMAF:$CAMMAC:$PYTHONPATH

# Set CliMAF cache to  a location with large (unsaved) disk space
if [[ $HOSTNAME == ciclad*  ]]  
  then export CLIMAF_CACHE=/scratchu/$USER/climafcache
  else export CLIMAF_CACHE=/homedata/$USER/climafcache # e.g. on Camelot
fi
export TMPDIR=$CLIMAF_CACHE
#
# -- For conversion of Notebooks to PDF
module load TeX-live


