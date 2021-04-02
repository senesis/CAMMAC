"""

CAMMAC ancilliary functions for :
  - handling CMIP6 data, experiments, tables, their models and institutes
  - handling data versions 


"""
import json

from ancillary import feed_dic

def read_versions_dictionnary(tag,directory=None) :
    """ 
    Dictionnary of data versions for each variable,table and model are computed 
    and written based on a notebook in another directory 'data_versions'
    This is the companion 'read' function

    Default directory for data_versions dicts is the same brother directory 
    """ 
    if directory is None :
        import os.path
        directory=os.path.dirname(os.path.dirname(os.path.abspath( __file__ )))+"/data_versions"
    with open("%s/Data_versions_selection_%s.json"%(directory,tag),"r") as f :
        d=json.load(f)
    return d


def models_for_experiments(dic,variable,table,experiments,excluded_models=[],included_models=None,one_per_model=True):
    """ 
    Provided with DIC a dictionnary of data versions, and a VARIABLE name, returns 
    a list of (model,variant) pairs that have data for VARIABLE and for all EXPERIMENTS 
    (according to DIC), and the same variant index for all EXPERIMENTS for one given model
    (excluding piControl re. variant)

    There is only one variant returned  per model, preferentially a 'r1' 

    The structure of the dictionnary should be as follow 
    dic[experiment][variable][table][model][realization] = (grid,anything,anything) 
    """

    if included_models=="None":
        included_models=None        
    
    # Store available realizations per model and exp
    variants=dict()
    for exp in experiments :
        for model in dic[exp][variable][table] :
            if included_models is None or model in included_models :
                #print "adding for model:",model
                for real in dic[exp][variable][table][model].keys() :
                    feed_dic(variants,dic[exp][variable][table][model][real],model.encode('ascii'),exp,real)
    # for m in variants :
    #     print m 
    #     for exp in variants[m] :
    #         print exp, variants[m][exp]
    #     print
    return choose_variant(variants,experiments,excluded_models,included_models)

def models_for_experiments_multi_var(dic,variable_table_pairs,experiments,excluded_models=[],included_models=None):
    """ 
    Same as models_for_experiments() but for a list of (variable,table) pairs
    """

    if included_models=="None":
        included_models=None        
    
    # Store available realizations per model and exp which have data for all variables
    # We use first variable,table pair as pivot
    variable,table=variable_table_pairs[0]
    variants=dict()
    #
    for exp in experiments :
        try :
            a=dic[exp][variable][table]
        except :
            print exp,variable,table
            raise ValueError("")
        for model in dic[exp][variable][table] :
            for real in dic[exp][variable][table][model].keys() :
                ok=True
                for var,tab in variable_table_pairs[1:] :
                    try :
                        a=dic[exp][var][tab][model][real]
                    except:
                        ok=False
                if ok :
                    feed_dic(variants,dic[exp][variable][table][model][real],model.encode('ascii'),exp,real)

    return choose_variant(variants,experiments,excluded_models,included_models)


def choose_variant(variants,experiments,excluded_models,included_models):

    """
    Provided with VARIANTS, a dict of variants , which keys are model and experiments, 
    and values are lists of available variants

    And EXPERIMENTS, a list of experiments

    Choose a variant common to all experiments but piControl, preferring ...
    """

    pairs=[]
    # Loop on models OK vs constraints, and having variant(s) for all experiments
    for model in variants :
        if model not in excluded_models and \
           (included_models is None or model in included_models) and \
           set(variants[model]) == set(experiments) :
            
            chosen_variant=None
            
            # Then search for common variants (excepting piControl)
            exps=[ e for e in experiments ]
            if "piControl" in experiments and len(experiments)>1 :
                exps.remove("piControl")
                    
            variants_set=set(variants[model][exps[0]])
            for exp in exps[1:] :
                variants_set   = variants_set.intersection(set(variants[model][exp]))
            if len(variants_set) > 0 :
                chosen_variant = prefered_variant(variants_set,experiments,model)
                if chosen_variant is None :
                    # a prefered variant was not found ; keep any variant
                    chosen_variant=variants_set.pop()
                pairs.append((model,chosen_variant))
        # else:
        #     print "model %s does not fit"%model , set(variants[model]), set(experiments) , included_models, excluded_models      
                
    pairs.sort(cmp=lambda x,y : cmp(x[0],y[0]))
    return pairs

