"""

CAMMAC top level functions for computing change fields with CMIP6 data, for
basic or derived variables, and for plotting corresponding figures 

Based on CliMAF >= 1.2.13

"""
import os
import os.path
import hashlib

from climaf.api import *

from variability import process_dataset, variability_AR5, agreement_fraction_on_sign, \
    agreement_fraction_on_lower, stippling_hatching_masks_AR5, \
    inter_annual_variability, control_inter_annual_variability

from ancillary import feed_dic, choose_regrid_option

from cancillary  import basin_average, mean_or_std, ensemble_stat, walsh_seasonality


from mips_et_al import table_for_var_and_experiment, project_for_experiment, project_for_model,\
     institute_for_model, mip_for_experiment, models_for_experiments, models_for_experiments_multi_var, \
     read_versions_dictionnary

from climaf.operators import gini

one_mm_per_day="%g"%(1./(24.*3600.)) # in S.I.


# A dict defining the operators which are passed to functions change_field and variability_AR5
# for deriving desired variables.
# See explanations of arguments OPERATOR and POST_OPERATOR for function variability_AR5 in module variability
derivations={
        # Default : no transformation of the variable
        "plain"        : {},
    
        # Annual count of number of dry days (when applied to daily precip by change_fields)
        "dry"          : { "operator" : ccdo,              
                           "operator_args" :{"operator" :"yearsum -ltc,"+one_mm_per_day }},
    
        # Annual average daily rain for non-dry days (when applied to daily precip  by change_fields)
        "drain"        : { "operator" : ccdo,              
                           "operator_args" : {"operator" :"yearmean -setrtomiss,-1,"+one_mm_per_day}},
    
        # Inter-annual variability (when applied to monthly data  by change_fields)
        "iav"          : { "post_operator" : inter_annual_variability, 
                           "post_operator_args" :{"house_keeping" : True, "compute": True}},
    
        # Gini index on annual values (when applied to monthly data by change_fields)
        "gini"         : { "post_operator" : gini},
    
        # Walsh seasonnality index (when applied to monthly precip by change_fields)
        "seasonality"  : { "operator" : walsh_seasonality }, 
    }


def stats_of_basins_changes(model_changes,ref_experiment,scenario,ref_period,
                            variable,table,time_stat,
                            data_versions,slices,stats_list,basins_data,
                            fprint=True,excluded_models=[], included_models=None,
                            must_have_vars=[],
                            relative=True,compute=False, house_keeping=False): 
    """
    Feed dic MODEL_CHANGES with change values for TIME_STAT of VARIABLE spatially averaged
    over basins listed in BASINS_DATA["basins"] (which can include "globe"); this with 
    respect to a REF_PERIOD and for a series of time SLICES in a given SCENARIO; and for the list of 
    models which, according to dict DATA_VERSIONS, provide VARIABLE for both experiments, 
    List EXCLUDED_MODELS allows to discard models
    List INCLUDED_MODELS, if not None, limits models used
    
    TIME_STAT can be "mean" or "std"

    Structure of MODEL_CHANGES (which forgets about TABLE) is :
       model_changes[scenario][variable][time_stat][basin][period][model]=change_value
    
    Also returns a dict of ensemble stats of changes across the ensemble of models, for STATS_LIST :
      ens_changes[basin][ensemble_stat][period] = stat_value
    For syntax and semantics of STATS_LIST, see function `py:func:cancillary.ensemble_stat()`

    BASINS_DATA is a dict with keys : 
      - basins : list of basin names for those basins to process
      - basins_file : filename for the file coding basins
      - basins_key : a dict of correspondance between basin names and basin numbers in basins_file
      
    Change values are relative changes, except if RELATIVE=False
    """
    
    lbasins=basins_data["basins"]
    
    # Compute variables values on ref_period and slices, 
    values=dict()
    if fprint : print "%6s %s %s %s"%(scenario,variable,table,time_stat),
    #models=models_for_experiments(data_versions,variable,table,[scenario,ref_experiment],excluded_models,included_models)
    pairs=must_have_vars + [ (variable,table) ]
    #print pairs,included_models,excluded_models
    models=models_for_experiments_multi_var(data_versions,pairs,[scenario,ref_experiment],excluded_models,included_models)
    #print "models=",models
    for model,variant in models :
        #if fprint : print "%6s %-15s %s"%(scenario,model,variable),
        if fprint : print " %s"%(model),
        for period in [ ref_period ] + slices :
            #if fprint : print "%s"%period[0:3],
            for basin in lbasins :
                if basin == "globe" :
                    operator=ccdo_fast
                    args={"operator":"fldmean"}
                else:
                    operator=basin_average
                    args={"model":model,"basin":basin,"basins":basins_data,"compute":True}
                value=cvalue(mean_or_std(scenario, ref_experiment, model, variant, "anm", variable, time_stat, table,
                                         period, data_versions, operator, args,
                                         compute=compute,house_keeping=house_keeping))
                feed_dic(values,value,model,basin,period)
    if fprint : print
    #csync()
    
    # Compute relative or absolute changes, and store it with model as last dict key
    model_changes=dict()
    for period in slices :
        for model in values :
            for basin in values[model] : 
                pro = values[model][basin][    period]
                ref = values[model][basin][ref_period]
                if relative  : 
                    change = 100 * ( pro - ref ) / ref 
                else: 
                    change = pro - ref
                feed_dic(model_changes,change,basin,period,model)

    # Compute stats on models ensemble (inside a scenario)
    ens_changes=dict()
    for period in slices :
        # Next on other variables, per basin
        for basin in model_changes:
            # Access relevant models ensemble
            ens = model_changes[basin][period]
            for ens_stat in stats_list :
                stat_value = ensemble_stat(ens,ens_stat)
                feed_dic(ens_changes,stat_value,basin,ens_stat,period)
    #
    return ens_changes,models



