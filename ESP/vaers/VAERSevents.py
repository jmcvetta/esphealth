## started january 11 2008 rml
## copyright ross lazarus 2008
## released under the LGPL v2 or any later version
##
## Basic idea is to follow each subject for 30 (or n) days after
## an exposure (vaccination initially but eventually rx or procedure)
## and look for out of range lab values or vital signs
##

import os, sys
import django
import time, datetime
import copy, logging


sys.path.append('../')
import settings

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

# FIXME: I still don't get all the contortions required for PYTHONPATH. 
# The two lines below should not be needed in a sane environment.
parent_dir = os.path.join(settings.TOPDIR, '../')
sys.path.append(parent_dir)

from esp.models import Immunization

import utils
import rules

NOW = datetime.datetime.now()
EPOCH = NOW - datetime.timedelta(days=3*365)



class AdverseEvent(object):
    def __init__(self, triggered_by):
        self.triggered_by = triggered_by
    def has_exclusion_rules(self):
        return False


class FeverEvent(AdverseEvent):
    TEMP_TO_REPORT = 100.4 # degrees are F in our records, 38C = 100.4F
    TIME_WINDOW_POST_EVENT = datetime.timedelta(days=7) # One week to report
    def detect_events(immunization):
        pass
        
    def __init__(self, triggered_by, **kw):
        super(FeverEvent, self).__init__(triggered_by)
        self.temp = kw.pop('temp', None)
    def has_exclusion_rules(self):
        return FeverEvent.TEMP_TO_REPORT >= self.temp


class Icd9DiagnosisEvent(AdverseEvent):
    def __init__(self, triggered_by, **kw):
        super(Icd9DiagnosisEvent, self).__init__(triggered_by)
        self.diagnosis = kw.pop('diagnosis', None)

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
            if '*' in low: low = low.replace('*', '.0')
            if '*' in high: high = high.replace('*', '.9')
            
        if '*' in expression and '-' not in expression:
            low, high = expression.replace('*', '.0'), expression.replace('*', '.9')
            
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

      

def detect_events(immunization, detect_only=None):

    def detect_fevers(imm):
        pass

    return []

def report(events):
    for evt in events:
        print evt


def run(**kw):

    detect_only = kw.pop('detect_only', None)
    start_date = kw.pop('start_date', EPOCH)
    end_date = kw.pop('end_date', NOW)

    
    immunizations = Immunization.manager.all_between(start_date, end_date)
    
    for imm in immunizations:
        events = detect_events(imm, detect_only=detect_only)
        report([ev for ev in events if not event.has_exclusion_rules()])



    
if __name__ == "__main__":
    run()
