"""
Ancillary functions for :

  - managing dictionnaries of dictionnaries of dictionnaries of ...
  - converting acronyms to nice labels
  - handling labelbars (using ImageMagick's convert) : extract, assemble

"""
from __future__  import division, print_function 


import json, os, os.path

#: A dictionnary of pretty labels for some acronyms 
prettier_label={  
    "ssp119":"SSP1-1.9","ssp126":"SSP1-2.6","ssp245":"SSP2-4.5","ssp370":"SSP3-7.0","ssp585":"SSP5-8.5",
    #
    "DJF":"DJF","JJA":"JJA","ann":"All seasons","ANN":"All seasons",
    #
    "pr":"precipitation","P-E":"P-E","evspsbl":"evapotranspiration",
    "mrso":"soil moisture","mrsos":"soil surface moisture", "mrro":"runoff", "sos":"sea surface salinity",
    #
    "drain" : "daily precipitation intensity",
    "dry":"dry days per year",
    "ydrain" : "daily precipitation intensity",
    "ydry":"dry days per year",
    #
    "mean_change"  :"mean change"  , "mean_schange"  :"mean standardized change"  , "mean_rchange"  : "mean percentage change",
    "means_rchange"  : "percentage change of mean",
    "median_change":"median change", "median_schange":"median standardized change", "median_rchange": "median percentage change",
    #
} 

# A constant useful when defining dry days
one_mm_per_day="%g"%(1./(24.*3600.)) # in S.I.

def feed_dic(dic,value,*keys,**kwargs):
    """ 
    Similar to bash  'mkdir -p' for a dict() : creates intermediate levels of keys
    for storing value VALUE in dict DIC, as e.g. :
    
    >>> d=dict()
    >>> feed_dic(d,3,1,"q")
    >>> print("d=",d)
    d= {1: {"q": 3}}
    >>> feed_dic(d,'a',1,4,"key")
    >>> print("d=",d)
    d= {1: {"q": 3, 4: {"key" : 'a'}}}
    
    With keyword arg use_list=True, will rather assume that stored values are lists, 
    and so will append VALUE :
    
    >>> e=dict()
    >>> feed_dic(e,18,key1,key2,use_list=True)
    >>> feed_dic(e,19,key1,key2,use_list=True)
    >>> print("e=",e)
    e= {key1: {key2: [18, 19]}}
    
    With keyword arg extend_list=True, will also assume that stored values are lists, 
    and that VALUE is a list, and concatenate it with value in dic

    With keyword arg use_count=True, will rather increment the dic value with VALUE 
    (starting from 0) :
    
    >>> e=dict()
    >>> feed_dic(e,2,"qq",3,use_count=True)
    >>> feed_dic(e,100,"qq",3,use_count=True)
    >>> print("e=",e)
    e= {"qq": {3: 102}}

    """
    if len(keys)==0 :
        raise ValueError("Must provide at least one key")
    for kw in kwargs :
        if kw not in [ "use_list","use_count","extend_list" ]:
            raise ValueError("Unknown keyword argument %s"%kw)
    #
    use_list     = kwargs.get('use_list'    ,False)
    extend_list  = kwargs.get('extend_list' ,False)
    use_count    = kwargs.get('use_count'   ,0)
    #        
    if extend_list and type(value) != list :
        raise ValueError("Cannot extend at leaf level in list mode with a non-list value : %s"%(str(value)))
    #
    d=dic
    level=0
    for k in keys[:-1] :
        level+=1
        if k not in d :
            d[k]=dict()
        if type(d) != type(dict()) :
            raise ValueError(str(d)+" is already a value, can't be a key!")
        d=d[k]
        if type(d) != type(dict()) :
            raise ValueError("There is already a non-dict value (%s) for key %s at level %d"%(str(d),k,level))
    #
    if use_list or use_count or extend_list :
        if keys[-1] in d :
            leaf=d[keys[-1]]
            if use_list :
                if type(leaf) != list :
                    raise ValueError("Cannot append %s at leaf level in list mode, value there is not a list : %s"%(value,leaf))
                else :
                    leaf.append(value)
            elif extend_list :
                if type(leaf) != list :
                    raise ValueError("Cannot expent %s at leaf level in list mode, value there is not a list : %s"%(value,leaf))
                else :
                    leaf.extend(value)
            elif use_count :
                if type(leaf) != int :
                    raise ValueError("Cannot increment at leaf level in count mode, value there is not an int %s"%(leaf))
                else :
                    d[keys[-1]] += value
        else :
            if use_list :
                d[keys[-1]] = [ value ]
            elif extend_list :
                d[keys[-1]] = value
            elif use_count :
                if type(value) != int :
                    raise ValueError("Cannot init count at leaf level in count mode, with a non-int value %s"%(value))
                else :
                    d[keys[-1]] = value
    else:
        d[keys[-1]]=value


