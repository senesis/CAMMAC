.. _user guide:

User guide
==========

Short cut
---------

On ESPRI platform, to create one of the AR6 figures that CAMMAC hanldes, just execute e.g. *jobs/fig_SOD_8.15.sh*. This will use the data versions selection which is currently configured in jobs/common_parameters.yml. The figure will be created in subdir e.g. *fig_SOD_8.15/figures* 


Available versions dictionaries
--------------------------------

Each CAMMACbook uses at least one data versions dictionary (see :ref:`traceability`), which represents a selection of available datasets. Three such dictionaries are provided in directory *select_data_versions*, with a name matching pattern *Data_versions_selection_<tag>.json*, and which are usable for CMIP6 data on the ESPRI platform in may 2020 :

- two of them for the monthly frequency, with tags :

  * 20200219 : a comprehensive, real-use-case one,
  * 5models  : a reduced one, created by notebook handmade_data_selection, and includes some wildcards for some attributes

- the third one for daily frequency; it has tag 20200320_pr_day and is limited to precipitation data

By default, at time of writing, the notebooks use either dictionnary 20190219 and 20190219d_pr_day. 


Notebooks common behaviour and parameters
------------------------------------------

All notebooks have their parameters grouped in a single notebook cell which is the first code cell. Among these parameters, two are related to software locations : **climaf_lib** and **CAMMAC**

For all notebooks where it makes sense, the following applies :

- regarding inputs :

  - parameters **data_versions_tag** and **data_versions_dir** are mandatory; the tag is included in the proposed automatic filename
  - parameter **models_with_enough_spinup** is mandatory; it is a list of model names, for those models which provided less than 500 years of piControl experiment, but nevertheless a long enough period; for those models, the AR5 method for computing internal variability is relaxed a bit regarding discarding the first 100 years : the logic is then to use the last 400 years of data; this is implemented in :py:func:`~variability.variability_AR5`

- regarding outputs :
  
  - for panels showing a map of change, parameter **field_type** allows to choose which type of change is shown : mean_change, mean_rchange, mean_schange, median_change, median_rchange, median_schange; where `mean` / `median` represent the ensemble operation, `change` represents the plain change, `rchange` represents the relative change, and `schange` represents the change standardized by the internal variability
  - the generated figure has a filename which is either completely defined by parameter **figure_filename** (if set), or built by concatenating enough parameters information for getting non-ambiguous naming;
  - for large figures, a small size figures (half size) is aslo generated, with suffix "_small"
  - in the case of automatic figure filename, parameter **version** is systematically a suffix for the filename, and parameter **outdir** is also used 
  - the figure title is either set using parameter **manual_title** or automatic
  - all figures showing maps of a multi-model variable change do show it according to method a) in AR5 report's Box 12.1, so with superimposition of : 

    - hatching for locations of lack of agreement across models and
    - stippling for locations with both agreement across models and exceedance of a threshold linked to internal variability




- computation parameters :
  
  - if the figure is about one single experiment, it is designated by parameter **experiment**, otherwise by a list in parameter **experiments**
  - the period of interest for the projection is provided through parameter **proj_period** which is a string matching `CliMAF syntax for periods <https://climaf.readthedocs.io/en/master/functions_internals.html?highlight=period>`_, as e.g. "1900-1910"
  - if any figure panel is about a change or a reference, parameters **ref_period**  and **ref_experiment** are used for the reference experiment and period
  - parameter **season** allows to specify the season for averaging the variables; tested values are "DJF" and "JJA", and also, for most notebooks, "ANN" (this is documented in the notebook)

