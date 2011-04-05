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
from ESP.hef.models import Timespan
from ESP.hef.base import AbstractLabTest
from ESP.hef.base import 
from ESP.nodis.base import Condition


class Diabetes(Condition):
    
    help = 'Generate report on all GDM cases'
    
    option_list = BaseCommand.option_list + (
        make_option('--generate', action='store_true', dest='generate',  default=False,
            help='Generate cases of gestational diabetes'),
        make_option('--report', action='store_true', dest='report',  default=False,
            help='Produce gestational diabetes report'),
        make_option('--riskscape', action='store_true', dest='riskscape', default=False,
            help='Produce Riskscape GDM report'),
        )
    
    GDM_PATTERN = Pattern.objects.get_or_create(
        name = 'Gestational Diabetes',
        pattern = 'Gestational Diabetes iterative code',
        hash = hashlib.sha224('Gestational Diabetes iterative code'),
        )[0]
    
    # One of these events, during pregnancy, is sufficient for a case of GDM
    CRITERIA_ONCE = [
        'lx--ogtt100_fasting--threshold--126.0',
        'lx--ogtt50_fasting--threshold--126.0',
        'lx--ogtt75_fasting--threshold--126.0',
        'lx--ogtt50_1hr--threshold--190.0',
        'lx--ogtt50_random--threshold--190.0',
        'lx--ogtt75_fasting--threshold--92.0',
        'lx--ogtt75_30min--threshold--200.0',
        'lx--ogtt75_1hr--threshold--180.0',
        'lx--ogtt75_90min--threshold--180.0',
        'lx--ogtt75_2hr--threshold--153.0',
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
    
    
    LINELIST_FIELDS = [
        #
        # Per-patient fields
        #
        'patient_id',
        'mrn',
        'last_name',
        'first_name',
        'date_of_birth',
        'ethnicity',
        'zip_code',
        'bmi',
        'gdm_icd9--any_time',
        'frank_diabetes--ever',
        'frank_diabetes--date',
        'frank_diabetes--case_id',
        'lancets_test_strips--any_time',
        #
        # Per-pregnancy fields
        #
        'pregnancy_id',
        'pregnancy', # Boolean
        'preg_start',
        'preg_end',
        'edd',
        'gdm_case', # Boolean
        'gdm_case--date',
        'gdm_icd9--this_preg',
        'intrapartum--ogtt50--positive',
        'intrapartum--ogtt50--threshold',
        'intrapartum--ogtt75--positive',
        'intrapartum--ogtt100--positive',
        'postpartum--ogtt75--order',
        'postpartum--ogtt75--any_result',
        'postpartum--ogtt75--positive',
        'postpartum--ogtt75--dm_threshold',
        'postpartum--ogtt75--igt_range',
        'postpartum--ogtt75--ifg_range',
        'early_postpartum--a1c--order',
        'early_postpartum--a1c--max',
        'late_postpartum--a1c--max',
        'lancets_test_strips--this_preg',
        'lancets_test_strips--14_days_gdm_icd9',
        'insulin_rx',
        'metformin_rx',
        'glyburide_rx',
        'referral_to_nutrition',
        ]
    
    
    RISKSCAPE_FIELDS = [
        'A',
        'B',
        'C',
        'D',
        'E',
        'F',
        'G',
        'H',
        'I',
        'J',
        'K',
        'L',
        'M',
        'N',
        'O',
        'P',
        'Q',
        'R',
        'S',
        'T',
        'U',
        'V',
        'W',
        'X',
        'Y',
        'Z',
        ]
   
  
    def handle(self, *args, **options):
        if not (options['generate'] or options['report'] or options['riskscape']):
            raise CommandError('Must specify either --generate, --report, or --riskscape')
        if options['generate']:
            self.generate_cases()
        if options['report']:
            self.report()
        if options['riskscape']:
            self.report(riskscape=True)
    
    def generate_cases(self, *args, **options):
        log.info('Generating cases for diabetes_gestational')
        #===============================================================================
        #
        # Build set of GDM pregnancy timespans
        #
        #===============================================================================
        gdm_timespan_pks = set()
        ts_qs = Timespan.objects.filter(name='pregnancy')
        ts_qs = ts_qs.exclude(case__condition='diabetes_gestational')
        #
        # Single event
        #
        once_qs = ts_qs.filter(
            patient__event__event_type__in=self.CRITERIA_ONCE,
            patient__event__date__gte=F('start_date'),
            patient__event__date__lte=F('end_date'),
            ).distinct().order_by('end_date')
        log_query('Single event timespans', once_qs)
        gdm_timespan_pks.update(once_qs.values_list('pk', flat=True))
        #
        # 2 or more events
        #
        twice_qs = ts_qs.filter(
            patient__event__event_type__in=self.CRITERIA_TWICE,
            patient__event__date__gte=F('start_date'),
            patient__event__date__lte=F('end_date'),
            ).annotate(count=Count('patient__event__id')).filter(count__gte=2).distinct()
        log_query('Two event timespans', twice_qs)
        gdm_timespan_pks.update(twice_qs.values_list('pk', flat=True))
        #
        # Dx or Rx
        #
        dx_ets=['dx--gestational_diabetes']
        rx_ets=['rx--lancets', 'rx--test_strips']
        # FIXME: This date math works on PostgreSQL, but I think that's just 
        # fortunate coincidence, as I don't think this is the righ way to 
        # express the date query in ORM syntax.
        _event_qs = Event.objects.filter(
            event_type__in=rx_ets,
            patient__event__event_type__in=dx_ets, 
            patient__event__date__gte = (F('date') - 14 ),
            patient__event__date__lte = (F('date') + 14 ),
            )
        dxrx_qs = ts_qs.filter(
            patient__event__in = _event_qs,
            patient__event__date__gte = F('start_date'),
            patient__event__date__lte = F('end_date'),
            )
        log_query('Dx or Rx', dxrx_qs)
        gdm_timespan_pks.update(dxrx_qs.values_list('pk', flat=True))
        #===============================================================================
        #
        # Generate one case per timespan
        #
        #===============================================================================
        all_criteria = self.CRITERIA_ONCE + self.CRITERIA_TWICE + dx_ets + rx_ets
        counter = 0
        total = len(gdm_timespan_pks)
        for ts_pk in gdm_timespan_pks:
            ts = Timespan.objects.get(pk=ts_pk)
            case_events = Event.objects.filter(
                patient = ts.patient,
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
                case_obj.events = case_events
                counter += 1
                log.info('Saved new case: %s (%8s / %s)' % (case_obj, counter, total))
            else:
                log.debug('Found exisiting GDM case #%s for %s' % (case_obj.pk, ts))
                log.debug('Timespan & events will be added to existing case')
                case_obj.events = case_obj.events.all() | case_events
            log_query('case events', case_events)
            case_obj.timespans.add(ts)
            case_obj.save()
        log.info('Generated %s new cases of diabetes_gestational' % counter)
        return counter
        
    def report(self, riskscape=False):
        log.info('Generating GDM report')
        if riskscape:
            fields = self.RISKSCAPE_FIELDS
        else:
            fields = self.LINELIST_FIELDS
        writer = csv.DictWriter(sys.stdout, fieldnames=fields, quoting=csv.QUOTE_ALL)
        pos_q = Q(event_type__name__endswith='--positive')
        a1c_q = Q(event_type__name__startswith='lx--a1c')
        ogtt50_q = Q(event_type__name__startswith='lx--ogtt50')
        ogtt50_threshold_q = Q(event_type__name__in = [
            'lx--ogtt50_1hr--threshold--190.0',
            'lx--ogtt50_random--threshold--190.0',
            ])
        ogtt75_q = Q(event_type__name__startswith='lx--ogtt75')
        ogtt75_threshold_q = Q(event_type__name__in = [
            'lx--ogtt75_1hr--threshold--180.0',
            'lx--ogtt75_1hr--threshold--200.0',
            'lx--ogtt75_2hr--threshold--155.0',
            'lx--ogtt75_2hr--threshold--200.0',
            'lx--ogtt75_30min--threshold--200.0',
            'lx--ogtt75_90min--threshold--180.0',
            'lx--ogtt75_90min--threshold--200.0',
            'lx--ogtt75_fasting--threshold--126.0',
            'lx--ogtt75_fasting--threshold--95.0',
            ])
        ogtt75_igt_q = Q(event_type__name__in = [
            'lx--ogtt75_1hr--range--140.0-200.0',
            'lx--ogtt75_2hr--range--140.0-200.0',
            'lx--ogtt75_30min--range--140.0-200.0',
            'lx--ogtt75_90min--range--140.0-200.0',
            ])
        ogtt75_ifg_q = Q(event_type__name = 'lx--ogtt75_fasting--range--100.0-125.0')
        ogtt100_q = Q(event_type__name__startswith='lx--ogtt100')
        ogtt100_threshold_q = Q(event_type__name__in = [
            ])
        order_q = Q(event_type__name__endswith='--order')
        any_q = Q(event_type__name__endswith='--any_result')
        dxgdm_q = Q(event_type='dx--gestational_diabetes')
        lancets_q = Q(event_type__in=['rx--test_strips', 'rx--lancets'])
        #
        # Header
        #
        header = dict(zip(fields, fields))
        writer.writerow(header)
        #
        # Report on all patients with GDM ICD9 or a pregnancy
        #
        #patient_qs = Patient.objects.filter(event__event_type='dx--gestational_diabetes')
        #patient_qs |= Patient.objects.filter(timespan__name='pregnancy')
        #patient_qs = patient_qs.distinct()
        #log_query('patient_qs', patient_qs)
        patient_pks = set()
        patient_pks.update( Event.objects.filter(event_type='dx--gestational_diabetes').values_list('patient', flat=True) )
        patient_pks.update( Timespan.objects.filter(name='pregnancy').values_list('patient', flat=True))
        counter = 0
        #total = patient_qs.count()
        total = len(patient_pks)
        for ppk in patient_pks:
            counter += 1
            log.info('Reporting on patient %8s / %s' % (counter, total))
            patient = Patient.objects.get(pk=ppk)
            event_qs = Event.objects.filter(patient=patient)
            preg_ts_qs = Timespan.objects.filter(name='pregnancy', patient=patient)
            gdm_case_qs = Case.objects.filter(condition='diabetes_gestational', patient=patient)
            frank_dm_case_qs = Case.objects.filter(condition__startswith='diabetes_type_', patient=patient).order_by('date')
            a1c_lab_qs = AbstractLabTest.objects.get(name='a1c').lab_results.filter(patient=patient).filter(patient=patient)
            #
            # Populate values that will be used all of this patient's pregnancies
            #
            try:
                zip_code = '%05d' % int( patient.zip[0:5] )
            except:
                log.warning('Could not convert zip code: %s' % patient.zip)
            if riskscape:
                # Age
                if patient.age:
                    years = patient.age.years
                    if years < 20:
                        age = 1
                    elif 20 <= years < 25:
                        age = 2
                    elif 25 <= years < 30:
                        age = 3
                    elif 30 <= years < 35:
                        age = 4
                    elif 35 <= years < 40:
                        age = 5
                    else:
                        age = 6
                else:
                    age = None
                # Race
                if patient.race:
                    race_string = patient.race.lower()
                else:
                    race_string = None
                if race_string == 'caucasian':
                    race = 1
                elif race_string == 'asian':
                    race = 2
                elif race_string == 'black':
                    race = 3
                elif race_string == 'hispanic':
                    race = 4
                elif race_string == 'other':
                    race = 5
                else:
                    race = 6
                patient_values = {
                    'A': patient.pk,
                    'B': age,
                    'C': race,
                    'D': zip_code,
                    }
            else:
                patient_values = {
                    'patient_id': patient.pk,
                    'mrn': patient.mrn,
                    'last_name': patient.last_name,
                    'first_name': patient.first_name,
                    'date_of_birth': patient.date_of_birth,
                    'ethnicity': patient.race,
                    'zip_code': zip_code,
                    'gdm_icd9--any_time': bool(event_qs.filter(dxgdm_q)),
                    'frank_diabetes--ever': bool(frank_dm_case_qs),
                    'lancets_test_strips--any_time': bool(event_qs.filter(lancets_q)),
                    }
            if frank_dm_case_qs and not riskscape:
                first_dm_case = frank_dm_case_qs[0]
                patient_values['frank_diabetes--date'] = first_dm_case.date
                patient_values['frank_diabetes--case_id'] = first_dm_case.pk
            #
            # Generate a row for each pregnancy (or 1 row if no pregs found)
            #
            if not preg_ts_qs:
                if not riskscape:
                    patient_values['pregnancy'] = False
                writer.writerow(patient_values)
                continue
            for preg_ts in preg_ts_qs:
                #
                # Find BMI closes to onset of pregnancy
                #
                bmi_qs = Encounter.objects.filter(
                    patient = patient,
                    bmi__isnull=False,
                    )
                preg_bmi_qs = bmi_qs.filter(
                    date__gte = preg_ts.start_date,
                    date__lte = preg_ts.start_date + relativedelta(months=4),
                    ).order_by('date')
                pre_preg_bmi_qs = bmi_qs.filter(
                    date__gte = preg_ts.start_date - relativedelta(years=1),
                    date__lte = preg_ts.start_date,
                    ).order_by('-date')
                if preg_bmi_qs:
                    bmi = preg_bmi_qs[0].bmi
                elif pre_preg_bmi_qs:
                    bmi = pre_preg_bmi_qs[0].bmi
                else:
                    bmi = None
                #
                # Patient's frank and gestational DM history
                #
                gdm_this_preg = gdm_case_qs.filter(
                    date__gte = preg_ts.start_date,
                    date__lte = preg_ts.end_date,
                    ).order_by('date')
                gdm_prior = gdm_case_qs.filter(date__lt=preg_ts.start_date)
                frank_dm_early_preg = frank_dm_case_qs.filter(
                    date__gte = preg_ts.start_date,
                    date__lte = preg_ts.end_date - relativedelta(weeks=24),
                    )
                frank_dm_late_preg = frank_dm_case_qs.filter(
                    date__gte = preg_ts.end_date - relativedelta(weeks=24),
                    date__lte = preg_ts.end_date,
                    )
                #
                # Events by time period
                #
                intrapartum = event_qs.filter(
                    date__gte = preg_ts.start_date,
                    date__lte = preg_ts.end_date,
                    )
                postpartum = event_qs.filter(
                    date__gt = preg_ts.end_date,
                    date__lte = preg_ts.end_date + relativedelta(days=120),
                    )
                early_pp = event_qs.filter(
                    date__gt = preg_ts.end_date,
                    date__lte = preg_ts.end_date + relativedelta(weeks=12),
                    )
                early_pp_q = Q(
                    date__gt = preg_ts.end_date,
                    date__lte = preg_ts.end_date + relativedelta(weeks=12),
                    )
                late_pp_q = Q(
                    date__gt = preg_ts.end_date + relativedelta(weeks=12),
                    date__lte = preg_ts.end_date + relativedelta(days=365),
                    )
                # FIXME: This date math works on PostgreSQL, but I think that's
                # just fortunate coincidence, as I don't think this is the
                # right way to express the date query in ORM syntax.
                lancets_and_icd9 = intrapartum.filter(
                    lancets_q,
                    patient__event__event_type='dx--gestational_diabetes',
                    patient__event__date__gte =  (F('date') - 14),
                    patient__event__date__lte =  (F('date') + 14),
                    )
                nutrition_referral = Encounter.objects.filter(
                    patient=patient,
                    date__gte=preg_ts.start_date, 
                    date__lte=preg_ts.end_date, 
                    ).filter(
                        Q(provider__title__icontains='RD') | Q(site_name__icontains='Nutrition')
                        )
                if preg_ts.pattern == 'EDD':
                    edd = preg_ts.end_date
                else:
                    edd = 'No EDD'
                if gdm_this_preg:
                    gdm_date = gdm_this_preg[0].date
                else:
                    gdm_date = None
                early_a1c_max = a1c_lab_qs.filter(early_pp_q).aggregate(max=Max('result_float'))['max'],
                late_a1c_max = a1c_lab_qs.filter(late_pp_q).aggregate(max=Max('result_float'))['max'],
                if riskscape:
                    bmi_value = None
                    if bmi < 25:
                        bmi_value = 1
                    elif 25 <= bmi <= 30:
                        bmi_value = 2
                    elif bmi > 30:
                        bmi_value = 3
                    values = {
                        'E': preg_ts.start_date.year,
                        'F': bmi_value,
                        'G': int( bool( gdm_this_preg ) ),
                        'H': int( bool( gdm_prior ) ),
                        'I': int( bool( frank_dm_early_preg ) ),
                        'J': int( bool( frank_dm_late_preg ) ),
                        'K': int( bool( intrapartum.filter(ogtt50_q, pos_q) ) ),
                        'L': int( bool( intrapartum.filter(ogtt50_threshold_q) ) ),
                        'M': int( bool( intrapartum.filter(ogtt75_q, pos_q) ) ),
                        'N': int( bool( intrapartum.filter(ogtt100_q, pos_q) ) ),
                        'O': int( bool( postpartum.filter(ogtt75_q, order_q) ) ),
                        'P': int( bool( intrapartum.filter(event_type='rx--insulin') ) ),
                        'Q': int( bool( intrapartum.filter(event_type='rx--metformin') ) ),
                        'R': int( bool( intrapartum.filter(event_type='rx--glyburide_rx') ) ),
                        'S': int( bool( nutrition_referral ) ),
                        'T': int( bool( postpartum.filter(ogtt75_q, any_q) ) ),
                        'U': int( bool( postpartum.filter(ogtt75_ifg_q) ) ),
                        'V': int( bool( postpartum.filter(ogtt75_igt_q) ) ),
                        'W': int( bool( postpartum.filter(ogtt75_ifg_q) | postpartum.filter(ogtt75_igt_q) ) ),
                        'X': int( bool( postpartum.filter(ogtt75_threshold_q) ) ),
                        'Y': int( early_a1c_max >= 6.5 ),
                        'Z': int( late_a1c_max >= 6.5 ),
                        }
                else:
                    values = {
                        'pregnancy_id': preg_ts.pk,
                        'pregnancy': True,
                        'preg_start': preg_ts.start_date,
                        'preg_end': preg_ts.end_date,
                        'edd': edd,
                        'bmi': bmi,
                        'gdm_case': bool( gdm_this_preg ),
                        'gdm_case--date': gdm_date,
                        'gdm_icd9--this_preg': bool( intrapartum.filter(dxgdm_q) ),
                        'intrapartum--ogtt50--positive': bool( intrapartum.filter(ogtt50_q, pos_q) ),
                        'intrapartum--ogtt50--threshold': bool( intrapartum.filter(ogtt50_threshold_q) ),
                        'postpartum--ogtt75--order': bool( postpartum.filter(ogtt75_q, order_q) ),
                        'postpartum--ogtt75--any_result': bool( postpartum.filter(ogtt75_q, any_q) ),
                        'postpartum--ogtt75--positive': bool( postpartum.filter(ogtt75_q, pos_q) ),
                        'postpartum--ogtt75--dm_threshold': bool( postpartum.filter(ogtt75_threshold_q) ),
                        'postpartum--ogtt75--igt_range': bool( postpartum.filter(ogtt75_igt_q) ),
                        'postpartum--ogtt75--ifg_range': bool( postpartum.filter(ogtt75_ifg_q) ),
                        'intrapartum--ogtt100--positive': bool( intrapartum.filter(ogtt100_q, pos_q) ),
                        'early_postpartum--a1c--order': bool( early_pp.filter(a1c_q, order_q) ),
                        'early_postpartum--a1c--max': early_a1c_max,
                        'late_postpartum--a1c--max': late_a1c_max,
                        'lancets_test_strips--this_preg': bool( intrapartum.filter(lancets_q) ),
                        'lancets_test_strips--14_days_gdm_icd9': bool( lancets_and_icd9 ),
                        'insulin_rx': bool( intrapartum.filter(event_type='rx--insulin') ),
                        'metformin_rx': bool( intrapartum.filter(event_type='rx--metformin') ),
                        'glyburide_rx': bool( intrapartum.filter(event_type='rx--glyburide') ),
                        'referral_to_nutrition': bool(nutrition_referral),
                        }
                values.update(patient_values)
                writer.writerow(values)




def get_heuristics():
    return [
        
        ]