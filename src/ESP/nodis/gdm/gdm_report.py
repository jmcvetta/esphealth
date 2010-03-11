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
    'edc',
    'positive glucose fasting',
    'positive OGTT50 intrapartum',
    'positive OGTT75 intrapartum',
    'positive OGTT75 postpartum',
    'positive OGTT100 intrapartum',
    'lancets test strips rx',
    'OGTT75 postpartum order',
    ]

def summarize_date_range(patient, start_date):
    cutoff_date = start_date + datetime.timedelta(days=250)
    q_obj = Q(patient=patient, date__gte=start_date, date__lte=cutoff_date)
    events = Event.objects.filter(q_obj)
    values = {
        'patient db id': patient.pk,
        'mrn': patient.mrn,
        'last_name': patient.last_name,
        'first_name': patient.first_name,
        'date_of_birth': patient.date_of_birth,
        'ethnicity': patient.race,
        'zip code': patient.zip,
        'start_date': start_date,
        'end_date': cutoff_date,
        'edc': Encounter.objects.filter(q_obj).aggregate(edc=Max('edc'))['edc'],
        'positive glucose fasting': bool(events.filter(name='glucose_fasting_pos').count() ),
        'positive OGTT50 intrapartum': bool(events.filter(name__in=OGTT50_EVENT_NAMES).count() ),
        'positive OGTT75 intrapartum': bool( events.filter(name__in=OGTT75_INTRAPARTUM_EVENT_NAMES).count() > 1),
        'positive OGTT75 postpartum': bool( events.filter(name__in=OGTT75_POSTPARTUM_EVENT_NAMES).count() ),
        'positive OGTT100 intrapartum': bool( events.filter(name__in=OGTT100_EVENT_NAMES).count() > 1 ),
        'lancets test strips rx': bool( Case.objects.filter(patient=patient, condition='gdm', date__gte=start_date, date__lte=cutoff_date ) ),
        'OGTT75 postpartum order': bool( Event.objects.filter(patient=patient, date__gt=cutoff_date, name__startswith='ogtt75', name__endswith='_order')  ),
        }
    return values


def main():
    writer = csv.DictWriter(sys.stdout, fieldnames=FIELDS)
    header = dict(zip(FIELDS, FIELDS)) 
    writer.writerow(header)
    for patient_id in Gdm.objects.values_list('patient_id', flat=True).distinct().iterator():
        patient = Patient.objects.get(pk=patient_id)
        # Find pregnancy ranges (identified by start date)
        dates = Gdm.objects.filter(patient_id=patient_id).values_list('date', flat=True).distinct().order_by('date')
        start_dates = [dates[0]]
        for d in dates:
            cutoff = start_dates[-1] + datetime.timedelta(days=250)
            if d <= cutoff:
                continue
            else:
                start_dates.append(d)
        # Now summarize each pregnancy
        for start in start_dates:
            rowdict = summarize_date_range(patient, start)
            writer.writerow(rowdict)


if __name__ == '__main__':
    main()
