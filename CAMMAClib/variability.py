"""

CAMMAC functions related to variability

- Computing variability of a variable in a control experiment (or simply providing the 
  ensemble of slice values), according to Box 2.1, note a) of AR5 WGI

- Computing stippling and hatching masks and agreement fraction according to AR6 guidelines

- Computing interannual variability on a dataset

Based on CliMAF >= 1.2.13

"""


from climaf.api import *
from climaf.period import init_period
from env.environment import cscripts
from mips_et_al import institute_for_model, project_for_model, table_for_var_and_experiment


def variability_AR5(model,realization,variable,table, data_versions,season="ANN", project="CMIP6", 
                    operator=None, operator_args={},
                    post_operator=None, post_operator_args={},
                    shift=100,nyears=20,number=20,
                    variability=True,
                    compute=True,house_keeping=False,detrend=True,
                    deep=None):
    """
    Compute the variability according to AR5 Box 2.1 : 
     - select data time series in piControl for the whole of the samples (from 
       its begin+SHIFT, duration consistent with NUMBER samples of size NYEARS);
       the data variant and version, and the begin date, are selected according to 
       dictionnary DATA_VERSIONS,
     - transform this data using OPERATOR (and its OPERATOR_ARGS) that should produce 
       one value per year (default being to compute annual or seasonal means)
     - detrend that data, if required (this is done by default)
     - build an ensemble representing the samples (NUMBER * NYEARS)
     - transform each member's result using POST_OPERATOR and POST_OPERATOR_ARGS (default 
       is to compute a time average)
     - if arg VARIABILITY is False , returns that result (i.e. by defaut the time mean),
     - otherwise computes and returns the variability as the ensemble standard deviation 
       multiplied by square root of 2

    Arg MODELS_WITH_ENOUGH_SPINUP is the list of those models for which the required 
    SHIFT may be relaxed, because they are supposed to be already in a balanced state 
    from the start of published piControl data

    The returned value is a CliMAF object (either a field or an ensemble, depending on VARIABILITY)

    Arg COMPUTE, if set to True, drives an immediate lauch of the computation, of CliMAF object, 
    and then, if arg DEEP is True, re-compute all results from scratch, without using CliMAF cached
    values for intermediate results.

    Arg HOUSE_KEEPING, if set to True, allows to release CliMAF cache intermediate results, to keep 
    cache use as low as possible

    Used e.g for variability of :
      - plain variables
      - walsh seasonnality index
      - number of  dry days per year 
      - year mean daily precipitation for non-dry days 
      - inter_annual variability for any variable, using :
           * post_operator=inter_annual_variability
           * post_operator_args={"factor" : 1.414}

    This version yet tested only on CMIP6 models 
    """
    init_trend()
    from climaf.operators import ctrend,csubtrend

    if realization not in data_versions["piControl"][variable][table][model] :
        realization=data_versions["piControl"][variable][table][model].keys()[0]
    grid,version,data_period=data_versions["piControl"][variable][table][model][realization]
    
    duration=nyears*number
    true_begin=int(data_period.split('-')[0][0:4])
    end=int(data_period.split('-')[1][0:4])
    begin=true_begin+shift
    if begin+duration-1 > end :
        # In CMIP6, some models have enough spinup before piControl start, but a too short piControl length
        # We assume that this has been dealt with at the stage of data selection, and allow
        # to release the constraint on shift at the beginning of the data period
        alt_begin=end-duration+1
        if alt_begin >= true_begin :
            begin=alt_begin                
        else :
            message="Duration for %s %s %s %s %s %s is too short : [%d - %d] even with no shift %d is shorter than %d years "%\
                        (model,variable,table,realization,version,grid,true_begin,end,shift,duration)
            raise ValueError(message)
    #
    period="%g-%g"%(begin,begin+duration-1)
    base_dict=dict(project=project, experiment="piControl",
                   model=model, institute=institute_for_model(model),
                   period=period, variable=variable, table=table, 
                   version=version, grid=grid, realization=realization)
    if project=="CMIP6" :
         base_dict.update(mip="CMIP")
    
    # Basic dataset (e.g. precip)
    basic=ds(**base_dict)
    dat=basic

    # Implement the operation if required, otherwise seasonal or yearly average
    if operator is None :
        if season in [ "ann","ANN","anm" ] :
            dat_op=ccdo(dat,operator="yearmean")
        else:
            dat_op=ccdo_fast(dat,operator="selseason,%s -seasmean"%season)
    else:
        if season in [ "ann","ANN","anm" ] :
            dat_op=operator(dat,**operator_args)
        else:
            dat_season=ccdo_fast(dat,operator="selseason,%s"%season)
            dat_op=operator(dat_season,**operator_args)
    dat=dat_op

    # Detrend the data if required
    if detrend :
        a=ctrend(dat) 
        ap=ccdo_fast(a,operator="mulc,0") # Do not want to have a zero-mean detrended serie
        detrended=csubtrend(dat,ap,a.b)
        dat=detrended

    # Build an ensemble which members are the slices
    econtrol=cens()
    slices=[ "%d-%d"%(begin+n*nyears,begin+(n+1)*nyears-1) for n in range(0,number) ]
    #print "model=",model," variant=",realization," slices=",slices
    for period in slices :
        econtrol[period]=ccdo_fast(dat,operator="seldate,"+init_period(period).iso())

    # On each slice, implement the required post operation, otherwise compute a plain average
    if post_operator is not None :
        cmeans=cens()
        for member in econtrol:
            cmeans[member]=post_operator(econtrol[member],**post_operator_args)
    else:
        cmeans=ccdo_fast(econtrol,operator="timmean")
        
    if variability is True :
        # Compute variability over the slices ensemble
        variab1=ccdo_ens(cmeans,operator='ensstd1')
        variab=ccdo_fast(variab1,operator="mulc,1.414") # cf. AR5 Box 2.1

    #
    if compute:
        if variability : cfile(variab,deep=deep)
        else : cfile(cmeans, deep=deep)
    if house_keeping : # Discard intermediate data
        cdrop(basic)
        cdrop(dat_op)
        if operator is not None and season not in [ "ann","ANN","anm" ] :
            cdrop(dat_season)
        if detrend :
            cdrop(a)
            cdrop(a.b)
            cdrop(ap)
            cdrop(detrended)
        cdrop(dat)
        for period in slices : cdrop(econtrol[period])
    #
    if variability :
        if house_keeping :
            cdrop(cmeans)
            cdrop(variab1)
        return variab
    else :
        return cmeans


