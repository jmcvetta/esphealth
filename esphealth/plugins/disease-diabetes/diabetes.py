'''
                                  ESP Health
                         Notifiable Diseases Framework
                            Diabetes Case Generator


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@contact: http://www.esphealth.org
@copyright: (c) 2010-2011 Channing Laboratory
@license: LGPL
'''

from ESP.emr.models import Encounter, LabOrder, LabResult, Patient, Prescription
from ESP.hef.base import AbstractLabTest, BaseHeuristic, DiagnosisHeuristic, \
    Dose, Icd9Query, LabOrderHeuristic, LabResultAnyHeuristic, \
    LabResultFixedThresholdHeuristic, LabResultPositiveHeuristic, \
    LabResultRangeHeuristic, LabResultRatioHeuristic, LabResultWesternBlotHeuristic, \
    PrescriptionHeuristic
from ESP.hef.models import Event, Timespan
from ESP.nodis.base import DiseaseDefinition, Report
from ESP.nodis.models import Case
from ESP.utils.utils import log
from ESP.utils.utils import log_query
from ESP.utils.utils import TODAY
from ESP.utils.plugins import IPlugin
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from django.db.models import Avg, Count, F, Max, Min, Q, Sum
from django.utils.encoding import smart_str
import csv
import datetime
import re
import sys
from functools import partial
from multiprocessing import Queue
from ESP.utils.utils import wait_for_threads
from sprinkles import implements





