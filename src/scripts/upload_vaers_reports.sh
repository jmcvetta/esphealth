#! /bin/bash

HL7_FOLDER=../ESP/vaers/assets/hl7_messages

if [ $# = 1 ] 
then
  DATE=`date -d $1 +%Y%m%d` 
  FOLDER=`date -d $1 +%Y/%m/%d` 
else
  DATE=`date -d "-1 day" +%Y%m%d`
  FOLDER=`date -d "-1 day" +%Y/%m/%d`  
fi

scp -r -P 8080 $HL7_FOLDER/$FOLDER/report* relul@esphealth.org:~/vaers