def prefered_variant (variants_set,experiments,model) :
    chosen_variant=None
    if len(variants_set) > 0 :
        # Preferentially keep a "r1" variant
        r1s=[]
        for variant in variants_set :
            if variant[0:3]=="r1i" :
                r1s.append(variant)
        if len(r1s) > 0 :
            if len(r1s) == 1  :
                chosen_variant=r1s[0]
            else:
                # Preferentially keep a "r1i1" variant
                r1i1s=[]
                for variant in r1s :
                    if "r1i1p" in variant:
                        r1i1s.append(variant)
                if len(r1i1s) > 0 :
                    if len(r1i1s) == 1  :
                        chosen_variant=r1i1s[0]
                    else:
                        # Preferentially keep a "r1i1p1" variant
                        r1i1p1s=[]
                        for variant in r1i1s :
                            if "r1i1p1f" in variant:
                                r1i1p1s.append(variant)
                        if len(r1i1p1s) > 0 :
                            if len(r1i1p1s) == 1  :
                                chosen_variant=r1i1p1s[0]
                            else:
                                if "r1i1p1f1" in r1i1p1s :
                                    chosen_variant="r1i1p1f1"
                                else: 
                                    raise ValueError("Should handle preference among forcing index for %s %s %s"%\
                                                     (experiments,model,`r1i1p1s`))
        else :
            # Choose any variant among those with lowest 'r' index
            rmin=10000
            for variant in variants_set :
                r=int(variant[1:variant.find("i")])
                if r < rmin :
                    chosen_variant=variant
                    rmin=r
    return chosen_variant


def TSU_metadata(experiments,models,variable,table,data_versions,panel_letter=None,project="CMIP6",mip=None,subexp="none"):
    """
    Returns, as a string, the lines of metadata describing the
    datasets used for a list of EXPERIMENTS, a VARIABLE and MODELS (a
    list of (model,variant) pairs), by querying dictionnary
    DATA_VERSIONS for the version used. This in the format defined by
    AR6/WGI Technical Support Unit. PANEL_LETTER is a string written
    at end of line 

    Example for one line of output : 

    CMIP6.CMIP.BCC.BCC-CSM2-MR.piControl  none         gn Amon    evspsbl r1i1p1f1 v20181016 a

    """
    examples_of_metadata_filename="""
      Fig1-1_md      (for Figure 1.1)
      CCB1-1_Fig1_md (for Cross-Chapter Box 1.1, Figure 1)
      Box1-1_Fig1_md (for Box 1.1, Figure 1)
      FAQ1-1_Fig1_md (for FAQ1.1, Figure 1)
      FigTS-1_md     (for Figure TS.1)
      BoxTS-1_Fig1_md(for Box TS.1, Figure 1)
      FigSPM-1_md    (for Figure SPM.1)
    """

    rep=""
    if type(experiments) != type([]) :
        experiments=[experiments]
    for experiment in experiments :
        for model,variant in models :
            if mip is None :
                mip2 = mip_for_experiment(experiment)
            else :
                mip2=mip
            institute = institute_for_model(model,mip2)
            drs='%s.%s.%s.%s.%s'%(project,mip,institute,model,experiment)
            realization=variant
            if table == 'yr' :
                if variable in [ 'dday' , 'drain' ]:
                    table = 'day'
                    variable = 'pr'
                else :
                    raise ValueError("Cannot process variable %s in table 'yr' ")
            if experiment=="piControl" and variant not in data_versions[experiment][variable][table][model] :
                realization=data_versions[experiment][variable][table][model].keys()[0]
            try :
                grid,version,_=data_versions[experiment][variable][table][model][realization]
            except :
                raise ValueError("Cannot get data_version for %s %s %s %s %s "%(experiment,variable,table,model,realization))
            if variable != "P-E" :
                pairs=[ (variable,version) ]
            else :
                # CliMAF has set 'last' for evspsbl version -> Search for version of evspsbl
                # in data_versions, assuming that last version is the unique one
                _,evspsbl_version,_= data_versions[experiment]['evspsbl'][table][model][realization]
                pairs=[ ('pr',version) , ('evspsbl',evspsbl_version) ]
            for vari,vers in pairs :
                rep+="%-60s %6s %10s %4s %10s %3s %9s"%(drs,subexp,realization,table,vari,grid,vers)
                if panel_letter is not None :
                    rep+=" "+panel_letter
                rep += "\n"
    return rep
    