class Diabetes(DiseaseDefinition):
    '''
    Diabetes Mellitus:
    - Pre-diabetes
    - Frank Diabetes
    - Gestational Diabetes
    '''
    
    conditions = [
        'diabetes:prediabetes'
        'diabetes:type-1',
        'diabetes:type-2',
        'diabetes:gestational'
        ]
    
    uri = 'urn:x-esphealth:disease:channing:diabetes:v1'
    
    short_name = 'diabetes'
    
    def generate(self):
        counter = 0
        counter += self.generate_frank_diabetes()
        counter += self.generate_gestational_diabetes()
        counter += self.generate_prediabetes()
        return counter
    
    @property
    def event_heuristics(self):
        heuristics = []
        #
        # Any Result Tests
        #
        for test_name in [
            'c-peptide',
            # Complete OGTT75 series
            'ogtt75-fasting',
            'ogtt75-30min',
            'ogtt75-1hr',
            'ogtt75-90min',
            'ogtt75-2hr',
            ]:
            heuristics.append(LabResultAnyHeuristic(test_name=test_name))
        #
        # Positive Tests
        #
        for test_name in [
            'ogtt100-fasting-urine',
            ]:
            heuristics.append(LabResultPositiveHeuristic(test_name=test_name))
        #
        # Threshold Tests
        #
        for test_name, match_type, threshold in [
                       
            # Fasting OGTT
            ('ogtt50-fasting', 'gte', 126),
            ('ogtt75-fasting', 'gte', 126),
            ('ogtt100-fasting', 'gte', 126),
            # OGTT50
            ('ogtt50-1hr', 'gte', 190),
            ('ogtt50-random', 'gte', 190),
            # OGTT75
            ('ogtt75-fasting', 'gte', 92),
            ('ogtt75-fasting', 'gte', 126),
            ('ogtt75-30m', 'gte', 200),
            ('ogtt75-1hr', 'gte', 180),
            ('ogtt75-1hr', 'gte', 200),
            ('ogtt75-90m', 'gte', 180),
            ('ogtt75-90m', 'gte', 200),
            ('ogtt75-2hr', 'gte', 153),
            ('ogtt75-2hr', 'gte', 200),
            # OGTT100
            ('ogtt100-fasting', 'gte', 95),
            ('ogtt100-30m', 'gte', 200),
            ('ogtt100-1hr', 'gte', 180),
            ('ogtt100-90m', 'gte', 180),
            ('ogtt100-2hr', 'gte', 155),
            ('ogtt100-3hr', 'gte', 140),
            ('ogtt100-4hr', 'gte', 140),
            ('ogtt100-5hr', 'gte', 140),
            # Auto-antibodies
            ('gad65', 'gt', 1),
            ('ica512', 'gt', 0.8),
            # A1C
            ('a1c', 'gte', 6.5),
            # C-Peptide
            ('c-peptide', 'lt', 0.8),
            ]:
            h = LabResultFixedThresholdHeuristic(
                test_name = test_name,
                match_type = match_type,
                threshold = Decimal(str(threshold)),
                )
            heuristics.append(h)
        #
        # Range Tests
        #
        for test_name, low, high in [
            ('a1c', 5.7, 6.4),
            ('ogtt75-fasting', 100, 125),
            # added the two below in threshold too
            #('ogtt50-random', 140, 199),
            ('glucose-fasting', 100, 125),
            ('ogtt75-30m', 140, 199),
            ('ogtt75-1hr', 140, 199),
            ('ogtt75-90m', 140, 199),
            ('ogtt75-2hr', 140, 199),
            ]:
            h = LabResultRangeHeuristic(
                test_name = test_name,
                min = Decimal(str(low)),
                max = Decimal(str(high)),
                )
            heuristics.append(h)
        #
        # Encounters
        #
        heuristics.append (DiagnosisHeuristic(
            name = 'gestational-diabetes',
            icd9_queries = [
                Icd9Query(starts_with = '648.8'),
                ]
            ) )
        heuristics.append (DiagnosisHeuristic(
            name = 'diabetes:all-types',
            icd9_queries = [
                Icd9Query(starts_with = '250.'),
                ]
            ) )
        heuristics.append (DiagnosisHeuristic(
            name = 'diabetes:type-1-not-stated',
            icd9_queries = [
                Icd9Query(starts_with = '250.', ends_with='1'),
                ]
            ) )
        heuristics.append (DiagnosisHeuristic(
            name = 'diabetes:type-1-uncontrolled',
            icd9_queries = [
                Icd9Query(starts_with = '250.', ends_with='3'),
                ]
            ) )
        heuristics.append (DiagnosisHeuristic(
            name = 'diabetes:type-2-not-stated',
            icd9_queries = [
                Icd9Query(starts_with = '250.', ends_with='0'),
                ]
            ) )
        heuristics.append (DiagnosisHeuristic(
            name = 'diabetes:type-2-uncontrolled',
            icd9_queries = [
                Icd9Query(starts_with = '250.', ends_with='2'),
                ]
            ) )


        #
        # Prescriptions
        #
        for drug in [
            'metformin', 
            'glyburide', 
            'test strips', 
            'lancets',
            'pramlintide',
            'exenatide',
            'sitagliptin',
            'meglitinide',
            'nateglinide',
            'repaglinide',
            'glimepiride',
            'glipizide',
            'gliclazide',
            'rosiglitizone',
            'pioglitazone',
            'acetone',
            'glucagon',
            'miglitol',
            ]:
            h = PrescriptionHeuristic(
                name = drug.replace(' ', '-'),
                drugs = [drug],
                )
            heuristics.append(h)
        h = PrescriptionHeuristic(
            name = 'insulin',
            drugs = ['insulin'],
            exclude = ['syringe'],
            )
        heuristics.append(h)
        #
        #  
        #
        # Cholesterol
        #
        for test_name in [
            'cholesterol-hdl',
            'cholesterol-ldl',
            'cholesterol-total',
            'triglycerides',
            ]:
            heuristics.append( LabResultAnyHeuristic(
                test_name = test_name,
                date_field = 'result',
                ) )
            heuristics.append( LabResultPositiveHeuristic(
                test_name = test_name,
                date_field = 'result',
                ) )
        #
        # Misc
        #
        heuristics.append( LabResultPositiveHeuristic(
            test_name = 'islet-cell-antibody',
            titer_dilution = 4, # 1:4 titer
            ) )
        return heuristics
    
    @property
    def timespan_heuristics(self):
        return []
    
    test_name_search_strings = [
            'cholesterol',
            'triglycerides',
            'peptide',
            'ogtt',
            'glucose',
            'gad65',
            'ica512',
            'a1c',
        ]
    
    #-------------------------------------------------------------------------------
    #
    # Frank Diabetes
    #
    #-------------------------------------------------------------------------------
    __FIRST_YEAR = 2006
    __FRANK_DM_CONDITIONS = ['diabetes:type-1', 'diabetes:type-2']
    __ORAL_HYPOGLYCAEMICS = [
        'rx:metformin',
        'rx:glyburide',
        'rx:gliclazide',
        'rx:glipizide',
        'rx:glimepiride',
        'rx:pioglitazone',
        'rx:rosiglitizone',
        'rx:repaglinide',
        'rx:nateglinide',
        'rx:meglitinide',
        'rx:sitagliptin',
        'rx:exenatide',
        'rx:pramlintide',
        'rx:miglitol'
        ]
    # If a patient has one of these events, he has frank diabetes
    __FRANK_DM_ONCE = [
        'lx:a1c:threshold:gte:6.5',
        'lx:glucose-fasting:threshold:gte:126',
        'rx:glyburide',
        'rx:gliclazide',
        'rx:glipizide',
        'rx:glimepiride',
        'rx:pioglitazone',
        'rx:rosiglitizone',
        'rx:repaglinide',
        'rx:nateglinide',
        'rx:meglitinide',
        'rx:sitagliptin',
        'rx:exenatide',
        'rx:pramlintide',
        ]
    # If a patient has one of these events twice, he has frank diabetes
    __FRANK_DM_TWICE = [
        'lx:glucose-random:threshold:gte:200',
        'dx:diabetes:all-types',
        ]
    __FRANK_DM_ALL = __FRANK_DM_ONCE + __FRANK_DM_TWICE
    __AUTO_ANTIBODIES_LABS = [
        'lx:ica512',
        'lx:gad65',
        'lx:islet-cell-antibody',
        'lx:insulin-antibody'
        ]
    
    def generate_frank_diabetes(self):
        log.info('Looking for cases of frank diabetes type 1 and 2.')
        pat_date_events = {}  # {patient: {date: set([event, event, ...]), ...}
        #
        # Frank DM critiera
        #
        # Start with a query of event types which need only a single event to indicate a case of DM
        once_and_insulin = self.__FRANK_DM_ONCE + ['rx:insulin']
        once_qs = Event.objects.filter(name__in=once_and_insulin)
        once_qs = once_qs.exclude(patient__case__condition__in=self.__FRANK_DM_CONDITIONS)
        dm_criteria_list = [once_qs]
        # Add event types which must occur >=2 times to indicate DM
        for event_name in self.__FRANK_DM_TWICE:
            twice_qs = Event.objects.filter(name=event_name).values('patient')
            twice_qs = twice_qs.exclude(patient__case__condition__in=self.__FRANK_DM_CONDITIONS)
            twice_vqs = twice_qs.annotate(count=Count('pk'))
            twice_vqs = twice_vqs.filter(count__gte=2)
            twice_patients = twice_vqs.values_list('patient')
            twice_criteria_qs = Event.objects.filter(name=event_name, patient__in=twice_patients)
            dm_criteria_list.append(twice_criteria_qs)
        for criteria_qs in dm_criteria_list:
            for this_event in criteria_qs:
                if this_event.name == 'rx:insulin' and Timespan.objects.filter(
                    name = 'pregnancy',
                    patient = this_event.patient,
                    start_date__lte = this_event.date,
                    end_date__gte = this_event.date,
                    ):
                    continue # Exclude insulin during pregnancy
                date_events_dict = pat_date_events.setdefault(this_event.patient.pk, {})
                events_set = date_events_dict.setdefault(this_event.date, set())
                events_set.add(this_event.pk)
                date_events_dict[this_event.date] = events_set
                pat_date_events[this_event.patient.pk] = date_events_dict
        # Calculate trigger dates and determine DM type
        total_pats = len(pat_date_events)
        pat_serial = 0
        funcs = []
        for pat_pk in pat_date_events:
            date_list = pat_date_events[pat_pk].keys()
            date_list.sort()
            trigger_date = date_list[0] # Trigger DM on earliest event date
            trigger_event_pks = pat_date_events[pat_pk][trigger_date]
            pat_serial += 1
            f = partial(self._determine_frank_dm_type, pat_pk, trigger_date, trigger_event_pks, pat_serial, total_pats)
            funcs.append( f )
        return wait_for_threads(funcs)
    
    def _determine_frank_dm_type(self, pat_pk, trigger_date, trigger_event_pks, pat_serial, total_pats):
        '''
        Determine type of Frank DM and generate a case, based on supplied patient 
            and trigger date.
        @param pat_pk:       Patient record primary key
        @type pat_pk:        Integer
        @param trigger_date: Date on which this patient got diabetes
        @type trigger_date:  DateTime.Date
        @param trigger_event_pks: List of relevant events occurring on trigger date
        @type trigger_event_pks:  [Int, Int, ...]
        @param pat_serial:   Serial number of this patient, for debug logging
        @type pat_serial:    Integer
        @param total_pats:   Total number of patients to be evaluated, for debug logging
        @type total_pats:    Integer
        @return:             Count of new cases created (always 1)
        @rtype:              Integer
        '''
        log.debug('Checking patient %8s / %s' % (pat_serial, total_pats))
        patient = Patient.objects.get(pk=pat_pk)
        condition = None
        criteria = None
        provider = None
        case_date = None
        case_events_qs = None
        patient_event_qs = Event.objects.filter(patient=patient)
        trigger_events_qs = Event.objects.filter(pk__in=trigger_event_pks)
        
        #===============================================================================
        #
        # Criteria for type 1 classification.  If no criteria met, then type 2.
        #
        #===============================================================================
        
        #===============================================================================
        #
        # 1. C-peptide test < 0.8
        #
        #-------------------------------------------------------------------------------
        c_peptide_lx_thresh = patient_event_qs.filter(name='lx:c-peptide:threshold:lt:0.8').order_by('date')
        if c_peptide_lx_thresh:
            provider = c_peptide_lx_thresh[0].provider
            case_date = c_peptide_lx_thresh[0].date
            case_events_qs = trigger_events_qs | c_peptide_lx_thresh
            criteria = 'C-Peptide result below threshold: Type 1'
            condition = 'diabetes:type-1'
            log.debug(criteria)
        
        #===============================================================================
        #
        # 2. Diabetes auto-antibodies positive
        #
        #-------------------------------------------------------------------------------
        pos_aa_event_types = ['%s:positive' % i for i in self.__AUTO_ANTIBODIES_LABS]
        aa_pos = patient_event_qs.filter(name__in=pos_aa_event_types).order_by('date')
        if aa_pos:
            provider = aa_pos[0].provider
            case_date = aa_pos[0].date
            case_events_qs = trigger_events_qs | aa_pos
            criteria = 'Diabetes auto-antibodies positive: Type 1'
            condition = 'diabetes:type-1'
            log.debug(criteria)
        
        #===============================================================================
        #
        # 3. Prescription for URINE ACETONE TEST STRIPS (search on keyword:  ACETONE)
        #
        #-------------------------------------------------------------------------------
        acetone_rx = patient_event_qs.filter(name='rx:acetone').order_by('date')
        if acetone_rx:
            provider = acetone_rx[0].provider
            case_date = acetone_rx[0].date
            case_events_qs = trigger_events_qs | acetone_rx
            criteria = 'Acetone Rx: Type 1'
            condition = 'diabetes:type-1'
            log.debug(criteria)
        
        #===============================================================================
        #
        # 4/5. Ratio of type 1 : type 2 ICD9s >50% and (never prescribed oral hypoglycemic 
        #    medications OR prescription for GLUCAGON)
        #
        #-------------------------------------------------------------------------------
        oral_hypoglycaemic_rx = patient_event_qs.filter(name__in=self.__ORAL_HYPOGLYCAEMICS).order_by('date')
        glucagon_rx = patient_event_qs.filter(name='rx:glucagon').order_by('date')
        if glucagon_rx or (not oral_hypoglycaemic_rx):
            type_1_dx = patient_event_qs.filter(name__startswith='dx:diabetes:type-1')
            type_2_dx = patient_event_qs.filter(name__startswith='dx:diabetes:type-2')
            count_1 = float(type_1_dx.count())
            count_2 = float(type_2_dx.count())
            # Is there a less convoluted way to express this and still avoid divide-by-zero errors?
            if (count_1 and not count_2) or ( count_2 and ( ( count_1 / count_2 ) > 0.5 ) ):
                provider = trigger_events_qs[0].provider
                case_date = trigger_events_qs[0].date
                case_events_qs = trigger_events_qs | type_1_dx | type_2_dx
                if glucagon_rx:
                    criteria = 'More than 50% of ICD9s are type 1, and glucagon rx: Type 1'
                else:
                    criteria = 'More than 50% of ICD9s are type 1, and never prescribed oral hypoglycaemics: Type 1'
                condition = 'diabetes:type-1'
                log.debug(criteria)
                
        #===============================================================================
        #
        # No Type 1 criteria met, therefore Type 2
        #
        #-------------------------------------------------------------------------------
        if not condition:
            provider = trigger_events_qs[0].provider
            case_date = trigger_events_qs[0].date
            case_events_qs = trigger_events_qs
            criteria = 'No Type 1 criteria met: Type 2'
            condition = 'diabetes:type-2'
            log.debug(criteria)
        
        #===============================================================================
        #
        # Generate new case
        #
        #===============================================================================
        assert patient     # Sanity check
        assert provider    # Sanity check
        assert condition   # Sanity check
        assert criteria    # Sanity check
        assert case_events_qs # Sanity check
        assert case_date   # Sanity check
        new_case = Case(
            patient = patient,
            provider = provider,
            date = case_date,
            condition =  condition,
            criteria = criteria,
            source = self.uri,
            )
        new_case.save()
        new_case.events = case_events_qs
        new_case.save()
        log.debug('Generated new case: %s (%s)' % (new_case, criteria))
        return 1  # 1 new case generated
            
    def generate_prediabetes(self):
        ONCE_CRITERIA = [
            'lx:a1c:range:gte:5.7:lte:6.4',
            'lx:glucose-fasting:range:gte:100:lte:125',
            ]
        TWICE_CRITERIA = [
            'lx:glucose-random:range:gte:140:lt:200',
            ]
        all_criteria = ONCE_CRITERIA + TWICE_CRITERIA
        qs = Event.objects.filter(name__in=TWICE_CRITERIA).values('patient')
        qs = qs.annotate(count=Count('pk'))
        patient_pks = qs.filter(count__gte=2).values_list('patient', flat=True).distinct()
        patient_pks = set(patient_pks)
        patient_pks |= set( Event.objects.filter(name__in=ONCE_CRITERIA).values_list('patient', flat=True).distinct() )
        # Ignore patients who already have a prediabetes case
        patient_pks = patient_pks - set( Case.objects.filter(condition='diabetes:prediabetes').values_list('patient', flat=True) )
        total = len(patient_pks)
        counter = 0
        for pat_pk in patient_pks:
            counter += 1
            event_qs = Event.objects.filter(
                patient = pat_pk,
                name__in = all_criteria,
                ).order_by('date')
            trigger_event = event_qs[0]
            trigger_date = trigger_event.date
            prior_dm_case_qs = Case.objects.filter(
                patient = pat_pk,
                condition__startswith = 'diabetes:',
                date__lte = trigger_date,
                )
            if prior_dm_case_qs.count():
                log.info('Patient already has diabetes, skipping. (%8s / %s)' % (counter, total))
                continue # This patient already has diabetes, and as such does not have prediabetes
            new_case = Case(
                patient = trigger_event.patient,
                provider = trigger_event.provider,
                date = trigger_event.date,
                condition =  'diabetes:prediabetes',
                source = self.uri,
                )
            new_case.save()
            counter += 1
            new_case.events = event_qs
            new_case.save()
            log.info('Saved new case: %s (%8s / %s)' % (new_case, counter, total))
        return counter
    
    GDM_ONCE = [
        
        'lx:ogtt100-fasting:threshold:gte:126',
        'lx:ogtt50-fasting:threshold:gte:126',
        'lx:ogtt75-fasting:threshold:gte:126',
        'lx:ogtt50-1hr:threshold:gte:190',
        'lx:ogtt50-random:threshold:gte:190',
        'lx:ogtt75-fasting:threshold:gte:92',
        'lx:ogtt75-30min:threshold:gte:200',
        'lx:ogtt75-1hr:threshold:gte:180',
        'lx:ogtt75-90min:threshold:gte:180',
        'lx:ogtt75-2hr:threshold:gte:153',
        ]
    # Two or more occurrences of these events, during pregnancy, is sufficient for a case of GDM
    GDM_TWICE = [
        'lx:ogtt75-fasting:threshold:gte:95',
        'lx:ogtt75-30min:threshold:gte:200',
        'lx:ogtt75-1hr:threshold:gte:180',
        'lx:ogtt75-90min:threshold:gte:180',
        'lx:ogtt75-2hr:threshold:gte:155',
        'lx:ogtt100-fasting-urine:positive',
        'lx:ogtt100-fasting:threshold:gte:95',
        'lx:ogtt100-30min:threshold:gte:200',
        'lx:ogtt100-1hr:threshold:gte:180',
        'lx:ogtt100-90min:threshold:gte:180',
        'lx:ogtt100-2hr:threshold:gte:155',
        'lx:ogtt100-3hr:threshold:gte:140',
        ]
    
    def generate_gestational_diabetes(self):
        log.info('Generating cases of gestational diabetes')
        #===============================================================================
        #
        # Build set of GDM pregnancy timespans
        #
        #===============================================================================
        gdm_timespan_pks = set()
        ts_qs = Timespan.objects.filter(name__startswith='pregnancy')
        ts_qs = ts_qs.exclude(case__condition='diabetes:gestational')
        #
        # Single event
        #
        once_qs = ts_qs.filter(
            patient__event__name__in = self.GDM_ONCE,
            patient__event__date__gte = F('start_date'),
            patient__event__date__lte = F('end_date'),
            ).distinct().order_by('end_date')
        gdm_timespan_pks.update(once_qs.values_list('pk', flat=True))
        #
        # 2 or more events
        #
        twice_qs = ts_qs.filter(
            patient__event__name__in = self.GDM_TWICE,
            patient__event__date__gte = F('start_date'),
            patient__event__date__lte = F('end_date'),
            ).annotate(count=Count('patient__event__id')).filter(count__gte=2).distinct()
        gdm_timespan_pks.update(twice_qs.values_list('pk', flat=True))
        #
        # Dx or Rx
        #
        dx_ets=['dx:diabetes:all-types','dx:gestational-diabetes']
        rx_ets=['rx:lancets', 'rx:test-strips']
        # TODO FIXME - add to redmine dont assign to release: This date math works on PostgreSQL, but I think that's just 
        # fortunate coincidence, as I don't think this is the righ way to 
        # express the date query in ORM syntax.
        _event_qs = Event.objects.filter(
            name__in=rx_ets,
            patient__event__name__in = dx_ets, 
            # date of diagnosis
            patient__event__date__gte = (F('date') - 14 ),
            patient__event__date__lte = (F('date') + 14 ),
            )
        # gestational diabetes so this filter below returns empty
        dxrx_qs = ts_qs.filter(
            patient__event__in = _event_qs,
            patient__event__date__gte = F('start_date'),
            patient__event__date__lte = F('end_date'),
            )
        # Currently preganant patients have a null end date
        dxrx_qs |= ts_qs.filter(
            end_date__isnull=True,
            patient__event__in = _event_qs,
            patient__event__date__gte = F('start_date'),
            )
        gdm_timespan_pks.update(dxrx_qs.values_list('pk', flat=True))
        #===============================================================================
        #
        # Generate one case per timespan
        #
        #===============================================================================
        all_criteria = self.GDM_ONCE + self.GDM_TWICE + dx_ets + rx_ets
        counter = 0
        total = len(gdm_timespan_pks)
        for ts_pk in gdm_timespan_pks:
            ts = Timespan.objects.get(pk=ts_pk)
            case_events = Event.objects.filter(
                patient = ts.patient,
                name__in=all_criteria,
                date__gte=ts.start_date, 
                )
            if ts.end_date:
                case_events = case_events.filter(date__lte=ts.end_date)
            else:
                case_events = case_events.filter(date__lte=TODAY)
            case_events = case_events.order_by('date')
            first_event = case_events[0]
            case_obj, created = Case.objects.get_or_create(
                patient = ts.patient,
                condition = 'diabetes:gestational',
                date = first_event.date,
                source = self.uri, 
                defaults = {
                    'provider': first_event.provider,
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
            case_obj.timespans.add(ts)
            case_obj.save()
        log.info('Generated %s new cases of diabetes_gestational' % counter)
        return counter
        

class GestationalDiabetesReport(Report):
    
    short_name = 'diabetes:gestational'
    
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
        'prior_gdm_case', # Boolean
        'prior_gdm_case--date',
        'prior_gdm_icd9--this_preg',
        'intrapartum--ogtt50--threshold',
        'intrapartum--ogtt50--threshold',
        'intrapartum--ogtt75--threshold',
        'intrapartum--ogtt100--threshold',
        'postpartum--ogtt75--order',
        'postpartum--ogtt75--any_result',
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
    
    def __init__(self):
        self.pos_q = Q(name__endswith=':positive')
        self.a1c_q = Q(name__startswith='lx:a1c')
        self.ogtt50_q = Q(name__startswith='lx:ogtt50')
        self.ogtt50_threshold_q = Q(name__in = [
            'lx:ogtt50-1hr:threshold:gte:190',
            'lx:ogtt50-random:threshold:gte:190',
            ])
        self.ogtt75_q = Q(name__startswith='lx:ogtt75')
        # OGTT75 intrapartum thresholds
        self.ogtt75_intra_thresh_q = Q(name__in = [
            'lx:ogtt75-fasting:threshold:gte:92',
            'lx:ogtt75-30min:threshold:gte:200',
            'lx:ogtt75-1hr:threshold:gte:180',
            'lx:ogtt75-90min:threshold:gte:180',
            'lx:ogtt75-2hr:threshold:gte:153',
            ])
        self.ogtt75_dm_q = Q(name__in = [
            'lx:ogtt75-fasting:threshold:gte:126',
            'lx:ogtt75-30min:threshold:gte:200',
            'lx:ogtt75-1hr:threshold:gte:200',
            'lx:ogtt75-90min:threshold:gte:200',
            'lx:ogtt75-2hr:threshold:gte:200',
            ])
        self.ogtt75_igt_q = Q(name__in = [
            'lx:ogtt75-1hr:range:gte:140:lte:200',
            'lx:ogtt75-2hr:range:gte:140:lte:200',
            'lx:ogtt75-30min:range:gte:140:lte:200',
            'lx:ogtt75-90min:range:gte:141:lte:200',
            ])
        self.ogtt75_ifg_q = Q(name='lx:ogtt75-fasting:range:gte:100:lte:125')
        self.ogtt100_q = Q(name__startswith='lx:ogtt100')
        self.ogtt100_threshold_q = Q(name__in=[
            'lx:ogtt100-fasting-urine:positive',
            'lx:ogtt100-fasting:threshold:gte:95',
            'lx:ogtt100-30m:threshold:gte:200',
            'lx:ogtt100-1hr:threshold:gte:180',
            'lx:ogtt100-90m:threshold:gte:180',
            'lx:ogtt100-2hr:threshold:gte:155',
            'lx:ogtt100-3hr:threshold:gte:140',
            'lx:ogtt100-4hr:threshold:gte:140',
            'lx:ogtt100-5hr:threshold:gte:140',
            ])
        self.order_q = Q(name__endswith=':order')
        self.any_q = Q(name__endswith=':any-result')
        self.dxgdm_q = Q(name='dx:gestational-diabetes')
        self.lancets_q = Q(name__in=['rx:test-strips', 'rx:lancets'])
        
    def run(self, riskscape=False):
        log.info('Generating GDM report')
        fields = self.LINELIST_FIELDS
        writer = csv.DictWriter(sys.stdout, fieldnames=fields, quoting=csv.QUOTE_ALL)
        #
        # Header
        #
        header = dict(zip(fields, fields))
        writer.writerow(header)
        #
        # Report on all patients with GDM ICD9 or a pregnancy
        #
        patient_pks = set()
        patient_pks.update( Event.objects.filter(name='dx:gestational-diabetes').values_list('patient', flat=True) )
        patient_pks.update( Timespan.objects.filter(name='pregnancy').values_list('patient', flat=True))
        counter = 0
        total = len(patient_pks)
        funcs = []
        for pat_pk in patient_pks:
            counter += 1
            f = partial(self.report_on_patient, pat_pk, writer, counter, total)
            funcs.append( f )
        wait_for_threads( funcs )
        log.info('Completed GDM report')
    
    def report_on_patient(self, patient_pk, writer, counter, total):
        log.info('Reporting on patient %8s / %s' % (counter, total))
        patient = Patient.objects.get(pk=patient_pk)
        event_qs = Event.objects.filter(patient=patient)
        preg_ts_qs = Timespan.objects.filter(name='pregnancy', patient=patient)
        gdm_case_qs = Case.objects.filter(condition='diabetes:gestational', patient=patient)
        frank_dm_case_qs = Case.objects.filter(condition__startswith='diabetes:type-', patient=patient).order_by('date')
        a1c_lab_qs = AbstractLabTest('a1c').lab_results.filter(patient=patient)
        #
        # Populate values that will be used all of this patient's pregnancies
        #
        try:
            zip_code = '%05d' % int( patient.zip[0:5] )
        except:
            log.warning('Could not convert zip code: %s' % patient.zip)
            zip_code = None
        patient_values = {
            'patient_id': patient.pk,
            'mrn': patient.mrn,
            'last_name': patient.last_name,
            'first_name': patient.first_name,
            'date_of_birth': patient.date_of_birth,
            'ethnicity': patient.race,
            'zip_code': zip_code,
            'gdm_icd9--any_time': bool(event_qs.filter(self.dxgdm_q)),
            'frank_diabetes--ever': bool(frank_dm_case_qs),
            'lancets_test_strips--any_time': bool(event_qs.filter(self.lancets_q)),
            }
        if frank_dm_case_qs:
            first_dm_case = frank_dm_case_qs[0]
            patient_values['frank_diabetes--date'] = first_dm_case.date
            patient_values['frank_diabetes--case_id'] = first_dm_case.pk
        #
        # Generate a row for each pregnancy (or 1 row if no pregs found)
        #
        if not preg_ts_qs:
            patient_values['pregnancy'] = False
            writer.writerow(patient_values)
            return # Nothing more to do for this patient
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
            if preg_ts.end_date:
                end_date = preg_ts.end_date
            else:
                end_date = datetime.datetime.today()
            gdm_this_preg = gdm_case_qs.filter(
                date__gte = preg_ts.start_date,
                date__lte = end_date,
                ).order_by('date')
            # Note GDM prior does not currently look for the IDCD9 in 
            # isolation, as spec requires
            gdm_prior = gdm_case_qs.filter(date__lt=preg_ts.start_date).order_by('-date')
            if gdm_prior:
                gdm_prior_date = gdm_prior[0].date
            else:
                gdm_prior_date = None
            #
            # Events by time period
            #
            prepartum = event_qs.filter(
                date__lte = preg_ts.start_date,
                )
            intrapartum = event_qs.filter(
                date__gte = preg_ts.start_date,
                date__lte = end_date,
                )
            postpartum = event_qs.filter(
                date__gt = end_date,
                date__lte = end_date + relativedelta(days=120),
                )
            early_pp = event_qs.filter(
                date__gt = end_date,
                date__lte = end_date + relativedelta(weeks=12),
                )
            early_pp_q = Q(
                date__gt = end_date,
                date__lte = end_date + relativedelta(weeks=12),
                )
            late_pp_q = Q(
                date__gt = end_date + relativedelta(weeks=12),
                date__lte = end_date + relativedelta(days=365),
                )
            # FIXME: This date math works on PostgreSQL, but I think that's
            # just fortunate coincidence, as I don't think this is the
            # right way to express the date query in ORM syntax.
            lancets_and_icd9 = intrapartum.filter(
                self.lancets_q,
                patient__event__name='dx:gestational-diabetes',
                patient__event__date__gte =  (F('date') - 14),
                patient__event__date__lte =  (F('date') + 14),
                )
            nutrition_referral = Encounter.objects.filter(
                patient=patient,
                date__gte=preg_ts.start_date, 
                date__lte=end_date,
                ).filter(
                    Q(provider__title__icontains='RD') | Q(site_name__icontains='Nutrition')
                    )
            edd_qs = Encounter.objects.filter(
                patient = patient,
                date__gte = preg_ts.start_date,
                date__lte = end_date,
                edd__isnull=False
                ).order_by('-date')
            if edd_qs:
                edd = edd_qs[0].edd
            else:
                edd = None
            if gdm_this_preg:
                gdm_date = gdm_this_preg[0].date
            else:
                gdm_date = None
            early_a1c_max = a1c_lab_qs.filter(early_pp_q).aggregate( max=Max('result_float') )['max']
            late_a1c_max = a1c_lab_qs.filter(late_pp_q).aggregate(max=Max('result_float'))['max']
            ogtt100_twice_qs = intrapartum.filter(self.ogtt100_threshold_q).\
                values('patient').annotate(count=Count('pk')).\
                filter(count__gte=2).values_list('patient', flat=True).distinct()
            values = {
                'pregnancy_id': preg_ts.pk,
                'pregnancy': True,
                'preg_start': preg_ts.start_date,
                'preg_end': end_date,
                'edd': edd,
                'bmi': bmi,
                'gdm_case': bool( gdm_this_preg ),
                'gdm_case--date': gdm_date,
                'gdm_icd9--this_preg': bool( intrapartum.filter(self.dxgdm_q) ),
                'prior_gdm_case': bool( gdm_prior ),
                'prior_gdm_case--date': gdm_prior_date,
                'prior_gdm_icd9--this_preg': bool( prepartum.filter(self.dxgdm_q) ),
                'intrapartum--ogtt50--threshold': bool( intrapartum.filter(self.ogtt50_threshold_q) ),
                'intrapartum--ogtt75--threshold': bool( intrapartum.filter(self.ogtt75_intra_thresh_q) ),
                'intrapartum--ogtt100--threshold': bool( ogtt100_twice_qs ),
                'postpartum--ogtt75--order': bool( postpartum.filter(self.ogtt75_q, self.order_q) ),
                'postpartum--ogtt75--any_result': bool( postpartum.filter(self.ogtt75_q, self.any_q) ),
                'postpartum--ogtt75--dm_threshold': bool( postpartum.filter(self.ogtt75_dm_q) ),
                'postpartum--ogtt75--igt_range': bool( postpartum.filter(self.ogtt75_igt_q) ),
                'postpartum--ogtt75--ifg_range': bool( postpartum.filter(self.ogtt75_ifg_q) ),
                'early_postpartum--a1c--order': bool( early_pp.filter(self.a1c_q, self.order_q) ),
                'early_postpartum--a1c--max': early_a1c_max,
                'late_postpartum--a1c--max': late_a1c_max,
                'lancets_test_strips--this_preg': bool( intrapartum.filter(self.lancets_q) ),
                'lancets_test_strips--14_days_gdm_icd9': bool( lancets_and_icd9 ),
                'insulin_rx': bool( intrapartum.filter(name='rx--insulin') ),
                'metformin_rx': bool( intrapartum.filter(name='rx--metformin') ),
                'glyburide_rx': bool( intrapartum.filter(name='rx--glyburide') ),
                'referral_to_nutrition': bool(nutrition_referral),
                }
            values.update(patient_values)
            writer.writerow(values)


class BaseDiabetesReport(Report):
    
    '''
    Base class for diabetes reports, containing various convenience methods.
    '''
    
    @property
    def YEARS(self):
        #return range(Diabetes.__FIRST_YEAR, datetime.datetime.now().year + 1)
        return range(Diabetes.__FIRST_YEAR, 2011) # Until data update
    
    def _sanitize_string_values(self, dictionary):
        '''
        Sanitizes string-like values in a dictionary using smart_str()
        '''
        for key in dictionary:
            value = dictionary[key]
            if type(value) in [str, unicode]:
                sanitized_value = smart_str(value)
                dictionary[key] = sanitized_value
        return dictionary
    
    def _vqs_to_pfv(self, vqs, field):
        '''
        Adds a ValuesQuerySet, which must include both 'patient' and 'value' 
        fields, to patient_field_values 
        '''
        for item in vqs:
            pat = item['patient']
            val = item['value']
            self.patient_field_values[pat][field] = val
    
    def _recent_rx(self, event_name_list):
        for event_type in event_name_list:
            field_drug = '%s--drug' % event_type
            field_date = '%s--date' % event_type
            self.FIELDS.append(field_drug)
            self.FIELDS.append(field_date)
            qs = Prescription.objects.filter(events__name=event_type)
            qs = qs.filter(patient__in=self.patient_qs)
            qs = qs.order_by('patient', '-date') # First record for each patient will be that patient's most recent result
            log.info('Collecting data for %s' % event_type)
            total_rows = qs.count()
            counter = 0
            last_patient = None
            for rx in qs.select_related():
                counter += 1
                if rx.patient == last_patient:
                    continue
                log.debug('%s %20s of %20s' % (event_type, counter, total_rows))
                self.patient_field_values[rx.patient.pk][field_drug] = rx.name
                self.patient_field_values[rx.patient.pk][field_date] = rx.date
                last_patient = rx.patient
    
    def _recent_dx(self):
        heuristic_names = [
            'diagnosis:gestational-diabetes',
            ]
        for heuristic_name in heuristic_names:
            field_code = '%s--code' % heuristic_name
            field_text = '%s--text' % heuristic_name
            field_date = '%s--date' % heuristic_name
            self.FIELDS.append(field_code)
            self.FIELDS.append(field_date)
            self.FIELDS.append(field_text)
            heuristic = BaseHeuristic.get_heuristic_by_name(heuristic_name)
            icd9_q = heuristic.icd9_q_obj
            qs = Encounter.objects.filter(events__name=heuristic_name)
            qs = qs.filter(patient__in=self.patient_qs)
            qs = qs.order_by('patient', '-date') # First record for each patient will be that patient's most recent result
            log.info('Collecting data for %s' % heuristic_name)
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
    
    def _blood_pressure(self):
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
            for item in vqs:
                field_values = self.patient_field_values[item['patient']]
                field_values[diastolic_field] = item['bp_diastolic']
                field_values[systolic_field] = item['bp_systolic']
                
    def _recent_lx(self):
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
            lab_qs = AbstractLabTest(lab_names[0]).lab_results
            for name in lab_names[1:]:
                lab_qs |= AbstractLabTest(name).lab_results
            lab_qs = lab_qs.filter(patient__in=self.patient_qs)
            lab_qs = lab_qs.order_by('patient', '-date') # First record for each patient will be that patient's most recent result
            vqs = lab_qs.values('patient', 'result_string')
            last_patient = None
            for item in vqs:
                patient_pk = item['patient']
                result = item['result_string']
                if patient_pk == last_patient:
                    continue
                field_values = self.patient_field_values[patient_pk]
                field_values[field] = result
                last_patient = patient_pk

    def _rx_ever(self):
        log.info('Querying Rx ever')
        self.FIELDS.append('rx_ever--oral_hypoglycemic_any')
        self.FIELDS.append('rx_ever--oral_hypoglycemic_non_metformin')
        rx_ever_events = Event.objects.filter(patient__in=self.patient_qs)
        oral_hyp = rx_ever_events.filter(name__in=Diabetes.__ORAL_HYPOGLYCAEMICS)
        non_met = oral_hyp.exclude(name='rx--metformin')
        oral_hyp_patients = oral_hyp.distinct('patient').values_list('patient', flat=True)
        non_met_patients = non_met.distinct('patient').values_list('patient', flat=True)
        total_count = self.patient_qs.count()
        counter = 0
        for patient in self.patient_qs:
            counter += 1
            log.debug('Rx ever %20s of %20s' % (counter, total_count))
            pat_pk = patient.pk
            field_values = self.patient_field_values[pat_pk]
            if pat_pk in oral_hyp_patients:
                field_values['rx_ever--oral_hypoglycemic_any'] = True
            else:
                field_values['rx_ever--oral_hypoglycemic_any'] = False
            if pat_pk in non_met_patients:
                field_values['rx_ever--oral_hypoglycemic_non_metformin'] = True
            else:
                field_values['rx_ever--oral_hypoglycemic_non_metformin'] = False
                
    def _yearly_minimum(self, test_list):
        log.info('Querying yearly minimums')
        for test in test_list:
            for year in self.YEARS:
                field = '%s--min--%s' % (test, year)
                self.FIELDS.append(field)
                abs_test = AbstractLabTest(name=test)
                vqs = abs_test.lab_results.filter(patient__in=self.patient_qs, 
                    date__year=year).values('patient').annotate(value=Min('result_float'))
                log.info('Collecting aggregate data for %s' % field)
                self._vqs_to_pfv(vqs, field)
    
    
    def _yearly_max(self, test_list):
        log.info('Querying yearly maximums')
        for test in test_list:
            for year in self.YEARS:
                field = '%s--max--%s' % (test, year)
                self.FIELDS.append(field)
                abs_test = AbstractLabTest(name=test)
                vqs = abs_test.lab_results.filter(patient__in=self.patient_qs, 
                    date__year=year).values('patient').annotate(value=Max('result_float'))
                log.info('Collecting aggregate data for %s' % field)
                self._vqs_to_pfv(vqs, field)
                
    def _yearly_max_events(self, name, event_names):
        log.info('Querying yearly maximums by event')
        for year in self.YEARS:
            field = '%s--max--%s' % (name, year)
            self.FIELDS.append(field)
            vqs = LabResult.objects.filter(patient__in=self.patient_qs, 
                events__name__in=event_names,
                date__year=year).values('patient').annotate(value=Max('result_float'))
            log.info('Collecting aggregate data for %s' % field)
            self._vqs_to_pfv(vqs, field)
    
    def _max_bmi(self):
        log.info('Querying yearly BMI maximums')
        for year in self.YEARS:
            field = 'bmi--max--%s' % year
            self.FIELDS.append(field)
            vqs = Encounter.objects.filter(patient__in=self.patient_qs, 
                bmi__isnull=False, 
                date__year=year).values('patient').annotate(value=Max('bmi'))
            log.info('Collecting aggregate data for %s' % field)
            self._vqs_to_pfv(vqs, field)
                
    def _total_occurrences(self):
        event_type_list = [
            'dx--diabetes_all_types',
            'dx--diabetes:type-1_not_stated',
            'dx--diabetes:type-1_uncontrolled',
            'dx--diabetes:type-2_not_stated',
            'dx--diabetes:type-2_uncontrolled',
            ]
        for event_type in event_type_list:
            field = '%s--total_count' % event_type
            self.FIELDS.append(field)
            vqs = Event.objects.filter(patient__in=self.patient_qs, 
                name=event_type).values('patient').annotate(value=Count('id'))
            log.info('Collecting aggregate data for %s' % field)
            self._vqs_to_pfv(vqs, field)
    
    def _recent_pregnancies(self):
        self.FIELDS.append('pregnancy_edd--1')
        self.FIELDS.append('pregnancy_edd--2')
        self.FIELDS.append('pregnancy_edd--3')
        preg_timespan_qs = Timespan.objects.filter(name__startswith='pregnancy')
        preg_timespan_qs = preg_timespan_qs.filter(patient__in=self.patient_qs)
        preg_timespan_qs = preg_timespan_qs.order_by('patient', '-end_date')
        vqs = preg_timespan_qs.values('patient', 'end_date').distinct()
        log.info('Collecting pregnancy data')
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
        
    def _first_cases(self, conditions=[], count=1, criteria=False, label=None):
        log.info('Collecting case data')
        assert conditions # Sanity check
        if not label:
            label = 'case'
        for num in range(1, count+1):
            self.FIELDS.append('%s--%s--date' % (label, num))
            self.FIELDS.append('%s--%s--condition' % (label, num))
            self.FIELDS.append('%s--%s--id' % (label, num))
            if criteria:
                self.FIELDS.append('%s--%s--criteria' % (label, num))
        case_qs = Case.objects.all()
        case_qs = case_qs.filter(patient__in=self.patient_qs)
        case_qs = case_qs.filter(condition__in=conditions)
        vqs = case_qs.values('patient', 'id', 'condition', 'criteria', 'date')
        vqs = vqs.order_by('patient', 'date')
        last_patient = None
        ordinal = 0
        for item in vqs:
            patient = item['patient']
            if not patient == last_patient:
                last_patient = patient
                ordinal = 0
            ordinal += 1
            if ordinal > count:
                continue
            field_values = self.patient_field_values[patient]
            date_field = '%s--%s--date' % (label, ordinal)
            condition_field = '%s--%s--condition' % (label, ordinal)
            id_field = '%s--%s--id' % (label, ordinal)
            criteria_field = '%s--%s--criteria' % (label, ordinal)
            field_values[date_field] = item['date']
            field_values[condition_field] = item['condition']
            field_values[id_field] = item['id']
            if criteria:
                field_values[criteria_field] = item['criteria']
            log.debug('Added fields & values for: %s' % item)
            
            
        
            



class FrankDiabetesReport(BaseDiabetesReport):
    
    short_name = 'diabetes:frank'

    def run(self):
        #-------------------------------------------------------------------------------
        #
        # Configuration
        #
        #-------------------------------------------------------------------------------
        demographic_fields = [
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
            'dx:diabetes:all-types',
            'rx:insulin',
            'lx:a1c:threshold:gte:6.5',
            'lx:glucose-fasting:threshold:gte:126',
            ] + Diabetes.__ORAL_HYPOGLYCAEMICS
        # FIXME: Only item in this list should be 'random glucose >= 200', which is not yet implemented
        linelist_patient_criteria_twice = [
            'lx:glucose-random:threshold:gte:200',
            ]
        #-------------------------------------------------------------------------------
        #
        # Report
        #
        #-------------------------------------------------------------------------------
        log.info('Generating patient line list report for frank diabetes')
        self.FIELDS = list(demographic_fields)
        #
        # Determine list of patients to be reported, and Populate self.patient_field_values 
        # with all patient PKs.
        #
        twice_qs = Event.objects.filter(name__in=linelist_patient_criteria_twice).values('patient')
        twice_qs = twice_qs.annotate(count=Count('pk'))
        patient_pks = twice_qs.filter(count__gte=2).values_list('patient', flat=True).distinct()
        patient_pks = set(patient_pks)
        patient_pks |= set( Event.objects.filter(name__in=linelist_patient_criteria_once).values_list('patient', flat=True).distinct() )
        self.patient_qs = Patient.objects.filter(pk__in=patient_pks)
        log.info('Collecting list of patients for report')
        log.info('Reporting on %s patients' % len(patient_pks))
        self.patient_field_values = {} # {patient_pk: {field_name: value}}
        for pat_pk in patient_pks:
            self.patient_field_values[pat_pk] = {}
        #
        # Collect data
        #
        self._first_cases(conditions=['diabetes:type-1', 'diabetes:type-2'], count=1, criteria=True)
        self._recent_pregnancies()
        self._max_bmi()
        self._yearly_max(test_list = [
            'a1c',
            'glucose-fasting',
            'cholesterol-total',
            'cholesterol-hdl',
            'cholesterol-ldl',
            'triglycerides',
            ])
        self._yearly_minimum(test_list = [
            'cholesterol-hdl',
            ])
        self._blood_pressure()
        #
        self._recent_rx(event_name_list = [
            'rx:metformin',
            'rx:insulin',
            ])
        self._recent_dx()
        self._recent_lx()
        self._rx_ever()
        self._total_occurrences()
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
            values = self._sanitize_string_values(values)
            #
            # Write CSV
            #
            writer.writerow(values)

class PrediabetesReport(BaseDiabetesReport):
    
    short_name = 'diabetes:prediabetes'
    
    def __two_highest_random_glucose(self):
        #
        # TODO: Implement me!
        #
        lab_qs = LabResult.objects.filter(patient__in=self.patient_qs)
        lab_qs = lab_qs.filter(events__name='lx:glucose-random:any-result')
    
    def __two_recent_gdm_cases(self):
        #
        # TODO: Implement me!
        #
        log.warning('Two recent GDM case fields not yet implemented')
        case_qs = Case.objects.filter(patient__in=self.patient_qs)
        case_qs = case_qs.filter(condition__startswith='diabetes:gestational')
        return
    
    def __recent_frank_dm_date(self):
        case_qs = Case.objects.filter(condition__startswith='diabetes:type', patient__in=self.patient_qs)
        vqs = case_qs.values('patient').annotate(value=Min('date'))
        field = 'recent-frank-dm'
        self._vqs_to_pfv(vqs, field)
    
    def run(self):
        #-------------------------------------------------------------------------------
        #
        # Configuration
        #
        #-------------------------------------------------------------------------------
        demographic_fields = [
            'patient_id', 
            'mrn', 
            'date_of_birth', 
            'gender', 
            'race', 
            'zip', 
            ]
        #-------------------------------------------------------------------------------
        #
        # Report
        #
        #-------------------------------------------------------------------------------
        log.info('Generating patient line list report for prediabetes')
        self.FIELDS = list(demographic_fields)
        #
        # Determine list of patients to be reported, and Populate self.patient_field_values 
        # with all patient PKs.
        #
        self.patient_qs = Patient.objects.filter(case__condition='diabetes:prediabetes')
        self.patient_qs = self.patient_qs.distinct()
        log.info('Collecting list of patients for report')
        log.info('Reporting on %s patients' % self.patient_qs.count())
        self.patient_field_values = {} # {patient_pk: {field_name: value}}
        for pat_pk in self.patient_qs.values_list('id', flat=True):
            self.patient_field_values[pat_pk] = {}
        #
        # Collect data
        #
        self._first_cases(conditions=['diabetes:prediabetes'], count=1, label='pre_dm')
        self._first_cases(conditions=['diabetes:type-1', 'diabetes:type-2'], count=1, label='frank_dm')
        self._first_cases(conditions=['diabetes:gestational'], count=2, label='gdm')
        self._max_bmi()
        self._yearly_max(test_list=[
            'a1c',
            ])
        self._yearly_max_events('glucose-fasting', ['lx:glucose-fasting:any-result'])
        self._blood_pressure()
        #
        self._recent_pregnancies()
        self._recent_rx([
            'rx:insulin',
            'rx:glyburide',
            'rx:gliclazide',
            'rx:glipizide',
            'rx:glimepiride',
            'rx:metformin',
            'rx:acarbose',
            'rx:miglitol',
            'rx:pioglitazone',
            'rx:rosiglitazone',
            'rx:repaglinide',
            'rx:nateglinide',
            'rx:meglitinide',
            'rx:sitagliptin',
            'rx:exenatide',
            'rx:pramlintide',
            ])
        self.__two_recent_gdm_cases()
        self.__two_highest_random_glucose()
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
                'gender': patient.gender, 
                'race': patient.race, 
                'zip': patient.zip, 
                'mrn': patient.mrn,
                }
            values.update(self.patient_field_values[patient.pk])
            values = self._sanitize_string_values(values)
            #
            # Write CSV
            #
            writer.writerow(values)

    

#-------------------------------------------------------------------------------
#
# Packaging
#
#-------------------------------------------------------------------------------

diabetes_definition = Diabetes()
frank_report = FrankDiabetesReport()
pre_report = PrediabetesReport()
gestational_report = GestationalDiabetesReport()

class DiabetesPlugin(object):
    implements(IPlugin)
    event_heuristics = diabetes_definition.event_heuristics
    timespan_heuristics = []
    disease_definitions = [diabetes_definition]
    reports = [
        frank_report,
        pre_report,
        gestational_report,
        ]