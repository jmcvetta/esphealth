#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#                                 ESP Health
#                               Install Script
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# This script must be run by a user with write permission on the 'esphealth'
# folder.
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

set -x
virtualenv --no-site-packages . 
. bin/activate
export PIP_RESPECT_VIRTUALENV=true
export PIP_REQUIRE_VIRTUALENV=true

read -p "Make sure eclipse is shutdown. Press any key to start svn update or Ctrl+C to abort..."

svn up
pip install -U -v -r requirements.txt
