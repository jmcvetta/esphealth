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
from dateutil.relativedelta import relativedelta

from django.db import connection
from django.db.models import Q
from django.db.models import F
from django.db.models import Sum
from django.db.models import Count
from django.db.models import Max
from django.db.models import Min
from django.core.management.base import BaseCommand

from ESP.utils.utils import log
from ESP.utils.utils import log_query

from ESP.conf.models import CodeMap

from ESP.emr.models import Patient
from ESP.emr.models import LabResult
from ESP.emr.models import LabOrder
from ESP.emr.models import Encounter
from ESP.emr.models import Prescription

from ESP.hef.models import Event
from ESP.hef.models import EventType
from ESP.hef.models import Timespan

from ESP.nodis.models import Case
from ESP.nodis.models import Pattern

from ESP.nodis.defs import gdm_ogtt50
from ESP.nodis.defs import ogtt75_multi_intrapartum
from ESP.nodis.defs import ogtt75_multi_postpartum
from ESP.nodis.defs import ogtt100_multi_intrapartum
OGTT50_EVENTS = gdm_ogtt50.patterns
OGTT75_INTRAPARTUM_EVENTS = ogtt75_multi_intrapartum.events
OGTT75_POSTPARTUM_EVENTS = ogtt75_multi_postpartum.events
OGTT100_EVENTS = ogtt100_multi_intrapartum.events
OGTT75_RESULT_EVENTS = EventType.objects.filter(name__startswith='ogtt75', name__endswith='_order')

FIELDS = [
    'patient db id',
    'mrn',
    'last_name',
    'first_name',
    'date_of_birth',
    'ethnicity',
    'zip code',
    'start_date',
    'end_date',
    'algorithm',
    'edd',
    'bmi',
    'age at preg onset',
    'intrapartum glucose fasting positive result',
    'intrapartum OGTT50 positive result',
    'intrapartum OGTT75 positive result',
    'intrapartum OGTT100 positive result',
    'postpartum OGTT75 order',
    'postpartum OGTT75 any result',
    'postpartum OGTT75 positive result',
    'postpartum A1C order',
    'postpartum A1C result',
    'lancets / test strips Rx',
    'new lancets / test strips Rx',
    'insulin rx during pregnancy',
    'referral to nutrition',
    ]