- other parameters :

  - a number of notebooks use a caching mechanism (atop of CliMAF one) for final fields ; in that case, they use a directory designated by **cachedir** , which default value is "./cache"; a parameter **use_cached_proj_fields** (which defaults to True) allows to (de-)activate this feature;
  - multi-model maps are based on reprojecting time averaged fields on a grid common to all models; it is designated by paramterer **common_grid** with CDO syntax (see `paragraph 1.3.2 of CDO doc <https://code.mpimet.mpg.de/projects/cdo/embedded/index.html>`_, and defaults to a 1° regular latlon grid
  - when the figure needs a computation of internal variability of some variable, parameter **variab_sampling_args**, which value is a dictionary,  allows :

    - to possibly change the parameters of AR5's method, namely : 
        - "shift", the length of the begin of the control period which is discarded
	- "size", the size of the samples (in years)
	- "number", the number of samples
	- "detrend", which drives a detrending before computing time variance (defaults to True)

    - to drive some internals :

      - "compute" (True/False) : should function variability_AR5 ask CliMAF to perform the actual computation or to just return the CliMAF object representing the variability field (with a deferred computation); this parameter has no actual effect when executing a notebook
      - "house_keeping" : should intermediate fields be erased from CliMAF cache after computing variability; beacuse of the length of the data periods for control experiment, this can have a strong impact on CliMAF cache size, which can be an issue with respect to file resources; re-running a notebook with house_keeping=True can be a way to save on file ressources
  


Available notebooks
-------------------

The figure creation notebooks are provided with expressive names; some details of their design show below, together with a link to their html rendering.

- :download:`change_map_1SSP_9vars <../html_nb/change_map_1SSP_9vars.html>` : compute a 9 panels-figure
  where each panel shows the map of the change of one variable and a single SSP

- :download:`change_map_3SSPs_2seasons  <../html_nb/change_map_1SSP_9vars.html>`: compute a 6 panels-figure
  for change for one variable and 2 seasons (columns) and 3 SSPs (rows)

- :download:`change_map_3SSPs_2vars  <../html_nb/change_map_1SSP_9vars.html>`: compute a 6 panels-figure
  for change for two variables (columns) and 3 SSPs (rows)

- :download:`change_map_3SSPs_3horizons <../html_nb/change_map_1SSP_9vars.html>` : compute a 9 panels-figure for
  change for one variable, three time horizons (columns) and 3 SSPs (rows)

- :download:`change_map_3SSPs_plus_ref <../html_nb/change_map_1SSP_9vars.html>` : compute a 4 panels-figure
  for one variable with the reference (top left) and the change for 3 SSPs

- :download:`change_rate_basins
  <../html_nb/change_map_1SSP_9vars.html>` : compute a 6-panels figure
  of time evolution for three ensemble-statistics (e.g. mean and two
  percentiles) for two variables integrated over three basins, and for
  three SSPs. The variables are a combination of a geopysical variable
  (e.g. "mrro") and a time statistics ("mean" or "std"). Few common
  notebooks parameters apply (see documentation in notebook itself)

- :download:`change_zonal_mean
  <../html_nb/change_map_1SSP_9vars.html>` : compute a 6-panels figure
  of zonal mean for statistics of two variables (rows) and three SSPs
  (columns). The statistics are : ensemble mean and 5% percentiles,
  ensemble mean on land, and ensemble 5% percentiles of internal
  variability. Graphs have a color code matching the SSPs.
  
- change_composite_seasons : TBD

- change_map : compute a single panel figure for the change of a
  single variable, with or without internal variability layers (TBD)

Variable derivation
-------------------

TBD
  
Batch execution of notebooks
-----------------------------

The way to use notebooks for batch execution is illustrated by the set of scripts for AR6 figures

One job script is provided (in directory jobs) for each of the AR6 figures in this list (which uses SOD figures numbering) :

- chapter 8 figures : 14, 15, 16, 17, 18, 19, 26, 27 and Box 2.8 figure1, and
- Technical Summary figures : 9 and 10

The general structure of the job script is :

- to create, in current directory, a working directory named with the script basename
- to prepare a file for changing notebook parameters (if needed : a number of notebooks are useable straight away)
- then to launch jobs/job_pm.sh (:download:`download to see auto-doc at head <../../jobs/job_pm.sh>`) which launches
  through qsub a job that :
    
    - initalize some environment parameters (using by default source file jobs/job_env.sh)
    - include further parameter settings through a file common_parameters.yaml (either from current directory
      , if missing there, or from directory 'jobs'); these parameters have lower priority vs the ones above
    - uses `Papermill <https://papermill.readthedocs.io>`_ for executing the notebooks with changed parameters;
    - traces the execution in a notebook named with script basename, created in the working directory;
      
If not requested otherwise, the figure is created in sub-directory 'figures', named with script basename

The syntax used for changing notebooks parameters in job scripts is Yaml, because Papermill requests it. Here is a short primer for the correspondance between Python and Yaml syntax. You may also refer to `Learn Yaml in minutes <https://learnxinyminutes.com/docs/yaml/>`_

=================================================== ==============================================
Python                                              Yaml    
=================================================== ==============================================
experiments = ["ssp126", "ssp245", "ssp585"]        experiments: [ssp126, ssp245, ssp585]

variability_sampling_args = { "nyears": 20 }        variability_sampling_args:
                                                       nyears: 20              

another_dict = { "nyears": 20 }                     another_dict : { "nyears": 20 }

a_number_as_a_string = "1"                          a_number_as_a_string: "1"
=================================================== ==============================================


Visual index of notebooks
--------------------------

TBD


Advanced use : CAMMAClib
-------------------------
.. include:: CAMMAClib.rst
	     
TBD





