'''
                                  ESP Health
                         Notifiable Diseases Framework
                         Frank Diabetes Case Generator


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@contact: http://www.esphealth.org
@copyright: (c) 2010 Channing Laboratory
@license: LGPL
'''


import sys
import csv
import hashlib
import datetime
import pprint
from dateutil.relativedelta import relativedelta

from django.db.models import Q
from django.db.models import F
from django.db.models import Sum
from django.db.models import Count
from django.db.models import Max
from django.db.models import Min
from django.db.models import Avg
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.utils.encoding import smart_str, smart_unicode
from optparse import make_option

from esp.utils import log
from esp.utils import log_query
from esp.emr.models import Patient
from esp.emr.models import Encounter
from esp.emr.models import Prescription
from esp.emr.models import LabResult
from esp.hef.models import Event
from esp.hef.models import EventType
from esp.hef.models import AbstractLabTest
from esp.hef.models import Timespan
from esp.nodis.models import Pattern
from esp.nodis.models import Case



FIRST_YEAR = 2006


class Command(BaseCommand):
    
    help = 'Generate frank diabetes type 1 and 2 data'
    
    option_list = BaseCommand.option_list + (
        make_option('--generate', action='store_true', dest='generate',  default=False,
            help='Generate cases of diabetes'),
        make_option('--linelist', action='store_true', dest='linelist',  default=False,
            help='Produce diabetes patient line list report'),
        )
    
    # Condition names for diabetes of both types
    DIABETES_CONDITIONS = ['diabetes_type_1', 'diabetes_type_2', 'diabetes_unknown_type']
    
    ORAL_HYPOGLYCAEMICS = [
        'rx--pramlintide',
        'rx--exenatide',
        'rx--sitagliptin',
        'rx--meglitinide',
        'rx--nateglinide',
        'rx--repaglinide',
        'rx--glimepiride',
        'rx--glipizide',
        'rx--gliclazide',
        'rx--glyburide',
        'rx--metformin',
        'rx--rosiglitizone',
        'rx--pioglitazone',
        ]
    
    AUTO_ANTIBODIES_LABS = [
        'lx--ica512',
        'lx--gad65',
        'lx--islet_cell_antibody',
        ]
    
    PATTERN_TYPE_1 = Pattern.objects.get_or_create(
        name = 'Frank DM Type 1 iterative code',
        pattern = 'Frank DM Type 1 iterative code',
        hash = hashlib.sha224('Frank DM Type 1 iterative code').hexdigest(),
        )[0]
    
    PATTERN_TYPE_2 = Pattern.objects.get_or_create(
        name = 'Frank DM Type 2 iterative code',
        pattern = 'Frank DM Type 2 iterative code',
        hash = hashlib.sha224('Frank DM Type 2 iterative code').hexdigest(),
        )[0]
    
    PATTERN_TYPE_UNKNOWN = Pattern.objects.get_or_create(
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
            ] + self.ORAL_HYPOGLYCAEMICS
        # If a patient has two or more of these events, he has frank diabetes
        frank_dm_twice_reqs = [
            'dx--diabetes_all_types',
            # FIXME: Not yet implemented:  "Random glucoses (RG) >=200 on two or more occasions"
            ]
        #
        # Find trigger dates for patients who have frank DM of either type, but no existing case
        # 
        frank_dm = {}
        # Insulin once is a trigger, but only if not during pregnancy
        insulin_events = Event.objects.filter(
            event_type='rx--insulin',
            patient__timespan__name='pregnancy',
            patient__timespan__start_date__lte = F('date'),
            patient__timespan__end_date__gte = F('date'),
            patient__timespan__pk__isnull=True,
            )
        qs = Event.objects.filter(event_type__in=frank_dm_once_reqs)
        qs |= insulin_events
        qs = qs.exclude(patient__case__condition__in=self.DIABETES_CONDITIONS)
        log_query('Frank DM once', qs)
        for i in qs.values('patient').annotate(trigger_date=Min('date')):
            pat = i['patient']
            trigger_date = i['trigger_date']
            events = qs.filter(patient=pat, date=trigger_date)
            date_events = (trigger_date, events)
            frank_dm[pat] = date_events
        for event_type in frank_dm_twice_reqs:
            qs = Event.objects.filter(event_type=event_type).values('patient')
            qs = qs.exclude(patient__case__condition__in=self.DIABETES_CONDITIONS)
            qs = qs.annotate(count=Count('pk'))
            patient_pks = qs.filter(count__gte=2).values_list('patient', flat=True).distinct().order_by('-patient')
            log_query('Patient PKs for %s twice' % event_type, patient_pks)
            for ppk in patient_pks:
                # Date of second event
                pat_events = Event.objects.filter(event_type=event_type, patient=ppk)
                if not pat_events:
                    continue
                trigger_date = pat_events.order_by('date').values_list('date', flat=True)[1]
                if (ppk not in frank_dm) or (frank_dm[ppk][0] > trigger_date):
                    frank_dm[ppk] = (trigger_date, pat_events.filter(date=trigger_date))
                    log.debug('%s: %s' % (ppk, trigger_date))
        #
        # Determine type and create cases
        #
        total_count = len(frank_dm)
        counter = 0
        type_1_counter = 0
        type_2_counter = 0
        unknown_counter = 0
        for pat_pk in frank_dm:
            counter += 1
            log.debug('Checking patient %8s / %s' % (counter, total_count))
            patient = Patient.objects.get(pk=pat_pk)
            trigger_date, trigger_events = frank_dm[pat_pk]
            condition, case_date, provider, events = self.determine_dm_type(patient, trigger_date, trigger_events)
            if condition == 'diabetes_type_1':
                pattern = self.PATTERN_TYPE_1
                type_1_counter += 1
            elif condition == 'diabetes_type_2':
                pattern = self.PATTERN_TYPE_2
                type_2_counter += 1
            elif condition == 'diabetes_unknown_type':
                pattern = self.PATTERN_TYPE_UNKNOWN
                unknown_counter += 1
            else:
                raise RuntimeError('WTF - invalid diabetes type')
            new_case = Case(
                patient = patient,
                provider = provider,
                date = case_date,
                condition =  condition,
                pattern = pattern,
                )
            new_case.save()
            new_case.events = events | trigger_events
            new_case.save()
            log.debug('Generated new case: %s' % new_case)
        log.info('%8s new cases of type 1 diabetes' % type_1_counter)
        log.info('%8s new cases of type 2 diabetes' % type_2_counter)
        log.info('%8s patients who matched general frank diabetes criteria, but not criteria for type 1 or 2' % unknown_counter)
            
    def determine_dm_type(self, patient, trigger_date, trigger_events):
        '''
        Determine if patient has Type 1, Type 2, or unknown type of diabetes
        @param patient:  patient to be tested
        @type patient:   Patient object
        @param trigger_date: Date at which patient met frank diabetes criteria
        @type trigger_date:  Date object
        @return: (condition, case_date, provider, events)
        '''
        patient_events = Event.objects.filter(patient=patient)
        #===============================================================================
        #
        # Patient ever prescribed insulin?
        #
        #-------------------------------------------------------------------------------
        insulin_rx = patient_events.filter(event_type='rx--insulin')
        if not insulin_rx:
            provider = trigger_events[0].provider
            return ('diabetes_type_2', trigger_date, provider, trigger_events)
        
        #===============================================================================
        #
        # C-peptide test done?
        #
        #-------------------------------------------------------------------------------
        c_peptide_lx_thresh = patient_events.filter(event_type='lx--c_peptide--threshold--1.0').order_by('date')
        c_peptide_lx_any = patient_events.filter(event_type='lx--c_peptide--any_result').order_by('date')
        if c_peptide_lx_thresh:
            provider = c_peptide_lx_thresh[0].provider
            case_date = c_peptide_lx_thresh[0].date
            case_events = trigger_events | c_peptide_lx_thresh
            return ('diabetes_type_2', case_date, provider, case_events)
        if c_peptide_lx_any: # Test was done, but result is below threshold
            provider = c_peptide_lx_any[0].provider
            case_date = c_peptide_lx_any[0].date
            case_events = trigger_events | c_peptide_lx_any
            return ('diabetes_type_1', case_date, provider, case_events)
        
        #===============================================================================
        #
        # Diabetes auto-antibodies test done?
        #
        #-------------------------------------------------------------------------------
        pos_aa_event_types = ['%s--positive' % i for i in self.AUTO_ANTIBODIES_LABS]
        neg_aa_event_types = ['%s--negative' % i for i in self.AUTO_ANTIBODIES_LABS]
        aa_pos = patient_events.filter(event_type__in=pos_aa_event_types).order_by('date')
        aa_neg = patient_events.filter(event_type__in=neg_aa_event_types).order_by('date')
        if aa_pos:
            provider = aa_pos[0].provider
            case_date = aa_pos[0].date
            events = trigger_events | aa_pos
            return ('diabetes_type_1', case_date, provider, events)
        if aa_neg:
            provider = aa_neg[0].provider
            case_date = aa_neg[0].date
            events = trigger_events | aa_neg
            return ('diabetes_type_2', case_date, provider, events)
        
        #===============================================================================
        #
        # Prescription for URINE ACETONE TEST STRIPS? (search on keyword: ACETONE)
        #
        #-------------------------------------------------------------------------------
        acetone_rx = patient_events.filter(event_type='rx--acetone').order_by('date')
        if acetone_rx:
            provider = acetone_rx[0].provider
            case_date = acetone_rx[0].date
            case_events = trigger_events | acetone_rx
            return ('diabetes_type_1', case_date, provider, case_events)
            
        #===============================================================================
        #
        # Prescription for GLUCAGON?
        #
        #-------------------------------------------------------------------------------
        glucagon_rx = patient_events.filter(event_type='rx--glucagon').order_by('date')
        if glucagon_rx:
            provider = glucagon_rx[0].provider
            case_date = glucagon_rx[0].date
            case_events = trigger_events | glucagon_rx
            return ('diabetes_type_1', case_date, provider, case_events)
        
        #===============================================================================
        #
        # Patient ever prescribed any oral hypoglycaemics?
        #
        #-------------------------------------------------------------------------------
        oral_hypoglycaemic_rx = patient_events.filter(event_type__in=self.ORAL_HYPOGLYCAEMICS).order_by('date')
        if oral_hypoglycaemic_rx:
            provider = oral_hypoglycaemic_rx[0].provider
            case_date = oral_hypoglycaemic_rx[0].date
            case_events = trigger_events | oral_hypoglycaemic_rx
            return ('diabetes_type_2', trigger_date, provider, case_events)
        
        #===============================================================================
        #
        # >50% OF ICD9s in record for type 1?
        #
        #-------------------------------------------------------------------------------
        type_1_dx = patient_events.filter(event_type__name__startswith='diabetes_type_1')
        type_2_dx = patient_events.filter(event_type__name__startswith='diabetes_type_2')
        count_1 = type_1_dx.count()
        count_2 = type_2_dx.count()
        # Is there a less convoluted way to express this and still avoid divide-by-zero errors?
        if (count_1 and not count_2):
            provider = trigger_events[0].provider
            case_date = trigger_events[0].date
            case_events = trigger_events | type_1_dx
            return ('diabetes_type_1', trigger_date, provider, case_events)
        elif count_2 and ( ( count_1 / count_2 ) > 0.5 ):
            provider = trigger_events[0].provider
            case_date = trigger_events[0].date
            case_events = trigger_events | type_1_dx
            return ('diabetes_type_1', trigger_date, provider, case_events)
        else:
            provider = trigger_events[0].provider
            case_date = trigger_events[0].date
            case_events = trigger_events | type_2_dx
            return ('diabetes_type_2', trigger_date, provider, case_events)
    
    def __vqs_to_pfv(self, vqs, field):
        '''
        Adds a ValuesQuerySet, which must include both 'patient' and 'value' 
        fields, to patient_field_values 
        '''
        for item in vqs:
            pat = item['patient']
            val = item['value']
            self.patient_field_values[pat][field] = val
    
    def __recent_rx(self):
        event_type_list = [
            'rx--metformin',
            'rx--insulin',
            ]
        for event_type in event_type_list:
            field_drug = '%s--drug' % event_type
            field_date = '%s--date' % event_type
            self.FIELDS.append(field_drug)
            self.FIELDS.append(field_date)
            qs = Prescription.objects.filter(tags__event__event_type=event_type)
            qs = qs.filter(patient__in=self.patient_qs)
            qs = qs.order_by('patient', '-date') # First record for each patient will be that patient's most recent result
            log.info('Collecting data for %s' % event_type)
            log_query('Recent Rx %s' % event_type, qs)
            last_patient = None
            for rx in qs:
                if rx.patient == last_patient:
                    continue
                self.patient_field_values[rx.patient.pk][field_drug] = rx.name
                self.patient_field_values[rx.patient.pk][field_date] = rx.date
                last_patient = rx.patient
    
    def __recent_dx(self):
        event_type_list = [
            'dx--abnormal_glucose'
            ]
        for event_type in event_type_list:
            field_code = '%s--code' % event_type
            field_text = '%s--text' % event_type
            field_date = '%s--date' % event_type
            self.FIELDS.append(field_code)
            self.FIELDS.append(field_date)
            self.FIELDS.append(field_text)
            #log_query('Recent Dx', events)
            heuristic = EventType.objects.get(name=event_type).heuristic.diagnosisheuristic
            icd9_q = heuristic.icd9_q_obj
            qs = Encounter.objects.filter(tags__event__event_type=event_type)
            qs = qs.filter(patient__in=self.patient_qs)
            qs = qs.order_by('patient', '-date') # First record for each patient will be that patient's most recent result
            log_query('Recent Dx %s' % event_type, qs)
            log.info('Collecting data for %s' % event_type)
            last_patient = None
            for enc in qs:
                if enc.patient == last_patient:
                    continue
                field_values = self.patient_field_values[enc.patient.pk]
                icd9_obj = enc.icd9_codes.filter(icd9_q)[0]
                field_values[field_code] = icd9_obj.code
                field_values[field_text] = icd9_obj.name
                field_values[field_date] = enc.date
                last_patient = enc.patient
    
    def __blood_pressure(self):
        '''
        Collect data on yearly average systolic and disastolic blood pressure 
        '''
        for year in self.YEARS:
            diastolic_field = 'bp_diastolic--%s' % year
            systolic_field = 'bp_systolic--%s' % year
            self.FIELDS.append(diastolic_field)
            self.FIELDS.append(systolic_field)
            qs = Encounter.objects.filter(patient__in=self.patient_qs)
            qs = qs.filter(date__year=year)
            vqs = qs.values('patient').annotate(bp_diastolic=Avg('bp_diastolic'), bp_systolic=Avg('bp_systolic'))
            log.info('Collecting aggregate data for %s and %s' % (systolic_field, diastolic_field))
            log_query('average blood pressure %s' % year, vqs)
            for item in vqs:
                field_values = self.patient_field_values[item['patient']]
                field_values[diastolic_field] = item['bp_diastolic']
                field_values[systolic_field] = item['bp_systolic']
                
    def __recent_lx(self):
        '''
        Collect data on most recent result from test groups
        '''
        lx_tuple_list = [
            ('dm_antibodies', ['gad65', 'ica512', 'islet_cell_antibody', 'insulin_antibody']),
            ('c_peptide', ['c_peptide',]),
            ]
    
        for tup in lx_tuple_list:
            self.FIELDS.append(tup[0])
            field = tup[0]
            lab_names = tup[1]
            abs_test_qs = AbstractLabTest.objects.filter(name__in=lab_names)
            lab_qs = abs_test_qs[0].lab_results
            for abs_test in abs_test_qs[1:]:
                lab_qs |= abs_test.lab_results
            lab_qs = lab_qs.filter(patient__in=self.patient_qs)
            lab_qs = lab_qs.order_by('patient', '-date') # First record for each patient will be that patient's most recent result
            vqs = lab_qs.values('patient', 'result_string')
            log_query(field, vqs)
            last_patient = None
            for item in vqs:
                patient_pk = item['patient']
                result = item['result_string']
                if patient_pk == last_patient:
                    continue
                field_values = self.patient_field_values[patient_pk]
                field_values[field] = result
                last_patient = patient_pk

    def __rx_ever(self):
        self.FIELDS.append('__rx_ever--oral_hypoglycemic_any')
        self.FIELDS.append('__rx_ever--oral_hypoglycemic_non_metformin')
        rx_ever_events = Event.objects.filter(patient__in=self.patient_qs)
        oral_hyp = rx_ever_events.filter(event_type__in=self.ORAL_HYPOGLYCAEMICS)
        non_met = oral_hyp.exclude(event_type='rx--metformin')
        oral_hyp_patients = oral_hyp.distinct('patient').values_list('patient', flat=True)
        non_met_patients = non_met.distinct('patient').values_list('patient', flat=True)
        for patient in self.patient_qs:
            pat_pk = patient.pk
            field_values = self.patient_field_values[pat_pk]
            if pat_pk in oral_hyp_patients:
                field_values['__rx_ever--oral_hypoglycemic_any'] = True
            else:
                field_values['__rx_ever--oral_hypoglycemic_any'] = False
            if pat_pk in non_met_patients:
                field_values['__rx_ever--oral_hypoglycemic_non_metformin'] = True
            else:
                field_values['__rx_ever--oral_hypoglycemic_non_metformin'] = False
                
    def __yearly_minimum(self):
        test_list = [
            'cholesterol_hdl',
            ]
        for test in test_list:
            for year in self.YEARS:
                field = '%s--min--%s' % (test, year)
                self.FIELDS.append(field)
                abs_test = AbstractLabTest.objects.get(name=test)
                vqs = abs_test.lab_results.filter(patient__in=self.patient_qs, date__year=year).values('patient').annotate(value=Min('result_float'))
                log.info('Collecting aggregate data for %s' % field)
                log_query(field, vqs)
                self.__vqs_to_pfv(vqs, field)
    
    
    def __yearly_max(self):
        test_list = [
            'a1c',
            'glucose_fasting',
            'cholesterol_total',
            'cholesterol_hdl',
            'cholesterol_ldl',
            'triglycerides',
            ]
        for test in test_list:
            for year in self.YEARS:
                field = '%s--max--%s' % (test, year)
                self.FIELDS.append(field)
                abs_test = AbstractLabTest.objects.get(name=test)
                vqs = abs_test.lab_results.filter(patient__in=self.patient_qs, date__year=year).values('patient').annotate(value=Max('result_float'))
                log.info('Collecting aggregate data for %s' % field)
                log_query(field, vqs)
                self.__vqs_to_pfv(vqs, field)
                
    def __total_occurrences(self):
        event_type_list = [
            'dx--diabetes_all_types',
            'dx--diabetes_type_1_not_stated',
            'dx--diabetes_type_1_uncontrolled',
            'dx--diabetes_type_2_not_stated',
            'dx--diabetes_type_2_uncontrolled',
            ]
        for event_type in event_type_list:
            field = '%s--total_count' % event_type
            self.FIELDS.append(field)
            vqs = Event.objects.filter(patient__in=self.patient_qs, event_type=event_type).values('patient').annotate(value=Count('id'))
            log.info('Collecting aggregate data for %s' % field)
            log_query(field, vqs)
            self.__vqs_to_pfv(vqs, field)
    
    def __recent_pregnancies(self):
        self.FIELDS.append('pregnancy_edd--1')
        self.FIELDS.append('pregnancy_edd--2')
        self.FIELDS.append('pregnancy_edd--3')
        preg_timespan_qs = Timespan.objects.filter(name='pregnancy', pattern__in=('EDD', 'ICD9_EOP'))
        preg_timespan_qs = preg_timespan_qs.filter(patient__in=self.patient_qs)
        preg_timespan_qs = preg_timespan_qs.order_by('patient', '-end_date')
        vqs = preg_timespan_qs.values('patient', 'end_date').distinct()
        log.info('Collecting pregnancy data')
        log_query('recent preg end dates', vqs)
        last_patient = None
        recent_preg_end_dates = []
        for item in vqs:
            patient = item['patient']
            if not patient == last_patient:
                recent_preg_end_dates = []
                last_patient = patient
            recent_preg_end_dates.append(item['end_date'])
            log.debug('pregnant patient: %s' % patient)
            log.debug('Recent EDDs: %s' % recent_preg_end_dates)
            if len(recent_preg_end_dates) > 3: # We only want the first three
                continue
            field_values = self.patient_field_values[patient]
            for i in range(0, len(recent_preg_end_dates)):
                ordinal = i + 1
                field = 'pregnancy_edd--%s' % ordinal
                if field in field_values:
                    continue
                end_date = recent_preg_end_dates[i]
                log.debug('Added value %s for field %s' % (end_date, field))
                field_values[field] = end_date
        
    def __diabetes_case(self):
        vqs = Case.objects.filter(condition__in=self.DIABETES_CONDITIONS).values('patient', 'id', 'condition', 'date')
        log_query('Diabetes cases', vqs)
        log.info('Collecting diabetes case data')
        for item in vqs:
            field_values = self.patient_field_values[item['patient']]
            field_values['case_id'] = item['id']
            field_values['diabetes_type'] = item['condition']
            field_values['case_date'] = item['date']
    
    def linelist(self):
        #-------------------------------------------------------------------------------
        #
        # Configuration
        #
        #-------------------------------------------------------------------------------
        demographic_fields = [
            'case_id',
            'diabetes_type', 
            'case_date',
            'patient_id', 
            'mrn', 
            'date_of_birth', 
            'date_of_death', 
            'gender', 
            'race', 
            'zip', 
            ]
        # Any patient with at least one of these events is included in report
        linelist_patient_criteria_once = [
            'dx--diabetes_all_types',
            'rx--insulin',
            'lx--a1c--threshold--6.5',
            'lx--glucose_fasting--threshold--126.0',
            ] + self.ORAL_HYPOGLYCAEMICS
        # FIXME: Only item in this list should be 'random glucose >= 200', which is not yet implemented
        linelist_patient_criteria_twice = [
            ]
        #-------------------------------------------------------------------------------
        #
        # Report
        #
        #-------------------------------------------------------------------------------
        log.info('Generating patient line list report for diabetes')
        self.YEARS = range(FIRST_YEAR, datetime.datetime.now().year + 1)
        self.FIELDS = list(demographic_fields)
        #
        # Determine list of patients to be reported, and Populate self.patient_field_values 
        # with all patient PKs.
        #
        self.patient_qs = Patient.objects.filter(event__event_type__in=linelist_patient_criteria_once)
        #self.patient_qs |= Patient.objects.filter(case__condition__in=self.DIABETES_CONDITIONS)
        self.patient_qs = self.patient_qs.distinct()
        log.info('Collecting list of patients for report')
        log_query('Patients to report', self.patient_qs)
        log.info('Reporting on %s patients' % self.patient_qs.count())
        self.patient_field_values = {} # {patient_pk: {field_name: value}}
        for pat_pk in self.patient_qs.values_list('id', flat=True):
            self.patient_field_values[pat_pk] = {}
        #
        # Collect data
        #
        self.__recent_pregnancies()
        self.__diabetes_case()
        self.__recent_rx()
        self.__recent_dx()
        self.__recent_lx()
        self.__rx_ever()
        self.__total_occurrences()
        self.__yearly_max()
        self.__yearly_minimum()
        self.__blood_pressure()
        #
        # Write Header
        #
        header = dict(zip(self.FIELDS, self.FIELDS)) 
        writer = csv.DictWriter(sys.stdout, fieldnames=self.FIELDS)
        writer.writerow(header)
        #
        # Compose Report
        #
        total_line_count = self.patient_qs.count()
        counter = 0
        for patient in self.patient_qs:
            counter += 1
            log.info('Reporting on patient %8s / %s' % (counter, total_line_count))
            values = {
                'patient_id': patient.pk,
                'date_of_birth': patient.date_of_birth, 
                'date_of_death': patient.date_of_death, 
                'gender': patient.gender, 
                'race': patient.race, 
                'zip': patient.zip, 
                'mrn': patient.mrn,
                }
            values.update(self.patient_field_values[patient.pk])
            #
            # Sanitize strings
            #
            for key in values:
                values[key] = smart_str(values[key])
            #
            # Write CSV
            #
            writer.writerow(values)
