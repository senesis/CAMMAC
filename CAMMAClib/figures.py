"""
A single function for plotting maps the AR6 way, possibly with hatching
"""
from climaf.api import plot
import os

def change_figure(variable, derivation_label, field,
                      shade=True, mask1="", mask2="",pattern1="hatching",
                      pattern2="stippling",
                      relative=True, labelbar="True", 
                      title=None, custom_plot={}, number=None, mask=None) :
    """

    Returns a CliMAF plot object showing a 2d FIELD, with
    superimposition of PATTERN1 (resp. PATTERN2) where field
    MASK1 (resp. MASK2) is 'set' (actually where it exceeds value 0.9)

    PATTERN1 and 2 are either :
    - Ncl settings for patterns, such as 'gsnShadeHigh=3', or 
    - keywords : 'hatching', 'stippling', 'crosses'

    PATTERN1 default to hatching, PATTERN2 to stippling

    Plot characteristics comply with AR6/WGI TSU guidelines
    re. colormaps, projection, ...  (except if changed through arg
    CUSTOM_PLOT, see below)

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

    patterns={
        "hlines"      : "gsnShadeHigh=1|gsnShadeFillScaleF=0.4.",
        "slashes"     : "gsnShadeHigh=3|gsnShadeFillScaleF=0.8",
        "backslashes" : "gsnShadeHigh=4|gsnShadeFillScaleF=0.8",
        "crosses"     : "gsnShadeHigh=6|gsnShadeFillScaleF=0.8",
        "hatching"    : "gsnShadeHigh=3",
        "stippling"   : "gsnShadeHigh=17|gsnShadeFillScaleF=1|gsnShadeFillDotSizeF=0.004",
        }
    
    if mask1 != "" and shade :
        pattern1 = patterns.get(pattern1,pattern1)
        plot_args.update(shading_options="%s|gsnAddCyclic=True"%pattern1, shade_above=0.9)
        
    if mask2 != "" and shade :
        pattern2 = patterns.get(pattern2,pattern2)
        plot_args.update( shade2_options="%s|gsnAddCyclic=True"%pattern2, shade2_below=-0.1, shade2_above=0.9)
        
    options_format="lbLabelBarOn=%s|lbBoxEndCapStyle=TriangleBothEnds|lbLabelFont=helvetica|" +\
        "lbTitleOn=True|lbTitleString='%s'|lbTitleFont=helvetica|lbTitlePosition=Bottom|"+\
        "lbLabelFontHeightF=0.015|cnMissingValFillColor=grey|cnInfoLabelOn=False|"+\
        "gsnRightStringFontHeightF=0.018|cnFillMode=CellFill|"
    #
    def colormap(variable) :
        if   variable in ["pr","pr_drain","pr_iav","P-E","mrro"] : return {"color":"AR6_Precip_12" }
        elif variable in ["pr_dry"]                     : return {"color":"AR6_Evap_12" }
        elif variable in ["pr_seasonality"]             : return {}
        elif variable in ["evspsbl"]                    : return {"color":"AR6_Temp_12" }
        elif variable in ["mrsos","mrso"]               : return {"color":"AR6_Precip_12" }
        elif variable in ["sos"]                        : return {"color":"AR6_Salinity_12" }
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
        if mask1 != "" : 
            mask1 = apply_mask(mask1,mask)
        if mask2 != "" : 
            mask2 = apply_mask(mask2 ,mask)
    #
    # write plot arguments in subdir .figures, in a file named after title
    outdir="./figures"
    if not os.path.exists(outdir) : os.makedirs(outdir)
    fn=outdir+"/plotargs_"+title.replace(" ","_").replace(",","_").replace("(","").replace(")","")
    with open(fn,"w") as f :
        f.write(repr(plot_args))
    #
    return plot(field,mask1,"","",mask2,title=title, **plot_args)


