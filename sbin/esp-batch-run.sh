#!/bin/bash
set -x
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#                            ESP Batch Run Script
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# EXIT CODES
#
# 0   Success
# 10  Invalid configuration
# 11  Bad directory structure
# 21  Loader failed
# 22  HEF run failed
# 23  Nodis run failed
# 24  Find unmapped labs failed
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# @author: Jason McVetta <jason.mcvetta@gmail.com>
# @organization: Channing Laboratory http://www.channing.harvard.edu
# @copyright: (c) 2009 Channing Laboratory
# @license: LGPL
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



#-------------------------------------------------------------------------------
#
#                           Platform Configuration
#
#
# You will need to populate these variables with the path to your Python 2.6+
# executable and the root of your ESP installation.
#
#-------------------------------------------------------------------------------
ESP_HOME=""
INCOMING_DATA=""
PYTHON=""
LOADER="" # Available options: 'Epic' or 'HL7'

ESP_HOME="/opt/esp"
INCOMING_DATA="/home/ftpuser/"
PYTHON="/usr/bin/python"
LOADER="Epic"


#-------------------------------------------------------------------------------
#
#        It should not be necessary to edit anything below this point.
#
#-------------------------------------------------------------------------------


#
# Sanity Checks
#
if [ -z "$ESP_HOME" ]; then
    echo "You must edit this script to set the \$ESP_HOME variable before running it."
    exit 10
fi
if [ -z "$INCOMING_DATA" ]; then
    echo "You must edit this script to set the \$INCOMING_DATA variable before running it."
    exit 10
fi
if [ -z "$PYTHON" ]; then
    echo "You must edit this script to set the \$PYTHON variable before running it."
    exit 10
fi
if [ -z "$LOADER" ]; then
    echo "You must edit this script to set the \$LOADER variable before running it."
    exit 10
fi


#
# Set up variables
#

PYTHONPATH="$ESP_HOME/src"
DJANGO_SETTINGS_MODULE="ESP.settings"

if [ "$LOADER" = "HL7" ]; then
    LOADER_CMD="emr/etl/load_hl7.py --input=$INCOMING_DATA"
elif [ "$LOADER" = "Epic" ]; then
    LOADER_CMD="emr/etl/load_epic.py --input=$INCOMING_DATA"
else
    echo "The variable \$LOADER must be set to 'Epic' or 'HL7'.  Cannot proceed." >> /dev/stderr
    exit 10
fi

# HACK!!  -- remove me after testing!
LOADER_CMD="$LOADER_CMD --no-archive"


#
# Run ESP
#

cd $ESP_HOME/src/ESP || exit 11
$PYTHON $LOADER_CMD || exit 21
$PYTHON hef/run.py || exit 22
$PYTHON nodis/run.py || exit 23
$PYTHON nodis/find_unmapped_labs.py || exit 24

#
# Success
#
exit 0
