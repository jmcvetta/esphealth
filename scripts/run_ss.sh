#! /bin/bash

APP_FOLDER="`pwd`/../ESP/utils"
FILE_FOLDER="`pwd`/../ESP/assets/SS"

if [ $# = 1 ] 
then
  DATE=`date -d $1 +%Y%m%d` 
  FOLDER=`date -d $1 +%Y/%m/%d` 
else
  DATE=`date -d "-1 day" +%Y%m%d`
  FOLDER=`date -d "-1 day" +%Y/%m/%d`  
fi

mkdir -p $FILE_FOLDER/$FOLDER

python $APP_FOLDER/espSS.py -s $DATE -e $DATE -z5 -o $FILE_FOLDER/$FOLDER -t -v 

