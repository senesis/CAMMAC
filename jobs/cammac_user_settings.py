# This file hosts a number of settings for CAMMAC which are common to
# a number of scripts/applications .... and which must be under the
# control of the user

# Here, we fix a number of errors for CMIP6 data for some models; and we define a variable P-E,
# we tell where additional fixed fields are stored
# and we tell CliMAF if we have a repository for derived CMIP6 data

# We need that two variables be set :
# - default_fixed_fields_dir (can be anything if not used)
# - derived_variables_pattern (can be None)

import climaf
from climaf.api import *

# Fix some model errors
calias('CMIP6','evspsbl',scale=-1,\
       conditions={"model":["CAMS-CSM1-0","EC-Earth3","EC-Earth3-Veg","EC-Earth3-LR","EC-Earth3-Veg-LR"]})
calias('CMIP6','pr',scale=1000.,conditions={"model" : "CIESM"})
calias('CMIP6','mrso',scale=1000.,conditions={"model" : "CIESM"})
calias('CMIP6','mrsos',scale=100.,conditions={"model" : "FGOALS-f3-L"})

# Define P-E for CMIP6 variables
derive('CMIP6', 'P-E','minus','pr','evspsbl')
derive('CMIP5', 'P-E','minus','pr','evspsbl')

# Define location of fixed fields
dataloc(project='CMIP6', organization='generic',
        url=default_fixed_fields_dir+"/${variable}_${table}_${model}_*_*${grid}.nc")
dataloc(project='CMIP5', organization='generic',
        url=default_fixed_fields_dir+"/${variable}_${table}_${model}_*.nc")

# Define location of derived variables if needed (e.g. yearly stats of daily precip)
if derived_variables_pattern is not None :
    climaf.dataloc.dataloc(project='CMIP6', organization='generic', 
                           url=derived_variables_pattern, table=derived_variable_table)
    climaf.dataloc.dataloc(project='CMIP5', organization='generic', 
                           url=derived_variables_pattern, table=derived_variable_table)