def amail(text,subject="The subject",to=["senesi@posteo.net"], sender="job_on_ciclad@anymail.fr"):
    import smtplib
    from email.mime.text import MIMEText
    #
    msg=MIMEText(text)
    msg["Subject"]=subject
    msg["From"]=sender
    msg["To"]=str(to)
    #
    S=smtplib.SMTP()
    S.connect()
    S.sendmail(sender,to,msg.as_string())


def choose_regrid_option(variable,table,model,grid):
    """
    Want to use a Cdo regrid option which can deal with published grid for Nemo, which has a band 
    of missing values in Indian Ocean
    The return value is a dict of arg/values for regridn
    """
    default = {"option" : "remapcon"}   
    if table != "Omon":
        return default
    elif model not in [ "CNRM-CM6-1", "CNRM-ESM2-1", "CNRM-CM6-1-HR", "IPSL-CM6A-LR", # Nemo Grid
                        "EC-Earth3",  "EC-Earth3-LR" ,
                        "EC-Earth3-CC", "EC-Earth3-AerChem",
                        "EC-Earth3P",  "EC-Earth3P-HR",
                        "EC-Earth3-Veg", "EC-Earth3-Veg-LR", 

                        "MPI-ESM1-2-HR","MPI-ESM1-2-LR","MPI-ESM1-2-XR","MPI-ESM-1-2-HAM", #
                        "NESM3",
                        "BCC-ESM1", "BCC-CSM2-MR", "FGOALS-f3-L", "FGOALS-g3", # Source grid cell corner coordinates missing
                        "AWI-CM-1-1-MR" ,
                        "CMCC-CM2-SR5" ,# this one generates CDO error "ERROR: invalid cell"
                        "HadGEM3-GC31-MM" , # ERROR: invalid cell
                        "HadGEM3-GC31-LL" , # ERROR: invalid cell
                        "IITM-ESM", # Source grid cell corner coordinates missing!
    ]:
        return default
    elif grid[0:2] == "gr":
        return default
    else :
        return {"option" : "remapdis"}
    


def extract_labelbar(figure_file, labelbar_file, y_offset=630) :
    """ Extract labelbar from FIGURE_FILE using external process and 
    put it in LABELBAR_FILE. Use Y_OFFSET, an offset on y axis, for 
    skipping the map part of the figure file. 
    Default y_offste value is OK with Ncl maps as long as they have a 'right string'
    """
    os.system("convert %s +repage -crop +0+%d -trim %s"%(figure_file,y_offset,labelbar_file))

def concatenate_labelbars(lbfile1,lbfile2,lbfile) :
    """ Just put side-by-side the two figures in LBFILE1 and LBFILE2, producing LBFILE"""
    # 
    os.system("convert -size 1650x100 xc:white %s -geometry 1100x100 -composite "%lbfile1 +
              " %s -geometry x100+550+0 -composite -trim %s"%(lbfile2,lbfile))

    
