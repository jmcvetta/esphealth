#!/bin/bash

#This will output the general population report as a CSV file, the run it through Pentaho to generate the riskscape file
#This program should be run in a directory where the user has write access.  
#If you run this as a user other than the ESPUSR, you will be prompted for a password.  
#
#Modify the following script variables as appropriate.
#This is the name of the esp database
ESPDB=esp3
#This is the name of the esp user
ESPUSR=esp3
#This is the path to the esp installation
ESPpath=/srv/esp/production
#This is the path to the Pentaho installation
panPath=/srv/pentaho/data-integration
#The rest of the file doesn't need to be modified
fileDateName="genpop-report`date +'%Y%m%d%H%M'`.csv"
psql -h 127.0.0.1 -d $ESPDB -U $ESPUSR -A -F"," < $ESPpath/share/sql_reports/CHA/general-population-report.pg.sql > $fileDateName && \
$panPath/pan.sh \
 -file=$ESPpath/share/sql_reports/CHA/riskscape.genepop-transformation.ktr \
 -param:INPUT_FILE=$fileDateName \
 -param:OUTPUT_FILE="genpop-report`date +'%Y%m%d%H%M'`.rsk"
