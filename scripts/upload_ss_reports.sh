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

# Rename files that are not being named properly by processSS
SITE_FILE="ESPAtrius_AllEnc_zip5_Excl_Site"
RES_FILE="ESPAtrius_AllEnc_zip5_Excl_Res"
mv $FILE_FOLDER/$FOLDER/$SITE_FILE".xls" $FILE_FOLDER/$FOLDER/$SITE_FILE"_"$DATE"_"$DATE".xls"
mv $FILE_FOLDER/$FOLDER/$RES_FILE".xls" $FILE_FOLDER/$FOLDER/$RES_FILE"_"$DATE"_"$DATE".xls"

scp -r -P 8080 $FILE_FOLDER/$FOLDER/*ILI* kyih@esphealth.org:~/ILI
scp -r -P 8080 $FILE_FOLDER/$FOLDER/*AllEnc* kyih@esphealth.org:~/ILI
scp -r -P 8080 $FILE_FOLDER/$FOLDER/* kyih@esphealth.org:~/other



