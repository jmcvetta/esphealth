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


import os
import datetime
import random
import pprint
import re

from hl7 import hl7

from ESP.conf.models import Icd9
from ESP.emr.models import Provider
from ESP.emr.models import Patient
from ESP.emr.models import Encounter
from ESP.emr.models import LabOrder
from ESP.emr.models import LabResult
from ESP.emr.models import Prescription
from ESP.utils.utils import log


UPDATED_BY = 'load_hl7.py'


HL7_FOLDER = '/home/rejmv/work/NORTH_ADAMS/incomingHL7/'
#TESTMSG = '/home/rejmv/work/NORTH_ADAMS/incomingHL7/NADAMS_e76e1d24-0e4c-11de-a002-fb07a536f7cf_2009-3-11 10.57.13.hl7'
#TESTMSG = '/home/rejmv/work/NORTH_ADAMS/incomingHL7/NADAMS_9da4c7c0-ca96-11dd-b49a-ea1688cfc655_2008-12-15 5.53.32.hl7'
#TESTMSG = '/home/rejmv/work/NORTH_ADAMS/incomingHL7/38389d3c-39e2-11de-94b5-c0e83ccf8498_2009-5-5 22.4.23.hl7'
#TESTMSG = '/home/rejmv/work/NORTH_ADAMS/incomingHL7/f51d44d4-39c5-11de-94b5-c0e83ccf8498_2009-5-5 18.42.5.hl7'
#TESTMSG = '/home/rejmv/work/NORTH_ADAMS/incomingHL7/9465302c-39ca-11de-94b5-c0e83ccf8498_2009-5-5 19.15.10.hl7'
#TESTMSG = '/home/rejmv/work/NORTH_ADAMS/incomingHL7/NADAMS_c0643514-10f8-11de-a002-fb07a536f7cf_2009-3-14 20.32.23.hl7'
#TESTMSG = '/home/rejmv/work/NORTH_ADAMS/incomingHL7/d5b4c164-39f4-11de-94b5-c0e83ccf8498_2009-5-6 0.17.38.hl7'
TESTMSG = '/home/rejmv/work/NORTH_ADAMS/incomingHL7/NADAMS_9014a784-0080-11de-a002-fb07a536f7cf_2009-2-21 20.31.44.hl7'





class Hl7ImportException(BaseException):
    '''
    Base exception for problems encountered while loading HL7 messages
    into the database.
    '''
    pass

class NoMSH(Hl7ImportException):
    '''
    HL7 message does not contain an MSH segment
    '''
    pass

class NoPID(Hl7ImportException):
    '''
    HL7 message does not contain an MSH segment
    '''
    pass

class NoPV1(Hl7ImportException):
    '''
    HL7 message does not contain an MSH segment
    '''
    pass


class Hl7MessageLoader(object):
    def __init__(self, msg_string):
        #
        # MSH
        #
        self.msg_string = msg_string
        self.message = hl7.parse(msg_string) # parsed msg
        print '+' * 80
        pprint.pprint(self.message)
        print '+' * 80
        msh_seg = hl7.segment('MSH', self.message)
        if not msh_seg:
            raise NoMSH
        self.msg_type = msh_seg[8] # Is it good to store this as a list?
        log.debug('Message type: %s' % self.msg_type)
        self.message_date = self.datetime_from_string(msh_seg[6][0])
        log.debug('Message date: %s' % self.message_date)
        #
        # PID
        #
        pid_seg = hl7.segment('PID', self.message)
        if not pid_seg:
            raise NoPID
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
            raise NoPV1
        self.visit_date = self.datetime_from_string(pv1_seg[-1]) # Will date always be last??
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
        pass
    
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
                ref_low = float_regex.match(ref_range[0]).group(1)
                result.ref_low_string = ref_low
                result.ref_low_float = float(ref_low)
                ref_high = float_regex.match(ref_range[1]).group(1)
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
        encounter = None # All segments will be looped over to generate single Encounter object
        for dg1 in hl7.segments('DG1', self.message):
            # Discard segments where diagnosis is not coded in ICD9:
            if dg1[3][2] != 'I9':
                continue
            icd9_str = dg1[3][0]
            icd9_obj = Icd9.objects.get(code=icd9_str)
            enc_date = self.datetime_from_string(dg1[5][0])
            if not encounter:
                encounter = Encounter(patient=self.patient, provider=self.provider, 
                    date=enc_date, updated_by = UPDATED_BY)
                encounter.save()
                log.debug('Created new encounter: %s' % encounter)
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
            raise 'Cannot convert string to datetime!'
        return datetime.datetime.strptime(str, dateformat)

    



def main():
    all_files = os.listdir(HL7_FOLDER)
    filename = random.choice(all_files)
    m = open(os.path.join(HL7_FOLDER, filename)).read()
    m = open(TESTMSG).read()
    log.debug('Loading HL7 message file "%s"' % filename)
    Hl7MessageLoader(m)


if __name__ == '__main__':
    main()