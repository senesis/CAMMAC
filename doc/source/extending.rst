.. _extending:

Extended use
==========================

Extending CAMMAC use beyond CMIP6
---------------------------------

CAMMAC is yet validated only with data for project CMIP6, and this
project name is implicit in some functions.  However, a former version
of CAMMAC was used to process CMIP5 data, and restoring this
possibility could be considered. For other projects, with a less
strict output data organization, an analysis would be necessary for
assessing CAMMAC hard needs for processsing it. It would also be
advisable to test the :ref:`derived_variable parameters
<derived_variable_parameters>` for reaching data in other projects

.. _adapting_for_data:

Using CAMMAC outside the `ESPRI`_ platform
--------------------------------------------

CAMMAC was developped on the `ESPRI`_ platform. Because CliMAF has a
built-in knowledge of CMIP6 data organization on that platform (and a
few others), this allows to avoid describing this data oragnization
in CAMMAC. For using CAMMAC on other platforms with CMIP6 data, two
cases arise :

- if the data is organized according to `CMIP6 Data Reference Syntax <https://goo.gl/v1drZl>`_, i.e. with that kind of file structure ::
    
   <some root>/
     <mip_era>/
       <activity_id>/
         <institution_id>/
           <source_id>/
             <experiment_id>/
               <member_id>/
                 <table_id>/
                   <variable_id>/
                     <grid_label>/
                       <version>/
              	         <variable_id>_<table_id>_<source_id>_<experiment_id >_<member_id>_<grid_label>[_<time_range>].nc


  the only need is to declare the CMIP6 data root directory to CliMAF, by :

  >>> cdef('root','/my/CMIP6/data_root',project="CMIP6")

- otherwise, one has to duplicate the declaration of `climaf module
  climaf.project.cmip6
  <https://github.com/rigoudyg/climaf/blob/master/climaf/projects/cmip6.py>`_
  with the needed changes regarding base_patterns (toward the end of
  the module).
  
- for using the data inspection notebook (see
  :ref:`data_related_notebooks`), a slight change is necessary to
  adapt to local data organization (see :ref:`there
  <dictionnary_structure>`).
