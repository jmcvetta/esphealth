#!/bin/bash

#This will output the ili reports
#This program should be run in a directory where the user has write access.  
#
#Modify the following script variables as appropriate.
#This is the name of the esp database
ESPDB=esp30
#This is the name of the esp user
ESPUSR=esp_mdphnet
#The rest of the file doesn't need to be modified
fileDateName="cdc-ili-report`date +'%Y%m%d%H%M'`.csv"
psql -h 127.0.0.1 -d $ESPDB -U $ESPUSR -W -A -F"," < /home/bzambarano/cdc_ili_report.pg.sql > $fileDateName
fileDateName="weekly-ili-report`date +'%Y%m%d%H%M'`.csv"
psql -h 127.0.0.1 -d $ESPDB -U $ESPUSR -W -A -F"," < /home/bzambarano/weekly_ili_report.pg.sql > $fileDateName
