.. _notebooks_parameters:

Common notebooks behaviour and parameters
===========================================

Parameters setting principles
-------------------------------
All notebooks have their parameters grouped in a single notebook cell
which is the first code cell. **The parameters are generally documented
in that first cell, otherwise their meaning is described hereafter.**

A further notebook cell usually supersedes the value of some
parameters, provided the ``do_test\\ parameter is set to True in first
cell (which is the default). This allows that the default behaviour
is to test the notebook on a small-size problem

This first cell also has a Jupyter metadata wich name is 'parameters'
and which allows `papermill`_ to supersede first cell's parameters
values when it runs the notebook (such as in `batch mode
<batch_mode>`; this is actually the way it knows after which cell it
should include the parameters which it is provided with

Note that the combination of both features implies that ``do_test``
should be set to False when launching in batch mode, except when
purposely wishing to activate the test paramaters set. 

.. _user_python_settings:

How to include own python code in all notebooks
------------------------------------------------
All notebooks execute (after parameters setting) the code they may
find in a file named 'user_python_settings.py' located in the
directory designated by environment variable
CAMMAC_USER_PYTHON_CODE_DIR (or the current execution directory if the
variable is not set). This allows to avoid code duplication among
numerous notebooks. Batch launcher ensures, by default, for setting
this variable to a proper value (i.e. directory jobs) for accessing
this version of file 'user_python_settings.py' : (see also
:ref:`batch_mode`)

.. code-block:: python

   from climaf.api import *

   # Fix some model errors
   calias('CMIP6','evspsbl',scale=-1,\
       conditions={"model":["CAMS-CSM1-0","EC-Earth3","EC-Earth3-Veg","EC-Earth3-LR","EC-Earth3-Veg-LR"]})
   calias('CMIP6','pr',scale=1000.,conditions={"model" : "CIESM"})
   calias('CMIP6','mrso',scale=1000.,conditions={"model" : "CIESM"})
   calias('CMIP6','mrsos',scale=100.,conditions={"model" : "FGOALS-f3-L"})

   # Define P-E for CMIP6 variables
   derive('CMIP6', 'P-E','minus','pr','evspsbl')

   # Define location of fixed fields
   dataloc(project='CMIP6', organization='generic',
        url=default_fixed_fields_dir+"/${variable}_${table}_${model}_*_*${grid}.nc")

   # Define location of derived variables if needed (e.g. yearly stats of daily precip)
   if derived_variables_pattern is not None :
	       climaf.dataloc.dataloc(project='CMIP6', organization='generic', 
   	                              url=derived_variables_pattern, table=derived_variable_table)


For all notebooks where it makes sense, the following applies :

Parameters related to inputs
-----------------------------

  - parameters ``data_versions_tag`` and ``data_versions_dir`` are 
    mandatory; the tag is included in output filenames

  - parameter ``excluded_models`` allows to explicitly exclude a list of
    models from the ensemble derived from the daat versions
    dictionnary; this is handy when some issue occurs with data
    quality; it is ususally a list od model identifiers, but for some
    notebooks it is a dictionnary of such lists, the dictionnary keys
    being variable names or experiment name
    
  - parameter ``included_models`` allows to explicitly limit the to a
    given list of models from the ensemble derived from the data
    versions dictionnary; this is handy for e.g. small-size notebook
    tests

.. _derived_variable_parameters:
    
  - parameters ``derived_variables_pattern`` and
    ``derived_variables_table`` allow to tell the notebook how to
    reach those input data which are not in the standard data
    directory. See :ref:`derived_variables`
    

Main parameters related to computation
----------------------------------------

  - if the figure is about one single experiment, it is designated by
    parameter ``experiment``, otherwise by a list in parameter
    ``experiments``

  - the period of interest for the projection is provided through
    parameter ``proj_period`` which is a string matching `CliMAF
    syntax for periods
    <https://climaf.readthedocs.io/en/master/functions_internals.html?highlight=period>`_,
    as e.g. "1900-1910"

  - if any figure panel is about a change or a reference, parameters
    ``ref_period`` and ``ref_experiment`` are used for the reference
    experiment and period
  - parameter ``season`` allows to specify the season for averaging
    the variables; tested values are "DJF" and "JJA", and also, for
    most notebooks, "ANN" (this is documented in the notebook)
    
.. _change_definitions:

  - for panels showing a map of change, parameter ``field_type``
    allows to choose which type of change is shown : ``mean_change``,
    ``mean_rchange``, ``mean_schange``, ``median_change``, ``median_rchange``,
    ``median_schange; where `mean` / `median` represent the ensemble
    operation``, `change` represents the plain change, `rchange`
    represents the relative change, and `schange` represents the
    change standardized by the internal variability

.. _confidence_schemes:

  - parameter ``scheme`` allows to call for superimposition on maps of
    confidence information (related to robustness and significance)
    according to three different schemes :

    - value ``AR5`` means method a) in AR5 report's Box 12.1, so with
      superimposition of :

      - hatching for locations of lack of agreement across models and

      - stippling for locations with both agreement across models and
        exceedance of a threshold linked to internal variability

    - values ``AR6`` and ``AR6S`` mean respectively the comprehensive
      and simple scheme defined for AR6 (see its Cross Chapter Box
      Alas 1). Parameter ``sign_threshold`` represenets the threshold
      used on the eprcent of models which should agree on sign for
      this method (which is by default 0.66 or 0.9 for the simple
      method, depending on the AR6 chapter). For method AR6, parameter
      ``confidence_factor`` represents the multiplicative factor
      applied to control variability for deciding a change is
      significant (besides sqrt(2)) (default value is 1.645 in AR method)

    - and, only for notebook basic.sh, value ``KS`` refers to the
      method of `Knutti and Sedlacek 2013 <http://doi.org/10.1038/NCLIMATE1716>`_,
      which admits an additional ``threshold`` parameter
      

