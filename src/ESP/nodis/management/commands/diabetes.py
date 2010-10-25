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
from dateutil.relativedelta import relativedelta

from django.db.models import Q
from django.db.models import F
from django.db.models import Sum
from django.db.models import Count
from django.db.models import Max
from django.db.models import Min
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.utils.encoding import smart_str, smart_unicode
from optparse import make_option

from ESP.utils import log
from ESP.utils import log_query
from ESP.emr.models import Patient
from ESP.emr.models import Encounter
from ESP.emr.models import Prescription
from ESP.hef.models import Event
from ESP.hef.models import AbstractLabTest
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
    
    diabetes_rx_events = [
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
            ] + self.diabetes_rx_events
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
            print trigger_events
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
            log.info('Generated new case: %s' % new_case)
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
        #
        # Patient ever prescribed insulin?
        #
        insulin_rx = patient_events.filter(event_type='rx--insulin')
        if not insulin_rx:
            provider = trigger_events[0].provider
            return ('diabetes_type_2', trigger_date, provider, trigger_events)
        #
        # Insulin within the first year following trigger date for frank diabetes?
        #
        first_year_end = trigger_date + relativedelta(days=365)
        insulin_first_year = insulin_rx.filter(date__gte=trigger_date, date__lte=first_year_end)
        if not insulin_first_year:
            provider = trigger_events[0].provider
            return ('diabetes_type_2', trigger_date, provider, trigger_events)
        #
        # Patient ever prescribed any oral hypoglycaemics (all those on the 
        # frank diabetes list + metformin, rosiglitizone, pioglitazone)
        #
        oral_hypoglycaemics = self.diabetes_rx_events + [
            'rx--metformin',
            'rx--rosiglitizone',
            'rx--pioglitazone',
            ]
        oral_hypoglycaemic_rx = patient_events.filter(event_type__in=oral_hypoglycaemics)
        if oral_hypoglycaemic_rx:
            provider = trigger_events[0].provider
            events = trigger_events | oral_hypoglycaemic_rx
            return ('diabetes_type_2', trigger_date, provider, events)
        #
        # C-peptide test done?
        #
        # TODO: this section needs implementation
        
        #
        # Diabetes auto-anDiabetes auto-antibodies test done?
        #
        pos_aa_event_types = ['%s--positive' % i for i in self.auto_antibodies_labs]
        neg_aa_event_types = ['%s--negative' % i for i in self.auto_antibodies_labs]
        aa_pos = patient_events.filter(event_type__in=pos_aa_event_types)
        aa_neg = patient_events.filter(event_type__in=neg_aa_event_types)
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
        
        #
        # Triglycerides > 200 or BMI >30
        #
        # TODO: Implement this!
        
        #
        # None of the conditions above applies, so unknown type
        #
        provider = trigger_events[0].provider
        return ('diabetes_unknown_type', trigger_date, provider, trigger_events)
            
            
    
    
    def linelist(self):
        FIELDS = [
            'case_id',
            'diabetes_type', 
            'case_date',
            'patient_id', 
            'mrn', 
            'dob', 
            'gender', 
            'race', 
            'bmi', 
            'zip', 
            'max_a1c_value', 
            'max_a1c_date',
            'max_glucose_fasting_value',
            'max_glucose_fasting_date',
            #'high_rand_glucose_1_value',
            #'high_rand_glucose_1_date',
            #'high_rand_glucose_2_value',
            #'high_rand_glucose_2_date',
            'dx--diabetes_type_1_not_stated--recent_1--value',
            'dx--diabetes_type_1_not_stated--recent_1--text',
            'dx--diabetes_type_1_not_stated--recent_1--date',
            'dx--diabetes_type_1_not_stated--recent_2--value',
            'dx--diabetes_type_1_not_stated--recent_2--text',
            'dx--diabetes_type_1_not_stated--recent_2--date',
            'dx--diabetes_type_2_not_stated--recent_1--value',
            'dx--diabetes_type_2_not_stated--recent_1--text',
            'dx--diabetes_type_2_not_stated--recent_1--date',
            'dx--diabetes_type_2_not_stated--recent_2--value',
            'dx--diabetes_type_2_not_stated--recent_2--text',
            'dx--diabetes_type_2_not_stated--recent_2--date',
            'dx--diabetes_type_1_uncontrolled--recent_1--value',
            'dx--diabetes_type_1_uncontrolled--recent_1--text',
            'dx--diabetes_type_1_uncontrolled--recent_1--date',
            'dx--diabetes_type_1_uncontrolled--recent_2--value',
            'dx--diabetes_type_1_uncontrolled--recent_2--text',
            'dx--diabetes_type_1_uncontrolled--recent_2--date',
            'dx--diabetes_type_2_uncontrolled--recent_1--value',
            'dx--diabetes_type_2_uncontrolled--recent_1--text',
            'dx--diabetes_type_2_uncontrolled--recent_1--date',
            'dx--diabetes_type_2_uncontrolled--recent_2--value',
            'dx--diabetes_type_2_uncontrolled--recent_2--text',
            'dx--diabetes_type_2_uncontrolled--recent_2--date',
            # These will always be the same
            #'recent_icd9_648.8_value',
            #'recent_icd9_648.8_text',
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
        header = dict(zip(FIELDS, FIELDS)) 
        writer = csv.DictWriter(sys.stdout, fieldnames=FIELDS)
        writer.writerow(header)
        for c in Case.objects.filter(condition__in=self.diabetes_conditions).order_by('date'):
            p = c.patient
            pat_events = Event.objects.filter(patient=p)
            pat_rxs = Prescription.objects.filter(patient=p)
            values = {
                'case_id': c.pk,
                'diabetes_type': c.condition, 
                'case_date': c.date,
                'patient_id': p.pk,
                'mrn': p.mrn, 
                'dob': p.date_of_birth, 
                'gender': p.gender, 
                'race': p.race, 
                'bmi': p.bmi(c.date), 
                'zip': p.zip, 
                }
            for name in ['a1c', 'glucose_fasting']:
                alt = AbstractLabTest.objects.get(name=name)
                pat_labs = alt.lab_results.filter(patient=p)
                if pat_labs:
                    max_result = pat_labs.order_by('-result_float')[0]
                    values['max_%s_value' % name] = max_result.result_float
                    values['max_%s_date' % name] = max_result.date
                else:
                    values['max_%s_value' % name] = None
                    values['max_%s_date' % name] = None
            event_type_suffix_map = {
                'diabetes_type_1_not_stated': '1',
                'diabetes_type_1_uncontrolled': '3',
                'diabetes_type_2_not_stated': '0',
                'diabetes_type_2_uncontrolled': '2',
                }
            for event_type in event_type_suffix_map:
                suffix = event_type_suffix_map[event_type]
                events = pat_events.filter(event_type=event_type).order_by('-date')
                for item in [0, 1]:
                    val_str = event_type + 'recent_%s' % str(item)
                    try:
                        this_enc = events[item].tag_set.all()[item] # Get first or second most recent encounter
                        icd9_code = this_enc.icd9_codes.filter(code__startswith='250.', code__endswith=suffix)[0]
                        values['%s_value' % val_str] = icd9_code.code
                        values['%s_text' % val_str] = icd9_code.name
                        values['%s_date' % val_str] = this_enc.date
                    except:
                        values['%s_value' % val_str] = None
                        values['%s_text' % val_str] = None
                        values['%s_date' % val_str] = None
            try:
                values['recent_icd9_648.8_date'] = pat_events.filter(event_type='dx--gestational_diabetes')
            except IndexError:
                values['recent_icd9_648.8_date'] = None
            for drug in [
                'insulin',
                'metformin',
                'acarbose',
                'repaglinide',
                'nateglinide',
                'meglitinide',
                'miglitol',
                ]:
                try:
                    recent_rx = pat_rxs.filter(name__icontains=drug).order_by('-date')[0]
                    values['recent_%s_date' % drug] = recent_rx.date
                    values['recent_%s_drug' % drug] = recent_rx.name
                except IndexError:
                    values['recent_%s_date' % drug] = None
                    values['recent_%s_drug' % drug] = None
            # Coerce all values to ascii string
            for key in values:
                val = values[key]
                if val:
                    values[key] = smart_str(val)
                else:
                    values[key] = None
            writer.writerow(values)
