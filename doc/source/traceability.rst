
.. _traceability:

Managing multi-model data and traceability
--------------------------------------------------------

For using multi-model output, one needs to choose some model ensemble,
which implies at some stage to make a list of available versions of
data for each model. Further, in order to implement traceable science,
each input dataset must be fully qualified by its metadata, which
include the simulation variant index (e.g. r1i1p1f2 for CMIP6), the
version and the grid of the dataset.  **The way CAMMAC handles these
points is through reading a dictionnary of available data versions (in
json format)**. This is hereafter called a 'data versions dictionnary'

CAMMAC includes a notebook for helping with that step, in directory
select_data_versions; it has to be launched once before invoking any
computation script or notebook, and should be redone when available
datasets do change. In its present version, and ony for performance
purpose, that notebook is slighlty dependent on data oragnization used
on the ESPRI platform; however, its data inspection mechanism mainly
relies on CliMAF data management and should work anywhere after a
slight adapatation.

More explicitly, for each interesting variable, each model and each
experiment of interest, that notebook analyzes available data at the host
computing/data center, for each available variant; this includes also
checking that the data period is consistent with the definition of the
experiment (or with a minimum duration for the control experiment)

Data versions dictionnaries are an input for the notebooks and some CAMMAClib
functions. The notebooks will usually insert the dictionnary 'tag' (or label)
as a suffix in the generated figure filename, in order to ensure traceability.

Most figure notebooks define the list of models and simulation variant
they use by reading these kind of dictionnary and then using a
CAMMAClib function for computing the intersection of available models
across the experiments they are dealing with (typically an
historical + a projection for assessing a change, and the control
experiment for assessing the variability, if needed) for the variable they are
analyzing. Ths also include choosing a variant when needed. Also,
notebooks usually allows to restrict models used to an explicit list,
and also allows to explicitly exclude some models

The notebooks use this detailed data version info to generate the data
documentation for each figure, formated according to the AR6/WGI/TSU
guidelines, and stored in a file named after the figure name and with
suffix "_md.txt" 

TBD In order to allow for small-size executions of notebooks, its is handy
to generate limited ensembles of dataset versions. Another notebook
"handmade_data_selection" allows for that (in same directory)

A reference data versions dictionnary is provided with the software (see :ref:`user guide`)

