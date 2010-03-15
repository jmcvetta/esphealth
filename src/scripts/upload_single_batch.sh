#! /bin/bash

FILE_FOLDER="`pwd`/../ESP/ss/assets"

for i in {14..3}
do 
  DATE=`date -d "-$i day" +%Y%m%d`
  FOLDER=`date -d "-$i day" +%Y/%m/%d`  
  scp -r -P 8080 $FILE_FOLDER/$FOLDER/*ILI* kyih@esphealth.org:~/ILI
  scp -r -P 8080 $FILE_FOLDER/$FOLDER/*AllEnc* kyih@esphealth.org:~/ILI
  scp -r -P 8080 $FILE_FOLDER/$FOLDER/* kyih@esphealth.org:~/other
done

