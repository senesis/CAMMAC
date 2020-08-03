"""

CAMMAC ancilliary functions using CiMAF for computing:

  - computing Walsh et al. (1981) seasonality index 
  - basin averages
  - mean or variability of data series
  - ensemble statistics on scalars

"""


import json, os, os.path, numpy as np
from scipy.stats import tvar
from climaf.api import *
from climaf.operators import ccdo,ccdo_fast,ccdo2
from mips_et_al import institute_for_model, table_for_var_and_experiment
from variability import init_trend

if "gini" not in climaf.operators.scripts:
    cscript("gini","python %s/gini.py ${in} ${out}"%__file__,_var="gini")

def init_yeardiv():
    """
    Implement a CliMAF operator which divides monthly averages by yearly sums, using CDO 
    operator 'yeardiv', and by creating 12 records per yearly sum

    So we assume that file argument #1 has monthly values and file argument #2 has 
    corresponding yearly sums (so 12 records in file #1 for one record in file #2)

    We use a feature of CDO operator mergetime, which, when provided with records of the same 
    time, just concatenate them (rather than discarding these redundant records)
    """
    if "yeardiv" in climaf.operators.scripts:
        return
    cscript( 'yeardiv','cdo -O div '\
             '${in} '\
             '-mergetime '\
                 '-mergetime '\
                    '-mergetime ${in_2} ${in_2} '\
                    '-mergetime ${in_2} ${in_2} '\
             '-mergetime '\
                    '-mergetime '\
                        '-mergetime ${in_2} ${in_2} '\
                        '-mergetime ${in_2} ${in_2} '\
                    '-mergetime '\
                        '-mergetime ${in_2} ${in_2}  '\
                        '-mergetime ${in_2} ${in_2}  '\
             '${out}')


def walsh_seasonality(precip_monthly_averages):
    """
    Implements Walsh (1981) seasonality index SIi (the version computed on individual years) 
    
    Time average among years of
       Sum on all months of the year of
          absolute value of 
             fraction of the annual rain occurring in the month
                minus 1./12.
    
    This is computed on the dataset provided as argument (assuming it is monthly means of 
    precipitation). 
    
    We do not convert to precipitation height but use fluxes
    
    We apply a 10mm per year threshold
    """
    # 1- compute annual rains as the sum of monthly rain average
    #annual_rains=ccdo_fast(precip_monthly_averages,operator="yearsum")
    annual_rains=ccdo_fast(precip_monthly_averages,operator="mulc,12 -yearmonmean")

    # 2- mask places where annual rains are very low, 
    threshold=10./(365./12. * 24 * 3600.) # 10mm (per year) converted to S.I. during one (average) month
    enough=ccdo_fast(annual_rains,operator="gec,%s"%threshold) # 1s and 0s
    
    masked_annual_rains=ccdo2(annual_rains,enough,operator="setctomiss,0 -mul")

    # 3- Use a CliMAF operator mimicking CDO's ymondiv over years, 
    # i.e. dividing each input field of 1st arg by the field with same year in 2nd arg
    init_yeardiv()
    from climaf.operators import yeardiv
    ratios=yeardiv(precip_monthly_averages,masked_annual_rains)

    # 4- Implement remaining operations :
    one_over_12="%f"%(1./12.)
    return ccdo_fast(ratios,operator="yearsum -abs -subc,"+one_over_12)    


def basin_average(data,model,basin,basins,compute=False,house_keeping=False,test=False) :
    """
    Computes average of DATA over a named BASIN, which should be a key of BASINS["basins_key"], 
    which itself provides the integer coding that basin in BASINS["basins_file"]

    If BASIN = 'land', the avergae is computed over the land described by sftlf' field of MODEL
    
    Better compute time mean upstream of this function (which has to regrid to a fine grid)

    Example : 
    >>> basin_average(mrro_data,"CNRM-CM6-1","Lena", {"basins_file":"./num_bas_ctrip.nc","basins_key":{ "Lena":8,"Amazon":1 ...}})
    """
    if basin=="land" :
        return land_average(data,model,compute,house_keeping,test)
    #
    bkey=basins["basins_key"]
    if basin not in bkey :
        raise ValueError("basin average cannot process basin %s"%basin)
        
    if "ccdo2_flip" not in climaf.operators.scripts :
        cscript('ccdo2_flip', 'cdo ${operator} ${in_2} ${in_1} ${out}')
    from climaf.operators import ccdo2_flip
        
    # First regrid to basin definition grid, with first order conservative remapping
    basin_data=fds(basins["basins_file"],simulation="basins", period="fx", model="basins_model")
    regridded=regrid(data,basin_data,option="remapcon")
    
    # Use CDO for masking on relevant basin, and computing mean
    mask=ccdo_fast(basin_data,operator="setvrange,%d,%d"%(bkey[basin],bkey[basin]))
    masked=ccdo2_flip(regridded,mask,operator="ifthen,%d"%bkey[basin])
    average=ccdo_fast(masked,operator="fldmean")
    if compute:
        ceval(average)
    if house_keeping :
        cdrop(regridded)
    if test :
        return masked
    else:
        return average
    
    
