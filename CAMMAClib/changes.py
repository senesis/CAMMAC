"""

CAMMAC top level functions for computing change fields with CMIP6 data, for
basic or derived variables, and for plotting corresponding figures 

Based on CliMAF >= 1.2.13

"""
import os, os.path

from climaf.api import *

from variability import process_dataset, variability_AR5, agreement_fraction, \
    stippling_hatching_masks_AR5, inter_annual_variability, control_inter_annual_variability

from ancillary import feed_dic, choose_regrid_option

from cancillary  import basin_average, mean_or_std, ensemble_stat, walsh_seasonality


from mips_et_al import table_for_var_and_experiment, project_for_experiment, project_for_model,\
     institute_for_model, mip_for_experiment, models_for_experiments, read_versions_dictionnary

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
                            tas=True,relative=True,must_have_vars=[], compute=False, house_keeping=False): 
    """
    Feed dic MODEL_CHANGES with change values for spatially aggregated TIME_STAT of VARIABLE 
    over basins listed in BASINS_DATA["basins"] (which can include "globe"); this with 
    respect to a REF_PERIOD and for a series of time SLICES in a given SCENARIO; and for the list of 
    models which, according to dict DATA_VERSIONS, which provide data for both experiments, 
    and both for VARIABLES and the variables in MUST_HAVE_VARS.
    List EXCLUDED_MODELS allows to discard models
    List INCLUDED_MODELS, if not None, limits models used
    
    TIME_STAT can be "mean" or "std"

    Structure of MODEL_CHANGES (which forgets about TABLE) is :
       model_changes[scenario][variable][time_stat][basin][period][model]=change_value
    
    Returns a dict of ensemble stats of changes across the ensemble of models, for STATS_LIST :
      ens_changes[basin][ensemble_stat][period] = stat_value
    For syntax and semantics of STATS_LIST, see function `py:func:cancillary.ensemble_stat()`

    BASINS_DATA is a dict with keys : 
      - basins : list of basin names for those basins to process
      - basins_file : filename for the file coding basins
      - basins_key : correspondance between basin names and basin numbers in basins_file
      
    Change values are relative changes, except if RELATIVE=False
    """
    
    lbasins=basins_data["basins"]
    
    # Compute variables values on ref_period and slices, 
    values=dict()
    if fprint : print "%6s %s %s %s"%(scenario,variable,table,time_stat),
    models=models_for_experiments(data_versions,variable,table,[scenario,ref_experiment],excluded_models,included_models)
    for model,variant in models :
        #if fprint : print "%6s %-15s %s"%(scenario,model,variable),
        if fprint : print " %s"%(model),
        for period in [ ref_period ] + slices :
            #if fprint : print "%s"%period[0:3],
            for basin in lbasins :
                if basin == "globe" :
                    value=cvalue(mean_or_std(scenario, ref_experiment, model, variant, "anm", variable, time_stat, table,
                                             period, data_versions,ccdo_fast,{"operator":"fldmean"},
                                             compute=compute,house_keeping=house_keeping))
                else:
                    value=cvalue(mean_or_std(scenario,ref_experiment,model,variant,"anm",variable,time_stat, table, 
                                             period, data_versions,basin_average,
                                             {"model":model,"basin":basin,"basins":basins_data,"compute":True},
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
    Returns a CliMAF ensemble of 1D fields representing the change for a VARIABLE along a PERIOD 
    of EXPERIMENT vs. a REF_PERIOD in another  REF_EXPERIMENT, for a list of MODELS

    The values are first yearly averaged and filtered on FILTER_LENGTH years

    DATA_VERSIONS, must be a  dictionnary with this structure (like provided by the notebook 
    in sibling directory data_versions) :

    >>> data_versions[experiment][variable][table][model]=(grid,variant,version,data_period)

     e.g.: 

     >>> data_versions["ssp245"]["pr"]["Amon"]["MPI-ESM1-2-HR"]=("gn","r1i1p1f1","v20190710","2015-2100")

    (data-period is used only for piControl)

    Tuned for CMIP6 only (yet). Use variable 'tas' in table 'Amon'

    Assumes that realization indices an grids are consistent among experiments for provided list of models 
    """
    #
    GSAT=cens()
    #
    for model,realization in models :
        grid,version,_=data_versions[experiment][variable][table][model][realization]
        print "Global_change - processing %20s %s %s"%(model,realization,version),
        dic=dict(project="CMIP6", experiment=experiment, model=model, 
                 institute=institute_for_model(model), period=period,
                 variable=variable, table=table_for_var_and_experiment(variable,experiment),
                 mip=mip_for_experiment(experiment),
                 realization=realization, version=version, grid=grid)
        filtered_tasmean=ccdo(ds(**dic),operator="runmean,%d -yearmean -fldmean"%filter_length)
        #
        _,version,_=data_versions[ref_experiment][variable][table][model][realization]
        ref=dic.copy()
        ref.update(experiment=ref_experiment, mip=mip_for_experiment(ref_experiment),
                   period=ref_period,version=version)
        ref_tasmean=ccdo(ds(**ref),operator="timmean -fldmean")
        cfile(ref_tasmean)
        ref=cvalue(ref_tasmean)
        print "GTAS = %g"%ref
        #
        GSAT[model]=ccdo_fast(filtered_tasmean,operator="subc,%g"%ref)
    #
    return GSAT


def change_fields(variable,experiments,seasons,ref_period,projection_period,
                  models_to_plot, data_versions, derivation_label=None,
                  relative=False, standardized=False, print_statistics=False,
                  ref_experiment="historical",
                  variab_sampling_args= {"house_keeping":True,"compute":True,"detrend":True,"shift":100,"nyears":20,"number":20},
                  common_grid=None,table=None,
                  models_with_enough_spinup=None,deep=False) :
    
    """
    Computes a series of change fields for one
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
      - "mean_rchange" is the ensemble mean of relative changes
      - "means_rchange" is the relative change of ensemble means
      - "median_rchange" is the ensemble median of relative changes

    Toggles STANDARDIZED activate the computation of change standardized by its 
    interannual variability. Field name suffix is "_schange"
      - "mean_schange" is the ensemble mean of standardized changes
      - "median_schange" is the ensemble median of standardized changes

    Argument MODELS_WITH_ENOUGH_SPINUPS provides a list of models
    which are supposed to have a sufficiently long spin-up period
    before published piControl data, so that the AR5 guidelines of
    discading the first 100 years of piControl can be relaxed (see function 
    variability_AR5)

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
        * median_variability, agreement_fraction,  stippling, hatching

    - field=dic[experiment][season][key][derivation_label][model]
      where key has values : reference, projection, change, rchange, schange, variability

    """
    aggregates=dict()
    dic=dict()

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
        #
        for season in seasons :
            if not print_statistics: print experiment,season,
            models=models_to_plot[experiment]
            for model,realization in models :
                change_fields_internal(dic,model,realization,variable,ref_period,
                            projection_period,ref_experiment,experiment,season,
                            derivation_label, relative,standardized,print_statistics,
                            variab_sampling_args,common_grid,table,
                            data_versions,models_with_enough_spinup,deep)
                if print_statistics : csync()
            #
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
                ref_ensavg=ccdo_ens(cens(dic[experiment][season]["reference"][derivation_label]),operator='ensmean')
                rmeans=ccdo2(ccdo2(ensavg,ref_ensavg,operator="sub"),ref_ensavg,operator="mulc,100 -div")
                feed(rmean,"means_rchange")
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
            # Compute figure masks
            #
            if variab_sampling_args != {} and variab_sampling_args is not None :
                if standardized :
                    agree_field="schange"
                    avg=smean
                else :
                    agree_field="change"
                    avg=ensavg
                agreef=agreement_fraction(cens(dic[experiment][season][agree_field][derivation_label]))
                feed(agreef,"agreement_fraction")
                medvar=ccdo_ens(cens(dic[experiment][season]["variability"][derivation_label]),operator='enspctl,50')
                feed(medvar,"median_variability")
                #
                s,h=stippling_hatching_masks_AR5(avg,medvar,agreef)
                feed(s,"stippling")
                feed(h,"hatching")
            #
            print
    return aggregates, dic



def change_fields_internal(dic,model,realization,variable,ref_period,
                           projection_period,ref_experiment,experiment,season,
                           derivation_label,relative,standardized,print_statistics,
                           variab_sampling_args,common_grid,table,
                           data_versions,models_with_enough_spinup,deep):
    """
    See function change_fields for documentation 
    """

    def feed(name,field):
            feed_dic(dic,field,experiment,season,name,derivation_label,model)

    if print_statistics :
        print "%s %s %-20s"%(experiment,season, model),
    else :
        print model,
    project=project_for_experiment(experiment)
    grid,version,_=data_versions[ref_experiment][variable][table][model][realization]
    roption=choose_regrid_option(variable,table,model,grid)
    derivation=derivations[derivation_label]
    #
    if  variab_sampling_args != {} and variab_sampling_args is not None :
        args=variab_sampling_args.copy()
        args.update(derivation)
        variability=variability_AR5(model,realization,variable,table,data_versions,
                                season=season,project=project, 
                                models_with_enough_spinup=models_with_enough_spinup,
                                **args)
        #
        if standardized :
            if "post_operator" in derivation or "operator" in derivation :
                raise ValueError("Cannot yet compute inter-annual variability "+\
                        "for a variable (%s) and a derivation (%s) which needs pre or post-processing"%\
                        (variable,derivation_label))
            inter_ann_var=control_inter_annual_variability(model,realization,variable,table,season,data_versions,**args)
            variability=ccdo2(variability,inter_ann_var,operator="div")
        #
        variability=regridn(variability,cdogrid=common_grid,**roption)
        feed("variability",variability)
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
    if relative  :
        if variable in ["pr","evspsbl", "P-E" ] and derivation_label not in ["dry","drain"] :
            zero_dot_1_mm_day=0.1/(24*3600) # in kg m2 s-1
            zero_dot_zero1_mm_day=0.01/(24*3600) # in kg m2 s-1
            epsilon=1.e-20
            #
            threshold=0.
            threshold=zero_dot_zero1_mm_day
            thresholded_reference=ccdo_fast(reference,operator="setrtomiss,-%f,%f"%(threshold,threshold))
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
        schange=ccdo2(change,inter_ann_var,operator="div")
        feed("schange_orig",schange)
        schange_remapped=regridn(schange,cdogrid=common_grid,**roption)
        feed("schange",schange_remapped)
    #
    if print_statistics :
        if variab_sampling_args != {} and variab_sampling_args is not None :
            variab_value=cvalue(ccdo_fast(variability,operator="fldmean"))
        else: 
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


 
def AR6_change_figure_with_caching(variable, experiment, season, 
                        data_versions_tag, data_versions_dir,
                        models=None, excluded_models=[],
                        ref_period="1995-2014", proj_period=None,
                        ref_experiment="historical",
                        table=None, field_type="mean_rchange",
                        derivation_label="plain", 
                        title=None, custom_plot={}, labelbar="True",
                        outdir=None, outfile=None,
                        print_statistics=True , deep=False, read=True, write=True, 
                        common_grid="r360x180", mask=None,
                        variab_sampling_args={"house_keeping":True, "compute":True,"detrend":True, "shift":100,"nyears":20,"number":20},
                        cache_dir="./aggregates",models_with_enough_spinup=["BCC-ESM1","CESM2-WACCM","CanESM5"],
                        drop=False
                        ) :
    """
    This is a wrapper around two functions :

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
    possible_models=models_for_experiments(data_versions,variable,table,
                                           ["piControl",ref_experiment,experiment],excluded_models,models)
    #
    models_dict={experiment:possible_models}
    # print 'models',models
    # print 'possible_models',possible_models
    # print 'models_dict',models_dict
    #
    aggregates={}
    read_failed=False
    if read and not deep :
        aggregates=read_aggregates(proj_period,data_versions_tag,cache_dir)
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
        print variable,derivations[derivation_label]
        aggregates,dic=change_fields(variable, experiments,seasons,ref_period,proj_period,
                                     models_dict, data_versions, derivation_label,
                                     relative,standardized,print_statistics,
                                     ref_experiment, variab_sampling_args,
                                     common_grid,table,
                                     models_with_enough_spinup)
        #
        #end_time = datetime.now()
        #duration = end_time - start_time
        #print "%6.2g seconds"%duration.total_seconds()
        if write and (not read or read_failed or deep) :
            dump_aggregates(aggregates,variable,derivation_label,proj_period,cache_dir,data_versions_tag,deep)
    #
    if title is None :
        title=field_type+" "+variable+" "+derivation_label+" "+season+" "+experiment
    field     = aggregates[variable][experiment][season][field_type] [derivation_label]
    if variab_sampling_args != {} and variab_sampling_args is not None :
        hatching  = aggregates[variable][experiment][season]["hatching"] [derivation_label]
        stippling = aggregates[variable][experiment][season]["stippling"][derivation_label]
    else :
        stippling,hatching="",""
    #
    relative = ( "_rchange" in field_type )
    plot1=AR6_change_figure(variable,derivation_label,field,stippling,hatching,
                            relative,labelbar,title,custom_plot,len(models_dict[experiment]),mask)
    if drop :
        cdrop(plot1)
    #
    if outfile is None :
        if outdir is None :
            raise Error("Must provide either outdir or outfile")
        if not os.path.exists(outdir) : os.makedirs(outdir)
        filename="%s/fig_%s_%s_%s_%s_%s_%s_%s.png"%(outdir,variable,derivation_label,experiment,
                                                season,field_type,proj_period,data_versions_tag)
    else:
        filename=outfile
    cfile(plot1,filename)
    print "Figure available as ",filename
    return filename,plot1,dic,possible_models

def dump_aggregates(aggregates,variable,derive,proj_period,cache_dir,data_versions_tag,deep=False) :
    """
    This is an ancillary function for AR6_change_figure_with_caching. See its doc
    """
    import os, os.path
    if not os.path.exists(cache_dir) : 
        os.makedirs(cache_dir)
    for exp in aggregates[variable] :
        for season in aggregates[variable][exp] :
            for field in aggregates[variable][exp][season] :
                ceval(aggregates[variable][exp][season][field][derive],deep=deep)
                cfile(aggregates[variable][exp][season][field][derive],
                      cache_dir+"/%s=%s=%s=%s=%s=%s=%s.nc"%(season,variable,exp,field,derive,proj_period,data_versions_tag),
                      ln=False)
                
def read_aggregates(proj_period,data_versions_tag,cache_dir) :
    """
    This is an ancillary function for AR6_change_figure_with_caching. See its doc
    """
    d=dict()
    import glob
    files=glob.glob(cache_dir+"/*=*=*=*=*=*=%s.nc"%data_versions_tag)
    #print files
    for f in files :
        bn=f.split("/")[-1]
        bn=bn.split(".")[0]
        bn=bn.split("=")
        season,variable,exp,field,derive,pperiod,_=bn
        if pperiod==proj_period :
            dataset=fds(f,period="1850-2100")
            # Need to erase cached value
            cdrop(dataset)
            feed_dic(d,dataset,variable,exp,season,field,derive)
    return d


def AR6_change_figure(variable, derivation_label, field, stippling="", hatching="", relative=True, labelbar="True",
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
    plot_args=dict(
        proj="Robinson", mpCenterLonF=2.0, gsnLeftString="", vcb=False,
        shading_options="gsnShadeHigh=3|gsnAddCyclic=True", shade_above=0.9, # Hatching for 1st mask
         # Stippling for 2nd mask
        shade2_options="gsnShadeHigh=17|gsnShadeFillScaleF=1|gsnShadeFillDotSizeF=0.004|gsnAddCyclic=True", 
        shade2_below=-0.1, shade2_above=0.9,
    )
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
        if variable in ["pr","P-E","mrro"] : return {"scale":24.*3600 }
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
        print var2,minmax(var2)
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
        stippling = apply_mask(stippling,mask)
        hatching  = apply_mask(hatching ,mask)
    return plot(field,hatching,"","",stippling,title=title, **plot_args)



