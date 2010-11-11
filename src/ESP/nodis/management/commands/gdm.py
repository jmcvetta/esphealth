'''
                                  ESP Health
                         Notifiable Diseases Framework
                      Gestational Diabetes Case Generator


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
    
    option_list = BaseCommand.option_list + (
        make_option('--generate', action='store_true', dest='generate',  default=False,
            help='Generate cases of gestational diabetes'),
        make_option('--report', action='store_true', dest='report',  default=False,
            help='Produce gestational diabetes report'),
        )
    
    GDM_PATTERN = Pattern.objects.get_or_create(
        name = 'Gestational Diabetes',
        pattern = 'Gestational Diabetes iterative code',
        hash = hashlib.sha224('Gestational Diabetes iterative code'),
        )[0]
    
    def handle(self, *args, **options):
        if not (options['generate'] or options['report']):
            raise CommandError('Must specify either --generate or --report')
        if options['generate']:
            self.generate_cases()
        if options['report']:
            self.report()
    
    def generate_cases(self, *args, **options):
        # One of these events, during pregnancy, is sufficient for a case of GDM
        CRITERIA_ONCE = [
            'lx--glucose_fasting--threshold--126.0',
            'lx--ogtt50_1hr--threshold--190.0'
            ]
        # Two or more occurrences of these events, during pregnancy, is sufficient for a case of GDM
        CRITERIA_TWICE = [
            'lx--ogtt75_fasting--threshold--95.0',
            'lx--ogtt75_30min--threshold--200.0',
            'lx--ogtt75_1hr--threshold--180.0',
            'lx--ogtt75_90min--threshold--180.0',
            'lx--ogtt75_2hr--threshold--155.0',
            'lx--ogtt100_fasting_urine--positive',
            'lx--ogtt100_fasting--threshold--95.0',
            'lx--ogtt100_30min--threshold--200.0',
            'lx--ogtt100_1hr--threshold--180.0',
            'lx--ogtt100_90min--threshold--180.0',
            'lx--ogtt100_2hr--threshold--155.0',
            'lx--ogtt100_3hr--threshold--140.0',
            ]
        #
        # Build set of GDM pregnancy timespans
        #
        gdm_timespan_pks = set()
        ts_qs = Timespan.objects.filter(name='pregnancy')
        ts_qs = ts_qs.exclude(case__condition='diabetes_gestational')
        once_qs = ts_qs.filter(
            patient__event__event_type__in=CRITERIA_ONCE,
            patient__event__date__gte=F('start_date'),
            patient__event__date__lte=F('end_date'),
            ).distinct().order_by('end_date')
        log_query('Single event timespans', once_qs)
        twice_qs = ts_qs.filter(
            patient__event__event_type__in=CRITERIA_TWICE,
            patient__event__date__gte=F('start_date'),
            patient__event__date__lte=F('end_date'),
            ).annotate(count=Count('patient__event__id')).filter(count__gte=2).distinct()
        log_query('Single event timespans', once_qs)
        log_query('Two event timespans', twice_qs)
        gdm_timespan_pks.update(once_qs.values_list('pk', flat=True))
        gdm_timespan_pks.update(twice_qs.values_list('pk', flat=True))
        #
        # Generate one case per timespan
        #
        all_criteria = CRITERIA_ONCE + CRITERIA_TWICE
        counter = 0
        for ts_pk in gdm_timespan_pks:
            ts = Timespan.objects.get(pk=ts_pk)
            case_events = Event.objects.filter(
                event_type__in=all_criteria,
                date__gte=ts.start_date, 
                date__lte=ts.end_date
                ).order_by('date')
            first_event = case_events[0]
            case_obj, created = Case.objects.get_or_create(
                patient = ts.patient,
                condition = 'diabetes_gestational',
                date = first_event.date,
                defaults = {
                    'provider': first_event.provider,
                    'pattern': self.GDM_PATTERN,
                    },
                )
            if created:
                case_obj.save()
                counter += 1
                log.info('Saved new case: %s' % case_obj)
            else:
                log.error('Found exisiting GDM case #%s for timespan #%s - this should not happen' % (case_obj.pk, ts.pk))
                log.debug('Timespan & events will be added to existing case')
            case_obj.events = case_obj.events.all() | case_events
            case_obj.timespans.add(ts)
            case_obj.save()
        log.info('Generated %s new cases of diabetes_gestational' % counter)
        return counter
        
    def report(self, *args, **options):
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
                postpartum_events = Event.objects.filter(patient=patient, date__gte=preg_end, 
                    date__lte=preg_end+relativedelta(weeks=12))
                postpartum_order_events = Event.objects.filter(patient=patient, date__gte=preg_end-relativedelta(days=60), 
                    date__lte=preg_end+relativedelta(weeks=12))
                ogtt75_postpartum_order = bool( postpartum_order_events.filter(event_type='ogtt75_series--order') )
                ogtt75_postpartum_result = bool( postpartum_events.filter(event_type__in=OGTT75_RESULT_EVENTS)  )
                ogtt75_postpartum_pos = bool( postpartum_events.filter(event_type__in=OGTT75_POSTPARTUM_EVENTS) )
                a1c_postpartum_order = bool( postpartum_order_events.filter(event_type='a1c--order') )
                a1c_tests = LabResult.objects.filter(patient=patient, date__gt=preg_end, 
                    date__lte=preg_end+relativedelta(weeks=12),  native_code__in=a1c_native_codes)
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
            previous_lancet_rx = lancets.filter(date__lte=preg_start, date__gte=preg_start-relativedelta(days=365))
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
    
