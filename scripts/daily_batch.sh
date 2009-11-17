#!/bin/bash
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# @author: Raphael Lullis <raphael.lullis@channing.harvard.edu>
# @organization: Channing Laboratory http://www.channing.harvard.edu
# @copyright: (c) 2009 Channing Laboratory
# @license: LGPL
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


ESP_HOME=`pwd`/../ESP

export PYTHONPATH=`pwd`/..
export DJANGO_SETTINGS_MODULE=`basename $ESP_HOME`.settings


python $ESP_HOME/utils/download_epic_files.py
python $ESP_HOME/utils/incomingParser.py
source ./run_ss.sh
source ./upload_ss_reports.sh

