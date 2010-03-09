#! /bin/bash


BASEDIR=`dirname $0`
ESP_HOME=$BASEDIR/../ESP

FILE_FOLDER=$BASEDIR/../ESP/ss/assets

if [ $# = 1 ] 
then
  DATE=`date -d $1 +%Y%m%d` 
  FOLDER=`date -d $1 +%Y/%m/%d` 
else
  DATE=`date -d "-1 day" +%Y%m%d`
  FOLDER=`date -d "-1 day" +%Y/%m/%d`  
fi

scp -r -P 8080 $FILE_FOLDER/$FOLDER/*ILI* kyih@esphealth.org:~/ILI
scp -r -P 8080 $FILE_FOLDER/$FOLDER/*AllEnc* kyih@esphealth.org:~/ILI
scp -r -P 8080 $FILE_FOLDER/$FOLDER/* kyih@esphealth.org:~/other