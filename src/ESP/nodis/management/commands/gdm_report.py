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

from ESP.emr.models import Patient
from ESP.emr.models import LabResult
from ESP.emr.models import Encounter
from ESP.emr.models import Prescription

from ESP.hef.models import Event
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
    'edc',
    'bmi',
    'intrapartum glucose fasting positive result',
    'intrapartum OGTT50 positive result',
    'intrapartum OGTT75 positive result',
    'intrapartum OGTT100 positive result',
    'postpartum OGTT75 order',
    'postpartum OGTT75 positive result',
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
        all_gdm_cases = Case.objects.filter(condition='gdm').order_by('date')
        case_count = all_gdm_cases.count()
        case_index = 0
        for gdm_case in all_gdm_cases:
            case_index += 1 # Increment case index
            log.debug('Case %6s of %6s' % (case_index, case_count))
            log.debug('%s' % gdm_case)
            log.debug('case date: %s' % gdm_case.date)
            patient = gdm_case.patient
            start_date = gdm_case.date - datetime.timedelta(days=280)
            cutoff_date = gdm_case.date + datetime.timedelta(days=280)
            log.debug('start_date: %s' % start_date)
            log.debug('cutoff_date: %s' % cutoff_date)
            q_obj = Q(patient=patient, date__gte=start_date, date__lte=cutoff_date)
            edc = Encounter.objects.filter(q_obj).aggregate(edc=Max('edc'))['edc']
            events = Event.objects.filter(q_obj)
            if edc:
                log.debug('edc: %s' % edc)
                preg_start = edc - datetime.timedelta(days=280)
                preg_end = edc
                postpartum_events = Event.objects.filter(patient=patient, date__gt=edc, date__lte=edc+datetime.timedelta(weeks=12))
                ogtt75_postpartum_order = bool( postpartum_events.filter(name__startswith='ogtt75', name__endswith='_order')  )
                ogtt75_postpartum_pos = bool( postpartum_events.filter(name__in=OGTT75_POSTPARTUM_EVENTS) )
            else:
                preg_timespans = Timespan.objects.filter(patient=patient, name__in=('pregnancy', 'mini_pregnancy'))
                log.debug('preg_timespans: %s' % preg_timespans)
                preg_start = preg_timespans.filter(start_date__gte=start_date).aggregate(min=Min('start_date'))['min']
                preg_end = preg_timespans.filter(start_date__lte=cutoff_date).aggregate(max=Max('end_date'))['max']
                ogtt75_postpartum_order = 'Unknown EDC'
                ogtt75_postpartum_pos = 'Unknown EDC'
            log.debug('preg_start: %s' % preg_start)
            log.debug('preg_end: %s' % preg_end)
            preg_events = Event.objects.filter(patient=patient, date__gte=preg_start, date__lte=preg_end)
            lancets = events.filter(name__in=['lancets_rx', 'test_strips_rx'])
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
                'edc': edc,
                'bmi': bmi,
                'intrapartum glucose fasting positive result': bool(preg_events.filter(name='glucose_fasting_126').count() ),
                'intrapartum OGTT50 positive result': bool(preg_events.filter(name__in=OGTT50_EVENTS).count() ),
                'intrapartum OGTT75 positive result': bool( preg_events.filter(name__in=OGTT75_INTRAPARTUM_EVENTS).count() > 1),
                'intrapartum OGTT100 positive result': bool( preg_events.filter(name__in=OGTT100_EVENTS).count() > 1 ),
                'postpartum OGTT75 order': ogtt75_postpartum_order,
                'postpartum OGTT75 positive result': ogtt75_postpartum_pos,
                'lancets / test strips Rx': bool(preg_lancet_rx.count()),
                'new lancets / test strips Rx': new_lancet_rx,
                'insulin rx during pregnancy': bool( preg_events.filter(name='insulin_rx').count() ),
                'referral to nutrition': nutrition_ref,
                }
            writer.writerow(values)
    
