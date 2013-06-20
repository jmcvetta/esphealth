#!/bin/bash

#This will regen the ILI table and output the ili reports
#
#Modify the following script variables as appropriate.
#This is the name of the esp database
ESPDB=esp30
#This is the name of the esp_mdphnet schema owner (authorized user)
ESPUSR=esp_mdphnet
#This is the path to where the sql scripts are stored
scriptpath=/srv/esp/prod/share/sql_reports/Atrius
#this defines the output folder
FILE_FOLDER=/srv/esp30/data

if [ $# = 1 ]
then
  DATE=`date -d $1 +%Y%m%d`
  YEAR=`date -d $1 +%Y`
  FOLDER=`date -d $1 +%Y/%m/%d`
else
  DATE=`date -d "-1 day" +%Y%m%d`
  YEAR=`date -d "-1 day" +%Y`
  FOLDER=`date -d "-1 day" +%Y/%m/%d`
fi
ili_folder=$FILE_FOLDER/ili_reports/$FOLDER
mkdir -p $ili_folder

#The rest of the file doesn't need to be modified
psql -d $ESPDB -U $ESPUSR -f $scriptpath/weekly_ili_summary_table.pg.sql
file=$ili_folder/cdc-ili-report-${DATE}
psql -d $ESPDB -U $ESPUSR -A -F"," < $scriptpath/cdc_ili_report.pg.sql > ${file}.csv
file=$ili_folder/weekly-ili-report-${DATE}
psql -d $ESPDB -U $ESPUSR -A -F"," < $scriptpath/weekly_ili_report.pg.sql > ${file}.csv