def global_change(variable,table,experiment,period,ref_experiment,ref_period,
                  models,data_versions,filter_length=21) :
    """
    Returns a CliMAF ensemble of 1D-vectors representing the global change for a 
    VARIABLE along a PERIOD of EXPERIMENT vs. a REF_PERIOD in another  REF_EXPERIMENT, 
    for a list of pairs (model,realization) (arg MODELS). The period can begin during 
    ref_experiment (but ref_experiment must end at experiements's begin)

    The values are first yearly averaged and filtered on FILTER_LENGTH years

    DATA_VERSIONS, must be a  dictionnary with this structure (like provided by the notebook 
    in sibling directory data_versions) :

    >>> data_versions[experiment][variable][table][model][variant]=(grid,version,data_period)

     e.g.: 

     >>> data_versions["ssp245"]["pr"]["Amon"]["MPI-ESM1-2-HR"]["r1i1p1f1"]=("gn","v20190710","2015-2100")

    (data-period is used only for piControl)

    Tuned for CMIP6 only (yet). Use variable 'tas' in table 'Amon'

    Assumes that realization indices and grids are consistent across experiments for each model in the 
    provided list 
    """
    #
    GSAT=cens()
    #
    for model,realization in models :
        grid,ref_version,_= data_versions[ref_experiment][variable][table][model][realization]
        grid,version,_    = data_versions[experiment]    [variable][table][model][realization]
        print "Global_change - processing %20s %s %s"%(model,realization,version),
        dic=dict(project="CMIP6_extent",
                 experiment=ref_experiment, extent_experiment=experiment,
                 model=model, 
                 institute=institute_for_model(model), period=period,
                 variable=variable, table=table_for_var_and_experiment(variable,experiment),
                 mip="*", realization=realization, version=ref_version,extent_version=version,grid=grid)
        filtered_tasmean=ccdo(ds(**dic),operator="runmean,%d -yearmean -fldmean"%filter_length)
        #
        _,version,_=data_versions[ref_experiment][variable][table][model][realization]
        ref=dic.copy()
        ref.update(experiment=ref_experiment, mip=mip_for_experiment(ref_experiment),
                   period=ref_period,version=version)
        ref_tasmean=ccdo(ds(**ref),operator="timmean -fldmean")
        cfile(ref_tasmean)
        ref=cvalue(ref_tasmean)
        #print "GTAS = %g"%ref
        #
        GSAT[model]=ccdo_fast(filtered_tasmean,operator="subc,%g"%ref)
    #
    return GSAT


