#! /bin/bash


BASEDIR=`dirname $0`
SVN_FOLDER=$BASEDIR/../../assets/ss/hsph
ESP_HOME=$BASEDIR/../ESP

FILE_FOLDER=$BASEDIR/../ESP/ss/assets/hsph

if [ $# = 1 ] 
then
  DATE=`date -d $1 +%Y%m%d` 
  YEAR=`date -d $1 +%Y` 
  FOLDER=`date -d $1 +%Y/%m` 
else
  DATE=`date -d "-1 day" +%Y%m%d`
  YEAR=`date -d "-1 day" +%Y` 
  FOLDER=`date -d "-1 day" +%Y/%m`  
fi

mkdir -p $SVN_FOLDER/$FOLDER &&
cp $FILE_FOLDER/$FOLDER/*.xls $SVN_FOLDER/$FOLDER/ 
cd $SVN_FOLDER/ &&
svn --force add $YEAR/ &&
svn ci -m "Commit made by automated script on $DATE"
