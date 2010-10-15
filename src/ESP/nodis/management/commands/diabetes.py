'''
                                  ESP Health
Diabetes Case Generator Hack


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2010 Channing Laboratory
@license: LGPL
'''


import hashlib
import csv
from dateutil.relativedelta import relativedelta

from django.db.models import Q
from django.db.models import F
from django.db.models import Sum
from django.db.models import Count
from django.db.models import Max
from django.db.models import Min
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from optparse import make_option

from ESP.utils import log
from ESP.utils import log_query
from ESP.emr.models import Patient
from ESP.hef.models import Event
from ESP.nodis.models import Pattern
from ESP.nodis.models import Case



class Command(BaseCommand):
    
    help = 'Generate frank diabetes type 1 and 2 data'
    
    option_list = BaseCommand.option_list + (
        make_option('--generate', action='store_true', dest='generate',  default=False,
            help='Generate cases of diabetes'),
        make_option('--linelist', action='store_true', dest='linelist',  default=False,
            help='Produce diabetes patient line list report'),
        )
    
    # Condition names for diabetes of both types
    diabetes_conditions = ['diabetes_type_1', 'diabetes_type_2', 'diabetes_unknown_type']
    
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
    
    pattern_type_unknown = Pattern.objects.get_or_create(
        name = 'Frank DM Unknown Type iterative code',
        pattern = 'Frank DM Unknown Type iterative code',
        hash = hashlib.sha224('Frank DM Unknown Type iterative code').hexdigest(),
        )[0]
    
    def handle(self, *args, **options):
        if not (options['generate'] or options['linelist']):
            raise CommandError('Must specify either --generate or --linelist')
        if options['generate']:
            self.generate()
        if options['linelist']:
            self.linelist()
    
    def generate(self):
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
        #
        # Find trigger dates for patients who have frank DM of either type, but no existing case
        # 
        qs = Event.objects.filter(event_type__in=frank_dm_once_reqs).values('patient').annotate(trigger_date=Max('date'))
        qs = qs.exclude(patient__case__condition__in=self.diabetes_conditions)
        log_query('Frank DM once', qs)
        patient_trigger_dates = {}
        for i in qs:
            pat = i['patient']
            td = i['trigger_date']
            patient_trigger_dates[pat] = td
        for event_type in frank_dm_twice_reqs:
            qs = Event.objects.filter(event_type=event_type).values('patient').annotate(count=Count('pk'))
            qs = qs.exclude(patient__case__condition__in=self.diabetes_conditions)
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
        unknown_counter = 0
        for pat_pk in patient_trigger_dates:
            counter += 1
            trigger_date = patient_trigger_dates[pat_pk]
            if self.check_type_1(pat_pk, trigger_date) == True:
                type_1_counter += 1
            # elif because we don't need to check type 2 if patient has type 1
            elif self.check_type_2(pat_pk, trigger_date):
                type_2_counter += 1
            else:
                patient = Patient.objects.get(pk=pat_pk)
                all_event_types = frank_dm_twice_reqs + frank_dm_once_reqs
                provider = Event.objects.filter(patient=patient, event_type__in=all_event_types, date=trigger_date)[0].provider
                new_case = Case(
                    patient = patient,
                    provider = provider,
                    date = trigger_date,
                    condition = 'diabetes_unknown_type',
                    pattern = self.pattern_type_unknown,
                    )
                new_case.save()
                unknown_counter += 1
            log.debug('Checking patient %8s / %s' % (counter, total_count))
        log.info('%8s new cases of type 1 diabetes' % type_1_counter)
        log.info('%8s new cases of type 2 diabetes' % type_2_counter)
        log.info('%8s patients who matched general frank diabetes criteria, but not criteria for type 1 or 2' % unknown_counter)
            
    def check_type_1(self, patient_pk, trigger_date):
            type_1_dxs = Event.objects.filter(patient=patient_pk, event_type='dx--diabetes_type_1', date__lte=trigger_date)
            #type_1_dxs = Event.objects.filter(patient=patient_pk, event_type='dx--diabetes_type_1')
            if not type_1_dxs.count() >= 2:
                return False # No type 1 diabetes
            begin = trigger_date - relativedelta(days=365)
            end = trigger_date + relativedelta(days=365)
            insulin_rxs = Event.objects.filter(patient=patient_pk, event_type='rx--insulin', date__gte=begin, date__lte=end)
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
    
    def linelist(self):
        FIELDS = [
            'patient_id', 
            'mrn', 
            'dob', 
            'sex', 
            'race', 
            'bmi', 
            'zip', 
            'diabetes_type', 
            'max_a1c_value', 
            'max_a1c_date',
            'max_fasting_glucose_value',
            'max_fasting_glucose_date',
            'high_rand_glucose_1_value',
            'high_rand_glucose_1_date',
            'high_rand_glucose_2_value',
            'high_rand_glucose_2_date',
            'recent_icd9_250.x0_1_value',
            'recent_icd9_250.x0_1_text',
            'recent_icd9_250.x0_1_date',
            'recent_icd9_250.x0_2_value',
            'recent_icd9_250.x0_2_text',
            'recent_icd9_250.x0_2_date',
            'recent_icd9_250.x2_1_value',
            'recent_icd9_250.x2_1_text',
            'recent_icd9_250.x2_1_date',
            'recent_icd9_250.x2_2_value',
            'recent_icd9_250.x2_2_text',
            'recent_icd9_250.x2_2_date',
            'recent_icd9_250.x1_1_value',
            'recent_icd9_250.x1_1_text',
            'recent_icd9_250.x1_1_date',
            'recent_icd9_250.x1_2_value',
            'recent_icd9_250.x1_2_text',
            'recent_icd9_250.x1_2_date',
            'recent_icd9_250.x3_1_value',
            'recent_icd9_250.x3_1_text',
            'recent_icd9_250.x3_1_date',
            'recent_icd9_250.x3_2_value',
            'recent_icd9_250.x3_2_text',
            'recent_icd9_250.x3_2_date',
            'recent_icd9_648.8_value',
            'recent_icd9_648.8_text',
            'recent_icd9_648.8_date',
            'recent_insulin_date',
            'recent_insulin_drug',
            'recent_metformin_date',
            'recent_metformin_drug',
            'recent_acarbose_date',
            'recent_acarbose_drug',
            'recent_repaglinide_date',
            'recent_repaglinide_drug',
            'recent_nateglinide_date',
            'recent_nateglinide_drug',
            'recent_meglitinide_date',
            'recent_meglitinide_drug',
            'recent_miglitol_date',
            'recent_miglitol_drug',
            ]
        writer = csv.DictWriter(fields=FIELDS)
        for c in Case.objects.filter(condition__in=self.diabetes_conditions).order_by('date'):
            pass