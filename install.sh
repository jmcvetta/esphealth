set -x
virtualenv .
. bin/activate
export PIP_RESPECT_VIRTUALENV=true
export PIP_REQUIRE_VIRTUALENV=true
pip install -v -r requirements.txt
