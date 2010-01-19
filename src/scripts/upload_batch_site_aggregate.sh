#! /bin/bash

FILE_FOLDER="`pwd`/../ESP/ss/assets"

for i in {71..1}
do 
  DATE=`date -d "-$i day" +%Y%m%d`
  FOLDER=`date -d "-$i day" +%Y/%m/%d`  
  scp -r -P 8080 $FILE_FOLDER/$FOLDER/ESPAtrius_SyndAgg_zip5_Site_Excl_ILI_*.xls kyih@esphealth.org:~/ILI
  scp -r -P 8080 $FILE_FOLDER/$FOLDER/ESPAtrius_SyndAgg_zip5_Site_Excl_*.xls kyih@esphealth.org:~/other
done

