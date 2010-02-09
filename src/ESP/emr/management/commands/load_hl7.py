#!/usr/bin/env python
'''
                                  ESP Health
                            EMR ETL Infrastructure
                              HL7 Message Loader


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory - http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#
# TODO:  This script must be refactored to work as a manage.py command.
#
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!



import os
import datetime
import random
import pprint
import re
import sys
import optparse
import tempfile
import operator
import shutil
import socket

from optparse import make_option
from optparse import Values

from django.db import transaction

from hl7 import hl7

from ESP.settings import DEBUG
from ESP.settings import TOPDIR
from ESP.settings import DATA_DIR
from ESP.conf.models import NativeVaccine, NativeManufacturer
from ESP.static.models import Icd9
from ESP.emr.management.commands.common import LoaderCommand
from ESP.emr.models import Provider
from ESP.emr.models import Patient
from ESP.emr.models import Encounter
from ESP.emr.models import LabResult
from ESP.emr.models import Prescription
from ESP.emr.models import Immunization
from ESP.emr.models import Provenance
from ESP.emr.choices import LOAD_STATUS
from ESP.utils.utils import log
from ESP.utils.utils import str_from_date, date_from_str

#
# Populate tables in old schema (Demog, Lx, Rx, etc)?
#




#
# Default folder from which to read HL7 messages
#
HL7_DIR = os.path.join(DATA_DIR, 'hl7')
INCOMING_DIR = os.path.join(HL7_DIR, 'incoming')
ATTEMPTED_DIR = os.path.join(HL7_DIR, 'attempted')
PROCESSED_DIR = os.path.join(HL7_DIR, 'processed')
FAILED_DIR = os.path.join(HL7_DIR, 'failed')
SKIPPED_DIR = os.path.join(HL7_DIR, 'skipped')


#
# Session info for provenance
#
TIMESTAMP = datetime.datetime.now()
HOSTNAME = socket.gethostname()


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
    HL7 message does not contain an PID segment
    '''
    pass

class NoPV1(Hl7LoaderException):
    '''
    HL7 message does not contain an PV1 segment
    '''
    pass


