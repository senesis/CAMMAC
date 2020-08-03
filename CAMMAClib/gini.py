"""
Script gini computes Gini index on the time series of its (NetCDF format) input file, 
which is assumed to be single-variable, and write it in NetCDF output file

Usage : gini file_in file_out
"""

import xarray as xr
import numpy as np
import sys


def gini_da(da,axis_name="time") : #da is a DataArray
    axis_num=da.get_axis_num(axis_name)
    da_sorted=da.copy(data=np.apply_along_axis(np.sort,axis_num,da))
    rank=xr.DataArray(np.arange(1,da.coords[axis_name].size+1), name="rank",dims=axis_name)
    product=da_sorted*rank
    n=np.float(rank.size)
    val= (2.* product.sum(dim=axis_name) / ( n * da_sorted.sum(dim=axis_name))) - (n+1)/n  
    val.name="gini(%s)"%da.name
    return val


def my_time_reduce(ds,func,varname,**args) :
    """ 
    Apply time-reducing function FUNC (with ARGS) to dataset DS, producing 
    variable VARNAME. Handle time bounds (but not yet central time coordinate) 

    DS should be a Dataset with only one variable (except coord related variables)
    FUNC should be a function which aggregate the variable over time
    VARNAME is the varible name for output variable
    """
    allvars= [ var for var in ds.keys() if "_bnds" not in var ]
    if len(allvars) > 1 :
        raise ValueError("Too many vars : %s"%allvars)
    var=allvars[0]
    #
    out = xr.Dataset()
    out.attrs=ds.attrs
    if "variable_id" in ds.attrs :
        out.attrs["variable_id"]="gini(%s)"%ds.attrs["variable_id"]
    #
    for v in [ "lat_bnds","lon_bnds"] :
        if v in ds :
            out[v]=ds[v]
    #
    # Compute time instant in the middle of input time period
    t=ds["time"]
    out.assign_coords(time=("time",t.isel(time=[t.size/2]).data))
    # 
    if "time_bnds" in ds :
        out["time_bnds"]   =ds["time_bnds"].isel(time=0)
        out["time_bnds"][1]=ds["time_bnds"].isel(time=-1)[1]
    #
    out[varname]=func(ds[var],**args)
    return out

#f="~/dev/tas_year.nc"

file_in=sys.argv[1]
file_out=sys.argv[2]
ds=xr.open_dataset(file_in).load()
ga=my_time_reduce(ds,gini_da,"gini")
ga.to_netcdf(file_out)
