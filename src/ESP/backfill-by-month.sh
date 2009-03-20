#!/bin/bash
#
# Script to load old North Adams HL7 data one month at a time, to avoid
# overwheling the import system.
#
#

ESP_HOME=/home/rejmv/work/north_adams/
ESP_SRC=$ESP_HOME/src/ESP/
ALL_HL7=$ESP_HOME/NORTH_ADAMS/all_HL7/
INCOMING_HL7=$ESP_HOME/NORTH_ADAMS/incomingHL7/
INCOMING_DATA=$ESP_HOME/NORTH_ADAMS/incomingData/


# Clean up any leftovers
cd $INCOMING_HL7 && rm -f * || exit

for year_month in 200{8..9}-{1..12}; do
    echo '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
    echo $year_month
    echo '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
    cd $ALL_HL7
    cp *_$year_month-* $INCOMING_HL7
    rm -f $INCOMING_DATA/* || exit
    cd $ESP_SRC
    python $ESP_SRC/utils/hl7_to_etl.py
    python $ESP_SRC/utils/incomingParser.py --all
done
