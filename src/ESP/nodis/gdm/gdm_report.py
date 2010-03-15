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


from ESP.utils.utils import log
from ESP.utils.utils import log_query

from ESP.emr.models import Patient
from ESP.emr.models import LabResult
from ESP.emr.models import Encounter
from ESP.emr.models import Prescription

from ESP.hef.core import BaseHeuristic

from ESP.nodis.models import ComplexEventPattern
from ESP.nodis.models import SimpleEventPattern
from ESP.nodis.models import Condition
from ESP.nodis import defs

from ESP.nodis.defs import jaundice_alt400
from ESP.nodis.defs import no_hep_b_surf
from ESP.nodis.defs import no_hep_b
from ESP.nodis.defs import hep_c_1
from ESP.nodis.defs import hep_c
from ESP.nodis.defs import chlamydia

from ESP.nodis.models import Case
from ESP.nodis.models import Pattern
from ESP.nodis.models import Gdm
from ESP.hef.models import Event
from ESP.hef.models import Pregnancy
from ESP.hef.core import PregnancyHeuristic

from ESP.conf.models import CodeMap
from ESP.utils.utils import log_query
from ESP.hef.models import Timespan




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
    'zip code',
    'start_date',
    'end_date',
    'algorithm',
    'edc',
    'intrapartum glucose fasting positive result',
    'intrapartum OGTT50 positive result',
    'intrapartum OGTT75 positive result',
    'intrapartum OGTT100 positive result',
    'postpartum OGTT75 order positive result',
    'postpartum OGTT75 positive result',
    'lancets / test strips Rx',
    'new lancets / test strips Rx',
    ]


def main():
    writer = csv.DictWriter(sys.stdout, fieldnames=FIELDS)
    header = dict(zip(FIELDS, FIELDS)) 
    writer.writerow(header)
    for gdm_case in Case.objects.filter(condition='gdm').order_by('date'):
        log.debug('%s' % gdm_case)
        patient = gdm_case.patient
        start_date = gdm_case.date - datetime.timedelta(days=250)
        cutoff_date = gdm_case.date + datetime.timedelta(days=250)
        q_obj = Q(patient=patient, date__gte=start_date, date__lte=cutoff_date)
        edc = Encounter.objects.filter(q_obj).aggregate(edc=Max('edc'))['edc']
        if edc:
            preg_start = edc - datetime.timedelta(days=250)
            preg_end = edc
            ogtt75_postpartum = bool( Event.objects.filter(patient=patient, date__gt=edc, name__startswith='ogtt75', name__endswith='_order')  )
        else:
            preg_timespans = Timespan.objects.filter(patient=patient, name__startswith='pregnancy_inferred')
            preg_start = preg_timespans.filter(start_date__gte=start_date).aggregate(min=Min('start_date'))['min']
            preg_end = preg_timespans.filter(start_date__lte=cutoff_date).aggregate(max=Max('end_date'))['max']
            ogtt75_postpartum = 'Unknown EDC'
        events = Event.objects.filter(q_obj)
        lancets = events.filter(patient=patient, name__in=['lancets_rx', 'test_strips_rx'])
        preg_lancet_rx = lancets.filter(date__gte=preg_start, date__lte=preg_end)
        previous_lancet_rx = lancets.filter(date__lte=preg_start, date__gte=preg_start-datetime.timedelta(days=365))
        if preg_lancet_rx and not previous_lancet_rx:
            new_lancet_rx = True
        else:
            new_lancet_rx = False
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
            'intrapartum glucose fasting positive result': bool(events.filter(name='glucose_fasting_126').count() ),
            'intrapartum OGTT50 positive result': bool(events.filter(name__in=OGTT50_EVENT_NAMES).count() ),
            'intrapartum OGTT75 positive result': bool( events.filter(name__in=OGTT75_INTRAPARTUM_EVENT_NAMES).count() > 1),
            'intrapartum OGTT100 positive result': bool( events.filter(name__in=OGTT100_EVENT_NAMES).count() > 1 ),
            'postpartum OGTT75 order positive result': ogtt75_postpartum,
            'postpartum OGTT75 positive result': bool( events.filter(name__in=OGTT75_POSTPARTUM_EVENT_NAMES).count() ),
            'lancets / test strips Rx': preg_lancet_rx,
            'new lancets / test strips Rx': new_lancet_rx,
            }
        writer.writerow(values)
    

if __name__ == '__main__':
    main()
