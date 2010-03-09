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

python $ESP_HOME/manage.py batch
python $ESP_HOME/ss/main.py -f --begin=$DATE --end=$DATE
python $ESP_HOME/vaers/main.py -c -r -a --begin=$DATE --end=$DATE

