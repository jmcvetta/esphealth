#! /bin/sh
# espSS modified nov 28 to only count Urgent care and visit events - less than half of
# all since denominators and rates are inflated
# script to rerun all SS data as requested by Inna
# one big file to oct03 and then daily files
#
echo 'remember to source /srv/esp/mysql-version/ESP/env-setup.sh first'
mkdir -p assets/SS/test
python utils/espSS.py -s 20060701 -e 20091003 -z5 -o ./assets/SS/test -t -v 
# date --date '54 days ago' +%Y%m%d takes us back to oct4
for i in $(seq 0 1 54)
do
sd=`date --date "$i days ago" +%Y%m%d`
echo $sd
python utils/espSS.py -s $sd -e $sd -z5 -o ./assets/SS/test -t -v 
done
