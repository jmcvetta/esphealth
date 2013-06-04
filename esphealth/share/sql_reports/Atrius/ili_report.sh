#!/bin/bash

#This will regen the ILI table and output the ili reports
#
#Modify the following script variables as appropriate.
#This is the name of the esp database
ESPDB=esp30
#This is the name of the esp_mdphnet schema owner (authorized user)
ESPUSR=esp_mdphnet
#This is the path to where the scripts are stored
scriptpath=/srv/opt/esp30/share/sql_reports/Atrius
outpath=/home/bzambarano/ili_reports
#The rest of the file doesn't need to be modified
psql -d $ESPDB -U $ESPUSR -f $scriptpath/weekly_ili_summary_table.pg.sql
fileDateName="cdc-ili-report`date +'%Y%m%d%H%M'`.csv"
psql -d $ESPDB -U $ESPUSR -A -F"," < $scriptpath/cdc_ili_report.pg.sql > $outpath/$fileDateName
fileDateName="weekly-ili-report`date +'%Y%m%d%H%M'`.csv"
psql -d $ESPDB -U $ESPUSR -A -F"," < $scriptpath/weekly_ili_report.pg.sql > $outpath/$fileDateName
