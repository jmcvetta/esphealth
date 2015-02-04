#!/bin/bash

#This will run the MDPHNET regeneration scripts.  
#Modify the following script variables as appropriate.
#This is the name of the esp database
ESPDB=esp
#This is the name of the esp_mdphnet schema owner (authorized user)
ESPUSR=esp_mdphnet
#This is the path to the sql script
scriptpath=/srv/esp/prod/share/sql_reports/CHA
logpath=/srv/esp/logs
runtime=`date -u +%Y%m%dT%H%M%SZ`
#The rest of the file doesn't need to be modified
#psql -d $ESPDB -U $ESPUSR -f $scriptpath/generate_mdphnet_functions.psql && \
psql -d $ESPDB -U $ESPUSR -f $scriptpath/regen_mdphnet.pg.sql -v ON_ERROR_STOP=1 > $logpath/regen_mdphnet.log.$runtime 2>&1

