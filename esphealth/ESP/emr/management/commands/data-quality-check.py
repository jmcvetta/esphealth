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

    $ python data-quality-check.py [options] reference_folder test_folder

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@contact: http://esphealth.org
@copyright: (c) 2010-2011 Channing Laboratory
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''


import sys
import os
import optparse
import re
import csv
import datetime
from django.core.management.base import BaseCommand
from ESP.utils import log

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
    
    def read(self, filepath, mode):
        '''
        Reads a data file and adds it to the reference or test comparison set.
        
        @param filepath: Full path to a data file
        @type  filepath: String
        @param mode: Is this a reference file or a test file?
        @type  mode: String (from choices 'reference', 'test')
        '''
        assert mode.lower() in ('reference', 'test') # Sanity check
        mode = mode.lower()
        filename = os.path.basename(filepath)
        # Check whether we are interested in this file, and if not return
        if not self.filename_regex.match(filename):
            return
        # This file is interesting.  Let's decide if it is a reference file or 
        # a test file, and set up the counter accordingly.
        if mode == 'reference':
            counter_set= self.ref_set
        elif mode == 'test':
            counter_set = self.test_set
        else:
            raise RuntimeError('WTF?!  Something is badly awry here...')
        # Read the file
        reader = csv.reader(open(filepath, 'rb'), delimiter='^')
        for line in reader:
            field = line[self.field_index].strip()
            counter_set.update([field])
    
    @property
    def missing_set(self):
        return self.ref_set - self.test_set
    
    @property
    def new_set(self):
        return self.test_set - self.ref_set
    
    @property
    def all_set(self):
        return self.ref_set | self.test_set
    
            

class Command(BaseCommand):
    args = 'reference_folder test_folder'
    help = 'Compare data quality of test files againt reference files'
    
    def handle(self, *args, **options):
        #usage = 'usage: %prog [options] folder'
        #parser = optparse.OptionParser(usage=usage)
        parser = optparse.OptionParser()
        parser.add_option("-d", "--detail", dest="detail", action='store_true', default=False,
                      help="Output detailed information")
        parser.add_option("--missing", dest="missing", action='store', 
                      help="File containing known-missing records")
        (options, args) = parser.parse_args()
        #
        # Sanity checks
        #
        try:
            assert len(args) == 3
            ref_folder = args[1]
            test_folder = args[2]
            assert os.path.isdir(ref_folder)
            assert os.path.isdir(test_folder)
        except:
            sys.stderr.write('Must specify valid reference and test folders to analyze.\n')
            sys.exit(-1)
        #
        # Set up counters
        #
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
        record_counters = [
            patient_counter,
            encounter_counter,
            lab_result_order_counter,
            prescription_counter,
            ]
        #
        # Read reference files
        #
        ref_filenames = os.listdir(ref_folder)
        ref_file_count = len(ref_filenames)
        ref_counter = 0
        for filename in os.listdir(ref_folder):
            ref_counter += 1
            log.info('Reading reference file %20s / %s:  %s' % (ref_counter, ref_file_count, filename))
            filepath = os.path.join(ref_folder, filename)
            for counter in record_counters:
                counter.read(filepath, 'reference')
        #
        # Read test files
        #
        test_filenames = os.listdir(test_folder)
        test_file_count = len(test_filenames)
        test_counter = 0
        for filename in os.listdir(test_folder):
            test_counter += 1
            log.info('Reading reference file %20s / %s:  %s' % (test_counter, test_file_count, filename))
            filepath = os.path.join(test_folder, filename)
            for counter in record_counters:
                counter.read(filepath, 'test')
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