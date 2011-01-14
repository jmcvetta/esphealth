#!/usr/bin/env python
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
#     python data-quality-check.py test_data_folder
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


import sys
import os
import optparse
import re
import csv

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Configuration
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
REF_FILE_REGEX = re.compile(r'^epic\w{3}.esp.*')
TEST_FILE_REGEX = re.compile(r'^epic\w{3}.test.*')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Logic
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class RecordCounter:
    def __init__(self, name, filename_regex, field_index):
        self.name = name
        self.filename_regex = filename_regex
        self.field_index = field_index
        self.ref_set = set()
        self.test_set = set()
    
    def read(self, folder, filename):
        # Check whether we are interested in this file, and if not return
        if not self.filename_regex.match(filename):
            return
        # This file is interesting.  Let's decide if it is a reference file or 
        # a test file, and set up the counter accordingly.
        if REF_FILE_REGEX.match(filename):
            counter_set= self.ref_set
            print >> sys.stderr, 'Reading reference %s file: %s' % (self.name, filename)
        elif TEST_FILE_REGEX.match(filename):
            counter_set = self.test_set
            print >> sys.stderr, 'Reading test %s file: %s' % (self.name, filename)
        else:
            sys.stderr.write('Could not understand filename: "%s"\n' % filename)
            return
        # Read the file
        path = os.path.join(folder, filename)
        reader = csv.reader(open(path, 'rb'), delimiter='^')
        for line in reader:
            field = line[self.field_index].strip()
            counter_set.update([field])
    
    def __get_missing_set(self):
        return self.ref_set - self.test_set
    missing_set = property(__get_missing_set)
    
    def __get_new_set(self):
        return self.test_set - self.ref_set
    new_set = property(__get_new_set)
    
    def __get_all_set(self):
        return self.ref_set | self.test_set
    all_set = property(__get_all_set)
    
            

patient_counter = RecordCounter(
    name = 'patients',
    filename_regex = re.compile('^epic.*'),
    field_index = 0, # patient_id is first field in every filetype
    )

encounter_counter = RecordCounter(
    name = 'encounters',
    filename_regex = re.compile('^epicvis.*'),
    field_index = 2,
    )

lab_result_order_counter = RecordCounter(
    name = 'lab result order numbers',
    filename_regex = re.compile('^epicres.*'),
    field_index = 2,
    )
        
prescription_counter = RecordCounter(
    name = 'prescriptions',
    filename_regex = re.compile('^epicmed.*'),
    field_index = 2,
    )


def main():
    parser = optparse.OptionParser()
    parser.add_option("-d", "--detail", dest="detail", action='store_true', default=False,
                  help="Output detailed information")
    (options, args) = parser.parse_args()
    #
    # Sanity checks
    #
    try:
        assert len(args) == 1
        folder = args[0]
        assert os.path.isdir(folder)
    except:
        sys.stderr.write('Must specify folder to analyze.\n')
        sys.exit(-1)
    record_counters = [
        patient_counter,
        encounter_counter,
        lab_result_order_counter,
        prescription_counter,
        ]
    #
    # Read files
    #
    for filename in os.listdir(folder):
        for counter in record_counters:
            counter.read(folder, filename)
    #
    # Summarize data
    #
    print
    print '~' * 80
    print
    print 'Data Quality Summary Analysis'
    print
    print '~' * 80
    for counter in record_counters:
        print
        print '%s:' % counter.name.capitalize()
        print '    All:     %s' % len(counter.all_set)
        print '    Missing: %s' % len(counter.missing_set)
        print '    New:     %s' % len(counter.new_set)
    #
    # Print detailed info if specified
    #
    if not options.detail:
        return # We are done
    print '~' * 80
    print
    print 'Missing Record Detail'
    print
    print '~' * 80
    for counter in record_counters:
        print
        print '=' * 80
        print 
        print 'Missing %s records:' % counter.name
        for record in counter.missing_set:
            print record
        

    
if __name__ == '__main__':
    main()

'''
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
patients_all=`cat $patients_prod $patients_test | sort| uniq | wc -l`
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
ordernums_all=`cat $ordernums_prod $ordernums_test | sort| uniq | wc -l`
ordernums_missing=`diff $ordernums_prod $ordernums_test  | grep '^<' | wc -l`
ordernums_new=`diff $ordernums_prod $ordernums_test  | grep '^>' | wc -l`
rm $ordernums_prod
rm $ordernums_test


#
# Encounters
#
encounters_prod=`mktemp`
encounters_test=`mktemp`
cat $folder/epicvis.esp.* | cut -d'^' -f3 | sort | uniq > $encounters_prod
cat $folder/epicvis.test.* | cut -d'^' -f3 | sort | uniq > $encounters_test
encounters_all=`cat $encounters_prod $encounters_test | sort| uniq | wc -l`
encounters_missing=`diff $encounters_prod $encounters_test  | grep '^<' | wc -l`
encounters_new=`diff $encounters_prod $encounters_test  | grep '^>' | wc -l`
rm $encounters_prod
rm $encounters_test


#
# Prescriptions
#
prescriptions_prod=`mktemp`
prescriptions_test=`mktemp`
cat $folder/epicmed.esp.* | cut -d'^' -f3 | sort | uniq > $prescriptions_prod
cat $folder/epicmed.test.* | cut -d'^' -f3 | sort | uniq > $prescriptions_test
prescriptions_all=`cat $prescriptions_prod $prescriptions_test | sort| uniq | wc -l`
prescriptions_missing=`diff $prescriptions_prod $prescriptions_test  | grep '^<' | wc -l`
prescriptions_new=`diff $prescriptions_prod $prescriptions_test  | grep '^>' | wc -l`
rm $prescriptions_prod
rm $prescriptions_test



echo
echo "Patients"
echo "    All:     $patients_all"
echo "    Missing: $patients_missing"
echo "    New:     $patients_new"
echo
echo "Lab Result Order Numbers"
echo "    All:     $ordernums_all"
echo "    Missing: $ordernums_missing"
echo "    New:     $ordernums_new"
echo
echo "Encounters"
echo "    All:     $encounters_all"
echo "    Missing: $encounters_missing"
echo "    New:     $encounters_new"
echo
echo "Prescriptions"
echo "    All:     $prescriptions_all"
echo "    Missing: $prescriptions_missing"
echo "    New:     $prescriptions_new"
'''