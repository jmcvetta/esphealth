#!/bin/sh
#
# Script to load old North Adams HL7 data one month at a time, to avoid
# overwheling the import system.
#
#
# Does NOT work yet!!!!
#

ESP_HOME=/home/rejmv/work/esp/
ESP_SRC=$ESP_HOME/src/ESP/
NORTH_ADAMS_DATA=$ESP_HOME/NORTH_ADAMS/


cd $NORTH_ADAMS_DATA/all_hl7
mv 2008-4* ../incomingHL7/
cd $ESP_SRC
python utils/hl7_to_etl.py
python utils/incomingParser.py


for filespec in _2008-{4..12}-; do
	cd $NORTH_ADAMS_DATA/all_hl7
	mv *$filespec* ../incomingHL7/
	cd $ESP_SRC
	python utils/hl7_to_etl.py
	python utils/incomingParser.py
done
