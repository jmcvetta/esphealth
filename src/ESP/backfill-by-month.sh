#!/bin/bash
#
# Script to load old North Adams HL7 data one month at a time, to avoid
# overwheling the import system.
#
#

ESP_HOME=/home/rejmv/work/esp/
ESP_SRC=$ESP_HOME/src/ESP/
ALL_HL7=$ESP_HOME/NORTH_ADAMS/all_HL7/
INCOMING_HL7=$ESP_HOME/NORTH_ADAMS/incomingHL7/
INCOMING_DATA=$ESP_HOME/NORTH_ADAMS/incomingData/


# Clean up any leftovers
cd $INCOMING_HL7
rm -f *

echo '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
echo '2008-4'
echo '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
cd $ALL_HL7
cp 2008-4* $INCOMING_HL7
cd $ESP_SRC
rm $INCOMING_DATA/*
python utils/hl7_to_etl.py
python utils/incomingParser.py --all


for year_month in 2008-{4..12}; do
	echo '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
	echo $year_month
	echo '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
	cd $ALL_HL7
	cp *_$year_month-* $INCOMING_HL7
	cd $ESP_SRC
	rm $INCOMING_DATA/*
	python utils/hl7_to_etl.py
	python utils/incomingParser.py --all
done
