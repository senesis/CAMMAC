{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# CAMMAC https://cammac.readthedocs.io\n",
    "S.Sénési for Météo-France - sept 2019 to march 2021\n",
    "\n",
    "# Create a derived varable from a (single) primary one, provided derivation can be formulated by a CDO operations pipe\n",
    "\n",
    "\n",
    "## Here, applied to the case of creating yearly stats out of daily precipitation, for selected experiments, models , variants; and create a data versions dictionnary for this derived data\n",
    "\n",
    "## Parameters stand in first cell, and are either commented here or in the doc (see above)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "from IPython.core.display import display, HTML, Image\n",
    "display(HTML(\"<style>.container { width:100% !important; }</style>\"))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "tags": [
     "parameters"
    ]
   },
   "outputs": [],
   "source": [
    "#\n",
    "# Define derived variables : output label, input variable and its table, and CDO operation to apply\n",
    "#\n",
    "one_mm_per_day=\"%g\"%(1./(24.*3600.)) # in S.I.\n",
    "cases = {\n",
    "    #\n",
    "    # Number of dry days per year\n",
    "    \"dry days\"   : {\"label\":\"dday\"  , \"variable\":\"pr\", \"table\":\"day\" ,\n",
    "               \"operator_args\" :{\"operator\" :\"expr,'dday=pr' -yearsum -ltc,\"+one_mm_per_day }},\n",
    "    #\n",
    "    # Mean precipitation for non-dry days\n",
    "    \"daily rain\" : {\"label\":\"drain\", \"variable\":\"pr\", \"table\":\"day\", \n",
    "               \"operator_args\" : {\"operator\" :\"expr,'drain=pr' -yearmean -setrtomiss,-1,\"+one_mm_per_day} } ,\n",
    "}\n",
    "#\n",
    "# List experiments to process, and period\n",
    "periods           = {\n",
    "    \"historical\" : \"1850-2014\",\n",
    "    \"ssp126\"     : \"2015-2100\",\n",
    "    \"ssp245\"     : \"2015-2100\",\n",
    "    \"ssp585\"     : \"2015-2100\",\n",
    "    \"piControl\"  : None\n",
    "\n",
    "}\n",
    "#\n",
    "excluded_models   = {} # A dict of list of excluded models, per experiment\n",
    "included_models   = {} # A dict of list of included models, per experiment\n",
    "#\n",
    "data_versions_tag    = \"20200918\"\n",
    "data_versions_dir    = \"/home/ssenesi/CAMMAC/select_data_versions\"\n",
    "\n",
    "# Define json output : \n",
    "#  - new (i.e. from scratch) or \n",
    "#  - add_separate (add to existing secondary dict) or \n",
    "#  - add_to_input (combine with input data versions dict, in a distinct file)\n",
    "output_option        = \"add_to_input\"\n",
    "version              = \"_derived\" # Used as a suffix to input name in output json file name\n",
    "\n",
    "output_root     = \"/data/ssenesi/CMIP6_derived_variables\"\n",
    "output_pattern  = output_root+\"/${variable}/${variable}_${table}_${model}_${experiment}_${realization}_${grid}_${version}_${PERIOD}.nc\"\n",
    "#\n",
    "# Should we recompute existing files ?\n",
    "recompute         = False\n",
    "#\n",
    "do_test           = True"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "if do_test :\n",
    "    # List experiments to process, and period\n",
    "    periods           = { \"ssp126\" : \"2015-2017\", }\n",
    "    #periods           = { \"historical\" : \"1850-1852\", }\n",
    "    #periods           = { \"piControl\"  : None, }\n",
    "    included_models   = { \"ssp126\" : [ \"EC-Earth3\" ] }\n",
    "    version=\"_test\"\n",
    "    if \"daily rain\" in cases : cases.pop(\"daily rain\")\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import sys\n",
    "from string import Template\n",
    "import os\n",
    "import json\n",
    "\n",
    "# Climaf setup (version >= 1.2.13 - see https://climaf.readthedocs.io)\n",
    "sys.path.append(climaf_lib) \n",
    "from climaf.api import *\n",
    "\n",
    "# Climaf settings\n",
    "climaf.cache.stamping=False\n",
    "\n",
    "sys.path.append(CAMMAClib ) \n",
    "from CAMMAClib.mips_et_al  import read_versions_dictionnary, \\\n",
    "            institute_for_model, mip_for_experiment, models_for_experiments\n",
    "from CAMMAClib.ancillary  import feed_dic"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "climaf.dataloc.dataloc(project='CMIP6', organization='generic', url=output_pattern, table='yr')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "data_versions=read_versions_dictionnary(data_versions_tag,data_versions_dir)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Set output data_version dictionnary "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "jsfile=\"%s/Data_versions_selection_%s%s.json\" % (data_versions_dir , data_versions_tag, version)\n",
    "if output_option == \"add_separate\" :\n",
    "    if os.path.exists(jsfile):\n",
    "        with open(jsfile,\"r\") as f :\n",
    "            print \"Loading data versions dict to complement from %s\"%jsfile\n",
    "            derived_versions=json.load(f)\n",
    "    else :\n",
    "        print \"Creating derived data versions from scratch \"\n",
    "        derived_versions=dict()\n",
    "elif output_option == \"add_to_input\" :\n",
    "    print \"Creating derived data versions dict from input dict %s in %s\"%(data_versions_tag,jsfile)\n",
    "    derived_versions=data_versions\n",
    "elif output_option == \"new\" :\n",
    "    print \"Creating derived data versions from scratch in %s\"%jsfile\n",
    "    derived_versions=dict()\n",
    "else :\n",
    "    raise Error(\"Unkown output_option value : %s\"%output_option)\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Compute pre-processed variables"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "for case in cases :\n",
    "    variable = cases[case][\"variable\"]\n",
    "    table    = cases[case][\"table\"]\n",
    "    for experiment in periods :\n",
    "        excluded = excluded_models.get(experiment,[])\n",
    "        included = included_models.get(experiment,None)\n",
    "        #\n",
    "        # Select data versions in the same way as for other processings,\n",
    "        # maybe with more models \n",
    "        models_variants=models_for_experiments(data_versions,variable,table,\n",
    "                                      [experiment],excluded,included)\n",
    "        for model,variant in models_variants :\n",
    "            # Compute list of relevant files for the period to process\n",
    "            grid,version,data_period=data_versions[experiment][variable][table][model][variant]\n",
    "            pperiod = periods[experiment]\n",
    "            if pperiod is None :\n",
    "                # For piControl, process whole available period\n",
    "                pperiod=data_period\n",
    "            print \"For %10s, %10s,%20s,%s %20s\"%(case, experiment,model,variant,pperiod),\n",
    "            #continue\n",
    "            dic=dict(project=\"CMIP6\", experiment=experiment, model=model, institute=institute_for_model(model), \n",
    "                     period=pperiod,variable=variable, table=table,mip=mip_for_experiment(experiment),\n",
    "                     realization=variant, version=version, grid=grid)\n",
    "            data=ds(**dic)\n",
    "            files=data.baseFiles().split()\n",
    "            print \"  % 3d file(s) to process\"%len(files)\n",
    "            #\n",
    "            #\n",
    "            dic[\"table\"]=\"yr\"\n",
    "            dic[\"variable\"]=cases[case][\"label\"]\n",
    "            all_periods=[] # The list of actually processed periods\n",
    "            # Compute total period and check if corresponding otuput file already exists\n",
    "            for each_file in files :\n",
    "                actual_period = each_file.split('_')[-1].replace(\".nc\",\"\")\n",
    "                all_periods.append(climaf.period.init_period(actual_period))\n",
    "            total_period=climaf.period.merge_periods(all_periods)\n",
    "            dic[\"PERIOD\"]=str(total_period[0])\n",
    "            out_file = Template(output_pattern).safe_substitute(**dic)\n",
    "            #print \"Outfile = %s\"%out_file\n",
    "            if recompute :\n",
    "                print \"First removing %s\"%out_file\n",
    "                os.system(\"rm -f %s\"%(out_file))\n",
    "            if not os.path.exists(out_file) :\n",
    "                #\n",
    "                files_to_merge = \"\" # The whitespace separated list of processed files, to merge at the end\n",
    "                for each_file in files :\n",
    "                    # Compute output filename\n",
    "                    actual_period = each_file.split('_')[-1].replace(\".nc\",\"\")\n",
    "                    dic[\"PERIOD\"]=actual_period\n",
    "                    one_file = Template(output_pattern).safe_substitute(**dic)\n",
    "                    if os.path.exists(one_file) and not recompute : \n",
    "                        continue\n",
    "                    else :\n",
    "                        #\n",
    "                        # Apply relevant operation\n",
    "                        print \"\\tProcessing\",each_file\n",
    "                        fdata=fds(each_file,simulation=experiment)\n",
    "                        derived=ccdo(fdata,**cases[case][\"operator_args\"])\n",
    "                        out_dir  = os.path.dirname(one_file)\n",
    "                        if not os.path.exists(out_dir) : \n",
    "                            os.makedirs(out_dir)\n",
    "                        cfile(derived,one_file,ln=True)\n",
    "                        # \n",
    "                    # Record filenames to merge\n",
    "                    files_to_merge += \" \"+one_file\n",
    "                    #\n",
    "                if len(files) > 1 :\n",
    "                    os.system(\"cdo mergetime %s %s\"%(files_to_merge,out_file))\n",
    "                    os.system(\"rm -f %s\"%(files_to_merge))\n",
    "            feed_dic(derived_versions,(grid,version,str(total_period[0])),experiment,cases[case][\"label\"],\"yr\",model,variant)\n",
    "                   \n",
    "            #\n",
    "#\n",
    "with open(jsfile,\"w\") as f :\n",
    "    json.dump(derived_versions,f,separators=(',', ': '),indent=3,ensure_ascii=True)\n",
    "print \"Data versions dictionnary written as \"+jsfile\n",
    "\n",
    "#write_versions_dic(\"201902071814\")   "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 2",
   "language": "python",
   "name": "python2"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 2
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython2",
   "version": "2.7.15"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
