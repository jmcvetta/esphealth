#!/bin/bash
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# @author: Rich Schaaf <rschaaf@commoninf.com>
# @organization: Commonwealth Informatics, Inc.
# @copyright: (c) 2013 Commonwealth Informatics
# @license: LGPL
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ESP_BASE_DIR=/opt/esp30
ESP_SQL_REPORTS_DIR=$ESP_BASE_DIR/share/sql_reports/Atrius
PENTAHO_DIR=/opt/data-integration
ESP_DB=esp30
ESP_DBUSER=esp30

FILE_FOLDER=/srv/esp30/data

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

# Gestational diabetes (GDM) report
gdm_folder=$FILE_FOLDER/gdm_reports/$FOLDER
mkdir -p $gdm_folder

file=$gdm_folder/gdm-report-${DATE}
$ESP_BASE_DIR/bin/esp report diabetes:gestational \
     > ${file}.csv && \
$PENTAHO_DIR/pan.sh \
 -file=$ESP_BASE_DIR/share/riskscape.gdm-transformation.ktr \
 -param:INPUT_FILE=${file}.csv \
 -param:OUTPUT_FILE=${file}.rsk
cp $ESP_BASE_DIR/share/riskscape.gdm-mapping.json $gdm_folder

# Post the RiskScape GDM report output to esphealth.org
curl -u riskscape:phiriskscape \
     -F "file=@${file}.rsk;filename=Pregnancy" \
     -F "site=ATR" \
     http://esphealth.org/riskscape/process/admin/put.py/submit_data_file


# General population report
genpop_folder=$FILE_FOLDER/gen_pop_reports/$FOLDER
mkdir -p $genpop_folder

file=$genpop_folder/genpop-report-${DATE}
psql -d $ESP_DB -U $ESP_DBUSER -A -F"," \
     < $ESP_SQL_REPORTS_DIR/general-population-report.pg.sql \
     > ${file}.csv && \
$PENTAHO_DIR/pan.sh \
 -file=$ESP_SQL_REPORTS_DIR/riskscape.genepop-transformation.ktr \
 -param:INPUT_FILE=${file}.csv \
 -param:OUTPUT_FILE=${file}.rsk
cp $ESP_SQL_REPORTS_DIR/riskscape.genpop-mapping.json $genpop_folder

# Post the RiskScape general population report output to esphealth.org
curl -u riskscape:phiriskscape \
     -F "file=@${file}.rsk;filename=General_Population" \
     -F "site=ATR" \
     http://esphealth.org/riskscape/process/admin/put.py/submit_data_file

