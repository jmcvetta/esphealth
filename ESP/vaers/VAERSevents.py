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

def diagnosis_codes():
    '''
    Returns a set of all the codes that are indicator of diagnosis
    that may be an adverse event.
    '''
    codes = []
    for key in rules.VAERS_DIAGNOSTICS.keys():
        codes.extend(key.split(';'))
    return set(codes)


# This can be a constant
VAERS_DIAGNOSTICS_CODES = diagnosis_codes()





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
        return self.temp < rules.TEMP_TO_REPORT


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
    - A wildcard to represent a family of codes: 320*, 345.*
    - An interval with a wildcard: 802.3-998*
    
    this function verifies if icd9_code matches the expression, 
    i.e, satisfies the condition represented by the expression
    '''

    def transform_expression(expression):

        if '-' in expression:
            # It's an expression to show a range of values
            low, high = expression.split('-')
            if '.*' in low: low = low.replace('.*', '.00')
            if '*' in low: low = low.replace('*', '.00')

            if '.*' in high: high = high.replace('.*', '.99')
            if '*' in high: high = high.replace('*', '.99')
            
        if '*' in expression and '-' not in expression:
            ls, hs = ('00', '99') if '.*' in expression else ('.00', '.99')
                
            low, high = expression.replace('*', ls), expression.replace('*', hs)
            
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

    def match_wildcard(code, regexp):
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
        #In case it is a code that is really out of the pattern
        return match_precise(icd9_code.strip(), 
                             expression_to_match.strip())
    
    try:
        expression = float(expression_to_match)
        return match_precise(target, expression)
    except ValueError:
        # expression_to_match is not a code
        return match_wildcard(target, expression_to_match)
        

def is_diagnostics_match(code):
    for expression in VAERS_DIAGNOSTICS_CODES:
        if match_icd9_expression(code, expression):
            return True

    return False
    

def diagnosis_by_code(icd9_code):
    # Check all rules, to see if the code we have is a possible adverse event
    for key in rules.VAERS_DIAGNOSTICS.keys():
        codes = key.split(';')
        # for all the codes that indicate the diagnosis, we see if it matches
        # It it does, we have it.
        for code in codes:
            if match_icd9_expression(icd9_code, code.strip()):
                return rules.VAERS_DIAGNOSTICS[key]

    # Couldn't find a match
    return None
        



def exclusion_codes(icd9_code):
    '''
    Given an icd9 code represented by event_code, returns a list of
    icd9 codes that indicate that the diagnosis is not an adverse
    event
    '''
    diagnosis = diagnosis_by_code(icd9_code)
    return (diagnosis and diagnosis.get('ignore_codes', None))


      

def get_immunization_adverse_events(immunization, detect_only=None):
    
    time_window = datetime.timedelta(days=rules.TIME_WINDOW_POST_EVENT)

    def detect_fevers(imm, patient):
        
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
    
        imm.date = datetime.datetime.strptime(imm.ImmDate, '%Y%m%d')
        patient_encounters = Enc.manager.from_patient(
            patient, start_date=imm.date, end_date=imm.date + time_window
            )
        
        result = []
        for encounter in patient_encounters:
            vaers_codes = [x for x in encounter.EncICD9_Codes.split(',') 
                           if (x.strip() and is_diagnostics_match(x))]

            for code in vaers_codes:
                event = Icd9DiagnosisEvent(imm, encounter, 
                                           diagnosis=diagnosis_by_code(code))
                result.append(event)

        return result

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



def any_event(**kw):
    start_date = kw.pop('start_date', EPOCH)
    end_date = kw.pop('end_date', NOW)
    detect_only = kw.pop('detect_only', None)
    
    imms = Immunization.manager.all_between(start_date, end_date)

    for imm in imms:
        events = get_immunization_adverse_events(imm, detect_only)
        if events: return events[0]

    return []
    
    
    
