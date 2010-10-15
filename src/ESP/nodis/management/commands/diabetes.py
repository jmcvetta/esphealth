'''
                                  ESP Health
Diabetes Case Generator Hack


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2010 Channing Laboratory
@license: LGPL
'''


import hashlib
import sys
import pprint
from dateutil.relativedelta import relativedelta

from django.db.models import Q
from django.db.models import F
from django.db.models import Sum
from django.db.models import Count
from django.db.models import Max
from django.db.models import Min
from django.core.management.base import BaseCommand
from optparse import make_option

from ESP.utils import log
from ESP.utils import log_query
from ESP.emr.models import Patient
from ESP.hef.models import Event
from ESP.nodis.models import Pattern
from ESP.nodis.models import Case



class Command(BaseCommand):
    
    help = 'Generate frank diabetes type 1 and 2 data'
    
    pattern_type_1 = Pattern.objects.get_or_create(
        name = 'Frank DM Type 1 iterative code',
        pattern = 'Frank DM Type 1 iterative code',
        hash = hashlib.sha224('Frank DM Type 1 iterative code').hexdigest(),
        )[0]
    
    pattern_type_2 = Pattern.objects.get_or_create(
        name = 'Frank DM Type 2 iterative code',
        pattern = 'Frank DM Type 2 iterative code',
        hash = hashlib.sha224('Frank DM Type 2 iterative code').hexdigest(),
        )[0]
    
    def handle(self, *args, **options):
        log.info('Looking for cases of frank diabetes type 1 and 2.')
        # If a patient has one of these events, he has frank diabetes
        frank_dm_once_reqs = [
	        'lx--a1c--threshold--6.5',
	        'lx--glucose_fasting--threshold--126.0',
	        'rx--insulin',
	        'rx--diabetes',
            ]
        # If a patient has two or more of these events, he has frank diabetes
        frank_dm_twice_reqs = [
	        'dx--diabetes_all_types',
	        # FIXME: Not yet implemented:  "Random glucoses (RG) >=200 on two or more occasions"
            ]
        # Condition names for diabetes of both types
        diabetes_conditions = ['diabetes_type_1', 'diabetes_type_2']
        #
        # Find trigger dates for patients who have frank DM of either type, but no existing case
        # 
        qs = Event.objects.filter(event_type__in=frank_dm_once_reqs).values('patient').annotate(trigger_date=Max('date'))
        qs = qs.exclude(patient__case__condition__in=diabetes_conditions)
        log_query('Frank DM once', qs)
        patient_trigger_dates = {}
        for i in qs:
            pat = i['patient']
            td = i['trigger_date']
            patient_trigger_dates[pat] = td
        for event_type in frank_dm_twice_reqs:
            qs = Event.objects.filter(event_type=event_type).values('patient').annotate(count=Count('pk'))
            qs = qs.exclude(patient__case__condition__in=diabetes_conditions)
            patient_pks = qs.filter(count__gte=2).values_list('patient', flat=True).distinct()
            log_query('Patient PKs for %s' % event_type, patient_pks)
            for ppk in patient_pks:
                # Date of second event
                trigger_date = Event.objects.filter(event_type=event_type, patient=ppk).order_by('date')[1].date
                if (ppk not in patient_trigger_dates) or (patient_trigger_dates[ppk] > trigger_date):
                    patient_trigger_dates[ppk] = trigger_date
        #
        # Determine type 1 / type 2
        #
        total_count = len(patient_trigger_dates)
        counter = 0
        type_1_counter = 0
        type_2_counter = 0
        neither_counter = 0
        for pat_pk in patient_trigger_dates:
            counter += 1
            trigger_date = patient_trigger_dates[pat_pk]
            if self.check_type_1(pat_pk, trigger_date) == True:
                type_1_counter += 1
            # elif because we don't need to check type 2 if patient has type 1
            elif self.check_type_2(pat_pk, trigger_date):
                type_2_counter += 1
            else:
                neither_counter += 1
            log.debug('Checking patient %8s / %s' % (counter, total_count))
        print '*' * 80
        print 'Created %8s new cases of type 1 diabetes' % type_1_counter
        print 'Created %8s new cases of type 2 diabetes' % type_2_counter
        print 'There were %8s patients who matched general frank diabetes criteria, but not criteria for type 1 or 2' % neither_counter
        print '*' * 80
            
    def check_type_1(self, patient_pk, trigger_date):
            type_1_dxs = Event.objects.filter(patient=patient_pk, event_type='dx--diabetes_type_1', date__lte=trigger_date)
            if not type_1_dxs.count() >= 2:
                return False # No type 1 diabetes
            begin = trigger_date - relativedelta(days=365)
            end = trigger_date + relativedelta(days=365)
            insulin_rxs = Event.objects.filter(patient=patient_pk, event_type='rx--insuline', date__gte=begin, date__lte=end)
            if not insulin_rxs:
                return False # No type 1 diabetes
            case_date = type_1_dxs.order_by('date')[1].date # dx--diabetes_type_1 is the most specific criterion for type 1, so use it for case date
            provider = type_1_dxs.order_by('date')[1].provider
            patient = Patient.objects.get(pk=patient_pk)
            new_case = Case(
                patient = patient,
                provider = provider,
                date = case_date,
                condition = 'diabetes_type_1',
                pattern = self.pattern_type_1,
                )
            new_case.save()
            new_case.events = type_1_dxs | insulin_rxs
            new_case.save()
            log.info('Created new frank diabetes type 1 case: %s' % new_case)
            return True # Patient does have type 1
    
    def check_type_2(self, patient_pk, trigger_date):
        has_type_2 = False
        case_date = None
        type_2_dxs = Event.objects.filter(patient=patient_pk, event_type='dx--diabetes_type_2', date__lte=trigger_date)
        if type_2_dxs.count() >= 2:
            has_type_2 = True
            case_date = type_2_dxs.order_by('date')[1].date
            provider = type_2_dxs.order_by('date')[1].provider
        rxs = Event.objects.filter(patient=patient_pk, event_type='rx--diabetes', date__lte=trigger_date)
        if rxs:
            has_type_2 = True
            rx_date = rxs.order_by('date')[0].date
            if (not case_date) or (case_date > rx_date):
                provider = rxs.order_by('date')[0].provider
                case_date = rx_date
        if has_type_2:
            patient = Patient.objects.get(pk=patient_pk)
            new_case = Case(
                patient = patient,
                provider = provider,
                date = case_date,
                condition = 'diabetes_type_2',
                pattern = self.pattern_type_2,
                )
            new_case.save()
            new_case.events = type_2_dxs | rxs
            new_case.save()
            log.info('Created new frank diabetes type 2 case: %s' % new_case)
            return True # Patient does have type 2
        else:
            return False # No type 2 diabetes for this patient
