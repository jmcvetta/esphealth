#!/bin/bash

#This will run the MDPHNET generation scripts.  
#This takes a considerable amount of time.  Use the MDPHNET update scripts 
# for daily updates.
#Modify the following script variables as appropriate.
#This is the name of the esp database
ESPDB=esp30
#This is the name of the esp_mdphnet schema owner (authorized user)
ESPUSR=esp_mdphnet
#This is the path to the sql script
scriptpath=/srv/esp/prod/share/sql_reports/Atrius
#The rest of the file doesn't need to be modified
psql -d $ESPDB -U $ESPUSR  -f $scriptpath/update_mdphnet_views_tables.pg.sql

