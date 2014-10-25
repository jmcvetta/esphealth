#!/bin/bash

#This will run the MDPHNET generation scripts.  
#This takes a considerable amount of time.  Use the MDPHNET update scripts 
# for daily updates.
#Modify the following script variables as appropriate.
#This is the name of the esp database
ESPDB=esp3
#This is the name of the esp_mdphnet schema owner (authorized user)
ESPUSR=esp_mdphnet
#This is the path to the sql script
scriptpath=/srv/esp/production/share/sql_reports/CHA
#The rest of the file doesn't need to be modified
#psql -d $ESPDB -U $ESPUSR -f $scriptpath/generate_mdphnet_functions.psql && \
psql -d $ESPDB -U $ESPUSR -f $scriptpath/regen_mdphnet.pg.sql -v ON_ERROR_STOP=1 > ~/regen_mdphnet.log 2>&1