def change_fields(variable,experiments,seasons,ref_period,projection_period,
                  models_to_plot, data_versions, derivation_label=None,
                  relative=False, standardized=False, print_statistics=False,
                  ref_experiment="historical",
                  variab_sampling_args= {"house_keeping":True,"compute":True,"detrend":True,
                                         "shift":100,"nyears":20,"number":20},
                  common_grid=None,table=None,
                  deep=None, threshold=None,low_change_agree_threshold=1.0) :
    
    """Computes a series of change fields for one
    VARIABLE and a list of EXPERIMENTS, for period PROJECTION_PERIOD
    with respect to ref_experiment for REF_PERIOD. Computed fields 
    are e.g. mean change and median realtive change. See 'aggregates' below for 
    the list of fields.

    The computation is performed for all seasons listed in arg SEASONS (e.g. ['DJF', 'ANN'])

    The variable may undergo some transformation rather than plain averaging over
    the period(s); such transforations are found in global dict 'derivations' and must be 
    designated by a label (DERIVATION_LABEL)

    See other examples in the scripts of the various figures of chapter 8 
 
    Also computes variability fields and other related fields (see below) using piControl 
    and some settings for sampling it. See explanations with function 'variability_AR5' and 
    'stippling_hatching_masks_AR5' in module 'variability'

    MODELS_TO_PLOT is a dictionnary which keys are experiments and values are lists 
    of the models to include for that experiment. 

    Toggles RELATIVE activate the computation of relative change (in addition to plain 
    change). Field name suffix is "_rchange". 
      - "mean_rchange" is the ensemble mean of (per-model) relative changes
      - "means_rchange" is the relative change of ensemble means
      - "median_rchange" is the ensemble median of (per-model) relative changes

    Toggles STANDARDIZED activate the computation of change standardized by its 
    interannual variability. Field name suffix is "_schange". 
      - "mean_schange" is the ensemble mean of standardized changes
      - "median_schange" is the ensemble median of standardized changes
    The (multi-decadal) variability is then also standardized the same way.

    Arg THRESHOLD (if not None) is used when relative is True, as a floor value of
    the reference field below which the per-model relative changes are set to missing

    Arg LOW_CHANGE_AGREE_THRESHOLD provides the threshold for
    computing the field of fractionnal agreement on a low change; it
    is compared to the ratio of absolute value of change by internal
    variability for each model separately for deciding for a low
    change. The fraction of agreement is returned with key
    "agree_low" (see below)

    The variable is sought in CMIP6 table Amon or Lmon (depending on the 
    variable), except specified otherwise using arg TABLE (e.g. value 'day' is 
    for processing variable 'pr', provided the derivation make sense for daily data)

    Other details of the variable are defined using dict DATA_VERSIONS, which must be a
    dictionnary with this structure (like provided by the notebook in sibling directory 
    data_versions) :
    >>>   data_versions[experiment][variable][table][model][variant]=(grid,version,data_period)
    e.g.
    >>>   data_versions["ssp245"]["pr"]["Amon"]["MPI-ESM1-2-HR"]["r1i1p1f1"]=("gn","v20190710","2015-2100")
    (data-period is used only for piControl)



    Returns all results through a pair of dicts of dicts : aggregates and dic
    
    Dict 'aggregates' provides ensemble statistics (e.g. mean or median among
    models), while dict 'dic' returns model specific fields

    Use it as : 

    - field=aggregates[variable][experiment][season][key][derivation_label] 
      where key has values : 

        * mean_change, mean_rchange, mean_schange, means_rchange
        * median_change, median_rchange, median_schange, 
        * median_variability, agreement_fraction,  stippling, hatching, low_change_agreement_fraction

    - field=dic[experiment][season][key][derivation_label][model]
      where key has values : reference, projection, change, rchange, schange, nchange, variability
    TBD : document keys above

    """
    aggregates=dict()
    dic=dict()
    if standardized and (variab_sampling_args == {} or variab_sampling_args is None) :
        raise Exception("Must provide variability sampling arguments when requesting "+\
                        "a variable standardized by inter_annual variability")
    #
    if print_statistics :
        print "Values below are field means, except for last two columns. Last third is median and %. Last three columns are %"
        print "exp.  seas model                 variablity   reference   projection       change|rel/std   :mdn     max     p90"
        print 120*"-"

    # a commodity function for storing resuts in dic aggregates
    def feed(value,key):
        feed_dic(aggregates,value,variable,experiment,season,key,derivation_label)
    
    for experiment in experiments :
        #
        if table is None :
            table=table_for_var_and_experiment(variable,experiment)
        project=project_for_experiment(experiment)
        control_models,models=models_to_plot[experiment]
        do_variability=variab_sampling_args != {} and variab_sampling_args is not None and len(control_models) > 0
        #
        for season in seasons :
            if not print_statistics: print experiment,season,
            #
            #
            for model,realization in models :
                change_fields_internal(dic,model,realization,variable,ref_period,
                            projection_period,ref_experiment,experiment,season,
                            derivation_label, relative,standardized,print_statistics,
                            common_grid,table,data_versions,deep,variab_sampling_args,
                            threshold)
            #
            if do_variability :
                if print_statistics : print "Variabilities :",
                for model,realization in control_models :
                    variability=variability_field(project,model,realization,
                            variable, season, derivation_label, standardized,
                            variab_sampling_args, common_grid,table,
                            data_versions,deep)
                    feed_dic(dic,variability,experiment,season,"variability",derivation_label,model)
                    if print_statistics :
                        print "%s % 7.2g / "%(model,cvalue(ccdo_fast(variability,operator="fldmean"))),
                    #
                    # Compute ratio of change to internal variability for models which allow for
                    # (done on common grid)
                    if model in [ m for m,r in models ]:
                        change=dic[experiment][season]["change"][derivation_label][model]
                        nchange=ccdo2(change,variability,operator="div")
                        feed_dic(dic,nchange,experiment,season,"nchange",derivation_label,model)

                if print_statistics : print
                
            # Compute ensemble statistics
            if print_statistics :
                print "%s medians :"%experiment,
            ensavg=ccdo_ens(cens(dic[experiment][season]["change"][derivation_label]),operator='ensmean')
            feed(ensavg,"mean_change")
            ensmdn=ccdo_ens(cens(dic[experiment][season]["change"][derivation_label]),operator='enspctl,50')
            feed(ensmdn,"median_change")
            if print_statistics :
                print "change %7.2g"%cvalue(ccdo_fast(ensmdn,operator="fldpctl,50")),
            if relative :
                rmean=ccdo_ens(cens(dic[experiment][season]["rchange"][derivation_label]),operator='ensmean')
                feed(rmean,"mean_rchange")
                rmedian=ccdo_ens(cens(dic[experiment][season]["rchange"][derivation_label]),operator='enspctl,50')
                feed(rmedian,"median_rchange")
                # Also compute the relative change of ensemble means
                ref_ensavg=ccdo_ens(cens(dic[experiment][season]["reference_remapped"][derivation_label]),operator='ensmean')
                proj_ensavg=ccdo_ens(cens(dic[experiment][season]["projection_remapped"][derivation_label]),operator='ensmean')
                rmeans=ccdo2(ccdo2(proj_ensavg,ref_ensavg,operator="sub"),ref_ensavg,operator="mulc,100 -div")
                feed(rmeans,"means_rchange")
            if print_statistics :
                print "relative %7.2g %%"%cvalue(ccdo_fast(rmedian,operator="fldpctl,50")),
            if standardized :
                smean=ccdo_ens(cens(dic[experiment][season]["schange"][derivation_label]),operator='ensmean')
                feed(smean,"mean_schange")
                smedian=ccdo_ens(cens(dic[experiment][season]["schange"][derivation_label]),operator='enspctl,50')
                feed(smedian,"median_schange")
            if print_statistics :
                csync()
                print 
            #
            #
            # Compute stippling and hatching fields for the figure 
            #
            if do_variability :
                if standardized :
                    agree_field="schange"
                    avg=smean
                else :
                    agree_field="change"
                    avg=ensavg
                agreef=agreement_fraction_on_sign(cens(dic[experiment][season][agree_field][derivation_label]))
                feed(agreef,"agreement_fraction_on_sign")
                medvar=ccdo_ens(cens(dic[experiment][season]["variability"][derivation_label]),
                                operator='enspctl,50')
                feed(medvar,"median_variability")
                #
                s,h=stippling_hatching_masks_AR5(avg,medvar,agreef)
                feed(s,"stippling")
                feed(h,"hatching")
                #
                # Agreement on low change wrt OWN internal variability
                if "nchange" in dic[experiment][season] :
                    agree_low=agreement_fraction_on_lower(
                        cens(dic[experiment][season]["nchange"][derivation_label]),
                        low_change_agree_threshold)
                    feed(agree_low,"agree_low")
                else:
                    print "No common model for ",variable,seasons,experiments
                    print "models: ",models
                    print "control_models:",control_models
            #
            print
    return aggregates, dic



