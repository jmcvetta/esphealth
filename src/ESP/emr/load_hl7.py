#!/usr/bin/env python
'''
                                  ESP Health
                              ETL Infrastructure
                            HL7 to Database Loader


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''


#
# Default folder from which to read HL7 messages
#
INCOMING_DIR = '/home/ESP/NORTH_ADAMS/incomingHL7'

#
# Used to populate the 'updated_by' field on db records
#
UPDATED_BY = 'load_hl7.py'


import os
import datetime
import random
import pprint
import re
import sys
import optparse
import tempfile
import operator

from hl7 import hl7

from ESP.conf.models import Icd9
from ESP.emr.models import Provider
from ESP.emr.models import Patient
from ESP.emr.models import Encounter
from ESP.emr.models import LabOrder
from ESP.emr.models import LabResult
from ESP.emr.models import Prescription
from ESP.emr.models import Immunization
from ESP.emr.models import Hl7Message
from ESP.emr.choices import HL7_MESSAGE_LOAD_STATUS
from ESP.utils.utils import log



HL7_FOLDER = '/home/rejmv/work/NORTH_ADAMS/incomingHL7/'
#TESTMSG = '/home/rejmv/work/NORTH_ADAMS/incomingHL7/NADAMS_e76e1d24-0e4c-11de-a002-fb07a536f7cf_2009-3-11 10.57.13.hl7'
#TESTMSG = '/home/rejmv/work/NORTH_ADAMS/incomingHL7/NADAMS_9da4c7c0-ca96-11dd-b49a-ea1688cfc655_2008-12-15 5.53.32.hl7'
#TESTMSG = '/home/rejmv/work/NORTH_ADAMS/incomingHL7/38389d3c-39e2-11de-94b5-c0e83ccf8498_2009-5-5 22.4.23.hl7'
#TESTMSG = '/home/rejmv/work/NORTH_ADAMS/incomingHL7/f51d44d4-39c5-11de-94b5-c0e83ccf8498_2009-5-5 18.42.5.hl7'
#TESTMSG = '/home/rejmv/work/NORTH_ADAMS/incomingHL7/9465302c-39ca-11de-94b5-c0e83ccf8498_2009-5-5 19.15.10.hl7'
#TESTMSG = '/home/rejmv/work/NORTH_ADAMS/incomingHL7/NADAMS_c0643514-10f8-11de-a002-fb07a536f7cf_2009-3-14 20.32.23.hl7'
#TESTMSG = '/home/rejmv/work/NORTH_ADAMS/incomingHL7/d5b4c164-39f4-11de-94b5-c0e83ccf8498_2009-5-6 0.17.38.hl7'
TESTMSG = '/home/rejmv/work/NORTH_ADAMS/incomingHL7/NADAMS_9014a784-0080-11de-a002-fb07a536f7cf_2009-2-21 20.31.44.hl7'





class Hl7LoaderException(BaseException):
    '''
    Base exception for problems encountered while loading HL7 messages
    into the database.
    '''
    pass

class CannotParseHl7(Hl7LoaderException):
    '''
    This HL7 message differs from the format we were expecting, and we
    therefore cannot parse it.
    '''
    pass

class NoMSH(Hl7LoaderException):
    '''
    HL7 message does not contain an MSH segment
    '''
    pass

class NoPID(Hl7LoaderException):
    '''
    HL7 message does not contain an MSH segment
    '''
    pass

class NoPV1(Hl7LoaderException):
    '''
    HL7 message does not contain an MSH segment
    '''
    pass


def record_file_status(filename, status, msg=None):
    '''
    Logs the status of a given filename to the database
    @type filename: String
    @type   status: String
    '''
    assert status in [item[0] for item in HL7_MESSAGE_LOAD_STATUS] # Sanity check
    try:
        h = Hl7Message.objects.get(filename=filename)
    except Hl7Message.DoesNotExist:
        h = Hl7Message(filename=filename)
    h.timestamp = datetime.datetime.now()
    h.status = status
    if msg:
        h.message = msg
    h.save()



class Hl7MessageLoader(object):
    def __init__(self, msg_string):
        #
        # MSH
        #
        self.msg_string = msg_string
        self.message = hl7.parse(msg_string) # parsed msg
        msh_seg = hl7.segment('MSH', self.message)
        if not msh_seg:
            raise NoMSH('No MSH segment found')
        self.msg_type = msh_seg[8] # Is it good to store this as a list?
        log.debug('Message type: %s' % self.msg_type)
        self.message_date = self.datetime_from_string(msh_seg[6][0])
        log.debug('Message date: %s' % self.message_date)
        #
        # PID
        #
        pid_seg = hl7.segment('PID', self.message)
        if not pid_seg:
            raise NoPID('No PID segment found')
        if not len(pid_seg) >= 9:
            raise CannotParseHl7('PID segment has only %s fields' % len(pid_seg))
        patient_id_num = pid_seg[3][0]
        log.debug('Patient ID #: %s' % patient_id_num)
        patient = Patient.objects.get_or_create(patient_id_num=patient_id_num)[0]
        patient.updated_by = UPDATED_BY
        patient.mrn = patient_id_num # Patient ID # is same as their Medical Record Number
        dob = pid_seg[8]
        if len(dob) == 6: # Partially deidentified -- only year & month
            dob = datetime.date(year=dob[0:4], month=dob[4:6], day=01) # Default to 1st of month
        else:
            dob = None
        patient.dob = dob
        patient.gender = pid_seg[8]
        patient.save()
        self.patient = patient
        #
        # PV1
        #
        pv1_seg = hl7.segment('PV1', self.message)
        if not pv1_seg:
            raise NoPV1('No PV1 segment found')
        self.visit_date = self.datetime_from_string(pv1_seg[-1][0]) # Will date always be last??
        provider_id_num = pv1_seg[7][0] # National Provider ID #
        if not provider_id_num:
            provider_id_num = '[Unknown]'
        log.debug('Provider ID (NPI) #: %s' % provider_id_num)
        prov_last = pv1_seg[7][1]
        prov_first = pv1_seg[7][2]
        provider = Provider.objects.get_or_create(provider_id_num=provider_id_num)[0]
        if prov_first:
            provider.first_name = prov_first
        if prov_last:
            provider.last_name = prov_last
        provider.updated_by = UPDATED_BY
        provider.save()
        self.provider = provider
        #
        # Call methods for other segment types
        #
        self.seg_types = set( [seg[0][0] for seg in self.message] ) - set( ['MSH', 'PID', 'PV1'] ) # What kind of segments do we have?
        log.debug('Payload segments: %s' % self.seg_types)
        mt = self.msg_type[0]
        if mt in ['ORU']:
            self.make_lab()
        if mt in ['ADT']:
            self.make_encounter()
        if mt in ['OMP']:
            self.make_prescription()
            self.make_allergy()
        if mt in ['VXU']:
            self.make_vaccination()
    
    def make_prescription(self):
        for rxo in hl7.segments('RXO', self.message):
            pre = Prescription(patient=self.patient, provider=self.provider, updated_by=UPDATED_BY)
            pre.date = self.visit_date
            log.debug('NEW PRESCRIPTION')
            pre.name = rxo[1][1]
            log.debug('Name: %s' % pre.name)
            pre.directions = rxo[2][0]
            log.debug('Directions: %s' % pre.directions)
            pre.quantity = rxo[3][0]
            log.debug('Quantity: %s' % pre.quantity)
            pre.dose = rxo[4][0]
            log.debug('Dose: %s' % pre.dose)
            pre.frequency = rxo[5][0]
            log.debug('Frequency: %s' % pre.frequency)
            pre.route = rxo[12][0]
            log.debug('Route: %s' % pre.route)
            pre.save()
    
    def make_vaccination(self):
        for rxa in hl7.segments('RXA', self.message):
            imm = Immunization(patient=self.patient, provider=self.provider, updated_by=UPDATED_BY)
            imm.name = rxa[5][1]
            imm.date = self.datetime_from_string(rxa[3][0])
            imm.imm_type = rxa[5][0]
            imm.lot = rxa[16][0]
            imm.save()
            log.debug('NEW IMMUNIZATION')
            log.debug('Name: %s (%s)' % (imm.name, imm.imm_type))
            log.debug('Date: %s' % imm.date)
            log.debug('Lot: %s' % imm.lot)
    
    def make_allergy(self):
        pass
    
    def make_lab(self):
        float_regex = re.compile(r'^(\d+\.?\d*)') # Copied from incomingParser -- maybe should be in util?
        for obx in hl7.segments('OBX', self.message):
            log.debug('NEW LAB RESULT')
            result = LabResult(patient=self.patient, provider=self.provider, updated_by=UPDATED_BY)
            result.date = self.datetime_from_string(obx[14][0])
            log.debug('Date: %s' % result.date)
            result.native_code = obx[3][0]
            result.native_name = obx[3][1]
            log.debug('Native code (name): %s (%s)' % (result.native_code, result.native_name))
            result.result_string = obx[5][0]
            match = float_regex.match(result.result_string)
            if match:
                res_float = float(match.group(1))
            else:
                res_float = None
            result.result_float = res_float
            result.ref_unit = obx[6][0]
            log.debug('Lab result: %s %s (float: %s)' % (result.result_string, result.ref_unit, result.result_float))
            ref_range = obx[7][0].split('-')
            if len(ref_range) == 2: # There must be both high and low
                low_match = float_regex.match(ref_range[0])
                if low_match:
                    ref_low = low_match.group(1)
                    result.ref_low_string = ref_low
                    result.ref_low_float = float(ref_low)
                high_match = float_regex.match(ref_range[1])
                if high_match:
                    ref_high = high_match.group(1)
                    result.ref_high_string = ref_high
                    result.ref_high_float = float(ref_high)
                    log.debug('Reference range: %s - %s' % (result.ref_low_float, result.ref_high_float))
            result.abnormal_flag = obx[8][0]
            if result.abnormal_flag:
                log.debug('Abnormal flag: %s' % result.abnormal_flag)
            result.status = obx[11][0]
            log.debug('Status: %s' % result.status)
            result.save()
            
    def make_encounter(self):
        encounter = Encounter(patient=self.patient, provider=self.provider, 
            updated_by = UPDATED_BY)
        encounter.save()
        log.debug('Created new encounter: %s' % encounter)
        for dg1 in hl7.segments('DG1', self.message):
            # Discard segments where diagnosis is not coded in ICD9:
            if dg1[3][2] != 'I9':
                continue
            icd9_str = dg1[3][0]
            try:
                icd9_obj = Icd9.objects.get(code=icd9_str)
            except Icd9.DoesNotExist, e:
                log.warning('Unknown ICD9 code: "%s".  Adding new code to table.' % icd9_str)
                name = '[Generated by load_hl7.py - may not be valid.]'
                icd9_obj = Icd9(code=icd9_str, name=name)
                icd9_obj.save()
            encounter.date = self.datetime_from_string(dg1[5][0])
            # We are going to presume (correctly?  falsely?) that the dates on all 
            # DG1 segments in the same message will be the same.  
            encounter.icd9_codes.add(icd9_obj)
            log.debug('Added ICD9 "%s" to %s' % (icd9_obj, encounter))
        #
        # In ADT AO1 type messages, OBX segments contain vital sign encounter 
        # data.  In ORU type messages, OBX segments contain lab results.
        #
        if self.msg_type == ['ADT', 'A01']:
            for obx in hl7.segments('OBX', self.message):
                encounter.date = self.datetime_from_string(obx[-1][0])
                desc = obx[2][0].lower().strip() # lower() to match lowercase search strings below
                value = obx[3][0].strip()
                units = obx[4][0].lower().strip()
                try:
                    value = float(value)
                except ValueError:
                    log.debug('Value "%s" for %s' % (value, desc))
                    continue
                #
                # Temp
                #
                if desc.find('temp') >= 0: # find() returns -1 if substring not found
                    if units == 'f':
                        value = (value - 32.0) * (5.0/9.0)
                    elif units != 'c':
                        log.warning('Could not convert temp units ("%s") to Celsius.' % units)
                        continue
                    encounter.temperature = value
                    log.debug('Temperature: %s C' % value)
                #
                # Systolic Blood Pressure
                #
                if desc.find('systolic') >= 0: 
                    if not units == 'mm hg':
                        log.warning('Could not convert systolic bp units ("%s") to mm Hg.' % units)
                        continue
                    encounter.bp_systolic = value
                    log.debug('Systolic blood pressure: %s mm Hg' % value)
                #
                # Diastolic Blood Pressure
                #
                if desc.find('diastolic') >= 0: 
                    if not units == 'mm hg':
                        log.warning('Could not convert diastolic bp units ("%s") to mm Hg.' % units)
                        continue
                    encounter.bp_diastolic = value
                    log.debug('Diastolic blood pressure: %s mm Hg' % value)
                #
                # Height
                #
                if desc.find('height') >= 0:
                    if units in ['in', 'inches']:
                        value = value / 2.54
                    elif units not in ['cm', 'centimeters']:
                        log.warning('Could not convert height units ("%s") to centimetres.' % units)
                        continue
                    encounter.height = value
                #
                # Weight
                #
                if desc.find('weight') >= 0:
                    if units in ['lb', 'lbs', 'pounds']:
                        value = value / 2.20462262
                    elif units not in ['kg', 'kilogram', 'kilograms']:
                        log.warning('Could not convert weight units ("%s") to kilograms.' % units)
                        continue
                    encounter.weight = value
        if encounter: # Ignore if it is still None
            encounter.save() # Save just once, after all info has been added
        
    def __has_seg(self, seg_type_list):
        if (self.seg_types & set(seg_type_list)):
            return True
        else:
            return False

    def datetime_from_string(self, str):
        l = len(str)
        if l == 8:
            dateformat = '%Y%m%d'
        elif l == 14:
            dateformat = '%Y%m%d%H%M%S'
        else:
            err_msg = "Don't know how convert %s character string to datetime:\n%s" % (l, str)
            raise ValueError(err_msg)
        return datetime.datetime.strptime(str, dateformat)

    



def oldmain():
    all_files = os.listdir(HL7_FOLDER)
    filename = random.choice(all_files)
    m = open(os.path.join(HL7_FOLDER, filename)).read()
    m = open(TESTMSG).read()
    log.debug('Loading HL7 message file "%s"' % filename)
    Hl7MessageLoader(m)
    
    
    
def main():
    # Set defaults:
    input_folder = INCOMING_DIR
    parser = optparse.OptionParser()
    parser.add_option('--new', action='store_true', dest='new', 
        help='Process only new HL7 messages')
    parser.add_option('--retry', action='store_true', dest='retry',
        help='Process only HL7 messages that have previously failed to process')
    parser.add_option('--all', action='store_true', dest='all', 
        help='Process new and retry HL7 messages.')
    parser.add_option('--no-load', action='store_false', dest='load', default=True,
        help='Do not load HL7 message data into ESP')
    parser.add_option('--mail', action='store_true', dest='mail', default=False,
        help='Send email notifications' )
    parser.add_option('--file', action='store', dest='single_file', metavar='FILEPATH', 
        help='Load an individual message file')
    parser.add_option('--input', action='store', dest='input_folder', default=INCOMING_DIR,
        metavar='FOLDER', help='Folder from which to read incoming HL7 messages')
    parser.add_option('--dry-run', action='store_true', dest='dry_run', default=False,
        help='Show which files would be loaded, but do not actually load them')
    options, args = parser.parse_args()
    log.debug('options: %s' % options)
    #
    if options.input_folder:
        assert os.path.isdir(options.input_folder) # Sanity check -- is really a folder?
        input_folder = options.input_folder
    all_files = set( os.listdir(input_folder) )
    log.debug('combined HL7 file count: %s' % len(all_files))
    if options.single_file:
        log.debug('Loading single file from command line:\n\t%s' % options.single_file)
        # Include only the one file specified on command line
        input_folder, basename = os.path.split(options.single_file)
        if Hl7Message.objects.filter(filename=basename, status='l'):
            sys.stderr.write('\nThis file has already been loaded into the database.  Aborting.\n\n')
            sys.exit()
        input_files = [basename]
    elif options.all or (options.new and options.retry): # Implies both 'new' and 'retry'
        # Include all files that have not yet been loaded
        input_files = all_files - set( Hl7Message.objects.filter(status='l').values_list('filename', flat=True) )
    elif options.retry:
        # Include only those files that have previously failed 
        input_files = all_files & set( Hl7Message.objects.filter(status='f').values_list('filename', flat=True) )
    elif options.new:
        # Include all files that have not loaded or failed
        input_files = all_files - set( Hl7Message.objects.filter(status__in=('l', 'f')).values_list('filename', flat=True) )
    else:
        sys.stderr.write('You must select either --new, --retry, or --all\n')
        parser.print_help()
        sys.exit()
    log.debug('input file count: %s' % len(input_files))
    files_by_month = {}
    date_regex = re.compile(r'(\d{4})-(\d{1,2})-(\d{1,2})')
    dated_input = [] # [(date, filename), (date, filename), ...]
    for f in input_files:
        m = date_regex.search(f)
        if not m:
            record_file_status(f, 's', msg='Could not parse file date stamp')
            continue
        year = int(m.group(1))
        month = int(m.group(2))
        day = int(m.group(3))
        date = datetime.date(year, month, day)
        dated_input += [(date, f),]
    dated_input.sort() # Sort by date
    input_files = [item[1] for item in dated_input]
    if options.dry_run:
        # Print file list then quit
        for f in input_files:
            print f
        sys.exit()
    log.info('Input folder: "%s"' % input_folder)
    loaded_counter = 0
    failure_counter = 0
    for filename in input_files:
        record_file_status(filename, 'a') # Status 'attempted'
        log.info('Loading HL7 message: "%s"' % filename)
        filepath = os.path.join(input_folder, filename)
        msg = open(filepath).read()
        try:
            Hl7MessageLoader(msg)
        # 
        # For debug we catch Hl7LoaderException, to draw attention to other 
        # kinds of exception; but in production all exceptions should be 
        # caught and logged, rather than allowing the program to crash.
        #
        #except BaseException, e:
        except Hl7LoaderException, e:
            failure_counter += 1
            log_msg = str(e)
            log.error(log_msg)
            record_file_status(filename, 'f', log_msg) # Status 'failure'
        else:
            record_file_status(filename, 'l') # Status 'loaded'
            loaded_counter += 1
    log.info('Attempted: %s' % len(input_files) )
    log.info('Loaded:    %s' % loaded_counter)
    log.info('Failed:    %s' % failure_counter)
    
            


if __name__ == '__main__':
    main()