def process_dataset(dat,season,operator=None, operator_args={},
                    post_operator=None, post_operator_args={}):
    """ 
    Similar to variability_AR5, but without slicing nor detrending nor 
    variability computation on slices. Also : the data to work on is directly 
    provided as argument DAT

    This function is used to process the reference period and the projection 
    periods in a way consistent with variability computation for the control period
    """

    # Implement the operation if required, otherwise seasonal or yearly average
    if operator is None :
        if season in [ "ann","ANN","anm" ] :
            dat_op=ccdo(dat,operator="yearmean")
        else:
            dat_op=ccdo_fast(dat,operator="selseason,%s -seasmean"%season)
    else:
        if season in [ "ann","ANN","anm" ] :
            dat_op=operator(dat,**operator_args)
        else:
            dat_season=ccdo_fast(dat,operator="selseason,%s"%season)
            dat_op=operator(dat_season,**operator_args)
    dat=dat_op
    
    # Implement the required post operation, otherwise compute a plain average
    if post_operator is not None :
        cmean=post_operator(dat_op,**post_operator_args)
    else:
        cmean=ccdo_fast(dat_op,operator="timmean")
    return cmean


def init_trend():
    """
    Initalize CliMAF operators 'ctrend' and 'csubtrend' for using CDO 
    operators 'trend' and 'subtrend'
    """
    
    if "ctrend" not in cscripts:
        cscript("ctrend", "cdo trend ${in} ${out} ${out_b}")
        cscript("csubtrend", "cdo subtrend ${in_1} ${in_2} ${in_3} ${out}")


def agreement_fraction_on_sign(ensemble):
    """
    Returns the field of fraction of members of ENSEMBLE which agree on their sign 
    """

    # Count negative values
    nchanges=ccdo_fast(ensemble,operator="lec,0")
    nchange=ccdo_ens(nchanges,operator="enssum")
    # Count positive values
    pchanges=ccdo_fast(ensemble,operator="gec,0")
    pchange=ccdo_ens(pchanges,operator="enssum")
    # Compute agreement fraction
    mchange=ccdo2(nchange,pchange,operator="max")
    nb=len(ensemble)
    fchange=ccdo_fast(mchange,operator="divc,%d.0"%nb)
    #
    return fchange

def agreement_fraction_on_lower(ensemble,threshold):
    """
    Returns the field of fraction of members of ENSEMBLE which agree on "|value| <= threshold" 
    """

    # 
    # Count absolute values below threshold values
    lows=ccdo_fast(ensemble,operator="lec,%g -abs"%threshold)
    #
    nb=len(ensemble)
    fagree=ccdo_fast(ccdo_ens(lows,operator="enssum"),operator="divc,%d.0"%nb)
    #
    return fagree


