Software organization
---------------------

The organization of the software is based on :

- CAMMAClib/, a library of python (2.7) modules providing shared functions

- notebooks/, a series of parameterized IPython notebooks, which can be
  seen as "main programs" using CAMMAClib; each notebook was inspired by
  the needs of one of the multi-panel AR6/WG1/Chapter8 figures, but
  designed to be more generic than these needs. 

- scripts/, a series of "job scripts", where each script is dedicated to launch
  a job for actually computing one single AR6 chapter 8 figure or table (or a
  Technical Summary figure or panel). These jobs allow for changing
  notebook parameters. These "job scripts" are, at the time of
  writing, not yet publicly available; they will became available when
  the AR6/WGI report is released, in the course of 2021. A single job
  is yet provided as an example

- select_data_versions/ : two notebooks for handling the selection of the set of CMIP6
  dataset versions used by the figure notebooks for the case of AR6 report

- data/ :

  - fixed_fields/, a series of fixed fields representing the land
    fraction for all models used has been gathered in a specific
    directory, in order to alleviate for the lack of those fields for
    some CMIP6 experiments for some models;

  - basins/ , a series of datafiles defining AR6 monsoon regions (courtesy of Sabin Thazhe Purayil) and a file describing world hydrological
    basins (courtesy of B.Decharme - ref TBD)

  - colomaps/ , the series of AR6 defined Ncl colormaps
