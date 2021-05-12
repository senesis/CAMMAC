Software organization, requirements and installation 
====================================================


.. _organization:

Software organization and directory structure
----------------------------------------------

The directory structure of the software is composed of 5 directories :

- **CAMMAClib**/, a library of python (2.7) modules providing shared
  functions, and documented :ref:`there <CAMMAClib>`

- **notebooks**/, a series of parameterized IPython notebooks, which can be
  seen as "main programs" using CAMMAClib; each notebook was inspired by
  the needs of one of the multi-panel AR6/WG1/Chapter8 figures, but
  designed to be more generic than these needs. See the :ref:`notebook_gallery`

- **jobs**/, a series of "job scripts", where each script is dedicated
  to launch a job for actually computing one single AR6 chapter 8
  figure or table (or a Technical Summary figure or panel). These jobs
  allow for changing notebook parameters. These "job scripts" are, at
  the time of writing, not yet publicly available; they will became
  available when the AR6/WGI report is released, in the course
  of 2021. A few jobs are yet provided as examples or for ancillary tasks.

- **select_data_versions**/ : notebooks for handling the selection of
  the set of CMIP6 dataset versions used by the figure notebooks for
  the case of AR6 report, and for data check and pre-processing

- **data**/ :

  - Data_versions_selection_20210201.json : a dictionnary of CMIP6
    data versions available on the `ESPRI`_ platform on 1st february
    2021, suited for use with the notebooks

  - fixed_fields/, a series of fixed fields representing the land
    fraction for all models used has been gathered in a specific
    directory, in order to alleviate for the lack of those fields for
    some CMIP6 experiments for some models;

  - basins/ , a series of datafiles defining AR6 monsoon regions (courtesy of Sabin Thazhe Purayil) and a file describing world hydrological
    basins (courtesy of B.Decharme - `Decharme et al. 2019 <https://doi.org/10.1029/2018MS001545>`_)

  - colomaps/ , the series of AR6 defined Ncl colormaps


.. _requirements: 

Sofware requirements
---------------------

CAMMAC main programs are notebooks and so need Jupyter. However, using
CAMMAClib in similar python main programs is also possible

CAMMAClib and notebooks heavily rely on `CliMAF
<https://climaf.readthedocs.io>`_ with a version >= 2.0.1 [#f1]_ for
implementing data access, for computations (mainly using `CDO
<https://code.mpimet.mpg.de/projects/cdo>`_ behind the curtain) and
for ploting figures (using `Ncl <https://www.ncl.ucar.edu/>`_ behind
the curtain).

Because CliMAF has a built-in knowledge of CMIP6 data organization on
the `ESPRI`_ platform, a slight adaptation has to be done for using
CAMMAC on other platforms (see :ref:`adapting_for_data`)

The job_pm.sh utility make use of `papermill`_ for launching batch executions of
notebooks, while allowing for changing their parameters.

Only quite common python packages are needed; they include numpy and
xarray (and requests when using the notebook queryin the ESGF errata
system). TBD : give a detailed list of actually required packages


.. _installation:

Installation
-------------

Once :ref:`required softwares <requirements>` are installed, installing
CAMMAC is as simple as :

.. _cloning:

- cloning the github repository (which amounts to less the 40 Mbytes) by

.. code-block:: bash

     mkdir <my_cammac_install>
     cd <my_cammac_install>
     git clone https://github.com/senesis/CAMMAC

     
- create a file similar to :download:`jobs/job_env_ciclad.sh
  <../../jobs/job_env_ciclad.sh>`, which will allow to set up the
  environment:
  
  - either automatically for jobs launched by jobs/job_pm.sh or
  - manually before launching jupyter for interactive use of CAMMAC
    notebooks

- change the symbolic link jobs/job_env.sh to designate that new file

- adapt the content of jobs/common_parameters.yaml, replacing all
  occurrences of /data/ssenesi/CAMMAC by the full path of your CAMMAC
  install directory

- adapt the code of :download:`jobs/job_pm.sh <../../jobs/job_pm.sh>`
  to your batch command if command 'qsub' is not available

- insert this code either in your profile or before using CAMMAC
  scripts or notebooks :

.. code-block:: bash

   export CLIMAF=<a CliMAF directory with version > 2.0>
   export CAMMAC=<my_cammac_install>/CAMMAC  # Must be a full path

  
.. rubric:: Footnotes

.. [#f1] CliMAF 2.0.0 is OK except for using the hatching confidence
         scheme based on Knutti and Sedlacek robustness index, in notebool `basic`
