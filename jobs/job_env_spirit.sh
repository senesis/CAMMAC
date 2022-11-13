#!/bin/bash

# Setting up CAMMAC environment on spirit for using CliMAF, IPython
# NoteBooks and colormaps used in CAMMAClib.

# Environment variable CAMMAC should be set; it allows to reach some
# Ncl AR6 colormaps and additionnal user code for notebooks
export NCARG_COLORMAP_PATH=${CAMMAC?}/data/colormaps:$NCARG_ROOT/lib/ncarg/colormaps
export CAMMAC_USER_PYTHON_CODE_DIR=${CAMMAC_USER_PYTHON_CODE_DIR:-$CAMMAC/jobs}

# A given level is needed for some utilities
module load /net/nfs/tools/Users/modulefiles/jservon/climaf/spirit_0

# Tell which Python kernel to use (this because some notebooks may have a
# metadata quoting another version, which mislead Papermill)
KERNEL=python3

PYTHONPATH=$CAMMAC:$PYTHONPATH

# Set CliMAF cache to  a location with large (unsaved) disk space
if [[ $HOSTNAME == spirit*  ]]  
  then export CLIMAF_CACHE=/scratchu/$USER/climafcache3
  else export CLIMAF_CACHE=/homedata/$USER/climafcache # e.g. on Camelot
fi
export TMPDIR=$CLIMAF_CACHE
#
