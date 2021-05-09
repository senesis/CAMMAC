
.. _data_related_notebooks:

Notebooks for data registering, control and pre-processing
============================================================

These notebooks are stored in directory select_data_versions

Creating a data versions dictionnary
-------------------------------------

Notebook :download:`data_selection </../html_nb/data_selection.html>` 
analyzes, for each interesting variable, each experiment of interest,
which are the available models, variants and versions at the host
computing/data center

This in line with what is described in :ref:`traceability`.

This allows to provide to computing notebooks a list of all datasets
available, for letting them build an ensemble. It includes checking that
the data period is consistent with the definition of the experiment
(or with a minimum duration for the control experiment)

The result is stored as a json file; such a file is provided with the
software (see :ref:`ref_data_dic`); it is named after the pattern
*Data_versions_selection_<some_tag>.json*; it is actually a
dictionnary of dictionnaries of ... organized that way :

.. _dictionnary_structure:

>>> data_versions[experiment][variable][table][model][variant]=(grid,version,data_period)

In its present version, and only for performance purpose, that
notebook code is slighlty dependent on data organization used on the
`ESPRI`_ platform; however, its data inspection mechanism mainly relies
on CliMAF data management and should work anywhere after a slight
adapatation (in the first few cells : search for '/bdd')

Creating a 'hand-made' data versions dictionnary
------------------------------------------------

Notebook :download:`handmade_data_selection
</../html_nb/handmade_data_selection.html>` is an example of how to
create a data versions dictionnary in a hard-coded mode. However, that example is based on an old structure of such dictionnaries and would have to be slightly reworked to match the :ref:`actual structure <dictionnary_structure>`

Checking ESGF errata
---------------------

Notebook :download:`Check_errata </../html_nb/Check_errata.html>` is
intended to automatically verify a subset of those datasets that are
registered in a data versions dictionnary, against the `ESGF errata
system <https://errata.es-doc.org>`_.

It uses a service point of this
system which, at the time of CAMMAC development, was not yet fully
stabilized, and which may have change and break the logic. The errata
system provides mesages which have to be manually interpreted. For
helping with that, the notebook organizes its output (in printed and
json format) by grouping the error messages by variable, then by
severity and then by error message text.

Checking data ranges
----------------------

Notebook :download:`Check_ranges </../html_nb/Check_ranges.html>`
prints user-chosen field statistics ot user-chose time statistics for
a series of variables and experiments.

It allows to detect e.g. those models which don't use the common
units. The field and time statistics are specified in CDO argument
syntax, and allow to elaborate complex operations thanks to CDO
operators piping syntax

Checking that data available on ESGF is locally available
----------------------------------------------------------

Notebook :download:`Check_errata </../html_nb/Check_errata.html>`
queries the ESGF for latest version for a series of variables and
experiments and checks its availability on the local file system;

At the time of writing, this notebook is tune for the `ESPRI`_ computing
system and makes use of the file hierarchy known on this system. It
can be run automatically, e.g. using job :download:`datasets_stat.sh
</../../jobs/datasets_stats.sh>`. It prints its results and send them to a
list of email adresses

.. _derived_variables:

Pre-processing data for generating derived variables
-------------------------------------------------------------------------

Notebook :download:`create_derived_variable
</../html_nb/create_derived_variable.html>` allows to create
datafiles for some derived variables, for a selection of the
experiments (using those datasets described in a data
versions dictionnary). These derived variables are defined using CDO
operators piping syntax and can have any frequency

.. note:: There are other, on-the-fly, ways to create derived
   variables; see :ref:`variable_derivation`

The default settings allow to derive the annual number of dry days and 
the average daily rain amount (or non-dry days), from the daily
precipitation data.

In order to allow for incremental processing of numerous datasets, a
setting allows to avoid recomputing already existing derived data.

The notebook produces a version of the dataset versions dictionnary
which is extended with the description of the derived variables; it
stores the output data at a location and with a file naming convention
which is fully configurable.  This information on derived variables
location and organization can be provided to CAMMAC by some CliMAF
call such as

>>> derived_variables_pattern  = "/data/ssenesi/CMIP6_derived_variables/${variable}"
>>> derived_variables_pattern += "/${variable}_${table}_${model}_${experiment}_${realization}_${grid}_${version}_${PERIOD}.nc"
>>> derived_variable_table='yr'
>>> climaf.dataloc.dataloc(project='CMIP6', organization='generic', url=derived_variables_pattern, table=derived_variable_table)

This is actually the case, by default : the first three commands are
included in (relevant) notebooks parameters setting cell, and the last one in all
notebooks as described :ref:`there <user_python_settings>`.

