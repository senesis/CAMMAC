"""
Implement the Knutti and Sedlacek robustness scheme (DOI: 10.1038/NCLIMATE1716)

Interface is tuned for use in CliMAF : 
  * first and second arguments are whitespace separated strings, each providing 
    a list of NetCDF filenames  :
     - one for the ensemble of reference fields  (each e.g. a yearly mean time series)
     - one for the ensemble of projection fields (id)
  * last argument is output filename
  * input fields are supposed to have a single variable

Input fields are supposed to be already re-mapped on the same grid. 
Input ensembles must be of the same size 

This is a wrapper around a code provided by Benjamin Cook (NCAR), for use in CliMAF

"""
from __future__  import division, print_function 

import xarray as xr
import numpy as np
import sys

def KandS(allmods_hist, allmods_fut, names) :
    """
    Compute Knutti robustness index on DataArrays 
    allmods_hist : list of reference  time series DataArrays 
    allmods_fut  : list of projection time series DataArrays 

    Based on a code provided by Benjamin Cook (NCAR)
    """

    lat=allmods_hist[0].lat
    lon=allmods_hist[0].lon
    time_size=allmods_hist[0].time.size
    ens_size=len(allmods_hist)

    models_in_error=[]
    for f,n in zip(allmods_fut,names) :
        if f.time.size != time_size :
            models_in_error.append(n)
        print("%30s %3d %3d %3d"%(n,f.lat.size, f.lon.size, f.time.size), np.asarray(f).shape)

    if len(models_in_error) !=0 :
        print("There are various shaeps for input data : ",{ f.shape for f in allmods_fut })
        print("These models doesn't have the right time size(%d)"%time_size,models_in_error)
        raise ValueError("These models doesn't have the right time size(%d)"%time_size,models_in_error))
        
    models_in_error=[]
    for f,n in zip(allmods_hist,names) :
        if f.time.size != time_size :
            models_in_error.append(n)
        print("%30s %3d %3d %3d"%(n,f.lat.size, f.lon.size, f.time.size), np.asarray(f).shape)

    if len(models_in_error) !=0 :
        print("There are various shaeps for input data : ",{ f.shape for f in allmods_hist })
        print("These models doesn't have the right time size(%d)"%time_size,models_in_error)
        raise ValueError("These models doesn't have the right time size(%d)"%time_size,models_in_error))

    # Array to store robustness metric
    Rrob = np.zeros((lat.size,lon.size))*np.nan
    
    # For CDF histograms for robustness calculation
    num_bins = 1000
    
    # Reshape arrays to separate out models. Dimensions on these arrays will be: models x yrs x lat x lon
    allmods_hist_rob = np.ma.stack(allmods_hist) 
    allmods_fut_rob = np.ma.stack(allmods_fut) 
    
    # Loop Through each grid cell and calculate the robustness metric
    for n_lat in enumerate(lat):
        for n_lon in enumerate(lon):
            
            # A1 Calculation (based on MME and full ensemble DIFFERENCES)-----------------------------------------------------------------
            
            # difference, full ensemble
            currcell_allmods = np.ma.masked_array.flatten(allmods_fut_rob[:,:,n_lat[0],n_lon[0]]-allmods_hist_rob[:,:,n_lat[0],n_lon[0]])
            
            # difference, MME
            currcell_mme = np.ma.mean( (allmods_fut_rob[:,:,n_lat[0],n_lon[0]]-allmods_hist_rob[:,:,n_lat[0],n_lon[0]]),axis=0 )

            if np.isnan(np.min(currcell_allmods)) or np.isnan(np.max(currcell_allmods)) :
                Rrob[n_lat[0],n_lon[0]] = np.nan
                continue

            # Create normalized CDFs
            # ensemble
            counts, bin_edges = np.histogram(currcell_allmods, bins=num_bins, density=True)
            cdf_ens = np.cumsum(counts)
            cdf_ens_norm = cdf_ens/cdf_ens[-1]
            # mme
            counts, bin_edges = np.histogram(currcell_mme, bins=num_bins, range=(np.min(bin_edges),np.max(bin_edges)), density=True)
            cdf_mme = np.cumsum(counts)
            cdf_mme_norm = cdf_mme/cdf_mme[-1]
            
            # Calculate A1
            a1=np.sum((cdf_ens_norm-cdf_mme_norm)**2)
            
            
            # A2 Calculation----------------------------------------------------------------------------------------------------------
            # MME, historical
            currcell_mme_hist = np.ma.masked_array.flatten(np.mean(allmods_hist_rob[:,:,n_lat[0],n_lon[0]],axis=0))
            # MME, SSP
            currcell_mme_ssp = np.ma.masked_array.flatten(np.mean(allmods_fut_rob[:,:,n_lat[0],n_lon[0]],axis=0))
            
            # Ranges for CDFs
            bin_min=np.min((np.min(currcell_mme_hist),np.min(currcell_mme_ssp)))
            bin_max=np.max((np.max(currcell_mme_hist),np.max(currcell_mme_ssp)))

            # Historical MME CDF
            counts, bin_edges = np.histogram(currcell_mme_hist, bins=num_bins, range=(bin_min,bin_max), density=True)
            cdf_hist = np.cumsum(counts)
            cdf_hist_norm = cdf_hist/cdf_hist[-1]
            # SSP MME CDF
            counts, bin_edges = np.histogram(currcell_mme_ssp, bins=num_bins, range=(bin_min,bin_max), density=True)
            cdf_ssp = np.cumsum(counts)
            cdf_ssp_norm = cdf_ssp/cdf_ssp[-1]
            
            # Calculate A2
            a2=np.sum((cdf_hist_norm-cdf_ssp_norm)**2)
            
            
            # Calculate Robustness Metric-------------------------------------------------------------------------------------------
            Rrob[n_lat[0],n_lon[0]] = 1-(a1/a2)
            
    return xr.DataArray(Rrob,coords=[("lat", lat), ("lon", lon)])


#
reference_files  = sys.argv[1].split()
projection_files = sys.argv[2].split()
outfilen         = sys.argv[3]

#
references  = [ xr.open_dataset(f,mask_and_scale=True).load() for f in reference_files  ]
projections = [ xr.open_dataset(f,mask_and_scale=True).load() for f in projection_files ]
#
out       = xr.Dataset()
out.attrs = projections[0].attrs
#
reference   = references[0]
# Set output variable name
if "variable_id" in reference.attrs :
    out.attrs["variable_id"]="KS_RI(%s)"%reference.attrs["variable_id"]
#
# Set output coordinate bounds
for v in [ "lat_bnds","lon_bnds"] :
    if v in reference :
        out[v]=reference[v]
        
# Also for time (use projections bounds)
if "time_bnds" in reference :
    out["time_bnds"]    = projections[0]["time_bnds"].isel(time=0)
    out["time_bnds"][1] = projections[0]["time_bnds"].isel(time=-1)[1]

# Compute time instant in the middle of projections time period
t=projections[0]["time"]
out.assign_coords(time=("time",t.isel(time=[t.size/2]).data))

# identify sole input var
allvars= [ var for var in reference.keys() if "_bnds" not in var ]
if len(allvars) > 1 :
    raise ValueError("Too many vars : %s"%allvars)
var=allvars[0]


out["KSRI"]= KandS([ ref[var]  for ref  in references  ] ,
                   [ proj[var] for proj in projections ],
                   [ proj.attrs.get("source_id","??") for proj in projections ],
                   )

out.to_netcdf(outfilen,encoding={'KSRI': { '_FillValue': 1e+20}})

