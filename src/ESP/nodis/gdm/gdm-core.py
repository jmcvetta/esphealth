#!/usr/bin/python
'''
Created on Jul 9, 2009

@author: jason
'''

import sys
import re
import pprint
import datetime
import csv
import hashlib

from django.db import connection
from django.db.models import Q
from django.db.models import F
from django.db.models import Sum
from django.db.models import Count
from django.db.models import Max
from django.db.models import Min

from ESP.utils.utils import log
from ESP.utils.utils import log_query

from ESP.emr.models import Patient
from ESP.emr.models import LabResult
from ESP.emr.models import Encounter
from ESP.emr.models import Prescription

from ESP.hef.core import BaseHeuristic
from ESP.hef.core import TimespanHeuristic

from ESP.nodis.models import ComplexEventPattern
from ESP.nodis.models import SimpleEventPattern
from ESP.nodis.models import Condition
from ESP.nodis import defs


from ESP.nodis.models import Case
from ESP.nodis.models import Pattern
from ESP.nodis.models import Gdm
from ESP.hef.models import Event
from ESP.hef.models import Timespan
from ESP.hef.core import PregnancyHeuristic

from ESP.conf.models import CodeMap
from ESP.utils.utils import log_query
from ESP.hef.core import TimespanHeuristic




OGTT50_EVENT_NAMES = [
    'ogtt50_fasting_95',
    'ogtt50_1hr_190',
    'ogtt50_random_190',
    ]


OGTT75_INTRAPARTUM_EVENT_NAMES = [
    'ogtt75_fasting_pos',
    'ogtt75_fasting_ur_pos',
    'ogtt75_30m_pos',
    'ogtt75_1hr_pos',
    'ogtt75_90m_pos',
    'ogtt75_2hr_pos',
    ]
    
OGTT75_POSTPARTUM_EVENT_NAMES = [
    'ogtt75_fasting_126',
    'ogtt75_30m_200',
    'ogtt75_1hr_200',
    'ogtt75_90m_200',
    'ogtt75_2hr_200',
    ]

OGTT100_EVENT_NAMES = [
    'ogtt100_1hr_pos',
    'ogtt100_2hr_pos',
    'ogtt100_30m_pos',
    'ogtt100_3hr_pos',
    'ogtt100_4hr_pos',
    'ogtt100_5hr_pos',
    'ogtt100_90m_pos',
    'ogtt100_fasting_pos',
    ]

FIELDS = [
    'patient db id',
    'mrn',
    'last_name',
    'first_name',
    'date_of_birth',
    'ethnicity',
    'start_date',
    'end_date',
    'edc',
    'positive glucose fasting count',
    'positive OGTT50 count',
    'positive OGTT75 intrapartum count',
    'positive OGTT75 postpartum count',
    'positive OGTT100 count',
    ]

PREGNANCY_TIMESPANS = [
    'pregnancy_inferred_by_edc',
    'pregnancy_inferred_by_icd9',
    ]

RECURRENCE_INTERVAL = 250 # GDM can recur after 250 days



def is_intrapartum(date, preg_ranges):
    '''
    Checks whether patient was pregnant on date, based on list of datetime pairs 'preg_ranges'
    '''
    for start, end in preg_ranges:
        if (date >= start) and (date <= end):
            return True
    return False

def is_postpartum(date, edcs):
    for edc in edcs:
        cutoff_date = edc + datetime.timedelta(weeks=12)
        if (date > edc) and (date <= cutoff_date):
            return True
    return False

def generate_gdm_cases(pattern, event_names, event_count, partum):
    if partum == 'intra':
        intrapartum = True
        postpartum = False
    elif partum == 'post':
        intrapartum = False
        postpartum = True
    else:
        raise 'Bad partum value'
    preg_patients = Timespan.objects.filter(name__in=PREGNANCY_TIMESPANS).values_list('patient', flat=True)
    cached_patient = None
    cached_preg_ranges = None
    cached_edcs = None
    cached_gdm_date = None
    q_obj = Q(patient__in=preg_patients, name__in=event_names)
    q_obj &= ~Q(case__condition='gdm')
    events = Event.objects.filter(q_obj)
    patient_dates = events.values('patient', 'date').distinct().annotate(count=Count('name')).filter(count__gte=1)
    log_query('Patient dates', patient_dates)
    for pd in patient_dates:
        patient = pd['patient']
        event_date = pd['date']
        if not patient == cached_patient:
            if intrapartum:
                cached_preg_ranges = Timespan.objects.filter(patient=patient).values_list('start_date', 'end_date').order_by('start_date', 'end_date')
            if postpartum:
                cached_edcs = Encounter.objects.filter(patient=patient, edc__isnull=False).order_by('date').values_list('date', flat=True)
            cached_patient = patient
            cached_gdm_date = None
        if cached_gdm_date and (e.date < cached_gdm_date + datetime.timedelta(RECURRENCE_INTERVAL)):
            continue # This event falls before next possible recurrence 
        if intrapartum and not is_intrapartum(event_date, cached_preg_ranges):
            continue # Patient was not pregnant at this event
        if postpartum and not is_postpartum(event_date, cached_edcs):
            continue
        #
        # If we've made it this far, we have a GDM case
        #
        events_to_attach = Event.objects.filter(patient=patient, date=event_date, name__in=event_names).order_by('date')
        log.debug('Events to attach: %s' % events_to_attach)
        # 'patient' is an Integer -- needs to be a Patient instance for use when creating a new Case instance
        patient_obj = Patient.objects.get(pk=patient)
        hash = hashlib.sha224(pattern).hexdigest()
        try: 
            pat_obj = Pattern.objects.get(hash=hash)
        except Pattern.DoesNotExist:
            pat_obj = Pattern(pattern=pattern, hash=hash, name=pattern)
            pat_obj.save()
        new_case = Case(
            patient = patient_obj,
            condition = 'gdm',
            provider = events_to_attach[0].content_object.provider,
            date = event_date,
            pattern = pat_obj,
            )
        new_case.save()
        cached_gdm_date = event_date
        new_case.events = events_to_attach
        new_case.save()
        log.info('Saved new GDM case: %s' % new_case)
            
    

def main():
    detection_schemes = [
        ('GDM:glucose_fasting', ['glucose_fasting_126'], 1, 'intra'),
        ('GDM:ogtt50_intrapartum', OGTT50_EVENT_NAMES, 1, 'intra' ),
        ('GDM:ogtt75_intrapartum', OGTT75_INTRAPARTUM_EVENT_NAMES, 2, 'intra' ),
        ('GDM:ogtt100_intrapartum', OGTT100_EVENT_NAMES, 2, 'intra' ),
        ('GDM:ogtt75_postpartum', OGTT75_POSTPARTUM_EVENT_NAMES, 1, 'post' ),
        ]
    for pattern, event_names, event_count, partum in detection_schemes:
        log.info('Generated GMD cases for "%s"' % pattern)
        generate_gdm_cases(pattern=pattern, event_names=event_names, event_count=event_count, partum=partum)
        
        
        
    
if __name__ == '__main__':
    main()