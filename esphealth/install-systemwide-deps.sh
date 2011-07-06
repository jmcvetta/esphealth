#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#                                 ESP Health
#                               Install Script
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# TODO: Check OS version too
if [ `lsb_release -is` = "Ubuntu" ]; then
    sudo apt-get install python-setuptools python-dev libpq-dev
    sudo easy_install -U pip virtualenv
else
    echo ERROR:
    echo
    echo Automatic installation of system-wide dependencies is currently supported only for Ubuntu Linux.
    echo
    exit -1
fi