def change_fields_internal(dic,model,realization,variable,ref_period,
                           projection_period,ref_experiment,experiment,season,
                           derivation_label,relative,standardized,print_statistics,
                           common_grid,table,data_versions,deep,variab_sampling_args,
                           threshold ):
    """
    See function change_fields for documentation 
    """

    def feed(name,field):
            feed_dic(dic,field,experiment,season,name,derivation_label,model)

    if print_statistics :
        print "%s %s %-20s"%(experiment,season, model),
    else :
        print model,
    #
    project=project_for_experiment(experiment)
    grid,version,_=data_versions[ref_experiment][variable][table][model][realization]
    roption=choose_regrid_option(variable,table,model,grid)
    derivation=derivations[derivation_label]
    #
    base_dict=dict(project=project, experiment=ref_experiment,
                        model=model, institute=institute_for_model(model),
                        period=ref_period, variable=variable, table=table, 
                        version=version, grid=grid,
                        realization=realization)
    #
    # Compute reference time mean over requested season
    reference_dict=base_dict.copy()
    reference_ds=ds(**reference_dict)
    reference=process_dataset(reference_ds,season,**derivation)
    feed("reference",reference)
    reference_remapped=regridn(reference,cdogrid=common_grid,**roption)
    feed("reference_remapped",reference_remapped)
    if relative  :
        # if variable in ["pr","evspsbl", "P-E" ] and derivation_label not in ["dry","drain"] :
        #     zero_dot_1_mm_day=0.1/(24*3600) # in kg m2 s-1
        #     zero_dot_zero1_mm_day=0.01/(24*3600) # in kg m2 s-1
        #     epsilon=1.e-20
        #     #
        #     threshold=0.
        #     threshold=zero_dot_zero1_mm_day
        #     if variable=="evspsbl" :
        #         thresholded_reference=ccdo_fast(reference,operator="setrtomiss,-%f,%f"%(threshold,threshold))
        #     else:
        #         thresholded_reference=ccdo_fast(reference,operator="setrtomiss,-1.e+10,%f"%threshold)
        if threshold is not None :
            thresholded_reference=ccdo_fast(reference,operator="setrtomiss,-1.e+10,%f"%threshold)
        else :
            thresholded_reference=reference
    #
    # Compute projection time mean over requested season
    projection_dict=reference_dict.copy()
    _,version,_=data_versions[experiment][variable][table][model][realization]
    projection_dict.update(experiment=experiment,period=projection_period,
                        realization=realization,version=version)
    projection_ds=ds(**projection_dict)
    projection=process_dataset(projection_ds,season,**derivation)
    feed("projection",projection)
    feed("projection_remapped",regridn(projection,cdogrid=common_grid,**roption))
    #
    # Compute absolute and relative changes, and regrid to common grid
    change=ccdo2(projection,reference,operator="sub")
    feed("change_orig",change)
    change_remapped=regridn(change,cdogrid=common_grid,**roption)
    feed("change",change_remapped)
    if relative :
        rchange=ccdo2(change,thresholded_reference,operator="mulc,100 -div")
        feed("rchange_orig",rchange)
        rchange_remapped=regridn(rchange,cdogrid=common_grid,**roption)
        feed("rchange",rchange_remapped)
    if standardized:
        inter_ann_var=variability_field(None,model,realization,
                            variable, season,derivation_label, standardized,
                            variab_sampling_args,None,table,
                            data_versions,
                            deep=None,only_inter_annual=True)
        schange=ccdo2(change,inter_ann_var,operator="div")
        feed("schange_orig",schange)
        schange_remapped=regridn(schange,cdogrid=common_grid,**roption)
        feed("schange",schange_remapped)
    #
    if print_statistics :
        variab_value=0.
        print "      %7.2g     %7.2g      %7.2g      %7.2g"%(
            variab_value,\
            cvalue(ccdo_fast(reference,operator="fldmean")),\
            cvalue(ccdo_fast(projection,operator="fldmean")),\
            cvalue(ccdo_fast(change,operator="fldmean"))),
        if relative :
            print "      %7.2g %7.2g  %7.2g"%(
                cvalue(ccdo_fast(rchange,operator="fldpctl,50")),
                cvalue(ccdo_fast(rchange,operator="fldmax")),
                cvalue(ccdo_fast(rchange,operator="fldpctl,90"))),
        if standardized :
            print "      %7.2g %7.2g  %7.2g"%(
                cvalue(ccdo_fast(schange,operator="fldmean")),
                cvalue(ccdo_fast(schange,operator="fldmax")),
                cvalue(ccdo_fast(schange,operator="fldpctl,90"))),
        print       
    return

