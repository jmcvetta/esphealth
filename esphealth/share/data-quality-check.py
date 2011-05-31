#!/usr/bin/env python
'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

                             Data Quality Checker

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This utility script was developed to help analyze whether data extracted from
Epic using a new procedure is more (or less) complete than data extractd using
the old process.  

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Usage:

    python data-quality-check.py test_data_folder

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@contact: http://esphealth.org
@copyright: (c) 2010 Channing Laboratory
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''


import sys
import os
import optparse
import re
import csv
import datetime

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
    name = 'Patient ID Numbers',
    filename_regex = re.compile('^epic.*'),
    field_index = 0, # patient_id is first field in every filetype
    )

encounter_counter = RecordCounter(
    name = 'Encounters ID Numbers',
    filename_regex = re.compile('^epicvis.*'),
    field_index = 2,
    )

lab_result_order_counter = RecordCounter(
    name = 'Lab Result Order Numbers',
    filename_regex = re.compile('^epicres.*'),
    field_index = 2,
    )
        
prescription_counter = RecordCounter(
    name = 'Prescription Order Numbers',
    filename_regex = re.compile('^epicmed.*'),
    field_index = 2,
    )


def main():
    usage = 'usage: %prog [options] folder'
    parser = optparse.OptionParser(usage=usage)
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
    print datetime.datetime.now()
    print
    print '~' * 80
    print
    print 'Data Quality Summary Analysis'
    print
    print '~' * 80
    for counter in record_counters:
        print
        print '%s:' % counter.name
        print '    All:     %s' % len(counter.all_set)
        print '    Missing: %s' % len(counter.missing_set)
        print '    New:     %s' % len(counter.new_set)
    #
    # Print detailed info if specified
    #
    if not options.detail:
        return # We are done
    print
    print
    print
    print '~' * 80
    print
    print 'Missing Record Detail'
    print
    print '~' * 80
    for counter in record_counters:
        print
        print '=' * 80
        print 
        print 'Missing %s:' % counter.name
        print
        for record in counter.missing_set:
            print record
        print
        

    
if __name__ == '__main__':
    main()
