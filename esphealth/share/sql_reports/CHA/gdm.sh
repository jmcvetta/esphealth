#!/bin/bash

#This will output the GDM report as a CSV file, the run it through Pentaho to generate the riskscape file
#This program should be run in a directory where the user has write access.
#
#Modify the following script variables as appropriate.
#This is the path to the esp installation
ESPpath=/srv/esp/production
#This is the path to the Pentaho installation
panPath=/srv/pentaho/data-integration
#The rest of the file doesn't need to be modified
fileDateName="GDM-report`date +'%Y%m%d%H%M'`.csv"

$ESPpath/bin/esp report diabetes:gestational > $fileDateName

$panPath/pan.sh  \
   -file=$ESPpath/share/riskscape.gdm-transformation.ktr  \
   -param:INPUT_FILE=./$fileDateName \
   -param:OUTPUT_FILE=./$fileDateName.rsk

