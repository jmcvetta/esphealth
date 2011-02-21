'''
                                  ESP Health
                         Notifiable Diseases Framework
                                  Data Models
                                  
@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@contact: http://esphealth.org
@copyright: (c) 2009-2010 Channing Laboratory
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''

import datetime
import pprint
import types
import sys
import optparse
import re
import hashlib
from operator import itemgetter

from django.db import connection
from django.db.models import Q
from django.db.models import F
from django.db.models import Sum
from django.db.models import Max
from django.db.models import Model
from django.db.models import Count
from django.db.models.query import QuerySet
from django.contrib.contenttypes.models import ContentType


from esp import settings
#from esp.hef import events # Ensure events are loaded
from esp.utils import utils as util
from esp.utils.utils import log
from esp.utils.utils import log_query
from esp.static.models import Icd9
#from esp.conf.models import CodeMap
from esp.conf.models import STATUS_CHOICES
from esp.conf.models import ReportableLab
from esp.conf.models import ReportableIcd9
from esp.conf.models import ReportableMedication
from esp.conf.models import IgnoredCode
from esp.emr.models import LabResult
from esp.emr.models import Encounter
from esp.emr.models import Prescription
from esp.emr.models import Immunization
from esp.emr.models import Patient
from esp.emr.models import Provider
from esp.hef.models import Heuristic
from esp.hef.models import DiagnosisHeuristic
from esp.hef.models import PrescriptionHeuristic
#from esp.hef.core import TimespanHeuristic
from esp.hef.models import Timespan
from esp.hef.models import Event
from esp.hef.models import EventType
from esp.conf.models import ConditionConfig

import datetime

from django.db import models
from django.db.models import Q

from esp.emr.models import Encounter
from esp.emr.models import Immunization
from esp.emr.models import LabResult
from esp.emr.models import Patient
from esp.emr.models import Prescription
from esp.emr.models import Provider
from esp.hef.models import Event

from esp.utils.utils import log
from esp.utils.utils import log_query


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Backwards Compatibility Fitings -- Temporary Only!
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class TimespanHeuristic:
    @classmethod
    def all_event_names(self):
        return ['pregnancy']

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


DISPOSITIONS = [
    ('exact', 'Exact'),
    ('similar', 'Similar'),
    ('missing', 'Missing'),
    ('new', 'New'),
    ]


#-------------------------------------------------------------------------------
#
#--- Exceptions
#
#-------------------------------------------------------------------------------

class NodisException(BaseException):
    '''
    A Nodis-specific error
    '''

class InvalidPattern(NodisException):
    '''
    Could not understand the specified pattern
    '''


class InvalidHeuristic(NodisException):
    '''
    You specified a heuristic that is not registered with the system.
    '''


#-------------------------------------------------------------------------------
#
#--- Pattern Matching Logic
#
#-------------------------------------------------------------------------------




class Condition(object):
    '''
    A medical condition, defined by matching at least one event pattern.
    '''
    
    __registry = {} # Class variable

    def __init__(self,
        name,
        patterns,
        recur_after,
        test_name_search,
        # Reporting
        #icd9s = [],
        #icd9_days_before = 14,
        #fever = True,
        #lab_days_before = 14,
        #med_names = [],
        #med_days_before = 14,
        ):
        '''
        NOTE: No need to specify the LOINCs used to detect the condition, 
            unless you want them reported even when negative.  All events
            forming part of a disease's definition are reported.
        @param name:             Name of this disease definition
        @type name:              String
        @param patterns:         Patterns and match windows that define this condition
        @type patterns:          List of (BaseEventPattern, Integer) tuples, 
                                 where integer is length (in days) of match window
        @param match_window:     Length (in days) of window in which pattern(s) must match
        @type match_window:      Integer
        @param recur_after:      Matches at least this many days after last case, count as 
                                 a new case.  If value is -1, condition cannot ever recur.
        @type recur_after:       Integer
        @param icd9s:            Report encounters matching these ICD9s
        @type icd9s:             List of strings
        @param icd9_days_before: How many days before case to search for encounters
        @type icd9_days_before:  Integer
        @param fever:            Do we report fever, determined as temp > 100.4, rather than as ICD9?
        @type fever:             Boolean
        @param lab_days_before:  How many days before case to search for labs
        @type lab_days_before:   Integer
        @param med_names:        Report medicines matching these names
        @type med_names:         List of strings
        @param med_days_before:  How many days before case to search for medicines
        @type med_days_before:   Integer
        '''
        assert name
        assert isinstance(recur_after, int)
        assert ' ' not in name # No spaces allowed in disease name
        assert isinstance(test_name_search, list)
        self.test_name_search = test_name_search
#        assert icd9_days_before
#        assert lab_days_before
#        assert med_days_before
        self.name = name
        self.recur_after = recur_after
        self.patterns = {}
        for pat, days in patterns:
            if not isinstance(days, int):
                raise InvalidPattern('Match window must be an integer; but you specified "%s"' % days)
            if isinstance(pat, BaseEventPattern):
                self.patterns[pat] = days
            else:
                raise InvalidPattern('Pattern not an instance of BaseEventPattern: %s' % pat)
#        self.icd9s = icd9s
#        self.icd9_days_before = datetime.timedelta(days = icd9_days_before)
#        self.fever = fever
#        self.lab_days_before = datetime.timedelta(days = lab_days_before)
#        self.med_names = med_names
#        self.med_days_before = datetime.timedelta(days = med_days_before)
        self.__existing = {} # Cache 
        if self.name in self.__registry:
            log.debug('A condition with the name "%s" is already registered.' % self.name)
            return
        else:
            log.debug('Registering condition %s' % self.name)
            self.__registry[self.name] = self
        if not ConditionConfig.objects.filter(name=self.name):
            c = ConditionConfig(name=self.name)
            c.save()
            log.debug('Added "%s" to condition config table, with default initial values' % self.name)

    @classmethod
    def all_conditions(cls):
        '''
        Get all registered conditions
        @return: List of Condition instances
        '''
        result = []
        keys = cls.__registry.keys()
        keys.sort()
        [result.extend([cls.__registry[k]]) for k in keys]
        log.debug('All Disease Definition instances: %s' % result)
        return result
    
    @classmethod
    def list_all_condition_names(cls):
        '''
        Get name of all registered conditions
        @return: List of strings
        '''
        out = cls.__registry.keys()
        out.sort()
        return out
    
    @classmethod
    def condition_choices(cls, wildcard=False):
        '''
        Return condition names in tuples suitable for use with forms.ChoiceField
        '''
        out = [(name, name) for name in cls.list_all_condition_names()]
        if wildcard:
            out = [('*', '*')] + out
        return out
    
    @classmethod
    def get_condition(cls, name):
        '''
        Returns a Condition object matching the specified name, or None if no
        match is found.
        '''
        return cls.__registry.get(name, None)

    def get_cases(self):
        '''
        Returns all cases of this disease currently __existing in db.  Does NOT 
        generate any new cases.
        '''
        return Case.objects.filter(condition = self.name)

    def __get_event_names(self):
        '''
        Return list of names of all heuristic event names included in this 
        disease's definition(s).
        '''
        names = []
        for p in self.patterns:
            names.extend(p.event_names)
        return set(names)
    event_names = property(__get_event_names)
    
    def __get_heuristics(self):
        '''
        Return a list of all the heuristics on which the events in this 
        condition's definition are based.
        '''
        regex = re.compile(r'(?P<heuristic>.*)(_pos|_neg|_ind|_order|_\d*x|_\d*$)')
        heuristics = set()
        for event_name in self.event_names:
            match = regex.search(event_name)
            if match:
                heuristics.add( match.group('heuristic') )
            else:
                heuristics.add( event_name )
        return heuristics
    heuristics = property(__get_heuristics)
    
    def __get_icd9s(self):
        icd9_objs = Icd9.objects.none()
        for heuristic_obj in DiagnosisHeuristic.objects.filter(name__in=self.heuristics):
                icd9_objs |= heuristic_obj.icd9_objects
        return icd9_objs.distinct()
    icd9s = property(__get_icd9s)
    
    def __get_medications(self):
        '''
        Returns set of medication names used in this condition's definition.
        '''
        med_names = set()
        for heuristic_obj in PrescriptionHeuristic.objects.filter(name__in=self.heuristics):
            med_names |= set( heuristic_obj.drugs )
        return med_names
    medications = property(__get_medications)

    def new_case(self, window, pattern):
        '''
        Creates, saves, and returns a new Case object.
        @param window: Create a new case in the DB based on this window
        @type window:  Window instance
        @param pattern: The pattern match triggering this case
        @type pattern:  ComplexEventPattern
        @return: Case instance
        '''
        case = Case()
        case.patient = window.patient
        case.provider = window.events[0].tag_set.all()[0].content_object.provider
        case.date = window.date
        case.condition = self.name
        case.pattern = pattern.pattern_obj
        #case.workflow_state = self.condition.ruleInitCaseStatus
        case.status = ConditionConfig.objects.get(name=self.name).initial_status
        case.save()
        case.events = window.events
        if window.events_before: # May be NoneType, so we can't rely on it being acceptable for ManyToManyField
            case.events_before = window.events_before
        if window.events_after: # May be NoneType, so we can't rely on it being acceptable for ManyToManyField
            case.events_after = window.events_after
        if window.events_ever: # May be NoneType, so we can't rely on it being acceptable for ManyToManyField
            case.events_ever = window.events_ever
        # TODO: Do we need to add events_after here?
        case.save()
        log.info('Created new %s case # %s for patient # %s based on %s' % (self.name, case.pk, case.patient.pk, window))
        return case

    def generate_cases(self):
        counter = 0            # Number of new cases generated
        log.debug('Generating cases for %s' % self.name)
        for win, pat in self.find_case_windows():
            self.new_case(window=win, pattern=pat)
            counter += 1
        log.info('Generated %s new cases of %s' % (counter, self.name))
        return counter
    
    def plausible_patients(self):
        '''
        Returns a QuerySet instance of Patients who might plausibly have his condition
        '''
        log.debug('Finding plausible patients for %s' % self.name)
        plausible = None # Plausible patients for all patterns combined
        for pattern in self.patterns:
            if not plausible:
                plausible = pattern.plausible_patients(exclude_condition=self.name)
            else:
                plausible = plausible | pattern.plausible_patients(exclude_condition=self.name)
        # 
        # HACK: Finding plausible patient PKs first, then filtering Patient by 
        # pk in a separate step, makes django produce efficient queries on 
        # PostgreSQL.  Have not tested it with other databases.
        #
        plausible_pks = plausible.values_list('pk', flat=True)
        plausible_patients = Patient.objects.filter(pk__in=plausible_pks).order_by('pk')
        log_query('Plausible patients for Condition %s' % self.name, plausible_patients)
        return plausible_patients
    
    def find_case_windows(self):
        '''
        @return: (Window, ComplexEventPattern)
        '''
        counter = 0
        log.info('Finding cases of %s' % self.name)
        #
        # We will loop over the list of all plausible patients for all patterns combined, 
        # so we need only consider one patient at a time
        #
        queue = {} # {Patient: (Window, ComplexEventPattern), ...}
        for patient in self.plausible_patients():
            log.debug('Patient # %s: %s' % (patient.pk, patient))
            queue = []
            existing_cases = Case.objects.filter(condition=self.name, patient=patient)
            if existing_cases and (self.recur_after == -1):
                log.debug('Case already exists, and condition cannot recur -- all future cases overlap')
                continue
            existing_case_dates = set(existing_cases.values_list('date', flat=True))
            #
            # For each patient, queue up windows that match any pattern
            #
            window_patterns = {} # {Window: ComplexEventPattern} -- keep track of what pattern generated a given window
            for pattern in self.patterns:
                days = self.patterns[pattern]
                for window in pattern.generate_windows(days=days, 
                    patients=[patient],  exclude_condition=self.name):
                    if window.overlaps(existing_case_dates, self.recur_after):
                        log.debug('Window overlaps with existing case')
                        continue 
                    else:
                        log.debug('Window added to queue')
                        queue.append(window)
                        window_patterns[window] = pattern
            if not queue:
                continue # no windows for this patient
            #queue.sort(lambda x, y: (x.date - y.date).days) # Sort by date
            queue.sort() # Sort by ascending date, then by descending number of bound events
            log.debug('sorted queue: %s' % queue)
            log.debug('sorted queue dates: %s' % [win.date for win in queue])
            #
            # Now we have a queue of cases that do not overlap existing (in db) 
            # cases.  Let's winnow down that queue to a list of valid windows.
            #
            if self.recur_after == -1:
                log.debug('Disease cannot recur, so limiting yield to the earliest window')
                queue = [queue[0]]
            else:
                log.debug('Examining queue')
            valid_windows = [queue[0]]
            for win in queue[1:]:
                log.debug('valid windows: %s' % valid_windows)
                log.debug('examining window: %s' % win)
                if win.overlaps([w.date for w in valid_windows], self.recur_after):
                    log.debug('Window overlaps valid window')
                    continue 
                else:
                    log.debug('Window %s added to valid windows' % win)
                    valid_windows.append(win)
            log.debug('Yielding these valid windows: %s' % valid_windows)
            #
            # Yield valid windows -- in date order :)
            #
            for win in valid_windows:
                yield (win, window_patterns[win])
    
    def purge_db(self):
        '''
        Remove all cases of this disease from the database
        '''
        all_cases = Case.objects.filter(condition = self.name)
        count = all_cases.count()
        log.warning('Purging all %s cases of %s from the database!' % (count, self.name))
        all_cases.delete()


    def regenerate(self):
        '''
        Purges all xisting cases from db, then calls generate_cases()
        '''
        log.info('Regenerating cases for %s' % self.name)
        self.purge_db()
        self.generate_cases()


    @classmethod
    def generate_all_cases(cls):
        '''
        Generates cases for all registered disease definitions.
        @return:           Integer number of new records created
        '''
        counter = {}# Counts how many total new records have been created
        total = 0
        for definition in cls.all_conditions():
            counter[definition.name] = definition.generate_cases()
        log.info('=' * 80)
        log.info('New Cases Generated')
        log.info('-' * 80)
        for name in counter:
            log.info('%20s  %s' % (name, counter[name]))
            total += counter[name]
        log.info('TOTAL: %s' % total)
        log.info('=' * 80)
        return total

    def update_case(self, case):
        '''
        Updates reportable data attached to a case.
        @param case: The case to update
        @type case:  Case instance
        '''
        log.ERROR('update_case() is deprecated')
        raise RuntimeError('update_case() is deprecated')
        log.debug('Updating case %s' % case)
        counter = 0
        patient = case.patient
        date = case.date
        if self.recur_after == -1:
            # If case cannot recur, then it is updated with relevant tests forever
            end_date = None
        else:
            end_date = date +  datetime.timedelta(days=self.recur_after)
        if self.icd9s:
            enc_q = Q(icd9_codes__code = self.icd9s[0])
            for code in self.icd9s[1:]:
                enc_q = enc_q | Q(icd9_codes__code = code)
            if self.fever:
                enc_q = enc_q | Q(temperature__gte = 100.4)
            enc_q = enc_q & Q(patient = patient)
            enc_q = enc_q & Q(date__gte = (date - self.icd9_days_before))
            if end_date:
                enc_q = enc_q & Q(date__lte = end_date)
            log.debug('enc_q: %s' % enc_q)
            encounters = Encounter.objects.filter(enc_q)
            new_encounters = set(case.encounters.all()) | set(encounters)
            counter += ( len(new_encounters) - len(case.encounters.all()) )
            case.encounters = new_encounters
        if self.lab_loinc_nums:
            lab_q = Q(patient = patient)
            lab_q = lab_q & Q(date__gte = (date - self.lab_days_before))
            if end_date:
                lab_q = lab_q & Q(date__lte = end_date)
            log.debug('lab_q: %s' % lab_q)
            labs = LabResult.objects.filter_loincs(self.lab_loinc_nums).filter(lab_q)
            # Some of these lab results will be for the same test (ie same 
            # LOINC code), but Mike only wants to see one result per test.  
            # It's probably better to handle that in the case management UI,
            # where we could potentially show a history for each test, than 
            # here.
            new_labs = set(case.lab_results.all()) | set(labs)
            counter += ( len(new_labs) - len(case.lab_results.all()) )
            case.lab_results = new_labs
        if self.med_names:
            med_q = Q(name__icontains = self.med_names[0])
            for name in self.med_names[1:]:
                med_q = med_q | Q(name__icontains = name)
            med_q = med_q & Q(patient = patient)
            med_q = med_q & Q(date__gte = (date - self.med_days_before))
            if end_date:
                med_q = med_q & Q(date__lte = end_date)
            log.debug('med_q: %s' % med_q)
            medications = Prescription.objects.filter(med_q)
            new_meds = set(case.medications.all()) | set(medications)
            counter += ( len(new_meds) - len(case.medications.all()) )
            case.medications = new_meds
        # Support for reporting immunizations has not yet been implemented
        case.save()
        log.debug('Updated case %s with %s new records' % (case, counter))
        return counter

    @classmethod
    def update_all_cases(cls):
        '''
        Updates reportable events for all __existing cases
        '''
        log.WARNING('update_all_cases() is deprecated')
        return
        log.info('Updating reportable events for __existing cases.')
        for definition in cls.get_all_diseases():
            q_obj = Q(condition = definition.name)
            existing_cases = Case.objects.filter(q_obj)
            for case in existing_cases:
                definition.update_case(case)
    
    def __get_relevant_event_names(self):
        '''
        Returns the set of heuristics required by any pattern defining this 
        condition
        '''
        names = set()
        for pat in self.patterns:
            names |= pat.event_names
        return names
    relevant_event_names = property(__get_relevant_event_names)
    
    def __get_relevant_labs(self):
        '''
        Return QuerySet of all lab results that may be relevant to this Condition
        '''
        heuristics = set()
        for event_name in self.relevant_event_names:
            h = EventType.objects.get(event_type=event_name).heuristic
            assert h, 'No heuristic found for "%s".' % event_name
            heuristics.add(h)
        heuristic_names = [h.name for h in heuristics]
        codes = LabTestMap.objects.filter(test__heuristic__in=heuristic_names).values('native_code')
        return LabResult.objects.filter(native_code__in=codes)
    relevant_labs = property(__get_relevant_labs)
    
    @classmethod
    def all_test_name_search_strings(cls):
        '''
        Returns a list of all suspicious strings to search for in lab names.
        '''
        #all_strings = set()
        #for c in Condition.all_conditions():
            #for string in c.test_name_search:
                #all_strings.add(string)
        #all_strings = list(all_strings)
        #log.debug('all test name strings: %s' % all_strings)
        #return all_strings
        return ['Fix me!'] * 3
        
    @classmethod
    def find_unmapped_labs(cls):
        '''
        Returns a QuerySet of unmapped lab tests whose native name contains
        a suspicious string.
        '''
        all_strings = cls.all_test_name_search_strings()
        mapped_codes = CodeMap.objects.values('native_code').distinct()
        ignored_codes = IgnoredCode.objects.values('native_code').distinct()
        q_obj = Q(native_name__icontains=all_strings[0])
        for string in all_strings[1:]:
            q_obj |= Q(native_name__icontains=string)
        q_obj &= ~Q(native_code__in=mapped_codes)
        q_obj &= ~Q(native_code__in=ignored_codes)
        qs = LabResult.objects.filter(q_obj).values('native_code', 'native_name').distinct()
        qs = qs.annotate(count=Count('id'))
        log_query('Test name search', qs)
        return qs
        
#-------------------------------------------------------------------------------
#
#--- Database models
#
#-------------------------------------------------------------------------------

class Pattern(models.Model):
    '''
    Hash of the ComplexEventPattern used to generate a particular case
    '''
    name = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    pattern = models.CharField(max_length=512, blank=False)
    hash = models.CharField(max_length=255, blank=False, null=False, unique=True, db_index=True)
    created_timestamp = models.DateTimeField(auto_now_add=True, blank=False)
    
    def __str__(self):
        return self.pattern
    

class Case(models.Model):
    '''
    A case of (reportable) disease
    '''
    patient = models.ForeignKey(Patient, blank=False)
    condition = models.CharField(max_length=100, blank=False, db_index=True)
    provider = models.ForeignKey(Provider, blank=False)
    date = models.DateField(blank=False, db_index=True)
    pattern = models.ForeignKey(Pattern, blank=False, db_index=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='AR') # Is it sensible to have default here?
    notes = models.TextField(blank=True, null=True)
    # Timestamps:
    created_timestamp = models.DateTimeField(auto_now_add=True, blank=False)
    updated_timestamp = models.DateTimeField(auto_now=True, blank=False)
    sent_timestamp = models.DateTimeField(blank=True, null=True)
    #
    # Events that define this case
    #
    events = models.ManyToManyField(Event, blank=False)
    timespans = models.ManyToManyField(Timespan, blank=False)
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #
    # Deprecated fields:
    #
    #
    # The events that caused this case to be generated, but occured before the event window
    events_before = models.ManyToManyField(Event, blank=True, null=True, related_name='case_before')
    # The events that caused this case to be generated, but occurred after the event window
    events_after = models.ManyToManyField(Event, blank=True, null=True, related_name='case_after')
    # The events that caused this case to be generated, but occurred after the event window
    events_ever = models.ManyToManyField(Event, blank=True, null=True, related_name='case_ever')
    # The events that caused this case to be generated, but occurred after the event window
    
    class Meta:
        permissions = [ ('view_phi', 'Can view protected health information'), ]
        unique_together = ['patient', 'condition', 'date']
        ordering = ['id']
    
    def __get_condition_config(self):
        '''
        Return the ConditionConfig object for this case's condition
        '''
        return ConditionConfig.objects.get(name=self.condition)
    condition_config = property(__get_condition_config)
    
    def __get_first_provider(self):
        '''
        Provider for chronologically first event
        '''
        return self.events.all().order_by('date')[0].tag_set.all()[0].content_object.provider
    first_provider = property(__get_first_provider)
    
    #
    # Events by class
    #
    def __get_all_events(self):
        #return self.events.all() | self.events_before.all() | self.events_after.all() | self.events_ever.all()
        #
        # Generate a list of event IDs to fetch.  We could just OR all the
        # event fields together and get the same result; but the query Django
        # generates for is quite a dog.
        #
        all_ids = set()
        for field in [self.events, self.events_before, self.events_after, self.events_ever]:
            ids = field.all().values_list('pk', flat=True)
            all_ids.update(ids)
        return Event.objects.filter(pk__in=all_ids)
    all_events = property(__get_all_events)
    
    def __get_lab_results(self):
        return LabResult.objects.filter(events__in=self.all_events).order_by('date')
    lab_results = property(__get_lab_results)
    
    def __get_encounters(self):
        return Encounter.objects.filter(events__in=self.all_events).order_by('date')
    encounters = property(__get_encounters)
    
    def __get_prescriptions(self):
        return Prescription.objects.filter(events__in=self.all_events).order_by('date')
    prescriptions = property(__get_prescriptions)
    
    def __get_reportable_labs(self):
        heuristics = Condition.get_condition(self.condition).heuristics
        reportable_codes = set( ReportableLab.objects.filter(condition=self.condition).values_list('native_code', flat=True) )
        reportable_codes |= set( CodeMap.objects.filter(heuristic__in=heuristics, reportable=True).values_list('native_code', flat=True) )
        q_obj = Q(patient=self.patient)
        q_obj &= Q(native_code__in=reportable_codes)
        conf = self.condition_config
        start = self.date - datetime.timedelta(days=conf.lab_days_before)
        end = self.date + datetime.timedelta(days=conf.lab_days_after)
        q_obj &= Q(date__gte=start)
        q_obj &= Q(date__lte=end)
        labs = LabResult.objects.filter(q_obj).distinct()
        log_query('Reportable labs for %s' % self, labs)
        return labs
    reportable_labs = property(__get_reportable_labs)
    
    def __get_reportable_icd9s(self):
        icd9_objs = Condition.get_condition(self.condition).icd9s
        icd9_objs |= Icd9.objects.filter(reportableicd9__condition=self.condition_config).distinct()
        return icd9_objs
    reportable_icd9s = property(__get_reportable_icd9s)
    
    def __get_reportable_encounters(self):
        q_obj = Q(patient=self.patient)
        q_obj &= Q(icd9_codes__in=self.reportable_icd9s)
        conf = self.condition_config
        start = self.date - datetime.timedelta(days=conf.icd9_days_before)
        end = self.date + datetime.timedelta(days=conf.icd9_days_after)
        q_obj &= Q(date__gte=start)
        q_obj &= Q(date__lte=end)
        encs = Encounter.objects.filter(q_obj)
        log_query('Encounters for %s' % self, encs)
        return encs
    reportable_encounters = property(__get_reportable_encounters)
    
    def __get_reportable_prescriptions(self):
        conf = self.condition_config
        med_names = Condition.get_condition(self.condition).medications
        med_names |= set( ReportableMedication.objects.filter(condition=self.condition_config).values_list('drug_name', flat=True) )
        if not med_names:
            return Prescription.objects.none()
        med_names = list(med_names)
        q_obj = Q(name__icontains=med_names[0])
        for med in med_names:
            q_obj |= Q(name__icontains=med)
        q_obj &= Q(patient=self.patient)
        start = self.date - datetime.timedelta(days=conf.med_days_before)
        end = self.date + datetime.timedelta(days=conf.med_days_after)
        q_obj &= Q(date__gte=start)
        q_obj &= Q(date__lte=end)
        prescriptions = Prescription.objects.filter(q_obj).distinct()
        log_query('Reportable prescriptions for %s' % self, prescriptions)
        return prescriptions
    reportable_prescriptions = property(__get_reportable_prescriptions)
    
    def __str__(self):
        return '%s # %s' % (self.condition, self.pk)
    
    def str_line(self):
        '''
        Returns a single-line string representation of the Case instance
        '''
        values = self.__dict__
        return '%(date)-10s    %(id)-8s    %(condition)-30s' % values

    @classmethod
    def str_line_header(cls):
        '''
        Returns a header describing the fields returned by str_line()
        '''
        values = {'date': 'DATE', 'id': 'CASE #', 'condition': 'CONDITION'}
        return '%(date)-10s    %(id)-8s    %(condition)-30s' % values
    
    def __get_collection_date(self):
        '''
        Returns the earliest specimen collection date
        '''
        if self.lab_results:
            return self.lab_results.aggregate(maxdate=Max('collection_date'))['maxdate']
        else:
            return None
    collection_date = property(__get_collection_date)
    
    def __get_result_date(self):
        '''
        Returns the earliest specimen collection date
        '''
        if self.lab_results:
            return self.lab_results.aggregate(maxdate=Max('result_date'))['maxdate']
        else:
            return None
    result_date = property(__get_result_date)
    


class CaseStatusHistory(models.Model):
    '''
    The current review status of a given Case
    '''
    case = models.ForeignKey(Case, blank=False)
    timestamp = models.DateTimeField(auto_now=True, blank=False, db_index=True)
    old_status = models.CharField(max_length=10, choices=STATUS_CHOICES, blank=False)
    new_status = models.CharField(max_length=10, choices=STATUS_CHOICES, blank=False)
    changed_by = models.CharField(max_length=30, blank=False)
    comment = models.TextField(blank=True, null=True)
    
    def  __unicode__(self):
        return u'%s %s' % (self.case, self.timestamp)
    
    class Meta:
        verbose_name = 'Case Status History'
        verbose_name_plural = 'Case Status Histories'


class ReportRun(models.Model):
    '''
    A run of the case_report command
    '''
    timestamp = models.DateTimeField(auto_now=True)
    hostname = models.CharField('Host on which data was loaded', max_length=255, blank=False)


    
class Report(models.Model):
    '''
    A reporting message generated from one or more Case objects
    '''
    timestamp = models.DateTimeField(auto_now=True, blank=False)
    run = models.ForeignKey(ReportRun, blank=False)
    cases = models.ManyToManyField(Case, blank=False)
    filename = models.CharField(max_length=512, blank=False)
    sent = models.BooleanField('Case status was set to sent?', default=False)
    message = models.TextField('Case report message', blank=False)
    


#===============================================================================
#
# Case Validator Models
#
#-------------------------------------------------------------------------------

class ReferenceCaseList(models.Model):
    '''
    A group of reference cases loaded from the same source.
    '''
    source = models.CharField(max_length=255, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return 'List # %s' % self.pk
    
    class Meta:
        verbose_name = 'Reference Case List'


class ReferenceCase(models.Model):
    '''
    A reference case -- provided from an external source (such as manual Health 
    Department reporting systems), this is presumed to be a known valid case.
    '''
    list = models.ForeignKey(ReferenceCaseList, blank=False)
    #
    # Data provided by Health Dept etc
    #
    patient = models.ForeignKey(Patient, blank=True, null=True) 
    condition = models.CharField(max_length=100, blank=False, db_index=True)
    date = models.DateField(blank=False, db_index=True)
    #
    ignore = models.BooleanField(default=False, db_index=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return '%s - %s - %s' % (self.condition, self.date, self.patient.mrn)
    
    class Meta:
        verbose_name = 'Reference Case'
    
    
class ValidatorRun(models.Model):
    '''
    One run of the validator tool.
    '''
    timestamp = models.DateTimeField(blank=False, auto_now_add=True)
    list = models.ForeignKey(ReferenceCaseList, blank=False)
    complete = models.BooleanField(blank=False, default=False) # Run is complete?
    related_margin = models.IntegerField(blank=False)
    #
    # Notes
    #
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return 'Run # %s' % self.pk
    
    class Meta:
        verbose_name = 'Validator Run'
    
    def __get_results(self):
        q_obj = Q(run=self) & ~Q(ref_case__ignore=True)
        qs = ValidatorResult.objects.filter(q_obj)
        log_query('Validator results', qs)
        return qs 
    results = property(__get_results)
    
    def __get_missing(self):
        return self.results.filter(disposition='missing')
    missing = property(__get_missing)
    
    def __get_exact(self):
        return self.results.filter(disposition='exact')
    exact = property(__get_exact)
        
    def __get_similar(self):
        return self.results.filter(disposition='similar')
    similar = property(__get_similar)
    
    def __get_new(self):
        return self.results.filter(disposition='new')
    new = property(__get_new)
    
    def __get_ignored(self):
        return ValidatorResult.objects.filter(run=self, ref_case__ignore=True)
    ignored = property(__get_ignored)
        
    def percent_ignored(self):
        return 100.0 * float(self.ignored.count()) / self.results.count()

    def percent_exact(self):
        return 100.0 * float(self.exact.count()) / self.results.count()
        
    def percent_similar(self):
        return 100.0 * float(self.similar.count()) / self.results.count()
    
    def percent_missing(self):
        return 100.0 * float(self.missing.count()) / self.results.count()
        
    def percent_new(self):
        return 100.0 * float(self.new.count()) / self.results.count()

    @classmethod
    def latest(cls):
        '''
        Return the most recent complete ValidatorRun
        '''
        return cls.objects.filter(complete=True).order_by('-timestamp')[0]
    

class ValidatorResult(models.Model):
    run = models.ForeignKey(ValidatorRun, blank=False)
    ref_case = models.ForeignKey(ReferenceCase, blank=True, null=True)
    condition = models.CharField(max_length=100, blank=False, db_index=True)
    date = models.DateField(blank=False, db_index=True)
    disposition = models.CharField(max_length=30, blank=False, choices=DISPOSITIONS)
    #
    # ManyToManyFields populated only for missing cases
    #
    events = models.ManyToManyField(Event, blank=True, null=True)
    cases = models.ManyToManyField(Case, blank=True, null=True)
    lab_results = models.ManyToManyField(LabResult, blank=True, null=True)
    encounters = models.ManyToManyField(Encounter, blank=True, null=True)
    prescriptions = models.ManyToManyField(Prescription, blank=True, null=True)

    def patient(self):
        return self.ref_case.patient
    
    class Meta:
        verbose_name = 'Validator Result'
    
    def __str__(self):
        return 'Result # %s' % self.pk
    
    def date_diff(self):
        '''
        For 'similar' cases, date_diff() returns the difference between the 
        reference case date and the ESP case date.
        '''
        if not self.disposition == 'similar':
            raise RuntimeError('date_diff() makes sense only for "similar" cases')
        return self.ref_case.date - self.cases.all()[0].date