def create_labelbar2(figure_file1,figure_file2,out_file,missing=True,
                     captions_dir=None,width=2100,height=130,scheme="AR6",y_offset=630,ratio=4.):

    """ Combine the labelbar part of FIGURE_FILE1 and FIGURE_FILE2 with a 
    third picture showing the legend relevant for the AR5 or AR6 hatching scheme  
    SCHEME can be AR5, AR6, AR6S (AR6 simple approach) or KS13 (Knutti & Sedlaceck 2013)
    Y_OFFSET is used for extracting labelbars (see fucntion extract_labelbars)
    WIDTH and HEIGHT are the target sizes for the output
    """

    # Extract labelbar from figure_file 
    extract_labelbar(figure_file1,"tmp_labelbar1.png",y_offset)
    extract_labelbar(figure_file2,"tmp_labelbar2.png",y_offset)
    
    # Combine with legend for shadings
    if captions_dir is None :
        captions_dir=os.path.dirname(os.path.abspath( __file__ ))+"/captions/"
    if scheme=="AR5" :
        if missing : caption="caption_signif_missing.png"
        else:        caption="caption_signif_centre.png"
    elif scheme=="AR6" :
        caption="AR6_hatching_legend.png"
    elif scheme in [ "AR6S" , "KS13" ] :
        caption="AR6S_hatching_legend.png"
    else :
        raise ValueError("Unknown hatching scheme %s"%scheme)
    shading_caption=captions_dir+caption

    if scheme != "AR6S" :
        # Divide width in segments 
        signif_width=width//7
        lbwidth= 3*signif_width
        margin=signif_width/6
    else:
        # Divide width in segments 
        signif_width=int(float(width)/ratio)
        lbwidth= int((width-signif_width)/2.)
        margin=signif_width/10
    signif_width = width - 2 * ( lbwidth + margin )

    if height is None : height=width/16
    command="rm -f %s ; "%out_file +\
              "convert -size %dx%d xc:white "%(width,height)+\
              " \( tmp_labelbar2.png -scale %dx%s -geometry +%d+0 \)  -composite "%\
              (lbwidth,height,lbwidth+signif_width) +\
              " \( %s                -scale %dx%d -geometry +%d-0  \)  -composite "%\
              (shading_caption,signif_width-2*margin,height,lbwidth+margin) +\
              " \( tmp_labelbar1.png -scale %dx%d -geometry +0+0    \)  -composite "%\
              (lbwidth,height) +\
              " -trim "+out_file
    print(command)
    os.system(command)
    #os.system("rm tmp_labelbar1.png  tmp_labelbar2.png")


def create_labelbar(figure_file,out_file,missing=True,captions_dir=None,width=1200,height=130,scheme="AR6",y_offset=630):

    """ Combine the labelbar part of FIGURE_FILE with a 
    third picture showing the legend relevant for the AR5 or AR6 hatching scheme  
    SCHEME can be AR5, AR6, AR6S (AR6 simple approach) or KS13 (Knutti & Sedlaceck 2013)
    Y_OFFSET is used for extracting labelbars (see fucntion extract_labelbars)
    WIDTH and HEIGHT are the target sizes for the output
    """
    # Extract labelbar from figure_file 
    extract_labelbar(figure_file,"tmp_labelbar.png",y_offset)
    
    # Combine with legend for shadings
    if captions_dir is None :
        captions_dir=os.path.dirname(os.path.abspath( __file__ ))+"/captions/"
        
    if scheme=="AR5" :
        if missing : caption="caption_signif_missing.png"
        else:        caption="caption_signif_centre.png"
    elif scheme=="AR6" :
        caption="AR6_hatching_legend.png"
    elif scheme in [ "AR6S" , "KS13" ] :
        caption="AR6S_hatching_legend.png"
    else :
        raise ValueError("Unknown hatching scheme %s"%scheme)
    shading_caption=captions_dir+caption

    # signif captions size is 314x175
    # label bars size is 872x130 (for page_width=2450,page_height=3444)

    # Divide width in segments : 3+1+3
    if scheme !=  "AR6S" :
        signif_width=width//4
        lbwidth= 3*signif_width
        margin=signif_width//8
    else :
        signif_width=width/3
        lbwidth= 2*signif_width
        margin=signif_width//10
    signif_width = width - lbwidth - margin 
        
    if height is None : height=width/16
    command="rm -f %s ; "%out_file +\
              "convert -size %dx%d xc:white "%(width,height)+\
              " \( %s                -scale %dx%d -geometry +%d-0  \)  -composite "%\
              (shading_caption,signif_width,height,lbwidth+margin) +\
              " \( tmp_labelbar.png -scale %dx%d -geometry +0+0    \)  -composite "%\
              (lbwidth,height) +\
              " -trim "+out_file
    os.system(command)
    os.system("rm tmp_labelbar.png")


