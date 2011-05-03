#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#                                 ESP Health
#                               Install Script
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# This script must be run by a user with write permission on the 'esphealth'
# folder.  On Ubuntu we recommend NOT installing the pip system package via
# apt-get, but instead installing pip with easy_install like this:
# 
#     $ sudo easy_install pip
#
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# TODO: Check OS version too
if [ `lsb_release -is` = "Ubuntu" ]; then
    sudo apt-get install python-setuptools python-dev libpq-dev
    sudo easy_install -U pip virtualenv
fi

set -x
virtualenv --no-site-packages . 
. bin/activate
export PIP_RESPECT_VIRTUALENV=true
export PIP_REQUIRE_VIRTUALENV=true
pip install -v -r requirements.frozen.txt
