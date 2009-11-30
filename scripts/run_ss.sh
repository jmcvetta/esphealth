#! /bin/sh
mkdir -p assets/SS/2009/09
mkdir -p assets/SS/2009/09/01
mkdir -p assets/SS/2009/09/02

python utils/espSS.py -s 20090901 -e 20090901 -z5 -o ./assets/SS/2009/09/01 -t -v 
python utils/espSS.py -s 20090902 -e 20090902 -z5 -o ./assets/SS/2009/09/02 -t -v 
