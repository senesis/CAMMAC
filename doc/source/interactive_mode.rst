Interactive mode
=====================

The interactive execution of notebooks provides extended flexibility
for testing and modifying the code. The preparation steps for an
interactive session are :

- to export variables ``CAMMAC`` and ``CLIMAF`` :
  
  .. code-block:: bash
		  
     export CAMMAC=/data/ssenesi/CAMMAC
     export CLIMAF=/home/ssenesi/climaf_installs/V2.0.1

- to source file ``jobs/job_env.sh``

  .. code-block:: bash
		  
     source $CAMMAC/jobs/job_env.sh
     
- if you wish to systematically load some of your code in CAMMAC notebooks,
  to export environment variable ``CAMMAC_USER_PYTHON_CODE_DIR`` with
  a value set to a directory containing a suitable
  cammac_user_settings.py file (otherwise, the one in $CAMMAC/jobs will be used)


and then to launch jupyter e.g. on a copy of some notebook 
  
