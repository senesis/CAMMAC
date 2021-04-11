
.. _requirements: 

Sofware requirements
---------------------

CAMMAClib and notebooks heavily rely on `CliMAF
<https://climaf.readthedocs.io>`_ for implementing data access, for
computations (mainly using `CDO
<https://code.mpimet.mpg.de/projects/cdo>`_ behind the curtain) and
for ploting figures (using `Ncl <https://www.ncl.ucar.edu/>`_ behind
the curtain).

CliMAF is designed for easing both the description of data
organization and the integration of user scripts. Because CliMAF has a built-in knowledge
of CMIP6 data organization on the ESPRI platform, a slight adaptation has to be
done for using CAMMAC on other platforms (see :ref:`adapting_for_data`) 

The job_pm.sh utility make use of `papermill <https://papermill.readthedocs.io>`_ for launching batch executions of notebooks, while allowing for changing their parameters.

Only quite common python packages are needed; package xarray is used when requesting Gini index computation 

TBD

