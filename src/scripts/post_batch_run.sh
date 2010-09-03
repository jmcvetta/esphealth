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

# DATE should be the first parameter, in the YYYYMMDD format.

if [ $# = 1 ] 
then
  DATE=$1 
else
  DATE=`date -d "-1 day" +%Y%m%d`
fi

# If you need to run any scripts besides daily_batch, add them here.
# Examples below, for sites that would run ESP:VAERS and ESP:SS

python $ESP_HOME/ss/main.py -f --begin=$DATE --end=$DATE
python $ESP_HOME/vaers/main.py -c -r -a --begin=$DATE --end=$DATE
source $BASEDIR/upload_ss_reports.sh
source $BASEDIR/upload_satscan_reports.sh
