#!/bin/bash
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# @author: Raphael Lullis <raphael.lullis@channing.harvard.edu>
# @organization: Channing Laboratory http://www.channing.harvard.edu
# @copyright: (c) 2009 Channing Laboratory
# @license: LGPL
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

BASEDIR=`dirname $0`
ESP_HOME=$BASEDIR/../ESP

export PYTHONPATH=$BASEDIR/..
export DJANGO_SETTINGS_MODULE=`basename $ESP_HOME`.settings

python $ESP_HOME/utils/download_epic_files.py &&
python $ESP_HOME/utils/incomingParser.py &&
python $ESP_HOME/utils/identifyCases.py &&
python $ESP_HOME/utils/send_hl7.py &&

# Sync to postgresql.
/opt/pdi-3.1.0/kitchen.sh -rep pdi_3_1_0 -user esp -dir prod-sync -job prod-sync
