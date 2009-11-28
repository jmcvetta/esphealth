#! /bin/sh
echo 'remember to source /srv/esp/mysql-version/ESP/env-setup.sh first'
mkdir -p assets/SS/test
#python utils/espSS.py -s 20091031 -e 20091031 -z5 -o ./assets/SS/test -t -v 
#python utils/espSS.py -s 20060701 -e 20091003 -z5 -o ./assets/SS/test -t -v 
# date --date '54 days ago' +%Y%m%d
for i in $(seq 0 1 54)
do
sd=`date --date "$i days ago" +%Y%m%d`
echo $sd
python utils/espSS.py -s $sd -e $sd -z5 -o ./assets/SS/test -t -v 
done