test_basin_average=False
#
if test_basin_average :
    model="CNRM-CM6-1"
    dic=dict(project="CMIP6_extent", experiment="ssp585",model=model, 
                   institute=institute_for_model(model),period="2015-2020",
                   variable="mrro", table="Lmon", version="latest",mip="ScenarioMIP",
                   realization=default_variant(model,"ssp585","mrro"))
    basin_mean=basin_average(ds(**dic),"","Amazon",True,False,True)
    ncview(basin_mean)


def land_average(data,model,compute=False,house_keeping=False,test=False) :
    """
    
    """
    # Try to access land fraction field sftlf
    base_dict=dict(project="CMIP6", experiment="piControl", mip="CMIP",
        model=model, institute=institute_for_model(model),version="*", 
        realization="*",table="fx",period="fx",variable="sftlf")
    #
    if "GFDL" in model or "INM" in model : 
        base_dict.update(grid="gr1")
    #
    sftlf=ds(**base_dict)
    try :
        cfile(sftlf)
    except : 
        base_dict["experiment"]="piControl"
        try :
            cfile(sftlf)
        except : 
            raise ValueError("No sftlf field for "+model)

    # Use CDO for masking on land, and computing mean
    mask=ccdo_fast(sftlf,operator="divc,100. -setvrange,100,100")
    masked=ccdo2(data,mask,operator="mul")
    average=ccdo_fast(masked,operator="fldmean")
    if test :
        return masked
    if compute:
        ceval(average)
    if house_keeping :
        cdrop(masked)
    return average



test_land_average=False
if test_land_average :
    model="CNRM-CM6-1"
    dic=dict(project="CMIP6_extent", experiment="ssp585",model=model, 
                   institute=institute_for_model(model),period="2015-2020",
                   variable="pr", table="Amon", version="latest",mip="ScenarioMIP",
                   realization=default_variant(model,"ssp585","pr"))
    land_mean=land_average(ds(**dic),model,True,False,True)
    ncview(land_mean)
    print cvalue(land_average(ds(**dic),model,True,False,False))*24.*3600