def project_for_experiment(experiment):
    if experiment in ["ssp119", "ssp126","ssp245", "ssp370","ssp585","rcp85","piControl","historical"] :
        return "CMIP6"
    elif experiment in ["rcp85"] : return "CMIP5"
    raise ValueError("Cannot tell which project defined  experiment "+experiment)
    

def mip_for_experiment(experiment):
    if experiment[0:3]=="ssp" :
        return "ScenarioMIP"
    if experiment=="piClim-ghg" :
        return "RFMIP"
    if experiment in ["historical", "piControl" ,"1ptCO2" ] :
        return "CMIP"
    raise ValueError("Cannot yet tell which MIP defined experiment "+experiment)

def table_for_var_and_experiment(variable,experiment):
    if experiment in ["ssp119", "ssp126","ssp245", "ssp370","ssp585","rcp85","piControl","historical"] :
        table="Amon"
        if variable in ["mrso","mrro","mrsos"] : 
            table="Lmon"
        if variable in ["snw","snc"] : 
            table="LImon"
        if variable in ["sos","tos"] : 
           table="Omon"
	if variable=="pr_day" :
	      table="day"
    else :
        table=None
    return table


models_data = {
    # Tells which are the project and institute for each model.
    # Third field, which is the start date for piControl, is no more used and then values here are not reliable
    
    "ACCESS-CM2"    : ("CMIP6","CSIRO-ARCCSS"     ,None),
    "ACCESS-ESM1-5" : ("CMIP6","CSIRO"            ,None),
#    "ACCESS1-CM2"   : ("CMIP6","CSIRO-ARCCSS"     ,None),
    "AWI-CM-1-1-MR" : ("CMIP6","AWI"		  ,2398) ,
    "AWI-ESM-1-1-LR": ("CMIP6","AWI"    	  ,None) , 
    "BCC-CSM2-HR"   : ("CMIP6","BCC"		  ,1850) ,
    "BCC-CSM2-MR"   : ("CMIP6","BCC"		  ,1850) ,
    "BCC-ESM1"      : ("CMIP6","BCC"		  ,1850) ,
    "CAMS-CSM1-0"   : ("CMIP6","CAMS"		  ,2900) ,  # nota : ne produit pas huss
    "CAS-ESM2-0"    : ("CMIP6","CAS"    	  ,None) , 
    "CESM1-1-CAM5-CMIP5" :("CMIP6","NCAR"	  ,None) ,
    "CESM1-1-CAM5-SE-HR" :("CMIP6","NCAR"	  ,None) ,
    "CESM1-1-CAM5-SE-LR" :("CMIP6","NCAR"	  ,None) ,
    "CESM2"	    : ("CMIP6","NCAR"		  ,   1) ,
    "CESM2-FV2"     : ("CMIP6","NCAR"		  ,   0) , # nota : demarre a 1, mais on ne saute que les 99 premieres annees, pour avoir 400 apres
    "CESM2-WACCM"   : ("CMIP6","NCAR"		  ,   0) , # nota : demarre a 1, mais on ne saute que les 99 premieres annees, pour avoir 400 apres
    "CESM2-WACCM-FV2":("CMIP6","NCAR"		  ,   0) , # nota : demarre a 1, mais on ne saute que les 99 premieres annees, pour avoir 400 apres
    "CIESM"         : ("CMIP6","THU"      	  ,None) , 
    "CNRM-CM6-1"    : ("CMIP6","CNRM-CERFACS"	  ,1850) , # manque evspsbl avant 2050, et sur une periode de 20 ans
    "CNRM-CM6-1-HR" : ("CMIP6","CNRM-CERFACS"	  ,1850) , 
    "CNRM-ESM2-1"   : ("CMIP6","CNRM-CERFACS"	  ,1850) ,
    "CanESM5"       : ("CMIP6","CCCma"		  ,5600) , # des manques pour pr et mrso
    "CanESM5-CanOE" : ("CMIP6","CCCma"		  ,None) , # des manques pour pr et mrso
    "CMCC-ESM2"     : ("CMIP6","CMCC"		  ,None) ,
    "CMCC-CM2-SR5"  : ("CMIP6","CMCC"		  ,None) ,
    "CMCC-CM2-HR4"  : ("CMIP6","CMCC"             ,None) ,
    "CMCC-CM2-VHR4" : ("CMIP6","CMCC"             ,None) ,
    "E3SM-1-0"      : ("CMIP6","E3SM-Project"	  ,1), 
    "E3SM-1-1"      : ("CMIP6","E3SM-Project"	  ,1850), 
    "E3SM-1-1-ECA"  : ("CMIP6","E3SM-Project"	  ,   None) , 
    "EC-Earth3"	    : ("CMIP6","EC-Earth-Consortium",2259) , # pas de pr pour historical (a verifier)
    "EC-Earth3-CC"  : ("CMIP6","EC-Earth-Consortium",None) , 
    "EC-Earth3-LR"  : ("CMIP6","EC-Earth-Consortium",None) , 
    "EC-Earth3P"    : ("CMIP6","EC-Earth-Consortium",None) , 
    "EC-Earth3P-HR" : ("CMIP6","EC-Earth-Consortium",None) , 
    "EC-Earth3-Veg" : ("CMIP6","EC-Earth-Consortium",1850) ,
    "EC-Earth3-Veg-LR":("CMIP6","EC-Earth-Consortium",None) ,
    "EC-Earth3-AerChem":("CMIP6","EC-Earth-Consortium",None) ,
    "FGOALS-f3-L"   : ("CMIP6","CAS"		  , 600) , 
    "FGOALS-g3"     : ("CMIP6","CAS"		  , 200) , 
    "FIO-ESM-2-0"   : ("CMIP6","FIO-QLNM"	  ,301) ,
    "GFDL-AM4"	    : ("CMIP6","NOAA-GFDL"	  ,None) , 
    "GFDL-CM4"	    : ("CMIP6","NOAA-GFDL"	  , 151) , # n'a pas fait ssp585, seulement ssp126 (en oct 2019, sur /bdd)
    "GFDL-ESM4"	    : ("CMIP6","NOAA-GFDL"	  ,   1) ,
    "GISS-E2-1-G"   : ("CMIP6","NASA-GISS"	  ,4150), 
    "GISS-E2-1-G-CC": ("CMIP6","NASA-GISS"	  ,None), 
    "GISS-E2-1-H"   : ("CMIP6","NASA-GISS"	  ,3180), 
    "GISS-E2-2-G"   : ("CMIP6","NASA-GISS"	  ,None) , 
    "HadGEM3-GC31-LL":("CMIP6","MOHC"		  ,1850) ,
    "HadGEM3-GC31-MM":("CMIP6","MOHC"		  ,1850) ,
    "IITM-ESM"      : ("CMIP6","CCCR-IITM"        ,1926) ,
    "INM-CM4-8"     : ("CMIP6","INM"		  ,1850) ,
    "INM-CM5-0"     : ("CMIP6","INM"		  ,1996) ,
    "INM-CM5-H"     : ("CMIP6","INM"		  ,1996) ,
    "IPSL-CM6A-ATM-HR": ("CMIP6","IPSL"		  ,1850) ,
    "IPSL-CM6A-LR"  : ("CMIP6","IPSL"		  ,1850) ,
    "IPSL-CM6A-LR-INCA": ("CMIP6","IPSL"		  ,1850) ,
    "IPSL-CM5A2-INCA":("CMIP6","IPSL"		  ,None) ,
    "IPSL-CM7A-ATM-LR": ("CMIP6","IPSL"		  ,1850) ,
    "IPSL-CM7A-ATM-HR": ("CMIP6","IPSL"		  ,1850) ,
    "4AOP-V1-5"     :("CMIP6","IPSL"		  ,None) ,
    "KACE-1-0-G"    : ("CMIP6","NIMS-KMA"	  ,None) , 
    "MCM-UA-1-0"    : ("CMIP6","UA"		  ,   1) , 
    "MIROC-ES2L"    : ("CMIP6","MIROC"		  ,1850) ,
    "MIROC-ES2H"    : ("CMIP6","MIROC"		  ,1850) ,
    "MIROC-ES2H-NB"    : ("CMIP6","MIROC"		  ,1850) ,
    "MIROC6"	    : ("CMIP6","MIROC"		  ,3200) ,
    "MPI-ESM-1-2-HAM":("CMIP6","HAMMOZ-Consortium",None) , 
    "MPI-ESM1-2-HR" : ("CMIP6","MPI-M"		  ,1850) ,
    "MPI-ESM1-2-LR" : ("CMIP6","MPI-M"		  ,None) ,
    "MPI-ESM1-2-XR" : ("CMIP6","MPI-M"		  ,None) ,
    "MPI-ESM1-2-HR" : ("CMIP6","MPI"		  ,None) ,
    "MRI-ESM2-0"    : ("CMIP6","MRI"		  ,1850) ,
    "NESM3"	    : ("CMIP6","NUIST"		  , 500) , #des periodes de piControl non publiees. Mail fait
    "NICAM16-7S"    : ("CMIP6","NIMS-KMA"	  ,None) , 
    "NICAM16-8S"    : ("CMIP6","NIMS-KMA"	  ,None) , 
    "NorCPM1"       : ("CMIP6","NCC"	          ,   1), 
    "NorESM1-F"     : ("CMIP6","NCC"	          ,1501), 
    "NorESM2-LM"    : ("CMIP6","NCC"	          ,1600), 
    "NorESM2-MM"    : ("CMIP6","NCC"	          ,None), 
    "SAM0-UNICON"   : ("CMIP6","SNU"	          ,   1), 
    "TaiESM1"       : ("CMIP6","AS-RCEC"	  ,None) , 
    "UKESM1-0-LL"   : ("CMIP6","MOHC"		  ,1960) ,
    #
    # Pour RCP85, cf fonction dans periodes_pic_hisr_pour_var_rcp85 dans 
    # script CS/periodes_picontrol_histo_pour_SSPs.sh
    "bcc-csm1-1-m"  :("CMIP5","BCC"		  ,-99) ,
    "bcc-csm1-1"    :("CMIP5","BCC"		  ,1) ,
    "BNU-ESM"	    :("CMIP5","BNU"		  ,1450) , # pas de realm atmos pour historical
    "CanESM2"	    :("CMIP5","CCCma"		  ,2015) ,
    "CMCC-CESM"	    :("CMIP5","CMCC"		  ,None) ,
    "CMCC-CM"	    :("CMIP5","CMCC"		  ,None) ,
    "CMCC-CMS"	    :("CMIP5","CMCC"		  ,3684) ,
    "CNRM-CM5"	    :("CMIP5","CNRM-CERFACS"	  ,1850) ,
    "ACCESS1-0"     :("CMIP5","CSIRO-BOM"         ,None),
    "ACCESS1-3"     :("CMIP5","CSIRO-BOM"         ,None),
    "CSIRO-Mk3-6-0" :("CMIP5","CSIRO-QCCCE"	  ,1) ,
    "FIO-ESM"	    :("CMIP5","FIO"		  ,401) ,
    "FGOALS-g2"     :("CMIP5","LASG-CESS"         ,700) , 
    "EC-EARTH"      :("CMIP5","ICHEC"             ,None),
    "inmcm4"        :("CMIP5","INM"               ,None),
    "IPSL-CM5A-LR"  :("CMIP5","IPSL"		  ,1800) ,
    "IPSL-CM5A-MR"  :("CMIP5","IPSL"		  ,None) ,
    "IPSL-CM5B-LR"  :("CMIP5","IPSL"		  ,None) ,
    "FGOALS-g2   "  :("CMIP5","LASG-CESS"	  ,None) ,
    "FGOALS-s2"	    :("CMIP5","LASG-IAP"	  ,1850) ,
    "MIROC5"	    :("CMIP5","MIROC"		  ,2000) , 
    "MIROC-ESM"	    :("CMIP5","MIROC"		  ,1800) ,
    "MIROC-ESM-CHEM":("CMIP5","MIROC"		  ,None) ,
    "HadGEM2-CC"    :("CMIP5","MOHC"		  ,None) ,
    "HadGEM2-ES"    :("CMIP5","MOHC"		  ,1859) ,
    "MPI-ESM-LR"    :("CMIP5","MPI-M"		  ,1850) ,
    "MPI-ESM-MR"    :("CMIP5","MPI-M"		  ,1850) , 
    "MRI-CGCM3"	    :("CMIP5","MRI"		  ,1851) ,
    "MRI-ESM1"	    :("CMIP5","MRI"		  ,None) ,
    "GISS-E2-H-CC"  :("CMIP5","NASA-GISS"	  ,None), 
    "GISS-E2-H"     :("CMIP5","NASA-GISS"	  ,None), 
    "GISS-E2-R-CC"  :("CMIP5","NASA-GISS"	  ,None), 
    "GISS-E2-R"	    :("CMIP5","NASA-GISS"	  ,8706), # en fait,  a fait 450 ans a/c de 8756 
    "CCSM4"	    :("CMIP5","NCAR"		  ,250) ,
    "NorESM1-ME"    :("CMIP5","NCC"		  ,None) ,
    "NorESM1-M"	    :("CMIP5","NCC"		  ,700) ,
    "HadGEM2-AO"    :("CMIP5","NIMR-KMA"	  ,1) ,
    "GFDL-CM3"	    :("CMIP5","NOAA-GFDL"	  ,1) , # 
    "GFDL-ESM2G"    :("CMIP5","NOAA-GFDL"	  ,1) , 
    "GFDL-ESM2M"    :("CMIP5","NOAA-GFDL"	  ,1) , 
    "CESM1-BGC"	    :("CMIP5","NSF-DOE-NCAR"	  ,101) ,
    "CESM1-CAM5-1-FV2":("CMIP5","NSF-DOE-NCAR"	  ,None) ,
    "CESM1-CAM5"    :("CMIP5","NSF-DOE-NCAR"	  ,None) ,
    "CESM1-WACCM"   :("CMIP5","NSF-DOE-NCAR"	  ,None) ,
}

    
def project_for_model(model):
    if "/" in model :
        model=model.split("/")[1]
    return models_data[model][0]


def institute_for_model(model,mip=None):
    if "/" in model :
        model=model.split("/")[1]
    if model=="MPI-ESM1-2-HR" :
       if mip == "ScenarioMIP" :
        return "DKRZ"
       elif mip in [ "CMIP","DCPP"] :
        return "MPI-M"
       else :
        return "*"
    return models_data[model][1]

def piControl_begin(model):
    if "/" in model :
        model=model.split("/")[1]
    return models_data[model][2]