def variability_field(project,model,realization,variable,season,
                           derivation_label,standardized,
                           variab_sampling_args,common_grid,table,
                           data_versions,deep,
                           only_inter_annual=False
):
    """
    Computes variability (either multi-decadal 'a la AR5' or inter_annual) for the
    requested model, and regrid it to common grid (provided it is not None)

    If only_inter_annual is True, returns the inter_annual version

    Otherwise, returns the multi-decadal, which, if standardized is True, is normalized 
    (i.e. divided) by the inter_annual variability
    """
    #
    if realization not in data_versions["piControl"][variable][table][model] :
        realization=data_versions["piControl"][variable][table][model].keys()[0]
    derivation=derivations[derivation_label]
    #
    args=variab_sampling_args.copy()
    args.update(derivation)
    if only_inter_annual is False :
        multi_dec_var=variability_AR5(model,realization,variable,table,data_versions,
                                season=season,project=project, 
                                **args)
    if standardized or only_inter_annual :
        if "post_operator" in derivation or "operator" in derivation :
            raise ValueError("Cannot yet compute inter-annual variability for a variable "+\
                             "(%s) and a derivation (%s) "%(variable,derivation_label)+\
                             "which needs pre or post-processing" )
        inter_ann_var=control_inter_annual_variability(model,realization,\
                            variable,table,season,data_versions,**args)
    #
    if only_inter_annual :
        variability = inter_ann_var
    else :
        if standardized :
            variability=ccdo2(multi_dec_var,inter_ann_var,operator="div")
        else:
            variability = multi_dec_var
        #
    if common_grid is not None :
        grid,_,_=data_versions["piControl"][variable][table][model][realization]
        roption=choose_regrid_option(variable,table,model,grid)
        variability=regridn(variability,cdogrid=common_grid,**roption)
    return variability 

