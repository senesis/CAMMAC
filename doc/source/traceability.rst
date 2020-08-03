
.. _traceability:

Traceability and building ensembles of datasets versions
--------------------------------------------------------

In order to implement traceable science (which has high priority in
AR6), each input dataset used in a single figure panel must be fully
qualified by its metadata, which include the version and the grid of
the dataset, and also its variant index (e.g. r1i1p1f2 for CMIP6) . This
implies, for all model :

- to analyze available data at the host computing/data center
- to decide for relevant combinations of available variants among experiments
- to record this decision 
- to feed the analyses with this record

A dedicated notebook, in directory select_data_versions, implements
the steps above and creates **dictionnaries in json format** for
recording the available model data and the choices described above;
there is one json file for each data frequency, which adresses all the
geophysical variables and experiments of interest.

These dictionnaries are an input for the notebooks and some CAMMAClib
functions. Unless instructed otherwise (through their parameters) the
notebooks will insert the dictionnary 'tag' (or label) as a suffix in the
generated figure filename, in order to ensure traceability.

Most figure notebooks or and some CAMMAClib functions define the list of
models they use by reading these kind of dictionnary and then
computing the intersection of available models across the experiments
they are dealing with (typically an historical + a projection for
assessing a change, and the control experiment for assessing the
variability) for the variable they are analyzing.

In order to allow for small-size executions of notebooks, its is handy
to generate limited ensembles of dataset versions. Another notebook
"handmade_data_selection" allows for that (in same directory)

A few versions dictionnaries are provided with the software (see :ref:`user guide`)