Parameters related to outputs
----------------------------------------

  - ``custom_plot`` allows to provide a dictionnary of plot options
    for superseding some CAMMAC default options; it has to comply with
    `CLiMAF plot arguments semantics
    <https://climaf.readthedocs.io/en/latest/scripts/plot.html>`_. See
    also the documentation for figure ploting function
    `figures.change_figure`

  - the generated figure has a filename which is either completely
    defined by parameter ``figure_filename`` (if set), or built by
    concatenating enough parameters information for getting
    non-ambiguous naming;

  - for large figures, a small size figures (half size) is also
    generated, with suffix "_small"

  - in the case of automatic figure filename, parameter ``version`` is
    systematically a suffix for the filename, and parameter ``outdir``
    is also used

  - the figure title is either set using parameter ``manual_title`` or
    automatic
    

  

Other parameters
-------------------

  - a number of notebooks use a caching mechanism (atop of CliMAF one)
    for final fields ; in that case, they use a directory designated
    by ``cachedir`` , which default value is "./cache"; a parameter
    ``use_cached_proj_fields`` (which defaults to True) allows to
    (de-)activate this feature;

  - multi-model maps are based on reprojecting time averaged fields on
    a grid common to all models; it is designated by paramterer
    ``common_grid`` with CDO syntax (see `paragraph 1.3.2 of CDO doc
    <https://code.mpimet.mpg.de/projects/cdo/embedded/index.html>`_,
    and defaults to a 1° regular latlon grid. The regridding algorithm
    used is a CDO's conservative reamp scheme, execpt when CDO does
    not support the input grid for this algorithm. This is fine tuned
    through function :func:`~ancillary.choose_regrid_option`

  - when the figure needs a computation of internal multi-decennal
    variability of some variable, parameter ``variab_sampling_args``,
    which value is a dictionary, allows :

    - to possibly change the parameters for multi-decennal variability
      computation in AR5 and AR6 methods :
      
        - "shift", the length of the begin of the control period which
          is discarded (if there is a long enough data period for that)
	- "size", the size of the samples (in years)
	- "number", the number of samples
	- "detrend", which drives a detrending before computing time
          variance (defaults to True)

    - to drive some internals :

      - "compute" (True/False) : should function variability_AR5 ask
        CliMAF to perform the actual computation or to just return the
        CliMAF object representing the variability field (with a
        deferred computation); this parameter has no actual effect
        when executing a notebook
      - "house_keeping" : should intermediate fields be erased from
        CliMAF cache after computing variability; beacuse of the
        length of the data periods for control experiment, this can
        have a strong impact on CliMAF cache size, which can be an
        issue with respect to file resources; re-running a notebook
        with house_keeping=True can be a way to save on file
        ressources

  - ``same_model_for_var`` is a logical toggle which indicates
    whether, when computing internal variability on an ensemble of
    models, the chosen ensemble should be the same that the ensemble
    used for computing the change; if this is the case, the list of
    models used for both computations is restricted to the set of
    models providing data for the control and the reference and the
    projection experiments. This parameter is not implemented in all
    notebooks, in which case it takes value 'False'. Implementing it
    is quite easy for notebooks producing chane maps by calling
    function :func:`changes.change_figure_with_caching`


All notebooks producing maps do use CAMMAClib function
:func:`~changes.change_figure_with_caching` which embedded documentation
can also be helpful