def AR6_change_figure_with_caching(variable, experiment, season, 
                        data_versions_tag, data_versions_dir,
                        models=None, excluded_models=[],
                        variability_models=None, variability_excluded_models=[],
                        ref_period="1995-2014", proj_period=None,
                        ref_experiment="historical",
                        table=None, field_type="mean_rchange",
                        derivation_label="plain", 
                        title=None, custom_plot={}, labelbar="True",
                        outdir=None, outfile=None,
                        print_statistics=True , deep=None, read=True, write=True, 
                        common_grid="r360x180", mask=None,
                        variab_sampling_args={"house_keeping":True, "compute":True,"detrend":True, "shift":100,"nyears":20,"number":20},
                        cache_dir="./aggregates",
                        drop=False, same_models_for_variability_and_changes=False,
                        threshold=None, stippling="stippling"
                        ) :
    """This is a wrapper around two functions :

     - 'change_fields', wich computes various fields related to the change of some variable between a 
       projection and an reference period in refrence experiment (either a plain or a derived variable)

     - 'AR6_change_figure', which tunes a plot of such change fields (including stippling and hatching for 
       representing inter-model agreement and significance of the change re. variability in control runs)

    See the documentation for these two functions (in the same module) for most arguments.

    Because the second step is usually undertaken much more often than the first one, this function 
    implements its own caching mechanism for the results of first step, using toggles WRITE (which 
    drives writing cache values) and READ (which allows to avoid re-doing first step). Compute step 
    will be launched anyway if cache does not contain the needed data.

    MODELS can indicate which models are to be used; if not, all models which provide data for 
    the experiment, the ref_experiment and piControl (in the dict indicated by DATA_VERSIONS_TAG and 
    DATA_VERSIONS_DIR) are used.

    EXCLUDED_MODELS is a list of models that must anyway be disregarded

    Toggle SAME_MODELS_FOR_VARIABILITY_AND_CHANGES allows to choose whether the list of models used for 
    computing changes should be restricted to the models for which variability can be computed (i.e. 
    present in dict DATA_VERSIONS for the control run, which means that there is  
    enough duration of that run). If set to False, one can control the list of models used for
    computing variability with arguments VARIABILITY_MODElS and VARIABILITY_EXCLUDED_MODElS in a way 
    similar to the models used for computing changes

    Argument STIPPLING allows to choose if the stippling is applied to :

      - areas with mean change less than one standard deviation of internal variability (default, 
        stippling="stippling") or 

      - areas where 90% of models agree that the change is less than 2
        standard deviation of their own internal variability (if stippling="agree_low")

    Argument DEEP, if set to True, will force CliMAF to restart all computations from scratch rather than 
    using its (own) cached values. This is done whatever the value of READ.

    Argument DROP, if set to True, ensures that the figure will not be taken from CliMAF cache; this is 
    useful when changing anything in figure compute workflow which is not duly reperesented in CliMAF 
    syntax for the figure definition (e.g. colormap directory, plot script code ...)

    Returned value is a triplet :
       - a filename for the figure file, 
       - a Climaf figure object, and 
       - a dict of all individual change fields as returned by function change_fields (or None if 
         not launched).

    If OUTFILE is not provided, the figure file is created in OUTDIR with a name which combines most 
    argument's values (and which is printed)

    """
    #
    experiments=[experiment] 
    seasons=[season]
    relative=True
    standardized=False
    if "schange" in field_type :
        standardized=True
    #
    data_versions=read_versions_dictionnary(data_versions_tag, data_versions_dir)
    #
    if same_models_for_variability_and_changes :
        changes_models=models_for_experiments(data_versions,variable,table,
                                           ["piControl",ref_experiment,experiment],excluded_models,models)
        changes_models.sort()
        variab_models=changes_models
    else:
        exps_list=[ref_experiment,experiment]
        if standardized :
            # Then need a piControl run for standardizing the variable by inter_annual variability
            exps_list.append("piControl")
        changes_models=models_for_experiments(data_versions,variable,table,
                                           exps_list,excluded_models,models)
        changes_models.sort()
        variab_models=models_for_experiments(data_versions,variable,table,["piControl"],
                                             variability_excluded_models,variability_models)
        variab_models.sort()
    #
    models_dict={experiment:(variab_models,changes_models)}
    
    models_reals_string=reduce(lambda x,y : "%s_%s"%(x,y), [ "%s%s"%(m,r) for m,r in changes_models])
    tag=data_versions_tag + "_" + hashlib.sha1(models_reals_string).hexdigest()[0:8]
    #
    # print 'models',models
    # print 'changes_models',changes_models
    # print 'models_dict',models_dict
    #
    aggregates={}
    read_failed=False
    if read and deep is not True :
        aggregates=read_aggregates(ref_period,proj_period,tag,cache_dir)
        try :
            a=aggregates[variable][experiment][season][field_type][derivation_label]
        except :
            print "Needed fields not found in cache; will launch comptation"
            read_failed=True
            aggregates={}
    #
    dic=None
    if len(aggregates)== 0 :
        #start_time = datetime.now()
        #print variable,derivations[derivation_label]
        aggregates,dic=change_fields(variable, experiments,seasons,ref_period,proj_period,
                                     models_dict, data_versions, derivation_label,
                                     relative,standardized,print_statistics,
                                     ref_experiment, variab_sampling_args,
                                     common_grid,table,threshold,deep)
        #
        #end_time = datetime.now()
        #duration = end_time - start_time
        #print "%6.2g seconds"%duration.total_seconds()
        if write and (not read or read_failed or deep) :
            dump_aggregates(aggregates,variable,derivation_label,ref_period,proj_period,cache_dir,tag,deep)
    #
    d=aggregates[variable][experiment][season]
    field = d[field_type] [derivation_label]
    if "hatching" in d :
        hatching  = d["hatching"] [derivation_label]
        stippling = d[stippling][derivation_label]
    else :
        stippling,hatching="",""
    #
    relative = ( "_rchange" in field_type )
    if title is None :
        title=field_type+" "+variable+" "+derivation_label+" "+season+" "+experiment
    plot1=AR6_change_figure(variable,derivation_label,field,stippling,hatching,
                            relative,labelbar,True,title,custom_plot,len(changes_models),mask)
    if drop :
        cdrop(plot1)
    #
    if outfile is None :
        if outdir is None :
            raise Error("Must provide either outdir or outfile")
        if not os.path.exists(outdir) : os.makedirs(outdir)
        filename="%s/fig_%s_%s_%s_%s_%s_%s_%s_%s.png"%(outdir,variable,derivation_label,experiment,
                                                    season,field_type,ref_period,proj_period,tag)
    else:
        filename=outfile
    cfile(plot1,filename)
    print "Figure available as ",filename
    return filename,plot1,dic,variab_models,changes_models
    #return "",plot1,dic,variab_models,changes_models

