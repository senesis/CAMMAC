.. _introduction:

Introduction
------------

This is both the README page of CAMMAC GitHub repository, and the
introduction page of the `CAMMAC doc which can be reached on
ReadTheDocs <https://cammac.readthedocs.io>`_. However it doesn't
render fully on GitHub

CAMMAC is designed for analyzing climate variables change in a `CMIP6
<https://www.wcrp-climate.org/wgcm-cmip/wgcm-cmip6>`_ multi-model
context, assuming that CMIP6 data is locally available.

It was originally developped and used for Météo-France's contribution
to `IPCC <https://www.ipcc.ch/>`_ Assessment Report #6 (`AR6
<https://www.ipcc.ch/assessment-report/ar6/>`_) WG1 Chapter 8 (that
chapter deals with hydrological aspects of Climate Change). This is
why it applies a 'one model / one vote' rule (but see
:ref:`one_model_on_vote`)

**The typical analyses** allowed by CAMMAC are :

- create multi-panel **figures showing global maps of the multi-model
  change** for some physical variables (or derived variables) between
  two periods (chosen in two CMIP6 experiments), or for a given
  global warming level. What varies between panels can be the
  projection experiment, or the variable, or the season... Various
  :ref:`change definitions <change_definitions>` are
  implemented. The maps also include hatching and or stippling for
  representing :ref:`confidence schemes <confidence_schemes>`
  according to AR5 or AR6 schemes
  
  .. image:: ../figures/Fig_ssp245_mrro_ANN_2081-2100_AR6S_0.66.png
   :scale: 25%

- create **plots of the dependance of relative change with warming
  level** for some physical variable; the change is evaluated after
  averaging on basins or seasons, or even hybrid seasons (such as
  'global winter', a composite of austral JJA and boreal DJF)

  .. image:: ../figures/extra-tropics_change_rate.png
   :scale: 100%
  
**The workflow** has three possible modes :

- launch batch jobs using e.g. one of the provided bash scripts
  (which is the easiest way) (see :doc:`batch_mode`)
- interactively run one of the :ref:`provided IPython notebooks
  <available_notebooks>` (which provides more flexiblility)
- build your own Python program using the :ref:`CAMMAClib library <CAMMAClib>`

The first mode, batch jobs, makes use of the notebooks
quoted for the second mode; in both cases, one sets :ref:`a number of
parameters <notebooks_parameters>` which allow to tune the processing. 

For all three modes **a data versions dictonnary is needed**, as a basis
for selecting the dataset to process (details :ref:`here <traceability>`)

A few notebooks dealing with data availability, quality control and
pre-processing are also provided and :ref:`described here <data_related_notebooks>`


While CAMMAC has been developped and used on `IPSL's
<https://www.ipsl.fr/>`_ `ESPRI`_ <https://en.aeris-data.fr/espri-2/>`_
platform, it is fully portable and usable on any machine with CMIP6
data and e.g. conda-enabled environments (see :ref:`requirements`)

The initial development was funded by Météo-France's `CNRM
<http://www.umr-cnrm.fr/>`_, and done by Stéphane Sénési
