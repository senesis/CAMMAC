
.. _traceability:

CAMMAC principles for managing multi-model data 
============================================================

.. _one_model_on_vote :

One model / one vote
-------------------------------------------------

CAMMAC has been designed for AR6 analysis, which included the rule
that only one variant (or simulation) must be used per experiment and
model.

This rule is implemented in function
:func:`mips_et_al.models_for_experiments`; because this function
actually returns a list of pairs (model,variant), it should be
possible to change its behaviour to return the result of any other
rule, and have a consistent computation downstream. This has however
not be tested


Rationale
----------

For using multi-model output, one needs to choose some model ensemble,
which implies at some stage to make a list of available versions of
data for each model. Further, in order to implement traceable science,
each input dataset should be fully qualified by its metadata, which
include the simulation variant index (e.g. r1i1p1f2 for CMIP6), the
version and the grid of the dataset.  **The way CAMMAC handles these
points is through reading a dictionnary of available data versions**
(in json format). This is hereafter called a 'data versions
dictionnary'

Building a data versions dictionnary
------------------------------------

CAMMAC includes a notebook for helping with that step,
:download:`data_selection </../html_nb/data_selection.html>` in directory
select_data_versions; it has to be launched once before invoking any
computation script or notebook, and this should be redone when
available datasets do change (this is actualy mandatory if some
dataset is withdrawn.  Helper script :download:`$CAMMAC/jobs/select_data.sh
</../../jobs/select_data.sh>` can be used

This notebook is further described in :ref:`the section for data
related notebooks <data_related_notebooks>`


Use of data versions dictionnary by processing notebooks
---------------------------------------------------------

Data versions dictionnaries are an input for most CAMMAC processing
notebooks : they define the list of models and simulation variant they
actually use by reading it and then using a CAMMAClib function for
computing the intersection of available models across the experiments
they are dealing with (typically an historical + a projection for
assessing a change, and the control experiment for assessing the
variability, if needed) for the variable they are analyzing. This also
include choosing a variant when needed. Notebooks parameters also
generally allows to restrict models used to an explicit list, and also
allows to explicitly exclude some models; ths is handy for small-size tests

The processing notebooks also use this detailed data version info to
generate the data documentation for each figure, formated according to
the AR6/WGI/TSU guidelines, and stored in a file named after the
figure name and with suffix "_md.txt"

The notebooks will usually insert the dictionnary 'tag' (or label) as
a suffix in the generated figure filename, in order to ensure
traceability.


.. _ref_data_dic:

Reference data versions dictionnary
------------------------------------

A reference data versions dictionnary is provided with the software in
directory *data* , and is usable for CMIP6 data on the `ESPRI`_
platform. It is based on the data available there as of february 1st,
2021; and its the one configured by default in all notebooks

At the time of writing, it can be used on the
`ESPRI`_ platform, and this will carry on as long as no data is
withdrawn; after some withdrawal occurs, that dictionnary will still be
usable if corresponding models are indicated as excluded using the relevant
notebooks parameter ('excluded_models')
