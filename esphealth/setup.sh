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
-i  Install ESP (first time installation) using frozen requirement file versions
-d  Update PyPI dependency modules from versions in requirements.pypi.txt
-p  Update ESP plugin modules to latest
-f  Freeze PIP requirements to requirements.frozen.txt and requirements.esp-plugins.frozen.tx
-r  Update ESP plugin modules with the frozen versions in requirements.esp-plugins.frozen.txt
-u  Uninstall ESP plugin modules from the file requirements.uninstall.txt 
-l  Lists ESP plugin modules installed 
-m  Create the virtual environment, then install modules from requirements.modules.txt
-?  Show this usage message"

function usage () {
    # Must be in quotes for multiline formatting
    echo "$USAGE_MSG"
}

function activate_virtualenv () {
    . bin/activate
    export PIP_RESPECT_VIRTUALENV=true
    export PIP_REQUIRE_VIRTUALENV=true
}

function install () {
    #
    # Create the virtual environment, then install modules from the frozen
    # list.
    #
    echo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    echo +
    echo + Installing ESP...
    echo +
    echo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    virtualenv --no-site-packages . 
    activate_virtualenv
    pip install -r requirements.frozen.txt
}

function install_modules () {
	#
    # Create the virtual environment, then install modules from the specified list
    #
    echo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    echo +
    echo + Installing ESP...
    echo +
    echo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    virtualenv --no-site-packages . 
    activate_virtualenv
    pip install -r requirements.modules.txt
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
    virtualenv --no-site-packages .
    activate_virtualenv
    pip install -U -v -r requirements.pypi.txt
}

function update_plugins () {
    #
    # Update ESP plugin modules with the latest versions.
    #
    echo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    echo +
    echo + Updating ESP plugin modules...
    echo +
    echo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    activate_virtualenv
    pip install -U -v -r requirements.plugins.txt
}

function release_plugins () {
    #
    # Update ESP plugin modules with the frozen versions.
    #
    echo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    echo +
    echo + Updating ESP frozen plugin modules...
    echo +
    echo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    activate_virtualenv
    pip install -U -v -r requirements.esp-plugins.frozen.txt
}

function uninstall_plugins () {
    #
    # Uninstall ESP plugin modules from requirements.uninstall.txt
    #
    echo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    echo +
    echo + Uninstalling ESP  plugin modules...
    echo +
    echo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    virtualenv --no-site-packages .
    activate_virtualenv
    pip uninstall -r requirements.uninstall.txt
    echo cd ./src/plugin name
    echo rm -R plugin name.egg-info
}

function list_plugins () {
	#
    # lists the list of plugings installed  
    #
    echo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    echo +
    echo + Listing installed pluggins...
    echo +
    echo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    activate_virtualenv
    pip freeze 
}

function freeze_requirements () {
    #
    # Freeze currently installed modules to requirements.frozen.txt
    # and to requirements.esp-plugins.frozen.txt 
    #
    echo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    echo +
    echo + Freezing requirements...
    echo +
    echo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    activate_virtualenv
    pip freeze > requirements.frozen.txt
    grep 'svn+http' requirements.frozen.txt > requirements.esp-plugins.frozen.txt 
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
while getopts "idpfrulm" options; do
  case $options in
    i  ) install;;
    d  ) update_dependencies;;
    p  ) update_plugins;;
    f  ) freeze_requirements;;
    r  ) release_plugins;;
    u  ) uninstall_plugins;;
    l  ) list_plugins;;
    m  ) install_modules;;
    \? ) usage;;
    *  ) usage
         exit 1;;
  esac
done