def lowchange_conflict_masks_AR6(sign_agree_fraction, low_change_agree_fraction,
                                 fraction_on_magnitude=0.33, fraction_on_sign=0.8) :
    """

    Returns the masks for low changes (or non-agreement on large changes)
    and significant changes with conflicting sign, according to AR6 scheme, given :

    - a field of the fraction of models which agree on sign of change
    - a field of the fraction of models which have a |change| lower than some threshold

    Returned fields :

    - lowchange field : value 1 if low_change_agree_fraction is more than 
      fraction_on_magnitude (and 0 otherwise)
    - conflict field : value 1 if low_change_agree_fraction is .le. 
      fraction_on_magnitude and sign_agree_fraction is less than fraction_on_sign
      (and 0 or missing otherwise)

    """

    lowchange = ccdo(low_change_agree_fraction, operator="gec,%g"%fraction_on_magnitude)
    sign_low_agree = ccdo(sign_agree_fraction, operator="ltc,%g"%fraction_on_sign)
    conflict = ccdo2(lowchange,sign_low_agree,operator="ifnotthen")
    return lowchange,conflict
    
def stippling_hatching_masks_AR5(change,variability,agreement_fract):
    """
    Returns the stippling and hatching masks according to method a) in AR5 Box2.1, given :

      - a field of changes CHANGE
      - a field of variability standard deviation VARIABILITY
      - a field of fraction of members which agree on sign of changes AGREEMENT_FRACTION

    Hatching : value 1 if change is less than one standard deviation of variability

    Stippling : value 1 if change is over two standard deviations of variability + agreement 
    of 90% of models on change sign

    Special case : if VARIABILITY is None, returned stippling and hatching is the empty 
    string (for compatibility with CliMAF plot operator)

    """
    masku=ccdo_fast(agreement_fract,operator="gec,0.9")
    
    if variability is not None :
        # 
        abs_change=ccdo_fast(change,operator='abs')
        hatching=ccdo2(abs_change,variability,operator="lt") 
        #
        var2=ccdo_fast(variability,operator="mulc,2")
        maskt=ccdo2(abs_change,var2,operator="ge")
        stippling=ccdo2(maskt,masku,operator="min") #
    else :
        hatching=""
        stippling=""
        
    return stippling,hatching


def inter_annual_variability(dat,factor=None,house_keeping=True,compute=False):
    """
    Computes inter_annual_variability like Pendergrass et al. 201x :
    Assuming input data has one value per year, detrend it and then computes 
    standard deviation, without multiplying by any factor (except if provided)
    """
    init_trend()
    from climaf.operators import ctrend,csubtrend
    #
    a=ctrend(dat) 
    b=csubtrend(dat,a,a.b)
    c=ccdo_fast(b,operator="timstd1")
    if factor is not None :
        rep=ccdo_fast(c,operator="mulc,%g"%factor)
        todrop=c
    else :
        rep=c
    #
    if compute :
        cfile(rep)
    if house_keeping :
        cdrop(a)
        cdrop(a.b)
        cdrop(b)
        if factor is not None :
            cdrop(todrop)
    return rep


def control_inter_annual_variability(model,realization,variable,table,season,data_versions,
                                     nyears=20,number=20,shift=100,
                                     house_keeping=True,compute=False,detrend=True):
    init_trend()
    from climaf.operators import ctrend,csubtrend

    if realization in data_versions["piControl"][variable][table][model] :
        variant=realization
    else :
        variant=data_versions["piControl"][variable][table][model].keys()[0]
    #
    try :
        grid,version,pperiod = data_versions["piControl"][variable][table][model][variant]
    except :
        raise ValueError("Cannot get data_version for %s %s %s %s %s nor %s "%\
                         ("piControl",variable,table,model,realization,variant))
        
    begin=int(pperiod.encode('ascii').split("-")[0])
    #
    length=nyears*number
    detrended=control_detrend(model,variable,begin,length,shift,
                              variant,version,
                              compute,house_keeping,detrend)
    std_dev=ccdo_fast(detrended,operator="timstd1 -seasmean -selseason,%s"%season)
    return(ccdo_fast(std_dev,operator="mulc,1.414"))

def control_detrend(model,variable,begin,length, shift,
                    variant,version,
                    compute=True,house_keeping=True,detrend=True):
    # Detrend the requested variable for the piControl run 
    # If compute is True, actually evaluates the result and get rid 
    #       of original data partial copy
    # If house_keeping is True, don't compute and remove existing file from cache
    
    from climaf.operators import ctrend,csubtrend

    project=project_for_model(model)
    institute=institute_for_model(model)
    table=table_for_var_and_experiment(variable,"piControl")
    control=dict(variable=variable, institute=institute, model=model, 
                 project=project,table=table,
                 experiment="piControl",version=version,realization=variant)
    if project=="CMIP6" : control.update(mip="CMIP")
    d=ds(period="%d-%d"%(begin+shift,begin+shift+length-1),**control)
    if detrend :
        a=ctrend(d) 
        ap=ccdo_fast(a,operator="mulc,0") # Do not want to have a zero-mean detrended serie
        detrended=csubtrend(d,ap,a.b)
        if compute :
            cfile(detrended)
        if house_keeping :
            cdrop(d) # Discard cache copy of original data
            cdrop(a)
            cdrop(a.b)
            cdrop(ap)
        return detrended
    else:
        return d

