## started january 11 2008 rml
## copyright ross lazarus 2008
## released under the LGPL v2 or any later version
##
## Basic idea is to follow each subject for 30 (or n) days after
## an exposure (vaccination initially but eventually rx or procedure)
## and look for out of range lab values or vital signs
##

import os, sys
import datetime
import logging
import operator

import pdb

sys.path.append('../')
import settings

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

# FIXME: I still don't get all the contortions required for PYTHONPATH. 
# The two lines below should not be needed in a sane environment.
parent_dir = os.path.join(settings.TOPDIR, '../')
sys.path.append(parent_dir)

from esp.models import Immunization, Enc

import utils
from utils.utils import debug

import rules

NOW = datetime.datetime.now()
EPOCH = NOW - datetime.timedelta(days=3*365)



class AdverseEvent(object):
    def __init__(self, trigger_immunization, encounter):
        self.encounter = encounter
        self.encounter.date = datetime.datetime.strptime(encounter.EncEncounter_Date, '%Y%m%d')
        self.trigger_immunization = trigger_immunization
        self.patient = trigger_immunization.ImmPatient
        self.patient_immunization_record = trigger_immunization.ImmRecId
    def has_exclusion_rules(self):
        return False


class FeverEvent(AdverseEvent):        
    def __init__(self, trigger_immunization, encounter, **kw):
        super(FeverEvent, self).__init__(trigger_immunization, encounter)
        self.temp = kw.pop('temp', None)
        self.name = 'Fever'
    def has_exclusion_rules(self):
        return rules.TEMP_TO_REPORT >= self.temp


class Icd9DiagnosisEvent(AdverseEvent):
    def __init__(self, trigger_immunization, encounter, **kw):
        super(Icd9DiagnosisEvent, self).__init__(trigger_immunization, encounter)
        self.diagnosis = kw.pop('diagnosis', None)
        self.name = self.diagnosis['name']

    def same_diagnosis_in_past(self, time_in_months):
        pass

    def related_codes_in_past(self):
        pass

    def has_exclusion_rules(self):
        ignore_period = self.diagnosis.get('ignore_period', None)
        ignore_codes = self.diagnosis.get('ignore_codes', None)
        
        return (self.same_diagnosis_in_past(ignore_period) or
                self.related_codes_in_past() or
                False)
 


def match_icd9_expression(icd9_code, expression_to_match):
    '''
    considering expressions to represent:
    - A code: 558.3
    - An interval of codes: 047.0-047.1
    - A regexp to represent a family of codes: 320*
    - An interval with a regexp: 802.3-998*
    
    this function verifies if icd9_code matches the expression, 
    i.e, satisfies the condition represented by the expression
    '''

    def transform_expression(expression):
        if '-' in expression:
            # It's an expression to show a range of values
            low, high = expression.split('-')
            if '*' in low: low = low.replace('*', '.00')
            if '*' in high: high = high.replace('*', '.99')
            
        if '*' in expression and '-' not in expression:
            low, high = expression.replace('*', '.00'), expression.replace('*', '.99')
            
        if '*' not in expression and '-' not in expression:
            raise ValueError, 'not a valid icd9 expression'


        # We must get two regular codes in the end.
        ll, hh = float(low), float(high)    


        assert(type(ll) is float)
        assert(type(hh) is float)
    
        return ll, hh
            
    
    def match_precise(code, expression):
        return code == expression
    
    def match_range(code, floor, ceiling):
        return floor <= code <= ceiling

    def match_regexp(code, regexp):
        floor, ceiling = transform_expression(regexp)
        return match_range(code, floor, ceiling)


    # Verify first if the icd9 code is valid
    # We will only accept icd9 codes in the DDD.D(D?) format
    try:
        length = len(icd9_code.strip())
        assert(5 <= length <= 6)
        assert('.' == icd9_code[3])
        target = float(icd9_code)
    except Exception:
        raise ValueError, 'icd9_code is not valid'
    
    try:
        expression = float(expression_to_match)
        return match_precise(target, expression)
    except ValueError:
        # expression_to_match is not a code
        return match_regexp(target, expression_to_match)
        
        

def diagnosis_by_code(icd9_code):
    # Check all rules, to see if the code we have is a possible adverse event
    for key in rules.VAERS_DIAGNOSTICS.keys():
        codes = key.split(';')
        # for all the codes that indicate the diagnosis, we see if it matches
        # It it does, we have it.
        for code in codes:
            if match_icd9_expression(icd9_code, code):
                return rules.VAERS_DIAGNOSTICS[key]

    # Couldn't find a match
    return None
        

def diagnosis_codes():
    '''
    Returns a set of all the codes that are indicator of diagnosis
    that may be an adverse event.
    '''
    codes = []
    for key in rules.VAERS_DIAGNOSTICS.keys():
        codes.extend(key.split(';'))
    return set(codes)


def exclusion_codes(icd9_code):
    '''
    Given an icd9 code represented by event_code, returns a list of
    icd9 codes that indicate that the diagnosis is not an adverse
    event
    '''
    diagnosis = diagnosis_by_code(icd9_code)
    return (diagnosis and diagnosis.get('ignore_codes', None))

def vaers_encounters(start_date=None, end_date=None):
    start_date = start_date or EPOCH
    end_date = end_date or NOW
    all_vaers_encounters = []

    for code in diagnosis_codes():
        encounters = Enc.objects.filter(EncEncounter_Date__gte=start_date,
                                        EncEncounter_Date__lte=end_date,
                                        EncICD9_Codes__icontains=code)
        if encounters: all_vaers_encounters.extend(encounters)
            
    return all_vaers_encounters

      

def get_immunization_adverse_events(immunization, detect_only=None):

    def detect_fevers(imm, patient):
        
        time_window = datetime.timedelta(days=rules.TIME_WINDOW_POST_EVENT)


#        FIXME: current model won't allow us to do this query. 
#
#
#        encounters = Enc.objects.filter(
#            patient=patient, 
#            date__gte=imm.date,
#            date__lte=imm.date + time_window,
#            temperature__gte=rules.TEMP_TO_REPORT            
#            )
#
#       I'm keeping the function below as a workaround.

        imm.date = datetime.datetime.strptime(imm.ImmDate, '%Y%m%d')        
        encounters = Enc.manager.withFever(patient, rules.TEMP_TO_REPORT, start_date=imm.date, end_date = imm.date + time_window)
        

        return [FeverEvent(imm, x, temp=float(x.EncTemperature)) for x in encounters]


    def detect_diagnosis_events(imm, patient):
        return []

    def detect_lab_results_events(imm, patient):
        return []


    patient = immunization.ImmPatient
    
    actions = { 
        'fever': detect_fevers(immunization, patient),
        'diagnosis': detect_diagnosis_events(immunization, patient),
        'lx': detect_lab_results_events(immunization, patient)
        }

    if detect_only in actions.keys():
        return actions[detect_only]
    else:
        return reduce(operator.add, actions.values())



def get_adverse_events(**kw):
    start_date = kw.pop('start_date', EPOCH)
    end_date = kw.pop('end_date', NOW)
    detect_only = kw.pop('detect_only', None)

    events = []

    imms = Immunization.manager.all_between(start_date, end_date)
    for imm in imms:
        events.extend(get_immunization_adverse_events(imm, detect_only))

    return events
