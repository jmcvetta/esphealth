#!/bin/bash
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
PRINT_PROGRESS=1  # Should we display progress as script runs?
ESP_HOME=""       # Root of ESP installation
INCOMING_DATA=""  # Folder where incoming data is stored
PYTHON=""         # Full path to Python 2.5+ executable
LOADER=""         # Available options: 'Epic' or 'HL7'



#===============================================================================
#
#        It should not be necessary to edit anything below this point.
#
#===============================================================================

function progress {
    if (($PRINT_PROGRESS)); then 
        echo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        echo $1
        echo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    fi
}


#-------------------------------------------------------------------------------
#
# Sanity Checks
#
#-------------------------------------------------------------------------------

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


#-------------------------------------------------------------------------------
#
# Set up variables
#
#-------------------------------------------------------------------------------

PYTHONPATH="$ESP_HOME/src"
DJANGO_SETTINGS_MODULE="ESP.settings"

if [ "$LOADER" = "HL7" ]; then
    LOADER_CMD="emr/etl/load_hl7.py --new --input=$INCOMING_DATA"
elif [ "$LOADER" = "Epic" ]; then
    LOADER_CMD="emr/etl/load_epic.py --input=$INCOMING_DATA"
else
    echo "The variable \$LOADER must be set to 'Epic' or 'HL7'.  Cannot proceed." >> /dev/stderr
    exit 10
fi

# HACK!!  -- remove me after testing!
LOADER_CMD="$LOADER_CMD --no-archive"


#-------------------------------------------------------------------------------
#
# Run ESP
#
#-------------------------------------------------------------------------------

cd $ESP_HOME/src/ESP || exit 11
progress "Loading new data"
$PYTHON $LOADER_CMD || exit 21
progress "Generating heuristic events"
$PYTHON hef/run.py || exit 22
progress "Detecting cases"
$PYTHON nodis/run.py || exit 23
progress "Compiling lab test concordance"
$PYTHON nodis/find_unmapped_labs.py || exit 24


#-------------------------------------------------------------------------------
#
# Success
#
#-------------------------------------------------------------------------------
exit 0
