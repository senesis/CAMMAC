.. _script_design:

Designing own scripts for batch
--------------------------------

You can design your own script for launching a notebook in batch mode,
taking e.g. script :download:`basic.sh <../../jobs/basic.sh>` as an
example. You should adopt the :ref:`recommended structure described
here <recommended_script_design>`. You may need to know a bit of
:ref:`Yaml syntax <yaml_syntax>`

You should better have your own version of file
``common_parameters.yaml``, and either put in in the directory you are
launching your script from, or explicitly provide its path as 5th
argument of the call to job_pm.sh. Otherwise, the file installed with
CAMMAC (in dir jobs/) will be used (see
:download:`common_parameters.yaml <../../jobs/common_parameters.yaml>`

Anyway, you can supersede the settings of common_parameters.yaml by
similar settings in your script

Remember also that some python code from file ``cammac_user_settings.py``
will be executed in one of the few first cells of the notebook. By
default, this file is sought in $CAMMAC/jobs/ (see
:download:`cammac_user_settings.py
<../../jobs/cammac_user_settings.py>`. If you want some control over
its content, put your own copy somewhere and set and export
environment variable ``CAMMAC_USER_PYTHON_CODE_DIR`` accordingly
