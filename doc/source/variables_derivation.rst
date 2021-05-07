.. _variable_derivation:

Variable derivation
=====================

For deriving new variables to be plotted, and besides the way which
involves pre-processing (see :ref:`derived_variables`), CAMMAC includes a
mechanics for use by its change compute function
`changes.change_fields`, which allows on-the-fly transformation of a
variable using any CliMAF operator, providing it with arguments.

This is based on a dictionnary (`changes.derivations`) defined as
shown below, and which links a derivation name (e.g. ``dry``) to a
CliMAF operator and its arguments (e.g. ``ccdo`` and ``:{"operator"
:"yearsum -ltc,"+one_mm_per_day }``). That exemple derives the annual
number of dry days from the daily precipitation values

How this information is used is explained with function `changes.change_fields`

Key value ``plain`` simply means : no derivation/transformation An
advanced use of this mechanics also allows to compute the inter-annual
variaility of some variable using key ``iav``


.. code-block:: python

   one_mm_per_day="%g"%(1./(24.*3600.)) # in S.I.

   derivations={
        # Default : no transformation of the variable
        "plain"        : {},
    
        # Annual count of number of dry days (when applied to daily precip by change_fields)
        "dry"          : { "operator" : ccdo,              
                           "operator_args" :{"operator" :"yearsum -ltc,"+one_mm_per_day }},
    
        # Annual average daily rain for non-dry days (when applied to daily precip  by change_fields)
        "drain"        : { "operator" : ccdo,              
                           "operator_args" : {"operator" :"yearmean -setrtomiss,-1,"+one_mm_per_day}},
    
        # Inter-annual variability (when applied to monthly data  by change_fields)
        "iav"          : { "post_operator" : inter_annual_variability, 
                           "post_operator_args" :{"house_keeping" : True, "compute": True}},
    
        # Gini index on annual values (when applied to monthly data by change_fields)
        "gini"         : { "post_operator" : gini},
    
        # Walsh seasonnality index (when applied to monthly precip by change_fields)
        "seasonality"  : { "operator" : walsh_seasonality }, 
    }
