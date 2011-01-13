#!/bin/bash
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#                            Data Quality Checker
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# This utility script was developed to help analyze whether data extracted from
# Epic using a new procedure is more (or less) complete than data extractd
# using the old process.  
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Usage:
#
#     ./data-quality-check.sh test_data_folder
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# @author: Jason McVetta <jason.mcvetta@gmail.com>
# @organization: Channing Laboratory http://www.channing.harvard.edu
# @contact: http://esphealth.org
# @copyright: (c) 2010 Channing Laboratory
# @license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


folder=$1
if [ -z $folder ]; then
    echo "Must specify folder to analyze" > /dev/stderr
    exit -1
fi

echo "Analyzing data files..."

#
# Patients
#
patients_prod=`mktemp`
patients_test=`mktemp`
cat $folder/epic*.esp.* | cut -d'^' -f1 | sort | uniq > $patients_prod
cat $folder/epic*.test.* | cut -d'^' -f1 | sort | uniq > $patients_test
patients_missing=`diff $patients_prod $patients_test  | grep '^<' | wc -l`
patients_new=`diff $patients_prod $patients_test  | grep '^>' | wc -l`
rm $patients_prod
rm $patients_test


#
# Lab Result Order Numbers
#
ordernums_prod=`mktemp`
ordernums_test=`mktemp`
cat $folder/epicres.esp.* | cut -d'^' -f3 | sort | uniq > $ordernums_prod
cat $folder/epicres.test.* | cut -d'^' -f3 | sort | uniq > $ordernums_test
ordernums_missing=`diff $ordernums_prod $ordernums_test  | grep '^<' | wc -l`
ordernums_new=`diff $ordernums_prod $ordernums_test  | grep '^>' | wc -l`
rm $ordernums_prod
rm $ordernums_test


#
# Encounters
#
encounters_prod=`mktemp`
encounters_test=`mktemp`
cat $folder/epicres.esp.* | cut -d'^' -f3 | sort | uniq > $encounters_prod
cat $folder/epicres.test.* | cut -d'^' -f3 | sort | uniq > $encounters_test
encounters_missing=`diff $encounters_prod $encounters_test  | grep '^<' | wc -l`
encounters_new=`diff $encounters_prod $encounters_test  | grep '^>' | wc -l`
rm $encounters_prod
rm $encounters_test


#
# Prescriptions
#
prescriptions_prod=`mktemp`
prescriptions_test=`mktemp`
cat $folder/epicres.esp.* | cut -d'^' -f3 | sort | uniq > $prescriptions_prod
cat $folder/epicres.test.* | cut -d'^' -f3 | sort | uniq > $prescriptions_test
prescriptions_missing=`diff $prescriptions_prod $prescriptions_test  | grep '^<' | wc -l`
prescriptions_new=`diff $prescriptions_prod $prescriptions_test  | grep '^>' | wc -l`
rm $prescriptions_prod
rm $prescriptions_test



echo
echo "Patients"
echo "    Missing: $patients_missing"
echo "    New:     $patients_new"
echo
echo "Lab Result Order Numbers"
echo "    Missing: $ordernums_missing"
echo "    New:     $ordernums_new"
echo
echo "Encounters"
echo "    Missing: $encounters_missing"
echo "    New:     $encounters_new"
echo
echo "Prescriptions"
echo "    Missing: $prescriptions_missing"
echo "    New:     $prescriptions_new"
