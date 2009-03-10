import os, sys
import datetime
import logging
import operator

sys.path.append(os.path.realpath('..'))
import settings

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from esp.models import Immunization, Enc
from vaers.models import AdverseEvent

import rules
import diagnostics

NOW = datetime.datetime.now()
EPOCH = NOW - datetime.timedelta(days=3*365)

YESTERDAY = NOW - datetime.timedelta(days=1)

def detect_fevers(immunization, time_window):

    patient = immunization.ImmPatient
    date = datetime.datetime.strptime(immunization.ImmDate, '%Y%m%d')        
    encounters = Enc.manager.withFever(
        patient, rules.TEMP_TO_REPORT, 
        start_date=date, end_date=date+time_window
        )
    
    return [dict(immunization=imm, encounter=e, 
                 explanation= 'Patient with %sF fever' % e.EncTemperature) 
            for e in encounters]

def detect_diagnosis_events(immunization, time_window):
    patient = imm.ImmPatient
    date = datetime.datetime.strptime(imm.ImmDate, '%Y%m%d')
    encounters = Enc.manager.from_patient(
        patient, start_date=date, end_date=date + time_window
        )
        
    detected = []
    for encounter in encounters:
        vaers_codes = [x for x in encounter.EncICD9_Codes.split(',') 
                       if (x.strip() and diagnostics.is_match(x))]

        for code in vaers_codes:
            d = diagnostics.by_code(code)
            event = dict(immunization=immunization, 
                         encounter=encounter, 
                         rule='Patient diagnosed with %s' % d['name'])
            detected.append(event)

    return detected
 

def detect_lab_results_events(immunization, time_window):
    return [dict()]


def detect_adverse_events(immunization, only=None):
    '''
    Given an immunization, detects adverse events that it may have
    caused to the patient that received it. 
    Filter the kind of events by passing 'only'. 
    '''
    interval = datetime.timedelta(days=rules.TIME_WINDOW_POST_EVENT)

    actions = { 
        'fever': detect_fevers,
        'diagnosis': detect_diagnosis_events,
        'lx': detect_lab_results_events
        }

    if only in actions.keys():
        return actions[only](immunization, interval)
    else:
        return reduce(operator.add, [f(immunization, interval) for f in actions.values()])



def record_new_adverse_events(**kw):
    start_date = kw.pop('start_date', YESTERDAY)
    end_date = kw.pop('end_date', NOW)
    detect_only = kw.pop('detect_only', None)

    def record_event(immunization, encounter, rule):
        ev, created = Adverse.objects.get_or_create(
            patient=immunization.ImmPatient,
            encounter=encounter,
            immunization=immunization,
            defaults = {'matching_rule_explain': rule}
            )
        return ev
    
    imms = Immunization.manager.all_between(start_date, end_date)
    
    for imm in imms:
        for ev in detect_adverse_events(imm, detect_only):
            record_event(**ev)