class Command(BaseCommand):
    
    help = 'Generate report on all GDM cases'
    
    def handle(self, *args, **options):
        writer = csv.DictWriter(sys.stdout, fieldnames=FIELDS)
        header = dict(zip(FIELDS, FIELDS)) 
        writer.writerow(header)
        ogtt75_native_codes = CodeMap.objects.filter(heuristic__istartswith='ogtt75').values_list('native_code', flat=True).distinct()
        a1c_native_codes = CodeMap.objects.filter(heuristic='a1c').values_list('native_code', flat=True).distinct()
        all_gdm_cases = Case.objects.filter(condition='gdm').order_by('date')
        case_count = all_gdm_cases.count()
        case_index = 0
        for gdm_case in all_gdm_cases:
            case_index += 1 # Increment case index
            log.debug('Case %6s of %6s' % (case_index, case_count))
            log.debug('%s' % gdm_case)
            log.debug('case date: %s' % gdm_case.date)
            patient = gdm_case.patient
            log.debug('patient id: %s' % patient.pk)
            events = Event.objects.filter(patient=patient)
            #
            # Pregnancy Dates
            #
            preg_timespans = Timespan.objects.filter(patient=patient, name='pregnancy', 
                start_date__lte=gdm_case.date, end_date__gte=gdm_case.date)
            preg_start = preg_timespans.aggregate(min=Min('start_date'))['min']
            preg_end = preg_timespans.aggregate(max=Max('end_date'))['max']
            preg_events = Event.objects.filter(patient=patient, date__gte=preg_start, date__lte=preg_end)
            log.debug('preg_start: %s' % preg_start)
            log.debug('preg_end: %s' % preg_end)
            #
            # EDD
            #
            edd_encs = Encounter.objects.filter(patient=patient, date__gte=preg_start, date__lte=preg_end, edc__isnull=False)
            if edd_encs:
                edd = edd_encs.order_by('-date')[0].edc
            else:
                edd = 'Unknown'
            log.debug('edd: %s' % edd)
            #
            # Postpartum
            #
            has_end_of_preg = bool( preg_timespans.filter(pattern__in=['EDD', 'ICD9_EOP']) )
            log.debug('has end of preg: %s' % has_end_of_preg)
            if has_end_of_preg:
                postpartum_events = Event.objects.filter(patient=patient, date__gt=preg_end, date__lte=preg_end+datetime.timedelta(weeks=12))
                #ogtt75_postpartum_order = bool( LabOrder.objects.filter(patient=patient, date__gt=preg_end, 
                    #date__lte=preg_end+datetime.timedelta(weeks=12), native_code__in=ogtt75_native_codes) )
                ogtt75_postpartum_order = bool( Event.objects.filter(patient=patient, date__gt=preg_end, 
                    date__lte=preg_end+datetime.timedelta(weeks=12), event_type='ogtt75_series--order') )
                ogtt75_postpartum_result = bool( postpartum_events.filter(event_type__in=OGTT75_RESULT_EVENTS)  )
                ogtt75_postpartum_pos = bool( postpartum_events.filter(event_type__in=OGTT75_POSTPARTUM_EVENTS) )
                #a1c_postpartum_order = bool( LabOrder.objects.filter(patient=patient, date__gt=preg_end, 
                    #date__lte=preg_end+datetime.timedelta(weeks=12), native_code__in=a1c_native_codes) )
                a1c_postpartum_order = bool( Event.objects.filter(patient=patient, date__gt=preg_end, 
                    date__lte=preg_end+datetime.timedelta(weeks=12), event_type='a1c--order') )
                a1c_tests = LabResult.objects.filter(patient=patient, date__gt=preg_end, 
                    date__lte=preg_end+datetime.timedelta(weeks=12),  native_code__in=a1c_native_codes)
                if a1c_tests:
                    a1c_postpartum_result = a1c_tests.aggregate(maxres=Max('result_float'))['maxres']
                else:
                    a1c_postpartum_result = 'Test not performed'
            else:
                ogtt75_postpartum_order = 'Delivery date unknown'
                ogtt75_postpartum_result = 'Delivery date unknown'
                ogtt75_postpartum_pos = 'Delivery date unknown'
                a1c_postpartum_order =  'Delivery date unknown'
                a1c_postpartum_result =  'Delivery date unknown'
            #
            # Lancets
            #
            lancets = events.filter(event_type__in=['lancets_rx', 'test_strips_rx'])
            preg_lancet_rx = preg_events & lancets
            # previous lancet rx = within previous year
            previous_lancet_rx = lancets.filter(date__lte=preg_start, date__gte=preg_start-datetime.timedelta(days=365))
            if preg_lancet_rx and not previous_lancet_rx:
                new_lancet_rx = True
            else:
                new_lancet_rx = False
            # 
            # Nutrition referral
            #
            nutrition_q = Q(provider__title__icontains='RD') | Q(site_name__icontains='Nutrition')
            nutrition_ref = bool( Encounter.objects.filter(date__gte=preg_start, date__lte=preg_end, patient=patient).filter(nutrition_q) )
            #
            # BMI
            #
            bmi = patient.bmi(date=preg_start, before=365, after=120)
            #
            # Generate output
            #
            values = {
                'patient db id': patient.pk,
                'mrn': patient.mrn,
                'last_name': patient.last_name,
                'first_name': patient.first_name,
                'date_of_birth': patient.date_of_birth,
                'ethnicity': patient.race,
                'zip code': patient.zip,
                'start_date': preg_start,
                'end_date': preg_end,
                'algorithm': gdm_case.pattern.name,
                'edd': edd,
                'bmi': bmi,
                'age at preg onset': relativedelta(preg_start, patient.date_of_birth).years,
                'intrapartum glucose fasting positive result': bool(preg_events.filter(event_type='glucose_fasting_126').count() ),
                'intrapartum OGTT50 positive result': bool(preg_events.filter(event_type__in=OGTT50_EVENTS).count() ),
                'intrapartum OGTT75 positive result': bool( preg_events.filter(event_type__in=OGTT75_INTRAPARTUM_EVENTS).count() > 1),
                'intrapartum OGTT100 positive result': bool( preg_events.filter(event_type__in=OGTT100_EVENTS).count() > 1 ),
                'postpartum OGTT75 order': ogtt75_postpartum_order,
                'postpartum OGTT75 any result': ogtt75_postpartum_result,
                'postpartum OGTT75 positive result': ogtt75_postpartum_pos,
                'postpartum A1C order': a1c_postpartum_order,
                'postpartum A1C result': a1c_postpartum_result,
                'lancets / test strips Rx': bool(preg_lancet_rx.count()),
                'new lancets / test strips Rx': new_lancet_rx,
                'insulin rx during pregnancy': bool( preg_events.filter(event_type='insulin_rx').count() ),
                'referral to nutrition': nutrition_ref,
                }
            writer.writerow(values)
    
