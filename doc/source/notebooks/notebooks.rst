.. _available_notebooks:

Notebooks for figures/tables generation
===========================================

This section describe figure and tables creation notebooks, while
notebooks related to creating a data versions dictionnary and to data
management and processing are described :ref:`there
<data_related_notebooks>`

The figures/tables creation notebooks are stored in directory
'notebooks';they are provided with expressive names; some details of
their design show below, together with a link to their html rendering.

Most notebooks include both a compute phase and a figure
plot phase, which can generally be activated separately

Notebooks for global change maps
-----------------------------------------------

Next notebooks all produce a multi-panel figure, except for the first
two. Excpet for the first one, they all basically call function
`changes.change_figure_with_caching`, which documentation is helpful
for understanding details of the computation. The plot itself is done
using function :func:`figures.change_figure`

- :download:`basic </../html_nb/basic.html>` : create a single map of
  the change in a variable between a reference period and a projection
  period. A hatching is superimposed, either after Knutti and Sedlacek 2013
  robustness index (`<https://doi.org/10.1038/NCLIMATE1716>`_) or AR6
  'simple' scheme

- :download:`change_map_simple </../html_nb/change_map_simple.html>` :
  same as basic, but allows for another set of hatching schemes: AR5,
  AR6 comprehensive and AR6 simple 'simple' scheme

- those notebooks use a single projection experiment, but multiple variable or seasons:  

  - :download:`change_map_4seasons
    </../html_nb/change_map_4seasons.html>` : compute a 4 panels-figure
    for one variable where each panel shows the map of the change for a
    season and a single SSP. Used for AR6/WGI/fig8.14

  - :download:`change_map_1SSP_4vars
    </../html_nb/change_map_1SSP_9vars.html>` : compute a 9
    panels-figure where each panel shows the map of the change of one
    variable and a single SSP. Used for AR6/WGI/TS7-fig1

  - :download:`change_map_1SSP_9vars
    </../html_nb/change_map_1SSP_9vars.html>` : compute a 9
    panels-figure where each panel shows the map of the change of one
    variable and a single SSP. Used in AR6/WGI for a preliminary TS figure

- while those one show 3 projection experiments: 

  - :download:`change_map_3SSPs_2seasons
    </../html_nb/change_map_3SSPs_2seasons.html>`: compute a 6
    panels-figure for change for one variable and 2 seasons (columns)
    and 3 SSPs (rows). Used for AR6/WGI/fig 8.15

  - :download:`change_map_3SSPs_2vars
    </../html_nb/change_map_3SSPs_2vars.html>`: compute a 6
    panels-figure for change for two variables (columns) and 3 SSPs
    (rows). Used for AR6/WGI/fig 8.17 and 8.18 

  - :download:`change_map_3SSPs_3horizons
    </../html_nb/change_map_3SSPs_3horizons.html>` : compute a 9
    panels-figure for change for one variable, three time horizons
    (columns) and 3 SSPs (rows). Used in AR6/WGI for a preliminary TS figure

  - :download:`change_map_3SSPs_plus_ref
    </../html_nb/change_map_3SSPs_plus_ref.html>` : compute a 4
    panels-figure for one variable with the reference (top left) and the
    change for 3 SSPs. Used for AR6/WGI/Box8.2 fig 1

- and these one deal with warming levels :

  - :download:`change_map_1var_at_WL_1SSP_with_clim
    </../html_nb/change_map_1var_at_WL_1SSP_with_clim.html>` : compute
    a single panel figure showing the map of a single variable change
    for a given warming level and a single SSP, with superimposition
    of a few contours of the climatology of this variable in e.g. a
    control experiment. Used in AR6/WGI/fig8.21.
    
  - :download:`change_map_path_dependance
    </../html_nb/change_map_path_dependance.html>` : compute a 6
    panels-figure showing the changes in some (raw or transformed)
    variable at two levels of warming, for a series of projection
    experiments, and their diff, for 2 seasons. Used for AR6/WGI/fig 8.25


  
Notebooks for plots/tables of rate of change vs warming level
-------------------------------------------------------------

