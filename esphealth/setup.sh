#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#                                 ESP Health
#                                Setup Script
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# This script must be run by a user with write permission on the 'esphealth'
# folder.
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


USAGE_MSG="usage: setup.sh option
-i  Install ESP (first time installation)
-d  Update PyPI dependency modules
-p  Update ESP plugin modules
-f  Freeze PIP requirements to requirements.frozen.txt
-?  Show this usage message"

function usage () {
    # Must be in quotes for mutliline formatting
    echo "$USAGE_MSG"
}

function activate_virtualenv () {
    . bin/activate
    export PIP_RESPECT_VIRTUALENV=true
    export PIP_REQUIRE_VIRTUALENV=true
}

function install () {
    #
    # Create the virutal environment, then install modules from the frozen
    # list.
    #
    echo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    echo +
    echo + Installing ESP...
    echo +
    echo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    virtualenv --no-site-packages . 
    activate_virtualenv
    pip install -v -r requirements.frozen.txt
}

function update_dependencies () {
    #
    # Update dependency modules with the latest version from PyPI.
    #
    echo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    echo +
    echo + Updating PyPI dependency modules...
    echo +
    echo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    activate_virtualenv
    pip install -U -v -r requirements.pypi.txt
}

function freeze_requirements () {
    #
    # Freeze currently installed modules to requirements.frozen.txt.
    #
    echo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    echo +
    echo + Freezing requirements...
    echo +
    echo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    activate_virtualenv
    pip freeze > requirements.frozen.txt
}

#set -x


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Main Logic
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if [ "$#" -eq 0 ]; then
    usage
    exit 1;
fi
#
# TODO: Add sanity checks for write permission on relevant folders
#
while getopts "idpf" options; do
  case $options in
    i  ) install;;
    d  ) update_dependencies;;
    f  ) freeze_requirements;;
    \? ) usage;;
    *  ) usage
         exit 1;;
  esac
done



