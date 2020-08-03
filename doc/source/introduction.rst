Introduction
------------

This document describes the a software originally developped by
Stéphane Sénési for helping with analyses and figures based on `CMIP6
<https://www.wcrp-climate.org/wgcm-cmip/wgcm-cmip6>`_ multi-model
results and needed in the context of `IPCC <https://www.ipcc.ch/>`_
Assessemnt Report #6 (`AR6
<https://www.ipcc.ch/assessment-report/ar6/>`_) WG1 Chapter 8 (that
chapter deals with hydrological aspects of Climate Change). This
development was funded by IPCC

The software is named CAMMAC, for "Projections Assessment with `CliMAF
<https://climaf.readthedocs.io>`_". Its design allows to re-use it for
multi-model analyses of changes of any climate variable, and potentially any
project results set (see `dependency_on_CMIP6`)
; it has been developped on `IPSL's <https://www.ipsl.fr/>`_ `ESPRI
<https://en.aeris-data.fr/espri/>`_ platform, and it is fully portable
and usable on any machine with CMIP6 data and
e.g. conda-enabled environments (see :ref:`requirements`)

The organization of this software is based on :

- CAMMAClib, a library of python (2.7) modules providing shared functions

- notebooks, a series of parameterized IPython notebooks, which can be
  seen as "main programs" using CAMMAClib; each notebook was inspired by
  the needs of one of the multi-panel AR6/WG1/Chapter8 figures, but
  designed to be more generic than these needs . Some of these
  notebooks are used for producing more than one figure (by changing
  their run parameters)

- a series of "job scripts", where each script is dedicated to launch
  a job for actually computing one single AR6 chapter 8 figure (or a
  Technical Summary figure or panel). These jobs allow for changing
  notebook parameters

- and two notebooks for handling the selection of the set of CMIP6
  dataset versions used by the figure notebooks

In addition, a series of fixed fields representing the land fraction
for all models used has been gathered in a specific directory, in
order to alleviate for the lack of those fields for some CMIP6
experiments for some models; and, courtesy of B.Decharme, a file
describing hydrological basins (ref TBD) is included.