- A series of notebooks name 'change_hybrid....' allow for computing
  changes over regions, integrated over seasons and hybrid_seasons.
  What is called an hybrid season here is the union of pairs
  (region,season), which allow to define e.g. a 'global winter' by
  (DFJ, northern hemisphere) + (JJA, souther hemisphere). A number of
  regions are knwon by keyword (globe, land, NH, SH ...)

  The change are computed with their direct or parametric dependance to the global
  warming level :

  - direct dependance means that, for each desired warming level, one
    computes for each model which is the central year corresponding to
    the warming level and then what is the change for that year in
    that model. These change values for the same warming level are
    then e.g. averaged across the models. 
  - parametric dependance means that, for a given set of time periods,
    one computes for each model, on one side the global warming which
    is then averaged across models, and on the other side the change
    value, which is also avreaged across models; this provide a
    parametric dependency of the change to the global warming, where
    the paremeter is the time period

  In the course of incremental CAMMAC development, the following
  redundant notebooks were successively developped :

  - notebook :download:`change_hybrid_seasons
    </../html_nb/change_hybrid_seasons.html>` only implements the
    parametric dependance scheme (it allows to compute changes for a
    series of time horizons) and has a companion notebooks
    :download:`change_hybrid_seasons_figure
    </../html_nb/change_hybrid_seasons_figure.html>` for creating a
    plot of the change time series. It was used for AR6/WGI figure
    8.16.

  - notebook :download:`change_hybrid_seasons_dT
    </../html_nb/change_hybrid_seasons_dT.html>` is derived form
    previous notebook, but implements both schemes (so, it also allows
    to compute changes for a series of warming levels); it was actualy
    tested only using the direct dependance scheme (so, for warming
    levels). With its companion notebook
    :download:`change_hybrid_seasons_dT_figure
    </../html_nb/change_hybrid_seasons_dT_figure.html>`, it was used
    for producing AR6/WGI figure Box TS 12; with its other companion
    notebook :download:`change_hybrid_seasons_dT_table
    </../html_nb/change_hybrid_seasons_dT_table.html>`, which allows
    to filter out models that do not reach a givel warming level, it
    was used for producing two panels for AR6/WGI figure Box TS X f3

  - notebook :download:`change_hybrid_seasons_must
    </../html_nb/change_hybrid_seasons_must.html>` is derived from
    previous notebook but can also produces results in a tabular form;
    it was used in AR6/WGI for producing the data for tables 8.1 and
    8.2, in CSV and text mode; it is the best basis for replacong 
    the other computation notebooks but its output dictionnary may
    have a some differences with what is expected by the
    change_hybrid..._figure figure creation notebboks

- :download:`change_rate_basins </../html_nb/change_rate_basins.html>`
  : compute a 6-to-9-panels figure of time evolution for three
  ensemble-statistics (e.g. mean and two percentiles) for two
  variables integrated over three basins, and for three SSPs. The
  variables are a combination of a geopysical variable (e.g. "mrro")
  and a time statistics ("mean" or "std"). Few common notebooks
  parameters apply (see documentation in notebook itself). There are
  two companion Ncl scripts, automatically called for ploting the
  results, one for the case of three basins and two statistics (mean
  an standard deviation), the other for up to 9 basins and only the
  time mean ( :download:`change_rate_basins_1var
  </../../notebooks/change_rate_basins_1var.ncl>` and
  :download:`change_rate_basins_2vars
  </../../notebooks/change_rate_basins_2vars.ncl>`)

	    


Meridional profiles of zonal means
-----------------------------------

- :download:`change_zonal_mean </../html_nb/change_zonal_mean.html>` :
  compute a 6-panels figure of zonal mean for statistics of two
  variables (rows) and three SSPs (columns). The statistics are :
  ensemble mean and 5% percentiles, ensemble mean on land, and
  ensemble 5% percentiles of internal variability. Graphs have a color
  code matching the SSPs. There is a companion Ncl script for ploting
  the figure, :download:`change_zonal_mean.ncl
  </../../notebooks/change_zonal_mean.ncl>`, which is automaticallty
  called by the notebook
  

 