class Hl7MessageLoader(object):
    
    
    def __init__(self, filepath, options):
        self.options = options
        self.filepath = filepath
        self.basename = os.path.basename(filepath)
        
    float_catcher = re.compile(r'(\d+\.?\d*)') 
    
    def float_or_none(self, string):
        m = self.float_catcher.match(string)
        if m and m.groups():
            result = float(m.groups()[0])
        else:
            result = None
        if result == float('infinity'): # Rare edge case, but it does happen
            result = None
        return result
    
    def date_or_none(self, string):
        try:
            return date_from_str(string)
        except ValueError:
            return None
    
    @transaction.commit_on_success
    def load(self):
        '''
        Loads the HL7 message into the database, with provenance & error 
        control.  Returns either "loaded" or "failure".
        '''
        log.info('Loading HL7 message: "%s"' % self.basename)
        #
        # Provenance
        #
        prov = Provenance(timestamp=TIMESTAMP, 
            source=self.basename, 
            hostname=HOSTNAME,
            )
        prov.status = 'attempted'
        self.provenance = prov
        self.provenance.save()
        log.debug(self.provenance)
        try:
            self.__parse() # If this runs without throwing an exception, load is successful
            status = 'loaded'
            comment = None
        except KeyboardInterrupt, e:
            raise e
        except BaseException as e:
            log.error('Caught Exception:')
            log.error('  File: %s' % self.basename)
            log.error('  Exception Type: %s' % type(e))
            log.error('  Exception Message: %s' % e)
            status = 'failure'
            comment = str(e)
        self.provenance.status = status
        self.provenance.comment = comment
        self.provenance.save()
        log.debug('Provenance updated to status "%s"' % self.provenance.status)
        return status
        
    def __parse(self):
        '''
        Parses an HL7 message and saves its data as model objects.  Always 
        called by load() -- should NOT be called directly.
        '''
        #
        # Read File
        #
        f = open(self.filepath)
        self.message = hl7.parse(f.read()) # parsed msg
        f.close()
        #
        # MSH
        #
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
        if not len(pid_seg) >= 30:
            raise CannotParseHl7('PID segment has %s fields, should have at least 30.' % len(pid_seg))
        patient_id_num = pid_seg[3][0]
        patient, is_new_patient = Patient.objects.get_or_create(patient_id_num=patient_id_num, 
            defaults={'provenance': self.provenance})
        if len(pid_seg[5]) >= 3:
            patient.first_name  = pid_seg[5][1]
            patient.middle_name = pid_seg[5][2]
            patient.last_name = pid_seg[5][0]
        elif len(pid_seg[5]) == 2:
            patient.first_name  = pid_seg[5][1]
            patient.last_name = pid_seg[5][0]
        else:    
            log.warning('PID segment in file does not contain patient name in a format we can understand:\n\t %s' % pid_seg[5])
        date_of_death = pid_seg[29][0] or None
        if date_of_death: 
            patient.date_of_death = date_from_str(date_of_death)
        patient.date_of_birth = date_from_str(pid_seg[7][0]) 
        patient.gender = pid_seg[8][0]
        patient.mrn = patient_id_num # Patient ID # is same as their Medical Record Number
        patient.provenance = self.provenance
        patient.save()
        self.patient = patient
        if is_new_patient:
            log.debug('NEW PATIENT')
            log.debug('\t Patient ID #: %s' % patient_id_num)
            log.debug('\t Name (l, f m): "%s, %s %s"' % (patient.last_name, patient.first_name, patient.middle_name))
            log.debug('\t DoB: %s' % patient.date_of_birth)
            log.debug('\t Gender: %s' % patient.gender)
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
        if not prov_last: # Better to have NULL than a blank string
            prov_last = None
        prov_first = pv1_seg[7][2]
        if not prov_first:
            prov_first = None
        provider, is_new_provider = Provider.objects.get_or_create(provider_id_num=provider_id_num,
            defaults={'provenance': self.provenance})
        provider.first_name = prov_first
        provider.last_name = prov_last
        provider.provenance = self.provenance
        provider.save()
        self.provider = provider
        if is_new_provider:
            log.debug('NEW PROVIDER')
            log.debug('Provider ID #: %s' % provider_id_num)
            log.debug('Name: %s, %s' % (prov_last, prov_first))
        #
        # Call methods for other segment types
        #
        self.seg_types = set( [seg[0][0] for seg in self.message] ) - set( ['MSH', 'PID', 'PV1'] ) # What kind of segments do we have?
        log.debug('Payload segments: %s' % self.seg_types)
        if hl7.segment('PD1', self.message):
            self.pcp()
        mt = self.msg_type[0]
        if mt in ['ORU']:
            self.make_lab()
        if mt in ['ADT']:
            self.make_encounter()
        if mt in ['OMP']:
            self.make_prescription()
            self.make_allergy()
        if mt in ['VXU']:
            self.make_immunization()

    def pcp(self):
        '''
        Create/update Primary Care Physician info.  At North Adams, we are 
        extracting this from PD1 segment.
        '''
        seg = hl7.segment('PD1', self.message)
        npi, last, first = seg[4][:3]

        provider, is_new_provider = Provider.objects.get_or_create(provider_id_num=npi,
            defaults={'provenance': self.provenance})
        provider.first_name = first
        provider.last_name = last
        provider.provenance = self.provenance
        provider.save()
        self.provider = provider
        if is_new_provider:
            log.debug('NEW PROVIDER')
            log.debug('Provider ID #: %s' % npi)
            log.debug('Name: %s, %s' % (last, first))
        self.patient.pcp = provider # Set patient's PCP
        self.patient.save()
        log.debug('Provider #%s set as PCP for patient #%s' % (provider.pk, self.patient.pk))
        
    def make_prescription(self):
        for rxo in hl7.segments('RXO', self.message):
            pre = Prescription(patient=self.patient, provider=self.provider)
            pre.date = self.visit_date
            name = rxo[1][1]
            directions = rxo[2][0]
            quantity = rxo[3][0]
            dose = rxo[4][0]
            frequency = rxo[5][0]
            route = rxo[12][0]
            pre.name = name
            pre.directions = directions if directions else None
            pre.quantity = quantity if quantity else None
            pre.quantity_float = self.float_or_none(quantity)
            pre.dose = dose if dose else None
            pre.frequency = frequency if frequency else None
            pre.route = route if route else None
            pre.provenance = self.provenance
            pre.save()
            log.debug('NEW PRESCRIPTION')
            log.debug('\t Name: %s' % pre.name)
            log.debug('\t Directions: %s' % pre.directions)
            log.debug('\t Quantity: %s' % pre.quantity)
            log.debug('\t Dose: %s' % pre.dose)
            log.debug('\t Frequency: %s' % pre.frequency)
            log.debug('\t Route: %s' % pre.route)
    
    def make_immunization(self):
        for rxa in hl7.segments('RXA', self.message):
            name = rxa[5][1]
            imm_date = self.datetime_from_string(rxa[3][0])
            imm_type = rxa[5][0]
            manufacturer = rxa[15][0]
            lot = rxa[16][0]
            imm = Immunization(patient=self.patient, provider=self.provider)
            imm.name = name if name else None
            imm.date = imm_date if imm_date else None
            imm.imm_type = imm_type if imm_type else None
            imm.manufacturer = manufacturer if manufacturer else None

            if imm_type:
                native_vaccine, new = NativeVaccine.objects.get_or_create(
                    code=imm_type, defaults={'name': name})

            if manufacturer:
                native_manuf, new = NativeManufacturer.objects.get_or_create(
                        name=manufacturer)

            

            imm.lot = lot if lot else None
            imm.provenance = self.provenance
            imm.save()
            log.debug('NEW IMMUNIZATION')
            log.debug('\t Name: %s (%s)' % (imm.name, imm.imm_type))
            log.debug('\t Date: %s' % imm.date)
            log.debug('\t Type: %s' % imm.imm_type)
            log.debug('\t Lot: %s' % imm.lot)
    
    def make_allergy(self):
        pass
    
    def make_lab(self):
        float_regex = re.compile(r'^(\d+\.?\d*)') # Copied from incomingParser -- maybe should be in util?
        # order_num defaults to None if no OBR segment is found
        order_num = None  
        # If order_date is not overwritten by an OBR segment, date from OBX 
        # segment will be used as both 'date' and 'order_date'.
        order_date = None 
        for seg in [segment for segment in self.message if segment[0][0] in ['OBR', 'OBX']]:
            if seg[0][0] == 'OBR':
                # Set the order variables, which are then consumed by all OBX 
                # segments, up until the next OBR segment is encountered
                order_num = seg[2][0]
                order_date = date_from_str(seg[7][0])
                log.debug('OBR segment')
                log.debug('\t Order number: %s' % order_num)
                log.debug('\t Order date: %s' % order_date)
                continue
            # Below this point, we will only have OBX segments
            resdate = self.datetime_from_string(seg[14][0])
            if not order_date:
                order_date = resdate
            native_code = seg[3][0]
            native_name = seg[3][1]
            result_string = seg[5][0]
            ref_unit = seg[6][0]
            ref_range = seg[7][0].split('-')
            abnormal_flag = seg[8][0]
            status = seg[11][0]
            if not abnormal_flag:
                abnormal_flag = None
            ref_low_string = None
            ref_high_string = None
            if len(ref_range) == 2: # There must be both high and low
                ref_low_string = ref_range[0]
                ref_high_string = ref_range[1]
            result = LabResult(patient=self.patient, provider=self.provider)
            # Set (result) date and order date to the same thing, since we do 
            # not have separate order date info.
            result.date = order_date if order_date else None
            result.result_date = resdate if resdate else None
            result.order_num = order_num if order_num else None
            result.native_code = native_code if native_code else None
            result.native_name = native_name if native_name else None
            result.result_string = result_string if result_string else None
            result.result_float = self.float_or_none(result_string)
            result.ref_low_string = ref_low_string if ref_low_string else None
            result.ref_high_string = ref_high_string if ref_high_string else None
            result.ref_low_float = self.float_or_none(ref_low_string)
            result.ref_high_float = self.float_or_none(ref_high_string)
            result.ref_unit = ref_unit if ref_unit else None
            #result.ref_range = ref_range if ref_range else None
            result.abnormal_flag = abnormal_flag if abnormal_flag else None
            result.status = status if status else None
            result.provenance = self.provenance
            result.save()
            log.debug('NEW LAB RESULT')
            log.debug('\t Date: %s' % result.date)
            log.debug('\t Native code (name): %s (%s)' % (result.native_code, result.native_name))
            log.debug('\t Lab result: %s %s (float: %s)' % (result.result_string, result.ref_unit, result.result_float))
            log.debug('\t Reference range: %s - %s' % (result.ref_low_float, result.ref_high_float))
            log.debug('\t Abnormal flag: %s' % result.abnormal_flag)
            log.debug('\t Status: %s' % result.status)
            
    def make_encounter(self):
        encounter = Encounter(patient=self.patient, provider=self.provider)
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
            encounter.date = date_from_str(dg1[5][0])
            encounter.provenance = self.provenance
            if not encounter.pk: encounter.save()

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
                encounter.date = date_from_str(obx[-1][0])
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
                encounter.provenance = self.provenance
                encounter.save()
        
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

    
class Command(LoaderCommand):
    
    help = 'Load medical record data from HL7 files'
    
    option_list = LoaderCommand.option_list + (
        make_option('--new', action='store_true', dest='new', 
            help='Process only new HL7 messages'),
        make_option('--retry', action='store_true', dest='retry',
            help='Process only HL7 messages that have previously failed to process'),
        make_option('--all', action='store_true', dest='all', 
            help='Process new and retry HL7 messages.'),
        make_option('--no-load', action='store_false', dest='load', default=True,
            help='Do not load HL7 message data into ESP'),
        make_option('--mail', action='store_true', dest='mail', default=False,
            help='Send email notifications' ),
        make_option('--dry-run', action='store_true', dest='dry_run', default=False,
            help='Show which files would be loaded, but do not actually load them'),
        )
        
    def handle(self, *args, **options):
        #
        # Sanity Check -- do folders exist?
        #
        for folder in [INCOMING_DIR, PROCESSED_DIR, 
                       ATTEMPTED_DIR, FAILED_DIR, SKIPPED_DIR]:
            if not os.path.exists(folder):  # Create folders if necessary
                os.makedirs(folder)
        # 
        # Setup Options
        #
        loaded_counter = 0
        failure_counter = 0
        folders = {}
        options = Values(options) # So we don't have to reference dictionary keys all the time.
        log.debug('options: %s' % options)
        if options.input_folder:
            folder = options.input_folder
            assert os.path.isdir(folder) # Sanity check -- is really a folder?
            folders[folder] = os.listdir(folder)
        if options.single_file:
            log.debug('Loading single file from command line:\n\t%s' % options.single_file)
            # Include only the one file specified on command line
            filepath = options.single_file
            basename = os.path.basename(filepath)
            if Provenance.objects.filter(source=basename, status__in=('loaded', 'errors')).count():
                sys.stderr.write('\nThis file has already been loaded into the database.  Aborting.\n\n')
                self.archive(options, filepath, 'loaded')
            else:
                status = Hl7MessageLoader(filepath=filepath, options=options).load()
                self.archive(options, filepath, status)
            sys.exit()
        if options.all:
            options.new = True
            options.retry = True
        if options.retry: folders[FAILED_DIR] = os.listdir(FAILED_DIR)
        if options.new: folders[INCOMING_DIR] = os.listdir(INCOMING_DIR)
        if options.dry_run:
            for folder, files in folders.items():
                for f in files: print os.path.abspath(os.path.join(folder, f))
            sys.exit()
        if not options.retry and not options.new:
            sys.stderr.write('You must select either --new, --retry, or --all\n')
            sys.exit()
        #
        # Load Files
        #
        loaded_sources = Provenance.objects.filter(status='loaded')
        for folder, files in folders.items():
            for f in files:
                filepath = os.path.join(folder, f)
                if loaded_sources.filter(source=f).count():
                    log.debug('File already loaded, skipping:  %s' % f)
                    self.archive(options, filepath, 'loaded')
                    continue
                res = Hl7MessageLoader(filepath=filepath, options=options).load()
                if res == 'loaded':
                    loaded_counter += 1
                elif res == 'failure':
                    failure_counter += 1
                else:
                    raise RuntimeError("WTF?!")
        log.info('Loaded:    %s' % loaded_counter)
        log.info('Failed:    %s' % failure_counter)
    
            