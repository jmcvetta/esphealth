'''
                                  ESP Health
Diabetes Case Generator Hack


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
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

from ESP.utils import log
from ESP.utils import log_query
from ESP.emr.models import Patient
from ESP.emr.models import Encounter
from ESP.emr.models import Prescription
from ESP.emr.models import LabResult
from ESP.hef.models import Event
from ESP.hef.models import EventType
from ESP.hef.models import AbstractLabTest
from ESP.hef.models import Timespan
from ESP.nodis.models import Pattern
from ESP.nodis.models import Case



FIRST_YEAR = 2006


class Command(BaseCommand):
    
    help = 'Generate frank diabetes type 1 and 2 data'
    
    option_list = BaseCommand.option_list + (
        make_option('--generate', action='store_true', dest='generate',  default=False,
            help='Generate cases of diabetes'),
        make_option('--linelist', action='store_true', dest='linelist',  default=False,
            help='Produce diabetes patient line list report'),
        )
    
    # Cache field for more efficient linelist reporting
    PATIENT_FIELD_VALUES = {} # {patient_pk: {field_name: value}}
    
    # Condition names for diabetes of both types
    diabetes_conditions = ['diabetes_type_1', 'diabetes_type_2', 'diabetes_unknown_type']
    
    oral_hypoglycaemics = [
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
    
    auto_antibodies_labs = [
        'lx--ica512',
        'lx--gad65',
        'lx--islet_cell_antibody',
        ]
    
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
            ] + self.oral_hypoglycaemics
        # If a patient has two or more of these events, he has frank diabetes
        frank_dm_twice_reqs = [
            'dx--diabetes_all_types',
            # FIXME: Not yet implemented:  "Random glucoses (RG) >=200 on two or more occasions"
            ]
        #
        # Find trigger dates for patients who have frank DM of either type, but no existing case
        # 
        frank_dm = {}
        qs = Event.objects.filter(event_type__in=frank_dm_once_reqs).exclude(patient__case__condition__in=self.diabetes_conditions)
        log_query('Frank DM once', qs)
        for i in qs.values('patient').annotate(trigger_date=Min('date')):
            pat = i['patient']
            trigger_date = i['trigger_date']
            events = qs.filter(patient=pat, date=trigger_date)
            date_events = (trigger_date, events)
            frank_dm[pat] = date_events
        for event_type in frank_dm_twice_reqs:
            qs = Event.objects.filter(event_type=event_type).values('patient')
            qs = qs.exclude(patient__case__condition__in=self.diabetes_conditions)
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
                pattern = self.pattern_type_1
                type_1_counter += 1
            elif condition == 'diabetes_type_2':
                pattern = self.pattern_type_2
                type_2_counter += 1
            elif condition == 'diabetes_unknown_type':
                pattern = self.pattern_type_unknown
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
        pos_aa_event_types = ['%s--positive' % i for i in self.auto_antibodies_labs]
        neg_aa_event_types = ['%s--negative' % i for i in self.auto_antibodies_labs]
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
        oral_hypoglycaemic_rx = patient_events.filter(event_type__in=self.oral_hypoglycaemics).order_by('date')
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
    
    def vqs_to_pfv(self, vqs, field):
        '''
        Adds a ValuesQuerySet, which must include both 'patient' and 'value' 
        fields, to PATIENT_FIELD_VALUES 
        '''
        for item in vqs:
            pat = item['patient']
            val = item['value']
            self.PATIENT_FIELD_VALUES[pat][field] = val
    
    def linelist(self):
        log.info('Generating patient line list report for diabetes')
        #-------------------------------------------------------------------------------
        #
        # Define fields & header
        #
        #-------------------------------------------------------------------------------
        DEMOGRAPHICS = [
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
        MISC = [
            'pregnancy_edd--1',
            'pregnancy_edd--2',
            'pregnancy_edd--3',
            'rx_ever--oral_hypoglycemic_any',
            'rx_ever--oral_hypoglycemic_non_metformin',
            ]
        RECENT_DX = [
            'dx--abnormal_glucose'
            ]
        RECENT_RX = [
            'rx--metformin',
            'rx--insulin',
            ]
        RECENT_LX = [
            ('dm_antibodies', ['gad65', 'ica512', 'islet_cell_antibody', 'insulin_antibody']),
            ('c_peptide', ['c_peptide',]),
            ]
        YEARLY_MAX = [
            'a1c',
            'glucose_fasting',
            'cholesterol_total',
            'cholesterol_hdl',
            'cholesterol_ldl',
            'triglycerides',
            ]
        YEARLY_MIN = [
            'cholesterol_hdl',
            ]
        TOTAL_OCCURENCES = [
            'dx--diabetes_all_types',
            'dx--diabetes_type_1_not_stated',
            'dx--diabetes_type_1_uncontrolled',
            'dx--diabetes_type_2_not_stated',
            'dx--diabetes_type_2_uncontrolled',
            ]
        YEARS = range(FIRST_YEAR, datetime.datetime.now().year + 1)
        FIELDS = list(DEMOGRAPHICS)
        FIELDS.extend(MISC)
        case_qs = Case.objects.filter(condition__in=self.diabetes_conditions).order_by('-id')
        #
        # Populate self.PATIENT_FIELD_VALUES with all patients
        #
        for pk in case_qs.values_list('patient', flat=True):
            self.PATIENT_FIELD_VALUES[pk] = {}
        #-------------------------------------------------------------------------------
        #
        # Aggregate queries
        #
        #-------------------------------------------------------------------------------
        patient_vqs = case_qs.values('patient').distinct()
        #
        # Recent Rx
        #
        for event_type in RECENT_RX:
            field_drug = '%s--drug' % event_type
            field_date = '%s--date' % event_type
            FIELDS.append(field_drug)
            FIELDS.append(field_date)
            qs = Prescription.objects.filter(tags__event__event_type=event_type)
            #qs = qs.filter(patient__in=patient_vqs)
            qs = qs.filter(patient__case__condition__startswith='diabetes', date__lte=F('patient__case__date'))
            qs = qs.order_by('patient', '-date') # First record for each patient will be that patient's most recent result
            log.info('Querying aggregate data for %s' % event_type)
            log_query('Recent Rx %s' % event_type, qs)
            last_patient = None
            for rx in qs:
                if rx.patient == last_patient:
                    continue
                self.PATIENT_FIELD_VALUES[rx.patient.pk][field_drug] = rx.name
                self.PATIENT_FIELD_VALUES[rx.patient.pk][field_date] = rx.date
                last_patient = rx.patient
        #
        # Recent Dx
        #
        for event_type in RECENT_DX:
            field_code = '%s--code' % event_type
            field_text = '%s--text' % event_type
            field_date = '%s--date' % event_type
            FIELDS.append(field_code)
            FIELDS.append(field_date)
            FIELDS.append(field_text)
            #log_query('Recent Dx', events)
            heuristic = EventType.objects.get(name=event_type).heuristic.diagnosisheuristic
            icd9_q = heuristic.icd9_q_obj
            qs = Encounter.objects.filter(tags__event__event_type=event_type)
            qs = qs.filter(patient__case__condition__startswith='diabetes', date__lte=F('patient__case__date'))
            qs = qs.order_by('patient', '-date') # First record for each patient will be that patient's most recent result
            log_query('Recent Dx %s' % event_type, qs)
            log.info('Querying aggregate data for %s' % event_type)
            last_patient = None
            for enc in qs:
                if enc.patient == last_patient:
                    continue
                field_values = self.PATIENT_FIELD_VALUES[enc.patient.pk]
                icd9_obj = enc.icd9_codes.filter(icd9_q)[0]
                field_values[field_code] = icd9_obj.code
                field_values[field_text] = icd9_obj.name
                field_values[field_date] = enc.date
                last_patient = enc.patient
        #
        # Blood Pressure
        #
        for year in YEARS:
            diastolic_field = 'bp_diastolic--%s' % year
            systolic_field = 'bp_systolic--%s' % year
            FIELDS.append(diastolic_field)
            FIELDS.append(systolic_field)
            qs = Encounter.objects.filter(patient__in=patient_vqs)
            qs = qs.filter(date__year=year)
            vqs = qs.values('patient').annotate(bp_diastolic=Avg('bp_diastolic'), bp_systolic=Avg('bp_systolic'))
            log.info('Querying aggregate data for %s and %s' % (systolic_field, diastolic_field))
            log_query('average blood pressure %s' % year, vqs)
            for item in vqs:
                field_values = self.PATIENT_FIELD_VALUES[item['patient']]
                field_values[diastolic_field] = item['bp_diastolic']
                field_values[systolic_field] = item['bp_systolic']
        #
        # Yearly Maximum
        #
        for test in YEARLY_MAX:
            for year in YEARS:
                field = '%s--max--%s' % (test, year)
                FIELDS.append(field)
                abs_test = AbstractLabTest.objects.get(name=test)
                vqs = abs_test.lab_results.filter(patient__in=patient_vqs, date__year=year).values('patient').annotate(value=Max('result_float'))
                log.info('Querying aggregate data for %s' % field)
                log_query(field, vqs)
                self.vqs_to_pfv(vqs, field)
        #
        # Yearly Minimum
        #
        for test in YEARLY_MIN:
            for year in YEARS:
                field = '%s--min--%s' % (test, year)
                FIELDS.append(field)
                abs_test = AbstractLabTest.objects.get(name=test)
                vqs = abs_test.lab_results.filter(patient__in=patient_vqs, date__year=year).values('patient').annotate(value=Min('result_float'))
                log.info('Querying aggregate data for %s' % field)
                log_query(field, vqs)
                self.vqs_to_pfv(vqs, field)
        #
        # Total Occurences
        #
        for event_type in TOTAL_OCCURENCES:
            field = '%s--total_count' % event_type
            FIELDS.append(field)
            vqs = Event.objects.filter(patient__in=patient_vqs, event_type=event_type).values('patient').annotate(value=Count('id'))
            log.info('Querying aggregate data for %s' % field)
            log_query(field, vqs)
            self.vqs_to_pfv(vqs, field)
        #
        # Recent Lx
        #
        for tup in RECENT_LX:
            FIELDS.append(tup[0])
            field = tup[0]
            lab_names = tup[1]
            abs_test_qs = AbstractLabTest.objects.filter(name__in=lab_names)
            lab_qs = abs_test_qs[0].lab_results
            for abs_test in abs_test_qs[1:]:
                lab_qs |= abs_test.lab_results
            lab_qs = lab_qs.filter(patient__in=patient_vqs)
            lab_qs = lab_qs.filter(date__lte=F('patient__case__date'))
            lab_qs = lab_qs.order_by('patient', '-date') # First record for each patient will be that patient's most recent result
            vqs = lab_qs.values('patient', 'result_string')
            log_query(field, vqs)
            last_patient = None
            for item in vqs:
                patient_pk = item['patient']
                result = item['result_string']
                if patient_pk == last_patient:
                    continue
                field_values = self.PATIENT_FIELD_VALUES[patient_pk]
                field_values[field] = result
                last_patient = patient_pk

        #
        # Rx Ever
        #
        rx_ever_events = Event.objects.filter(patient__in=patient_vqs)
        oral_hyp = rx_ever_events.filter(event_type__in=self.oral_hypoglycaemics)
        non_met = oral_hyp.exclude(event_type='rx--metformin')
        oral_hyp_patients = oral_hyp.distinct('patient').values_list('patient', flat=True)
        non_met_patients = non_met.distinct('patient').values_list('patient', flat=True)
        for item in patient_vqs:
            pat_pk = item['patient']
            field_values = self.PATIENT_FIELD_VALUES[pat_pk]
            if pat_pk in oral_hyp_patients:
                field_values['rx_ever--oral_hypoglycemic_any'] = True
            else:
                field_values['rx_ever--oral_hypoglycemic_any'] = False
            if pat_pk in non_met_patients:
                field_values['rx_ever--oral_hypoglycemic_non_metformin'] = True
            else:
                field_values['rx_ever--oral_hypoglycemic_non_metformin'] = False
        #
        # Write Header
        #
        header = dict(zip(FIELDS, FIELDS)) 
        writer = csv.DictWriter(sys.stdout, fieldnames=FIELDS)
        writer.writerow(header)
        #
        # Generate Report
        #
        total_case_count = case_qs.count()
        counter = 0
        report_start_time = datetime.datetime.now()
        for c in case_qs:
            counter += 1
            delta = datetime.datetime.now() - report_start_time
            rate = float(delta.seconds) / float(counter) # Seconds per case
            remaining_cases = total_case_count - counter
            estimated_seconds = remaining_cases * rate # How many seconds til report is done
            estimated_string = str(datetime.timedelta(seconds=estimated_seconds)) 
            rd = relativedelta(datetime.datetime.now(), report_start_time) # Supposedly relativedelta is more accurate
            elapsed_string = '%02d:%02d:%02d' % (rd.hours, rd.minutes, rd.seconds)
            log.info('Reporting on frank diabetes case %8s / %s (%s elapsed, %s remaining)' % (counter, total_case_count, elapsed_string, estimated_string))
            p = c.patient
            pat_events = Event.objects.filter(patient=p)
            pat_rxs = Prescription.objects.filter(patient=p)
            case_values = {
                'case_id': c.pk,
                'diabetes_type': c.condition, 
                'case_date': c.date,
                'patient_id': p.pk,
                'mrn': p.mrn, 
                'date_of_birth': p.date_of_birth, 
                'date_of_death': p.date_of_death, 
                'gender': p.gender, 
                'race': p.race, 
                'zip': p.zip, 
                }
            if p.pk in self.PATIENT_FIELD_VALUES:
                field_values = self.PATIENT_FIELD_VALUES[p.pk]
            else:
                field_values = {}
            # 
            # Most recent three pregnancy EDDs
            #
            preg_timespans = Timespan.objects.filter(patient=p, name='pregnancy', pattern__in=('EDD', 'ICD9_EOP')).order_by('-end_date')
            log_query('Pregnancy timespans', preg_timespans)
            for i in range(0, 3):
                try:
                    ts = preg_timespans[i]
                except IndexError:
                    break # No more timespans
                s = 'pregnancy_edd--%s' % (i + 1) # i counts by 0
                case_values[s] = ts.end_date
            #
            # Populate everything we can get from patient_values
            #
            for field in FIELDS:
                if field in field_values:
                    case_values[field] = field_values[field]
            #
            # Sanitize strings
            #
            for key in case_values:
                case_values[key] = smart_str(case_values[key])
            #
            # Write CSV
            #
            writer.writerow(case_values)