def dump_aggregates(aggregates,variable,derive,ref_period,proj_period,cache_dir,tag,deep=None) :
    """
    This is an ancillary function for AR6_change_figure_with_caching. See its doc
    """
    import os, os.path
    if not os.path.exists(cache_dir) : 
        os.makedirs(cache_dir)
    for exp in aggregates[variable] :
        for season in aggregates[variable][exp] :
            for field in aggregates[variable][exp][season] :
                cfile(aggregates[variable][exp][season][field][derive],
                      cache_dir+"/%s=%s=%s=%s=%s=%s=%s=%s.nc"%(season,variable,exp,field,derive,ref_period,proj_period,tag),
                      deep=None,ln=False)
                
def read_aggregates(ref_period,proj_period,tag,cache_dir) :
    """
    This is an ancillary function for AR6_change_figure_with_caching. See its doc
    """
    d=dict()
    import glob
    files=glob.glob(cache_dir+"/*=*=*=*=*=*=*=%s.nc"%tag)
    #print files
    for f in files :
        bn=f.split("/")[-1]
        bn=bn.split(".")[0]
        bn=bn.split("=")
        season,variable,exp,field,derive,rperiod,pperiod,_=bn
        if pperiod==proj_period and rperiod==ref_period :
            dataset=fds(f,period="1850-2100")
            # Need to erase cached value
            cdrop(dataset)
            feed_dic(d,dataset,variable,exp,season,field,derive)
    return d


