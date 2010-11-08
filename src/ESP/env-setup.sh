#!/bin/bash
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#            Setup shell environment for use with an ESP component
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Usage:
#   $ source ./esp_env.sh
#
# WARNING: Strange behavior may occur if you source this file from anywhere
# except the folder where it lives.
#

echo $0 | grep -q env-setup 
if [ $? -eq 0 ]; then
    echo "Usage:" >> /dev/stderr
    echo "  $ source ./env-setup.sh" >> /dev/stderr
    exit
fi

cur_dir=`pwd`
mod_name=`basename $cur_dir`
export PYTHONPATH=`cd ..; pwd`
export DJANGO_SETTINGS_MODULE=$mod_name.settings
echo Shell enviornment has been configured for $mod_name:
echo "    PYTHONPATH=$PYTHONPATH"
echo "    DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE"
