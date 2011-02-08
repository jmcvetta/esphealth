'''
                                  ESP Health
                         Notifiable Diseases Framework
                          Prediabetes Case Generator


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@contact: http://www.esphealth.org
@copyright: (c) 2010 Channing Laboratory
@license: LGPL
'''

import csv
import pprint
import re
import sys
import hashlib
from optparse import make_option
from dateutil.relativedelta import relativedelta

from django.db.models import Q
from django.db.models import F
from django.db.models import Sum
from django.db.models import Count
from django.db.models import Max
from django.db.models import Min
from django.db.models import Avg
from django.core.management.base import BaseCommand, CommandError

from ESP.nodis.models import Case
from ESP.nodis.models import Pattern
from ESP.utils.utils import log
from ESP.utils.utils import log_query
from ESP.emr.models import Encounter
from ESP.emr.models import LabOrder
from ESP.emr.models import LabResult
from ESP.emr.models import Patient
from ESP.emr.models import Prescription
from ESP.hef.models import Event
from ESP.hef.models import EventType
from ESP.hef.models import Timespan
from ESP.hef.models import AbstractLabTest


class Command(BaseCommand):
    
    help = 'Generate and report on Prediabetes cases'
    
    option_list = BaseCommand.option_list + (
        make_option('--generate', action='store_true', dest='generate',  default=False,
            help='Generate cases of prediabetes'),
        make_option('--report', action='store_true', dest='report',  default=False,
            help='Produce prediabetes report'),
        )
    
    PRE_DM_PATTERN = Pattern.objects.get_or_create(
        name = 'Prediabetes',
        pattern = 'Prediabetes iterative code',
        hash = hashlib.sha224('Prediabetes iterative code'),
        )[0]
    
    def handle(self, *args, **options):
        if not (options['generate'] or options['report']):
            raise CommandError('Must specify either --generate or --report')
        if options['generate']:
            self.generate_cases()
        if options['report']:
            self.report()
    
    def generate_cases(self, *args, **options):
        ALL_CRITERIA = [
            'lx--a1c--range--5.7-6.4',
            'lx--glucose_fasting--range--100.0-125.0',
            'lx--ogtt50_random--range--140.0-200.0',
            ]
        ONCE_CRITERIA = [
            'lx--a1c--range--5.7-6.4',
            'lx--glucose_fasting--range--100.0-125.0',
            ]
        qs = Event.objects.filter(event_type='lx--ogtt50_random--range--140.0-200.0').values('patient')
        qs = qs.exclude(patient__case__condition__in=self.DIABETES_CONDITIONS)
        qs = qs.annotate(count=Count('pk'))
        patient_pks = qs.filter(count__gte=2).values_list('patient', flat=True).distinct()
        patient_pks = set(patient_pks)
        patient_pks |= set( Event.objects.filter(event_type_id__in=ONCE_CRITERIA).values_list('patient', flat=True).distinct() )
        # Ignore patients who already have a prediabetes case
        patient_pks = patient_pks - set( Case.objects.filter(condition='prediabetes').values_list('patient', flat=True) )
        total = len(patient_pks)
        counter = 0
        for pat_pk in patient_pks:
            counter += 1
            event_qs = Event.objects.filter(
                patient = pat_pk,
                event_type_id__in = ALL_CRITERIA,
                ).order_by('date')
            trigger_event = event_qs[0]
            trigger_date = trigger_event.date
            prior_dm_case_qs = Case.objects.filter(
                patient = pat_pk,
                condition__startswith = 'diabetes_type_',
                date__lte = trigger_date,
                )
            if prior_dm_case_qs.count():
                continue # This patient already has diabetes, and as such does not have prediabetes
            new_case = Case(
                patient = trigger_event.patient,
                provider = trigger_event.provider,
                date = trigger_event.date,
                condition =  'prediabetes',
                pattern = self.PRE_DM_PATTERN,
                )
            new_case.save()
            new_case.events = event_qs
            new_case.save()
            log.info('Saved new case: %s (%8s / %s)' % (new_case, counter, total))
            
            
        
    def report(self, *args, **options):
        pass