def AR6_change_figure(variable, derivation_label, field, stippling="", hatching="",
                      relative=True, labelbar="True", shade=True,
                      title=None, custom_plot={}, number=None, mask=None) :
    """

    Returns a CliMAF plot object showing a 2d FIELD, with
    superimposition of stippling (resp. hatching) where field
    STIPPLING (resp.HATCHING) is 'set' (actually where it exceeds value 0.9)

    Plot characteristics comply with AR6/WGI TSU guidelines re. colormaps, projection, ...
    (except maybe if changed through arg CUSTOM_PLOT, see below)

    Toggle LABELBAR drives the presence of a labelbar in the plot. Its type is 
    string => value must be "True" or "False"

    The provided TITLE is plotted too. If a NUMBER is provided, it will
    be plotted in upper righ corner

    VARIABLE, DERIVATION_LABEL, and logical toggle RELATIVE are used in order 
    to choose a colormap and sensible data intervals for a change of the variable
    (arg RELATIVE indicating if FIELD is for a relative change)

    However, this can be superseded by providing through CUSTOM_PLOT
    argument a dict of arguments for CliMAF function plot(), as e.g.

    >>> custom_plot={"color":"AR6_Precip_12","min":-2, "max":2,"delta":0.4 ,focus:"land"}

    For the time being, the most used value for DERIVATION_LABEL is 'plain',
    and the only other known cases are 'dry' (which stands for: the number of dry
    days per year) and 'drain' (daily rain depth for rainy days)

    """
    plot_args=dict( proj="Robinson", mpCenterLonF=2.0, gsnLeftString="", vcb=False)
    if hatching != "" and shade :
        plot_args.update(shading_options="gsnShadeHigh=3|gsnAddCyclic=True",
                         shade_above=0.9) 
    if stippling != "" and shade :
         # Stippling for 2nd mask
        plot_args.update( shade2_options="gsnShadeHigh=17|gsnShadeFillScaleF=1|gsnShadeFillDotSizeF=0.004|gsnAddCyclic=True", 
                          shade2_below=-0.1, shade2_above=0.9)
    options_format="lbLabelBarOn=%s|lbBoxEndCapStyle=TriangleBothEnds|lbLabelFont=helvetica|" +\
        "lbTitleOn=True|lbTitleString='%s'|lbTitleFont=helvetica|lbTitlePosition=Bottom|"+\
        "lbLabelFontHeightF=0.015|cnMissingValFillColor=grey|cnInfoLabelOn=False|"+\
        "gsnRightStringFontHeightF=0.018|cnFillMode=CellFill|"
    #
    def colormap(variable) :
        if   variable in ["pr","pr_drain","pr_iav","P-E","mrro"] : return {"color":"AR6_Precip_12s" }
        elif variable in ["pr_dry"]                     : return {"color":"AR6_Evap_12s" }
        elif variable in ["pr_seasonality"]             : return {}
        elif variable in ["evspsbl"]                    : return {"color":"AR6_Temp_12s" }
        elif variable in ["mrsos","mrso"]               : return {"color":"AR6_Precip_12s" }
        elif variable in ["sos"]                        : return {"color":"AR6_Salinity_12s" }
        else : return {}
    #
    def unit_string(variable) :
        if variable in ["pr","P-E", "evspsbl"] : return "mm/d"
        elif variable == "pr_drain"            : return "mm"
        elif variable == "pr_seasonality"      : return "-"
        elif variable == "pr_dry"              : return "day"
        elif variable in ["mrso","mrsos"]      : return "kg/m**2"
        elif variable in ["mrro"]              : return "kg/m**2/d"
        elif variable == "sos"                 : return "psu"
        else                                   : return "?"
    #
    def scale(variable) :
        if variable in ["pr","P-E","mrro","evspsbl"] : return {"scale":24.*3600 }
        else : return {}

    def minmax(variable) :
        if   variable == "pr"     : return { "min":-2, "max":2,"delta":0.4}
        elif variable == "pr_dry" : return { "colors":"-32 -16 -8 -4 -2 0 2 4 8 16 32"}
        elif variable == "pr_drain":return { "colors":"-2 -1 -0.5 -0.2 -0.1 0 0.1 0.2 0.5 1 2"}
        elif variable == "pr_seasonality": return { "min":0.2, "max":1.5, "delta":0.1 }
        elif variable == "P-E"    : return { "min":-2, "max":2,"delta":0.4}
        elif variable == "evspsbl": return { "min":-1, "max":1,"delta":0.2},
        elif variable == "mrsos"  : return { "colors":"-5 -2 -1 -0.5 -0.25 0.25 0.5 1 2 5"}
        elif variable == "mrro"   : return { "min":-0.5, "max":0.5,"delta":0.1}
        else : return {}
        
    def relative_minmax(variable) :
        if   variable == "mrso" :    return dict(colors="-5 -2 -1 -0.5 -0.25 0 0.25 0.5 1 2 5")
        elif variable == "sos" :     return dict(colors=" -4. -3. -2. -1. -0.5 0. 0.5 1. 2. 3. 4. ")        
        elif variable == "evspsbl" : return dict(colors=" -100. -50. -25. -10. -5 0. 5 10. 25. 50. 100. ")        
        else                       : return dict(colors=" -50. -40. -30. -20. -10. 0. 10. 20. 30. 40. 50.")  
    #
    def apply_mask(field,mask_field):
        """ 
        Assumes that mask field has non-zero non-missing values on interesting places (to keep), 
        and zero or missing on places to mask 
        Result has input field value on interesting places, and missing value elsewhere
        Assumes that grids for both fields are consistent
        """
        if type(mask_field) is str :
            mask_field=fds(mask_field)
        return ccdo2_flip(field,mask_field,operator="ifthen")

    var2=variable
    if derivation_label != 'plain' :
        var2=variable+"_"+derivation_label
    if relative :
        plot_args.update(**relative_minmax(var2))
        plot_args.update(options=options_format%(labelbar,"%"))
    else:
        #print var2,minmax(var2)
        plot_args.update(**minmax(var2))
        plot_args.update(**scale(var2))
        ustring=custom_plot.get("units",unit_string(var2))
        plot_args.update(options=options_format%(labelbar,ustring))
    plot_args.update(**colormap(var2))
    #
    # Must combine 'options' defined above and those in custom_plot
    custom_options=custom_plot.pop("options","")
    plot_args["options"]=plot_args["options"]+custom_options
    #
    # Apply caller's custom options
    plot_args.update(custom_plot)
    #
    if number is not None :
        if type(number) is int : number_string="%d  "%number
        else :                   number_string="%s  "%number
        plot_args.update(gsnRightString=number_string)
    #
    if mask is not None :
        field     = apply_mask(field,mask)
        if stippling != "" : 
            stippling = apply_mask(stippling,mask)
        if hatching != "" : 
            hatching  = apply_mask(hatching ,mask)
    return plot(field,hatching,"","",stippling,title=title, **plot_args)