def mean_or_std(scenario, ref_experiment, model, realization, season, variable, stat, table,  
                period, data_versions, operator=None, operator_args={}, compute=False,
                detrend=True, house_keeping=False) :
    """
    Compute a STAT ("mean" or "std") of annual or seasonal means 
    of a VARIABLE  over a PERIOD for a given MODEL and a virtual experiment 
    which merges REF_EXPERIMENT and SCENARIO (but REF_EXPERIMENT can be None) 

    Detrending is performed before computing standard deviation, except if requested 
    otherwise using arg 'detrend'

    Additionnaly, a CliMAF OPERATOR can be applied after time averaging (and before 
    standard deviation computation if applicable). 
    
    Dict DATA_VERSIONS provide details (grid, version, realization) for the data to use 
    
    PERIOD can extend from some date in REF_EXPERIMENT to some other date of SCENARIO, 
    but then, the end of REF_EXPERIMENT must match the beginning of SCENARIO
    
    Works for CMIP6 only, yet
    """
    #
    # Define relevant dataset
    if ref_experiment is not None :
        grid,version,_=data_versions[ref_experiment][variable][table][model][realization]
        _,scenario_version,_=data_versions[scenario][variable][table][model][realization]
        dic=dict(project="CMIP6_extent", 
             experiment=ref_experiment, extent_experiment=scenario,
             variable=variable, period= period,
             mip="*", model=model, institute=institute_for_model(model),
             table=table_for_var_and_experiment(variable,scenario), 
             version=version, extent_version=scenario_version, grid=grid, 
             realization=realization)
    else :
        grid,version,_=data_versions[scenario][variable][table][model][realization]
        dic=dict(project="CMIP6", 
             experiment=scenario,
             variable=variable, period= period,
             mip="*", model=model, institute=institute_for_model(model),
             table=table_for_var_and_experiment(variable,scenario), 
             version=version, grid=grid, 
             realization=realization)
    #
    # Compute relevant stat
    if stat=="mean" : 
        # Average over years, possibly after selecting season
        time_operation="timmean"
        if season != "anm" : time_operation +="-selseason,%s"%season
        rep=ccdo(ds(**dic),operator=time_operation )
        if operator is not None:
            rep=operator(rep,**operator_args)
    #
    elif stat=="std" : 
        # First compute annual mean or seasonal mean for each year
        time_operation="yearmean"
        if season != "anm" : time_operation ="selseason,%s -seasmean"%season
        cached=ccdo(ds(**dic),operator=time_operation)
        if operator is not None:
            cached=operator(cached,**operator_args)
        if detrend :
            # Must detrend 
            init_trend()
            from climaf.operators import ctrend,csubtrend
            a=ctrend(cached)
            detrended=csubtrend(cached,a,a.b)
        else :
            detrended=cached
        # Compute standard deviation of seasonal values series
        rep=ccdo_fast(detrended,operator="timstd1")
    else :
        raise ValueError("stat %s cannot yet be processed by mean_or_std for season %s"+\
                    "and variable %s"%(stat,season,variable))
    if compute : ceval(rep)
    #
    if house_keeping and stat=='std':
            cdrop(cached)
            cdrop(detrended)
    return rep

def ensemble_stat(ens,option) :
    """ 
    Assuming ENS is a dict of values for an ensemble, computes :
      * min, max, mean or percentile of values , 
      * or just return :
         - the ensemble with numpy.float64 values (with OPTION='ens') or 
         - the dict value which key equals OPTION
    
    For percentiles options, 
        - "l5"  means lower 5% empirical percentile with linear interpolation
        - "n95" means higher 5% percentile with log-normal approximation
        - only percentiles 5, 25, 75 and 95  are processed

    Returned values are NumPy floats
    """
    #
    if option in [ "mean"]:
        sum=0 
        wsum=0
        for e in ens : 
            wsum+=1.
            sum+=ens[e]
        return sum/wsum
    #
    elif option in ["min","max","second","butlast" ] :
        l=ens.values()
        l.sort()
        if option=="min"     : return np.float64(l[0])
        if option=="second"  : return np.float64(l[1])
        if option=="butlast" : return np.float64(l[-2])
        if option=="max"     : return np.float64(l[-1])
    #
    elif option in ["median", "mdn" ] : #mdeian with linear interpolation 
        l=ens.values()
        l.sort()
        return np.percentile(l, 50,interpolation='linear')
    #
    elif option in ["lq5","lq95" ] : #percentiles with linear interpolation 
        l=ens.values()
        l.sort()
        if option=="lq5"     : return np.percentile(l, 5,interpolation='linear')
        if option=="lq95"    : return np.percentile(l,95,interpolation='linear')
    #
    elif option in ["lq25","lq75" ] : #percentiles with linear interpolation 
        l=ens.values()
        l.sort()
        if option=="lq25"    : return np.percentile(l,25,interpolation='linear')
        if option=="lq75"    : return np.percentile(l,75,interpolation='linear')
    #
    elif option in ["nq5","nq95","nq25","nq75" ] : #percentiles with gaussian hypothesis
        mean=np.mean(ens.values())
        std1=np.std(ens.values(),ddof=1)
        if option == "nq5"   : return mean - 1.645*std1
        if option == "nq25"  : return mean - 0.675*std1
        if option == "nq75"  : return mean + 0.675*std1
        if option == "nq95"  : return mean + 1.645*std1
        #raise ValueError("Cannot yet compute percentiles based on normal distribution assumption")    
    #
    elif option == "ens"  :
        rep=dict()
        for key in sorted(ens.keys()) : 
            rep[key] = np.float64(ens[key])
        return rep
    #
    elif option in ens : # return a single model, which name is passed with 'option'
        return np.float64(ens[option])
    else:
        raise ValueError("Time to use some library for stats (%s) !"%option)
    
