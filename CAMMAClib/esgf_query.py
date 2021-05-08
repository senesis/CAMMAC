"""
Two functions for querying the ESGF errata service and summarizing its results
"""

from __future__  import division, print_function 

import requests  # use pip or conda to install it if needed
import json
from datetime import datetime

def query_errata_service(dataset_drs,base_url="https://errata.es-doc.org/1/"):

    """
    Query the errata service for erratas on a dataset DRS, such as
    >>> dataset_drs="CMIP6.DAMIP.NASA-GISS.GISS-E2-1-G.hist-sol.r1i1p1f1.AERmon.bldep.gn.v20180912"
    and returns a list of pairs (severity, description) for relevant erratas
    """

    erratas=[]    
    resolve_url=base_url+"resolve/simple-pid?datasets="+dataset_drs
    r=requests.get(resolve_url)
    try :
        r=r.json()
    except ValueError :
        print("\nNo Json object for "+dataset_drs)
        return None
    if 'errorCode' not in r :
        for handle in r :
            l=r[handle]['errataIds']
            if type(l) != type([]) :
                l=eval(l)
            for uid in l :
                e=requests.get(base_url+"issue/retrieve?uid="+uid).json()['issue']
                erratas.append((e['severity'],e['description']))
    else :
        return None
    return erratas

def analyze_erratas(fn,max_count=None, do_print=True, panel=None, variable=None) :

    """
    Reads the kind of AR6 metadata file which describes data used for a figure (or figure panel) and
    query the ESGF errata service for all corresponding datasets
    
    Returns a dictionnary of experiment DRS with an errata, grouped that way :
    
    >>>  d[variable][severity][errata_description] = [ ... list of experiment DRS ...]
    
    Arg count allows to limit the number of requests to the errata service
    Arg variable allows to restrict the analysis to those metadata lines which are for a given variable
    Arg panel allows to restrict the analysis to those metadata lines which have a given panel label
    
    Example of a metadata file line: 
       CMIP6.CMIP.MPI-M.MPI-ESM1-2-HR.piControl   none   r1i1p1f1 Amon         pr  gn v20190710 ssp126 a 

    Note : sub-experiment ids are not (yet) handled
      
    """
    
    errata_base_url="https://errata.es-doc.org/1/"
    with open(fn) as fic : 
        lines=fic.readlines()
    count=0
    berrata2models=dict()
    variables=[]
    for line in lines :
        count+=1
        fields=line.split()
        if len(fields) >= 7 and fields[1]=='none' and (max_count==None or count <= max_count) :
            print(".",end='')
            expid=fields[0]
            variant=fields[2]
            table=fields[3]
            rvariable=fields[4]
            grid=fields[5]
            version=fields[6]
            if len(fields)>7:
                rpanel=fields[7]
            else: 
                rpanel=False
            if (panel is None or panel==rpanel) and (variable is None or variable==rvariable):
                drs="%s.%s.%s.%s.%s.%s"%(expid,variant,table,rvariable,grid,version)
                err_list=query_errata_service(drs,errata_base_url)
                if err_list is not None :
                    if rvariable not in berrata2models :
                        berrata2models[rvariable]=dict()
                    for severity,description in err_list :
                        if severity not in berrata2models[rvariable]:
                            berrata2models[rvariable][severity]=dict()
                        if description not in berrata2models[rvariable][severity] :
                            berrata2models[rvariable][severity][description]=set()
                        berrata2models[rvariable][severity][description].add(expid)
    print
    if do_print :
        for variable in berrata2models :
            print("variable",variable)
            for severity in berrata2models[variable] :
                print("\tseverity",severity)
                for description in berrata2models[variable][severity] :
                    print("\t\t",description,berrata2models[variable][severity][description])
    #
    berrata2models["Errata service query date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    berrata2models["Errata service query url"]  = errata_base_url
    #
    return berrata2models
