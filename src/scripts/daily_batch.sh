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

if [ $# = 1 ] 
then
  DATE=`date -d $1 +%Y%m%d` 
else
  DATE=`date -d "-1 day" +%Y%m%d`
fi


#
# Sync to PostgreSQL
#
# PostgreSQL JDBC driver issues necessitate that the sync be done in two
# stages, using different driver versions.
#
/opt/pdi-3.1.0-pg7.4/kitchen.sh -rep pdi_3_1_0 -user esp -dir prod-sync -job prod-sync &&
/opt/pdi-3.1.0-pg8.4/pan.sh -rep pdi_3_1_0 -user esp -dir prod-sync -trans "sync encounter icd9s" &&
python $ESP_HOME/ss/main.py -f --begin=$DATE --end=$DATE &&
source $BASEDIR/upload_ss_reports.sh &&
python $ESP_HOME/vaers/main.py -c -r -a --begin=$DATE --end=$DATE &&
source $BASEDIR/upload_vaers_reports.sh &&
source $BASEDIR/upload_satscan_reports.sh 

