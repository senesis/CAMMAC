"""

CAMMAC ancillary functions for :

  - managing dictionnaries of dictionnaries of dictionnaries of ...
  - converting acronyms to nice labels
  - handling labelbars (using ImageMagick's convert) : extract, assemble

"""


import json, os, os.path

# A dictionnary of pretty labels for some acronyms
prettier_label={
    "ssp126":"SSP1-1.9","ssp126":"SSP1-1.9","ssp245":"SSP2-4.5","ssp585":"SSP5-8.5",
    #
    "DJF":"DJF","JJA":"JJA","ann":"All seasons","ANN":"All seasons",
    #
    "pr":"precipitation","P-E":"P-E","evspsbl":"evapotranspiration",
    "mrso":"Soil moisture","mrsos":"soil surface moisture", "mrro":"runoff", "sos":"sea surface salinity",
    #
    "drain" : "daily precipitation intensity",
    "dry":"dry days per year",
    #
    "mean_change"  :"mean change"  , "mean_schange"  :"mean standardized change"  , "mean_rchange"  : "mean percentage change",
    "means_rchange"  : "percentage change of mean",
    "median_change":"median change", "median_schange":"median standardized change", "median_rchange": "median percentage change",
    #
}

# A constant useful when defining dry days
one_mm_per_day="%g"%(1./(24.*3600.)) # in S.I.

def feed_dic(dic,value,*keys):
    """ 
    Similar to bash  'mkdir -p' for a dict() : creates intermediate levels of keys
    for storing value VALUE in dict DIC, as e.g. :
    
    >>> d=dict()
    >>> feed_dic(d,3,1,2)
    >>> print "d=",d
    d= {1: {2: 3}}
    >>> feed_dic(d,"a",1,3,4)
    >>> print "d=",d
    d= {1: {2: 3, 3: {4: 'a'}}}
    
    """
    if len(keys)==0 :
        raise ValueError("Must provide at least one key")
    d=dic
    level=0
    for k in keys[:-1] :
        level+=1
        if k not in d :
            d[k]=dict()
        if type(d) != type(dict()) :
            raise ValueError(`d`+" is already a value, can't be a key!")
        d=d[k]
        if type(d) != type(dict()) :
            raise ValueError("There is already a non-dict value (%s) for key %s at level %d"%(`d`,k,level))
    d[keys[-1]]=value


def choose_regrid_option(variable,table,model,grid):
    """
    Want to use a Cdo regrid option which can deal with published grid for Nemo, which has a band 
    of missing values in Indian Ocean
    The return value is a dict of arg/values for regridn
    """
    default = {"option" : "remapcon"}   
    default = {}   
    if table != "Omon":
        return default
    if model not in [ "CNRM-CM6-1", "CNRM-ESM2-1", "IPSL-CM6A-LR", "AWI-CM-1-1-MR" ,"BCC-CSM2-MR",
                      "EC-Earth3", "EC-Earth3-Veg","MPI-ESM1-2-HR","NESM3"]:
        return default
    if grid[0:2] == "gr":
        return default
    return {"option" : "remapdis"}
    


def extract_labelbar(figure_file,labelbar_file) :
    # Extract labelbar from figure_file using external process
    os.system("convert -extract +0+740 %s -trim %s"%(figure_file,labelbar_file))

def concatenate_labelbars(lbfile1,lbfile2,lbfile) :
    # 
    os.system("convert -size 1650x100 xc:white %s -geometry 1100x100 -composite "%lbfile1 +
              " %s -geometry x100+550+0 -composite -trim %s"%(lbfile2,lbfile))


def create_labelbar(figure_file,out_file,missing=True,signif=True,captions_dir=None):

    # Extract labelbar from figure_file 
    extract_labelbar(figure_file,"tmp_labelbar.png")
    
    # Combine with legend for shadings
    if captions_dir is None :
        captions_dir=os.path.dirname(os.path.abspath( __file__ ))+"/captions/"

    if missing :
        if signif :
            caption="caption_signif_missing.png"
        else: 
            caption="caption_signif_missing.png"
            #caption="caption_agree_missing.png"
    else:
        if signif :
            caption="caption_signif_centre.png"
        else:
            caption="caption_signif_centre.png"
            #caption="caption_agree.png"

    shading_caption=captions_dir+caption
    os.system("rm -f %s "%(out_file))
    # signif captions size is 314x175
    # label bars size is 872x130 (for page_width=2450,page_height=3444)
    os.system("convert "+\
              "-size 1150x130 xc:white "+\
              "\( tmp_labelbar.png -scale x130 \) -composite "+\
              "\( %s -scale x130 -geometry +900+0 \) -composite -trim %s"%(shading_caption,out_file))
    os.system("rm tmp_labelbar.png")

def create_labelbar2(figure_file1,figure_file2,out_file,missing=True,captions_dir=None):

    # Extract labelbar from figure_file 
    extract_labelbar(figure_file1,"tmp_labelbar1.png")
    extract_labelbar(figure_file2,"tmp_labelbar2.png")
    
    # Combine with legend for shadings
    if captions_dir is None :
        captions_dir=os.path.dirname(os.path.abspath( __file__ ))+"/captions/"
    if missing : caption="caption_signif_missing.png"
    else:        caption="caption_signif_centre.png"
    shading_caption=captions_dir+caption

    # signif captions size is 314x175
    # label bars size is 872x130 (for page_width=2450,page_height=3444)
    os.system("rm %s ; "%out_file +
              "convert -size 2200x130 xc:white "+
              " \( tmp_labelbar2.png -scale x130 -geometry +1200+0 \)  -composite " +
              " \( %s                -scale x130 -geometry +900-0  \)  -composite " % shading_caption +
              " \( tmp_labelbar1.png -scale x130 -geometry +0+0    \)  -composite " +
              " -trim "+out_file)
    
    os.system("rm tmp_labelbar1.png  tmp_labelbar2.png")


