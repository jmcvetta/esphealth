#! /bin/bash


BASEDIR=`dirname $0`
SATSCAN_SVN_FOLDER=$BASEDIR/../../assets/ss/
ESP_HOME=$BASEDIR/../ESP

FILE_FOLDER=$BASEDIR/../ESP/ss/assets/satscan

if [ $# = 1 ] 
then
  DATE=`date -d $1 +%Y%m%d` 
  YEAR=`date -d $1 +%Y` 
  FOLDER=`date -d $1 +%Y/%m/%d` 
else
  DATE=`date -d "-1 day" +%Y%m%d`
  YEAR=`date -d "-1 day" +%Y` 
  FOLDER=`date -d "-1 day" +%Y/%m/%d`  
fi

scp -r -P 8080 $FILE_FOLDER/$FOLDER/*.zip kyih@esphealth.org:~/satscan &&
mkdir -p $SATSCAN_SVN_FOLDER/$FOLDER &&
cp $FILE_FOLDER/$FOLDER/*.zip $SATSCAN_SVN_FOLDER/$FOLDER/ &&
cp $FILE_FOLDER/$FOLDER/*.txt $SATSCAN_SVN_FOLDER/$FOLDER/ &&
cp /opt/satscan/boston.geo $SATSCAN_SVN_FOLDER/$FOLDER/ &&
cd $SATSCAN_SVN_FOLDER/ &&
svn --force add $YEAR/ &&
svn ci -m "Commit made by automated script on $DATE" &&
cd $BASEDIR