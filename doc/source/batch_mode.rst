.. _batch_mode:

Batch execution of notebooks
==============================

The way to use notebooks for batch execution is illustrated by the set
of scripts for AR6 figures and other scripts in directory $CAMMAC/jobs.

.. note::

  In short : these scripts can be launched from any directory, they allow to change
  notebook's parameters, their output will go in a sub-directory named
  after the scrips's name, and they take care of setting the execution
  environment defined at install stage. You can create your own version of
  such scripts, see :ref:`script_design`
  
The scripts can be launched after setting the minimal environment, e.g. :

.. code-block:: bash

   export CLIMAF=/home/ssenesi/climaf_installs/climaf_running
   export CAMMAC=/data/ssenesi/CAMMAC

Provided scripts for batch jobs
--------------------------------
Unfortunately, before the AR6 report goes public, the full set of AR6
scripts cannot be disclosed to the public, so the examples provided
are limited to:

- :download:`basic.sh <../../jobs/basic.sh>` which allows to create a
  singe-panel figure with the map of a variable change by launching
  notebook basic; it takes arguments for variable, projection experiment,
  season, hatching scheme and its threshold.

- :download:`select_data.sh <../../jobs/select_data.sh>` which allows
  to build a data versions dictionnary by launching notebook
  data_selection

- :download:`check_ranges.sh <../../jobs/check_ranges.sh>` which allows
  to launch notebook Chek_ranges
  
- :download:`datasets_stats.sh <../../jobs/datasets_stats.sh>` which allows
  to launch notebook Chek_ESGF_lists_on_bdd
  
- :download:`pr_day_stat.sh <../../jobs/pr_day_stat.sh>` which allows
  to derive daily precipitations statistics by launching notebook
  create_derived_variable
  
.. _recommended_script_design:

Recommended script design
-------------------------
These scripts all follow the recommended structure of a job script :

- create, in current directory, a working directory named with the
  script basename
- prepare a file for changing notebook parameters (note : parameter
  ``do_test`` should usually be set to False, there, except if you
  intend to execute the cell setting parameters to test values)
- execute jobs/job_pm.sh (:download:`download to see auto-doc
  at top <../../jobs/job_pm.sh>`) which launches through qsub a job
  that :
    
    - initalize some environment variables (using by default source
      file jobs/job_env.sh, which has been set at :ref:`CAMMAC install
      phase <installation>`, or the one designated by environment
      varable ENV_PM)
    - include further parameter settings through a file
      common_parameters.yaml (either from current directory, 
      or from the arguments, of from directory 'jobs');
      these parameters have **lower priority** than the ones above
    - exports environemnt variable CAMMAC_USER_PYTHON_CODE_DIR,
      setting it to the 'jobs' directory if not set upstream
    - uses `papermill`_ for executing the notebooks with parameters
      values which supersedes the one in notebook's first cell
    - traces the execution in a notebook named with script's basename,
      created in the working directory;
      
If not requested otherwise, the figure is created in sub-directory
'figures', named with script basename

.. _yaml_syntax:

Yaml syntax for setting parameters in scripts
---------------------------------------------

The syntax used for changing notebooks parameters in job scripts is
Yaml, because `papermill`_ requests it. Here is a short primer for the
correspondance between Python and Yaml syntax. You may also refer to
`Learn Yaml in minutes <https://learnxinyminutes.com/docs/yaml/>`_

=================================================== ==============================================
Python                                              Yaml    
=================================================== ==============================================
experiments = ["ssp126", "ssp245", "ssp585"]        experiments: [ssp126, ssp245, ssp585]
                                                    
variability_sampling_args = { "nyears": 20 }        variability_sampling_args:
                                                       nyears: 20              

another_dict = { "nyears": 20 }                     another_dict : { "nyears": 20 }

a_number_as_a_string = "1"                          a_number_as_a_string: "1"
=================================================== ==============================================

