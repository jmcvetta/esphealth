#!/usr/bin/env bash

export ESP_HOME=/srv/esp
export PYTHON=/opt/python-2.6.1/bin/python2.6 
export PYTHON_EGG_CACHE=~ 


cd $ESP_HOME/src/ESP 
source ./env-setup.sh \
&& $PYTHON ./emr/load_hl7.py --input=/home/ESP/NORTH_ADAMS/incomingHL7/ --all\
&& $PYTHON ./hef/run.py --incremental \
&& $PYTHON ./nodis/run.py -c \
&& $PYTHON ./utils/status_report.py | mail -s 'ESP Status Report' jason.mcvetta@channing.harvard.edu \
|| echo "ERROR HIT"
