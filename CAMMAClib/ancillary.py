from __future__  import division
"""

CAMMAC ancillary functions for :

  - managing dictionnaries of dictionnaries of dictionnaries of ...
  - converting acronyms to nice labels
  - handling labelbars (using ImageMagick's convert) : extract, assemble

"""


import json, os, os.path

# A dictionnary of pretty labels for some acronyms
prettier_label={
    "ssp126":"SSP1-1.9","ssp126":"SSP1-2.6","ssp245":"SSP2-4.5","ssp585":"SSP5-8.5",
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
    >>> print "d=",d
    d= {1: {"q": 3}}
    >>> feed_dic(d,'a',1,4,"key")
    >>> print "d=",d
    d= {1: {"q": 3, 4: {"key" : 'a'}}}
    
    With keyword arg use_list=True, will rather assume that stored values are lists, 
    and so will append VALUE :
    
    >>> e=dict()
    >>> feed_dic(e,18,key1,key2,use_list=True)
    >>> feed_dic(e,19,key1,key2,use_list=True)
    >>> print "e=",e
    e= {key1: {key2: [18, 19]}}
    
    With keyword arg extend_list=True, will also assume that stored values are lists, 
    and that VALUE is a list, and concatenate it with value in dic

    With keyword arg use_count=True, will rather increment the dic value with VALUE 
    (starting from 0) :
    
    >>> e=dict()
    >>> feed_dic(e,2,"qq",3,use_count=True)
    >>> feed_dic(e,100,"qq",3,use_count=True)
    >>> print "e=",e
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
            raise ValueError(`d`+" is already a value, can't be a key!")
        d=d[k]
        if type(d) != type(dict()) :
            raise ValueError("There is already a non-dict value (%s) for key %s at level %d"%(`d`,k,level))
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


def create_labelbar0(figure_file,out_file,missing=True,signif=True,captions_dir=None):

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

def create_labelbar2(figure_file1,figure_file2,out_file,missing=True,captions_dir=None,width=2100,height=130):

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

    # Divide width in segments : 3+1+3
    signif_width=width//7
    lbwidth= 3*signif_width
    margin=signif_width/6
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
    os.system(command)
    os.system("rm tmp_labelbar1.png  tmp_labelbar2.png")


def create_labelbar(figure_file,out_file,missing=True,captions_dir=None,width=1200,height=130):

    # Extract labelbar from figure_file 
    extract_labelbar(figure_file,"tmp_labelbar.png")
    
    # Combine with legend for shadings
    if captions_dir is None :
        captions_dir=os.path.dirname(os.path.abspath( __file__ ))+"/captions/"
    if missing : caption="caption_signif_missing.png"
    else:        caption="caption_signif_centre.png"
    shading_caption=captions_dir+caption

    # signif captions size is 314x175
    # label bars size is 872x130 (for page_width=2450,page_height=3444)

    # Divide width in segments : 3+1+3
    signif_width=width//4
    lbwidth= 3*signif_width
    margin=signif_width/6
    if height is None : height=width/16
    command="rm -f %s ; "%out_file +\
              "convert -size %dx%d xc:white "%(width,height)+\
              " \( %s                -scale %dx%d -geometry +%d-0  \)  -composite "%\
              (shading_caption,signif_width-2*margin,height,lbwidth+margin) +\
              " \( tmp_labelbar.png -scale %dx%d -geometry +0+0    \)  -composite "%\
              (lbwidth,height) +\
              " -trim "+out_file
    os.system(command)
    os.system("rm tmp_labelbar.png")


