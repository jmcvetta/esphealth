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
import re
import csv
import datetime
from optparse import make_option
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
    
    instances = [] # Class variable
    
    def __init__(self, name, record_type, filename_regex, field_index):
        self.name = name
        self.record_type = record_type
        self.filename_regex = filename_regex
        self.field_index = field_index
        self.ref_set = set()
        self.test_set = set()
        self.instances.append(self)
    
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
            self.counter_set= self.ref_set
        elif mode == 'test':
            self.counter_set = self.test_set
        else:
            raise RuntimeError('WTF?!  Something is badly awry here...')
        # Read the file
        reader = csv.reader(open(filepath, 'rb'), delimiter='^')
        for line in reader:
            self.process_line(line)
            
    def process_line(self, line):
        '''
        Processes a single record.  This implementation simply counts unique 
        identifiers; but it could be subclassed to perform more complex 
        analysis.
        
        @param line: A single line of data (as interated by csv.DictReader)
        @type  line: Dictionary
        '''
        field = line[self.field_index].strip()
        self.counter_set.update([field])
        return counter_set
    
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
    option_list = BaseCommand.option_list + (
        make_option("-d", "--detail", dest="detail", action='store_true', default=False,
                      help="Output detailed information"),
        make_option("--missing", dest="missing", action='store', type='string', 
                      metavar='FILE', help="File containing known-missing records"),
        )
    
    def handle(self, *args, **options):
        #
        # Sanity checks
        #
        try:
            assert len(args) == 2
            ref_folder = args[0]
            test_folder = args[1]
            assert os.path.isdir(ref_folder)
            assert os.path.isdir(test_folder)
        except:
            sys.stderr.write('Must specify valid reference and test folders to analyze.\n')
            sys.exit(-1)
        missing_rec_dict = {}
        if options['missing']:
            assert os.path.exists(options['missing'])
            reader = csv.DictReader(
                open(options['missing'], 'rb'), 
                fieldnames = ['record_type', 'identifider']
                )
            for line in reader:
                rec_type = line['record_type'].lower().strip()
                rec_set = missing_rec_dict.get(rec_type, set())
                rec_set.add(line['identifider'].strip())
                missing_rec_dict[rec_type] = rec_set
            print missing_rec_dict
            counter = 0
            for s in missing_rec_dict:
                counter += len(s)
            log.info('Loaded %s missing records' % counter)
        #
        # Set up counters
        #
        patient_counter = RecordCounter(
            name = 'Patient ID Numbers',
            record_type = 'Patient',
            filename_regex = re.compile('^epic.*'),
            field_index = 0, # patient_id is first field in every filetype
            )
        encounter_counter = RecordCounter(
            name = 'Encounters ID Numbers',
            record_type = 'Encounter',
            filename_regex = re.compile('^epicvis.*'),
            field_index = 2,
            )
        lab_result_order_counter = RecordCounter(
            name = 'Lab Result Order Numbers',
            record_type = 'LabResult',
            filename_regex = re.compile('^epicres.*'),
            field_index = 2,
            )
        lab_order_counter = RecordCounter(
            name = 'Lab Order Numbers',
            record_type = 'LabOrder',
            filename_regex = re.compile('^epicord.*'),
            field_index = 2,
            )
        prescription_counter = RecordCounter(
            name = 'Prescription Order Numbers',
            record_type = 'Prescription',
            filename_regex = re.compile('^epicmed.*'),
            field_index = 2,
            )
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
            for counter in RecordCounter.instances:
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
            for counter in RecordCounter.instances:
                counter.read(filepath, 'test')
        self.summarize(options, missing_rec_dict)
        if options['detail']:
            self.details(options, missing_rec_dict)
    
    def summarize(self, options, missing_rec_dict):
        '''
        Summarize data
        '''
        print
        print datetime.datetime.now()
        print
        print '~' * 80
        print
        print 'Data Quality Summary Analysis'
        print
        print '~' * 80
        for counter in RecordCounter.instances:
            print
            print '%s:' % counter.name
            print '    All:     %s' % len(counter.all_set)
            print '    Missing: %s' % len(counter.missing_set)
            print '    New:     %s' % len(counter.new_set)
            if options['missing']:
                known_missing_set = missing_rec_dict.get(counter.record_type.lower(), set())
                still_missing_count = len(known_missing_set - counter.test_set)
                print 'Specific records missing from referecnce: %s' % len(known_missing_set)
                print 'Specific records still missing from test: %s' % still_missing_count
    
    def details(self, options, missing_rec_dict):
        #
        # Print detailed info if specified
        #
        print
        print
        print
        print '~' * 80
        print
        print 'Missing Record Detail'
        print
        print '~' * 80
        for counter in RecordCounter.instances:
            print
            print '=' * 80
            print 
            print 'Missing %s:' % counter.name
            print
            for record in counter.missing_set:
                print record
            print


class EncounterCounter:
    '''
    Adds support for checking for the presence of specific patient/date/ICD9 combinations 
    when counting Encounter records.
    '''
    
    def __init__(self, name, record_type, filename_regex, field_index, mis_enc_filepath):
        '''
        @param mis_enc_filepath: Path to file containing missing encounter info
        @type mis_enc_filepath:  String
        '''
        assert os.path.exists(mis_enc_filepath) # Sanity check