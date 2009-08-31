'''
                                  ESP Health
                         Notifiable Diseases Framework
                                Core Components


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''

import datetime
import pprint
import types
import sets
import sys
import optparse
import re
from operator import itemgetter

from django.db import connection
from django.db.models import Q
from django.db.models import F
from django.db.models import Sum
from django.db.models import Model
from django.db.models.query import QuerySet
from django.contrib.contenttypes.models import ContentType


from ESP import settings
from ESP.utils import utils as util
from ESP.utils.utils import log
from ESP.utils.utils import log_query
from ESP.emr.models import LabResult
from ESP.emr.models import Encounter
from ESP.emr.models import Prescription
from ESP.emr.models import Immunization
from ESP.emr.models import Patient
from ESP.emr.models import Provider
from ESP.hef2 import events
from ESP.hef2.core import BaseHeuristic
from ESP.hef2.models import HeuristicEvent
from ESP.nodis.models import Case
from ESP.nodis.models import CaseEvents


CACHE_WARNING_THRESHOLD = 100


class DiseaseDefinitionAlreadyRegistered(BaseException):
    '''
    A BaseDiseaseDefinition instance has already been registered with the same 
    name as the instance you are trying to register.
    '''
    pass


#===============================================================================
#
#--- ~~~ Disease Definition Framework ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class OutOfWindow(ValueError):
    '''
    Raised when attempting to add an event to EventTimeWindow, where the 
    event's date falls outside the window.
    '''
    pass


class OutOfClump(ValueError):
    '''
    Raised when attempting to add an event to EventClump, where the 
    event's date falls outside the window.
    '''
    pass


class InvalidRequirement(ValueError):
    '''
    Could not understand this requirement.
    '''
    pass

class InvalidPattern(ValueError):
    '''
    Could not understand this pat.
    '''
    pass


class InvalidHeuristic(ValueError):
    '''
    You specified a heuristic that is not registered with the system.
    '''
    pass


class DiseaseDefinition(object):
    '''
    One set of rules for algorithmically defining a disease.  Satisfying a 
    single disease definition is sufficient to indicate a case of that disease, 
    but a given disease may have arbitrarily many definitions.
    '''
    def __init__(self, name, version, window, require, require_past = [], require_past_window = None,
        exclude = [], exclude_past = []):
        '''
        @param name: Name of this definition
        @type name: String
        @param version: Definition version
        @type version: Integer
        @param window: Time window in days
        @type window: Integer
        @param require: Events that must have occurred within 'window' days of one another
        @type require:  List of tuples of HeuristicEvent instances.  The tuples 
            are AND'ed together, and each item in a tuple is OR'ed.
        @param require_past: Events that must have occurred in the past, but 
            not within this definition's time window
        @type require_past: List of tuples.  See above.
        @param require_past_window: require_past events must have occurred 
            prior to 'window', but less than this many days in the past
        @type require_past_window: Integer
        @param exclude: Events that must not have occurred within window days of one another
        @type exclude: List of tuples.  See above.
        @param exclude_past: Events that must not have ever occurred prior to 'window'
        @type exclude_past: List of tuples.  See above.
        '''
        assert name
        assert version
        assert window
        assert require
        if require_past:
            assert require_past_window
            self.require_past_window = datetime.timedelta(require_past_window)
        self.name = name
        self.version = version
        self.window = datetime.timedelta(window)
        self.require = require
        self.require_past = require_past
        self.exclude = exclude
        self.exclude_past = exclude_past

    def __get_plausible_pids(self):
        '''
        Returns a list of pids identifying plausible patients -- those who at
            least potentially *could* have the disease
        @param matches: A match dictionary, in the same format as this 
            function returns.  New matches are added to this dictionary, and 
            the combined dict returned.
        @type matches:  {Demog: [EventTimeWindow, EventTimeWindow, ...], ...}
        @return:        {Demog: [EventTimeWindow, EventTimeWindow, ...], ...}
        '''
        log.info('Finding plausible patients for %s' % self.name)
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # First we do some simple queries and set arithmetic to generate a list
        # of patients who *could* have the disease.
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #
        # 'pids' are patient IDs -- db primary keys
        all_events = HeuristicEvent.objects.all()
        for req in (self.require + self.require_past):
            pids_this_req = set()
            for h in req: # One or more BaseHeuristic instances
                s = set(h.get_events().values_list('patient_id', flat = True))
                pids_this_req = pids_this_req | s
                log.debug('%50s: %s' % (h, len(pids_this_req)))
            try:
                pids = pids & pids_this_req
            except UnboundLocalError:
                pids = pids_this_req
        for item in self.exclude:
            pids_this_item = set()
            for h in item: # One or more BaseHeuristic instances
                s = set(h.get_events().values_list('patient_id', flat = True))
                pids_this_item = pids_this_item | s
                log.debug('%50s: %s' % (h, len(pids_this_item)))
            pids = pids - pids_this_item
        log.debug('Plausible %50s: %s' % (self.name, len(pids)))
        return pids

    def __match_plausible_patient(self, patient_pk):
        '''
        For a given plausible (meeting match()'s screening definitions) patient, 
        identified by db primary key, return EventTimeWindow objects matching
        disease requirements.
        '''
        log.debug('Examining plausible patient #%s to detect %s' % (patient_pk, self.name))
        t_windows = [] # [EventTimeWindow, EventTimeWindow, ...]
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Create all possible time windows from first set of required events
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        for h in self.require[0]: # Create EventTimeWindows for first req
            for event in h.get_events().filter(patient__pk = patient_pk):
                found_window = False # Did we find an existing window for this event?
                for win in t_windows:
                    try:
                        win.add_event(event)
                        log.debug('Added event %s to %s' % (event, win))
                        found_window = True
                    except OutOfWindow:
                        continue
                if not found_window:
                    # This event didn't fit in any existing window, so 
                    # create a new window for it.
                    win = EventTimeWindow(self.window, definition = self.name,
                        def_version = self.version, events = [event])
                    log.debug('Created %s for event %s' % (win, event))
                    t_windows.append(win)
        log.debug('Possible time windows: %s' % t_windows)
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # For each remaining set of requirements, see if we can fit the 
        # the required events into one of our time windows.  If no events fit
        # in a given window, that window does not fulfill this disease 
        # definition.
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        for req in self.require[1:]:
            new_windows = [] # EventWindows containing events for this req
            for h in req: # h is HeuristicEvent type
                events = h.get_events().filter(patient__pk = patient_pk)
                for win in t_windows:
                    found_event = False # Did we find event that fits this window?
                    for e in events:
                        try:
                            win.add_event(e)
                            log.debug('Event %s fits in %s' % (e, win))
                            found_event = True
                        except OutOfWindow:
                            log.debug('Event %s does NOT fit in %s' % (e, win))
                            continue
                    if found_event:
                        new_windows.append(win)
            discarded = set(t_windows) - set(new_windows)
            if discarded:
                log.debug('Discarding following windows, because they did meet requirement %s' % str(req))
                [log.debug('    %s' % w) for w in discarded]
            t_windows = list(new_windows)
            log.debug('Remaining valid time windows: %s' % t_windows)
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Exclude if we match exclude_past
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        for req in self.exclude_past:
            valid_windows = [] # EventWindows matching all requirements
            for h in req: # h is HeuristicEvent type
                for win in t_windows:
                    events = h.get_events().filter(patient__pk = patient_pk, date__lt = win.start)
                    if events:
                        log.debug('Window %s was excluded by past event %s' % (win, h))
                    else:
                        valid_windows.append(win)
                    t_windows = list(valid_windows)
            log.debug('Remaining valid time windows: %s' % t_windows)
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Check that we fulfill require_past
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        for req in self.require_past:
            valid_windows = [] # EventWindows matching all requirements
            for h in req: # h is HeuristicEvent type
                for win in t_windows:
                    end = win.start
                    start = win.start - self.require_past_window
                    events = h.get_events().filter(patient__pk = patient_pk, date__gte = start, date__lt = end)
                    if events:
                        win.past_events += events
                        log.debug('Window %s matches require_past %s' % (win, h))
                        valid_windows.append(win)
                    t_windows = list(valid_windows)
            log.debug('Remaining valid time windows: %s' % t_windows)
        return t_windows


    def matches(self, matches = {}):
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Now that we have screened for patients who are plausible disease
        # candidates, we individually examine them to see if they match the 
        # full battery of requirements.
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        pids = self.__get_plausible_pids()
        for pid in list(pids):
            wins = self.__match_plausible_patient(pid)
            if wins:
                try:
                    matches[pid] += wins
                except KeyError:
                    matches[pid] = wins
        return matches

    def get_all_event_names(self):
        '''
        Returns a list of the names of all heuristic events that appear in this definition
        '''
        names = []
        for req in self.require + self.require_past + self.exclude:
            names += [event.heuristic_name for event in req]
        return set(names)








class Disease(object):
    '''
    '''

    def __init__(self,
        name,
        definitions,
        # Reporting
        icd9s = [],
        icd9_days_before = 14,
        icd9_days_after = 14,
        fever = True,
        lab_loinc_nums = [],
        lab_days_before = 14,
        lab_days_after = 14,
        med_names = [],
        med_days_before = 14,
        med_days_after = 14,
        ):
        '''
        NOTE: No need to specify the LOINCs used to detect the condition, 
            unless you want them reported even when negative.  All events
            forming part of a disease's definition are reported.
        @param name:             Name of this disease definition
        @type name:              String
        @param definitions:         Criteria used to identify cases of this disease
        @type definitions:          [DiseaseDefinition, DiseaseDefinition, ...]
        @param time_window:      Events occurring within the specified time 
            window will be grouped into a single case.  If zero, all events
            will be considered part of the same case.
        @type time_window:       Integer
        @param icd9s:            Report encounters matching these ICD9s
        @type icd9s:             List of strings
        @param icd9_days_before: How many days before case to search for encounters
        @type icd9_days_before:  Integer
        @param icd9_days_after:  How many days after case to search for encounters
        @type icd9_days_after:   Integer
        @param fever:            Do we report fever, determined as temp > 100.4, rather than as ICD9?
        @type fever:              Boolean
        @param lab_loinc_nums:   Report lab results matching these LOINCs
        @type lab_loinc_nums:    List of strings
        @param lab_days_before:  How many days before case to search for labs
        @type lab_days_before:   Integer
        @param lab_days_after:   How many days after case to search for labs
        @param med_names:        Report medicines matching these names
        @type med_names:         List of strings
        @param med_days_before:  How many days before case to search for medicines
        @type med_days_before:   Integer
        @param med_days_after:   How many days after case to search for medicines
        @type med_days_after:    Integer
        '''
        assert name
        assert ' ' not in name # No spaces allowed in disease name
        assert icd9_days_before
        assert icd9_days_after
        assert lab_days_before
        assert lab_days_after
        assert med_days_before
        assert med_days_after
        self.name = name
        self.definitions = definitions
        self.icd9s = icd9s
        self.icd9_days_before = datetime.timedelta(days = icd9_days_before)
        self.icd9_days_after = datetime.timedelta(days = icd9_days_after)
        self.fever = fever
        self.lab_loinc_nums = lab_loinc_nums
        self.lab_days_before = datetime.timedelta(days = lab_days_before)
        self.lab_days_after = datetime.timedelta(days = lab_days_after)
        self.med_names = med_names
        self.med_days_before = datetime.timedelta(days = med_days_before)
        self.med_days_after = datetime.timedelta(days = med_days_after)
        self._register()

    __registry = {} # Class variable
    def _register(self):
        if self.name in self.__registry:
            raise DiseaseDefinitionAlreadyRegistered('A disease definition with the name "%s" is already registered.' % self.name)
        else:
            self.__registry[self.name] = self

    @classmethod
    def get_all_diseases(cls):
        '''
        Returns a list of all registered disease definitions.
        '''
        result = []
        keys = cls.__registry.keys()
        keys.sort()
        [result.extend([cls.__registry[k]]) for k in keys]
        log.debug('All Disease Definition instances: %s' % result)
        return result
    
    @classmethod
    def list_all_disease_names(cls):
        return cls.__registry.keys()
    
    @classmethod
    def get_disease_by_name(cls, name):
        '''
        Returns a Disease object matching the specified name, or None if no
        match is found.
        '''
        return cls.__registry.get(name, None)

    def get_cases(self):
        '''
        Returns all cases of this disease currently existing in db.  Does NOT 
        generate any new cases.
        '''
        return Case.objects.filter(condition = self.name)

    def get_all_event_names(self):
        '''
        Return list of names of all heuristic events included in this 
        disease's definition(s).
        '''
        names = []
        for d in self.definitions:
            names.extend(d.get_all_event_names())
        return set(names)

    def new_case(self, etw):
        '''
        Creates, saves, and returns a new Case object.
            #
        @type patient: esp.models.Demog
        @type etw:     EventTimeWindow
        '''
        patient = etw.events[0].patient
        case = Case()
        case.patient = patient
        case.provider = etw.events[0].content_object.provider
        case.date = etw.start
        case.condition = self.name
        case.definition = etw.definition
        case.def_version = etw.def_version
        #case.workflow_state = self.condition.ruleInitCaseStatus
        case.save()
        case.events = etw.all_events()
        case = self.update_reportable_events(case)
        case.save()
        log.info('Created new %s case #%s for patient #%s based on %s' % (self.name, case.pk, patient.pk, etw))
        return case

    def generate_cases(self):
        counter = 0            # Number of new cases generated
        log.info('Generating cases for %s' % self.name)
        existing_cases = Case.objects.filter(condition = self.name)
        # Primary keys of events already bound to a Case object:
        bound_event_pks = HeuristicEvent.objects.filter(case__in = existing_cases).values_list('pk') # ValuesListQuerySet
        bound_event_pks = [item[0] for item in bound_event_pks]
        log.debug('number of bound_events: %s' % len(bound_event_pks))
        matches = {}
        for d in self.definitions:
            matches = d.matches(matches = matches)
        for pid in matches:
            for etw in matches[pid]:
                bound = False
                for event in etw.events:
                    if event.pk in bound_event_pks:
                        log.debug('Event #%s is already bound to a case' % event.pk)
                        bound = True
                        break # Event already attached to a case
                if bound:
                    # Ignore this match, as it appears to be already bound.  Note this will cause
                    # problems if events can validly be bound to more than one case of the same disease.
                    break
                else:
                    self.new_case(etw)
                    # Add new events to list of bound events, to avoid duplicate cases.
                    bound_event_pks += [event.pk for event in etw.events]
                    counter += 1
        log.debug('Generated %s new cases of %s' % (counter, self.name))
        return counter

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
        Purges all existing cases from db, then calls generate_cases()
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
        for definition in cls.get_all_diseases():
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

    def update_reportable_events(self, case):
        '''
        Updates the reportable events for a given case, based on rules defined
            when at BaseDiseaseDefinition instantiation.  
        @param case: The case to update
        @type case:  Case
        '''
        log.debug('Updating reportable events for case %s' % case)
        patient = case.patient
        date = case.date
        if self.icd9s:
            enc_q = Q(icd9_codes__code = self.icd9s[0])
            for code in self.icd9s[1:]:
                enc_q = enc_q | Q(icd9_codes__code = code)
            if self.fever:
                enc_q = enc_q | Q(temperature__gte = 100.4)
            enc_q = enc_q & Q(patient = patient)
            enc_q = enc_q & Q(date__gte = (date - self.icd9_days_before))
            enc_q = enc_q & Q(date__lte = (date + self.icd9_days_after))
            log.debug('enc_q: %s' % enc_q)
            encounters = Encounter.objects.filter(enc_q)
            case.encounters = sets.Set(case.encounters.all()) | sets.Set(encounters)
        if self.lab_loinc_nums:
            lab_q = Q(patient = patient)
            lab_q = lab_q & Q(date__gte = (date - self.lab_days_before))
            lab_q = lab_q & Q(date__lte = (date + self.lab_days_after))
            log.debug('lab_q: %s' % lab_q)
            labs = LabResult.objects.filter_loincs(self.lab_loinc_nums).filter(lab_q)
            # Some of these lab results will be for the same test (ie same 
            # LOINC code), but Mike only wants to see one result per test.  
            # It's probably better to handle that in the case management UI,
            # where we could potentially show a history for each test, than 
            # here.
            case.lab_results = sets.Set(case.lab_results.all()) | sets.Set(labs)
        if self.med_names:
            med_q = Q(name__icontains = self.med_names[0])
            for name in self.med_names[1:]:
                med_q = med_q | Q(name__icontains = name)
            med_q = med_q & Q(patient = patient)
            med_q = med_q & Q(date__gte = (date - self.med_days_before))
            med_q = med_q & Q(date__lte = (date + self.med_days_after))
            log.debug('med_q: %s' % med_q)
            medications = Prescription.objects.filter(med_q)
            case.medications = sets.Set(case.medications.all()) | sets.Set(medications)
        # Support for reporting immunizations has not yet been implemented
        case.save()
        return case

    @classmethod
    def update_all_cases(cls):
        '''
        Updates reportable events for all existing cases
        '''
        log.info('Updating reportable events for existing cases.')
        for definition in cls.get_all_diseases():
            q_obj = Q(condition = definition.name)
            existing_cases = Case.objects.filter(q_obj)
            for case in existing_cases:
                definition.update_reportable_events(case)




#---****************************************************************************************************




class Window(object):
    '''
    A time window containing one or more events
    '''
    
    def __init__(self, days, events):
        '''
        @param days: Max number of days between events
        @type days:  Int
        @param events: Events to populate window
        @type events:  List of HeuristicEvent instances
        '''
        assert isinstance(days, int)
        self.delta = datetime.timedelta(days=days)
        self.__events = []
        self.__patient = None
        for e in events:
            assert isinstance(e, HeuristicEvent)
            if not self.__patient:
                self.__patient = e.patient
            self._check_event(e)
            self.__events += [e]
            self.__events.sort(lambda x, y: (x.date - y.date).days) # Sort by date
        self.past_events = [] 
        log.debug('Initialized %s day window with %s events' % (days, len(events)))
    
    def _check_event(self, event):
        '''
        Raises OutOfWindow exception if event does not fit within this window
        @type event:  HeuristicEvent instance
        '''
        if self.__events: # Cannot check date range if window has no events
            if not (event.date >= self.start) and (event.date <= self.end):
                raise OutOfWindow('Date outside window')
        if not self.__patient == event.patient:
            raise OutOfWindow('Patient does not match')
        
    def _get_start_date(self):
        return self.__events[-1].date - self.delta
    start = property(_get_start_date)

    def _get_end_date(self):
        return self.__events[0].date + self.delta
    end = property(_get_end_date)

    def _get_events(self):
        return self.__events
    events = property(_get_events)
    
    def _get_patient(self):
        return self.__patient
    patient = property(_get_patient)

    def fit(self, event):
        '''
        Try to fit a new event into the window.  If it fits, a *new* Window 
        instance containing new + old events is returned
        '''
        self._check_event(event)
        new_events = self.events + [event]
        return Window(days=self.delta.days, events=new_events)

    def __repr__(self):
        return 'Window %s - %s (%s events)' % (self.start, self.end, len(self.events))



class BaseEventPattern(object):
    '''
    A pattern of one or more heuristic events occurring within a specified 
    time window
    '''
    
    def plausible_patients(self):
        '''
        Returns a QuerySet of Patient records which may plausibly match this pattern
        '''
        raise NotImplementedError
        
    def plausible_events(self, patients=None):
        '''
        Returns a QuerySet of HeuristicEvent records which may plausibly match this pattern
        '''
        raise NotImplementedError
        
    def generate_windows(self, days, patients=None, exclude=None):
        '''
        Iterator yielding Window instances matching this pattern.  Matches can 
        be constrained to a given set of patients.  Events already bound to 
        exclude model are excluded.
        @param days: Length of match window
        @type days:  Integer
        @param patients: Generate windows for specified patients only
        @type patients:  ESP.emr.models.Patient QuerySet
        @param exclude: Exclude events already bound to this model
        @type exclude:  django.db.models.Model instance, which has this field:
            events = models.ManyToManyField(HeuristicEvent)
        '''
        raise NotImplementedError

    def match_window(self, reference, exclude=False):
        '''
        Returns set of zero or more windows, falling within a reference window,
        that match this pattern.
        @param reference: Reference window
        @type reference: Window instance
        @param exclude: Exclude events already bound to this model instance
        @type exclude: django.db.models.Model instance, which has this field:
            events = models.ManyToManyField(HeuristicEvent)
        @return: set of Window instances
        '''
        raise NotImplementedError
    
    def __get_string_hash(self):
        '''
        Returns a string that uniquely represents this pattern.  Cf the integer 
        returned by __hash__().
        '''
        raise NotImplementedError
    string_hash = property(__get_string_hash)


class SimpleEventPattern(BaseEventPattern):
    '''
    An event pattern consisting of only a single heuristic event type.  
    Instances of this class typically will be created internally by 
    ComplexEventPattern instances.
    '''
    
    # Class variables
    #
    # {heuristic: {patient_pk: {date: event_pk}}}
    __dated_events_cache = {} 
    # {heuristic: {condition: event_pk_set}}
    __excluded_events_cache = {}
    
    def __init__(self, heuristic):
        from ESP.hef import events # Ensure events are loaded
        if not heuristic in BaseHeuristic.list_heuristic_names():
            raise InvalidHeuristic('Unknown heuristic: %s' % heuristic)
        self.heuristic = heuristic
    
    def plausible_patients(self):
        return Patient.objects.filter(heuristicevent__heuristic_name=self.heuristic).distinct()
    
    def plausible_events(self, patients=None):
        log.debug('Building plausible events query for %s' % self)
        q_obj = Q(heuristic_name=self.heuristic)
        if patients:
            q_obj = q_obj & Q(patient__in=patients)
        return HeuristicEvent.objects.filter(q_obj)
    
    def generate_windows(self, days, patients=None, exclude_condition=None):
        log.debug('Generating windows for %s' % self)
        events = self.plausible_events(patients=patients)
        if exclude_condition:
            assert isinstance(exclude_condition, str) # Sanity checks
            cases = Case.objects.filter(condition=exclude_condition)
            pks = CaseEvents.objects.filter(case__in=cases).values_list('pk', flat=True).distinct()
            q_obj = ~Q(pk__in=pks)
            events = events.filter(q_obj)
        for e in events:
            yield Window(days=days, events=[e])
                
    def _get_dated_events(self, patient):
        '''
        Return event primary keys matching this heuristic for patient, 
            organized by date.
        @param patient: Patient for whom we want to retrieve events
        @type patient:  Patient object
        @return: {date: pk}  Dictionary matching dates to event primary keys
        '''
        log.debug('Retrieve dated %s events for patient %s' % (self.heuristic, patient))
        if not self.heuristic in self.__dated_events_cache:
            self.__dated_events_cache[self.heuristic] = {}
        cache = self.__dated_events_cache[self.heuristic]
        if patient not in cache:
            values = HeuristicEvent.objects.filter(heuristic_name=self.heuristic, patient=patient).values('pk', 'date')
            log_query('Patient not found in cache -- querying database:', values)
            patient_dates = {}
            for val in values:
                patient_dates[val['date']] = val['pk']
            cache[patient] = patient_dates
            if len(cache) >= CACHE_WARNING_THRESHOLD:
                log.warning('More than %s patients cached:  %s' % (CACHE_WARNING_THRESHOLD, len(cache)))
        return cache[patient]
    
    def _get_excluded_event_pks(self, exclude_condition):
        '''
        @param exclude_condition: Condition to exclude
        @type exclude_condition:  String
        @return: Set of integers (primary keys of excluded events)
        '''
        log.debug('Retrieve excluded event PKs for %s' % exclude_condition)
        if not self.heuristic in self.__excluded_events_cache:
            self.__excluded_events_cache[self.heuristic] = {}
        cache = self.__dated_events_cache[self.heuristic]
        if exclude_condition not in cache:
            cases = Case.objects.filter(condition=exclude_condition)
            pks = CaseEvents.objects.filter(case__in=cases).values_list('pk', flat=True).distinct()
            log_query('Excluded condition not found in cache -- querying database:', pks)
            pks = set(pks)
            cache[exclude_condition] = pks
            if len(cache) >= CACHE_WARNING_THRESHOLD:
                log.warning('More than %s excluded conditions cached:  %s' % (CACHE_WARNING_THRESHOLD, len(cache)))
        return cache[exclude_condition]
        
    def match_window(self, reference, exclude_condition=None):
        assert isinstance(reference, Window)
        dated_events = self._get_dated_events(reference.patient)
        #
        # Exclude bound events
        #
        if exclude_condition:
            ex_pks = self._get_excluded_event_pks(exclude_condition)
            for date in dated_events:
                pk = dated_events[date]
                if pk in ex_pks:
                    del dated_events[date]
        matched_windows = set()
        for event_date in dated_events:
            # If date is outside window, skip it
            if (event_date > reference.end) or (event_date < reference.start):
                continue
            event_pk = dated_events[event_date]
            event = HeuristicEvent.objects.get(pk=event_pk)
            win = reference.fit(event)
            matched_windows.add(win)
        return matched_windows
        
    def __get_string_hash(self):
        return '[%s]' % self.heuristic
    
    def __repr__(self):
        return 'SimpleEventPattern: %s' % self.heuristic


class ComplexEventPattern(BaseEventPattern):
    '''
    An event pattern composed of one or more SimpleEventPattern or 
    ComplexEventPattern instances.  
    '''
    def __init__(self, operator, patterns, require_past=[], exclude=[], exclude_past=[]):
        operator = operator.lower()
        self.__sorted_pattern_cache = None
        assert operator in ('and', 'or')
        self.operator = operator
        valid_heuristic_names = BaseHeuristic.list_heuristic_names()
        self.patterns = []
        self.exclude = []
        for pat in patterns:
            if isinstance(pat, ComplexEventPattern):
                self.patterns.append(pat)
            elif pat in valid_heuristic_names: # Implies req is a string
                pat_obj = SimpleEventPattern(heuristic=pat)
                self.patterns.append(pat_obj)
            else:
                raise InvalidRequirement('%s [%s]' % (pat, type(pat)))
        for pat in exclude:
            if isinstance(pat, ComplexEventPattern):
                self.exclude.append(pat)
            elif pat in valid_heuristic_names: # Implies req is a string
                pat_obj = SimpleEventPattern(heuristic=pat)
                self.exclude.append(pat_obj)
            else:
                raise InvalidRequirement('%s [%s]' % (pat, type(pat)))
        count = {} # Count of plausible events per req
        for name in require_past + exclude_past:
            if not name in valid_heuristic_names:
                log.error('"%s" not in valid hueristic names:' % name)
                log.error('\t%s' % valid_heuristic_names)
                raise InvalidRequirement('%s [%s]' % (name, type(name)))
        self.require_past = require_past
        self.exclude_past = exclude_past
        log.debug('Initializing new ComplexEventPattern instance')
        log.debug('    operator:    %s' % operator)
        log.debug('    patterns:    %s' % patterns)
        log.debug('    require_past:  %s' % require_past)
        log.debug('    exclude:  %s' % exclude)
        log.debug('    exclude_past:  %s' % exclude_past)
    
    def __get_string_hash(self):
        op_delim = '_%s_' % self.operator
        h = op_delim.join([str(pat.string_hash) for pat in self.patterns])
        h = '[%s]' % h
        if self.require_past:
            h += '_require_past_'
            h += '[%s]' % op_delim.join([str(pat) for pat in self.require_past])
        if self.exclude:
            h += '_exclude_'
            h += '[%s]' % op_delim.join([str(pat.string_hash) for pat in self.exclude])
        if self.exclude_past:
            h += '_exclude_past_'
            h += '[%s]' % op_delim.join([str(pat) for pat in self.exclude_past])
        return h
    
    def plausible_patients(self):
        plausible = self.patterns[0].plausible_patients()
        for pat in self.patterns[1:]:
            if self.operator == 'and':
                plausible = plausible & pat.plausible_patients()
            else: # 'or'
                plausible = plausible | pat.plausible_patients()
        for heuristic in self.require_past:
            plausible = plausible & Patient.objects.filter(heuristicevent__heuristic_name=heuristic).distinct()
        return plausible
    
    def plausible_events(self, patients=None):
        log.debug('Building plausible events query for %s' % self)
        patients = self.plausible_patients()
        plausible = self.patterns[0].plausible_events(patients=patients)
        for pat in self.patterns[1:]:
            if self.operator == 'and':
                plausible = plausible & pat.plausible_events(patients=patients)
            else: # 'or'
                plausible = plausible | pat.plausible_events(patients=patients)
        purpose = 'Querying plausible events for %s' % self
        log_query(purpose, plausible)
        return plausible
    
    def sorted_patterns(self):
        '''
        Returns the patterns composing this ComplexEventPattern sorted from 
        lowest to highest number of plausible patients
        '''
        if not self.__sorted_pattern_cache:
            #log.debug('Sorting patterns by plausible event count')
            log.debug('Sorting patterns by plausible patient count')
            plausible = self.plausible_patients()
            count = {}
            for pat in self.patterns:
                #count[pat] = pat.plausible_events(patients=plausible).count()
                count[pat] = pat.plausible_patients().count()
            #log.debug('Plausible events by pattern: \n%s' % pprint.pformat(count))
            log.debug('Plausible patients by pattern: \n%s' % pprint.pformat(count))
            self.__sorted_pattern_cache = [i[0] for i in sorted(count.items(), key=itemgetter(1))]
        return self.__sorted_pattern_cache

    def generate_windows(self, days, patients=None, exclude_condition=None):
        if not patients:
            patients = self.plausible_patients()
        if self.operator == 'and':
            # Order does not matter with 'or' operator, so only 'and' operator 
            # needs to perform expensive pattern sort.
            sorted_patterns = self.sorted_patterns()
            first_pattern = sorted_patterns[0]
            #
            # All patterns must be matched, so we start with the pattern which 
            # has fewest plausible events, and thus is likely to yield the 
            # fewest windows.  
            #
            # Starting with these reference windows, we loop through each 
            # remaining pattern.  Any windows matching all patterns are yeilded.
            for ref_win in first_pattern.generate_windows(days=days, patients=patients, exclude_condition=exclude_condition):
                queue = set([ref_win])
                for pattern in sorted_patterns[1:]:
                    matched_windows = set()
                    for win in queue:
                        matched_windows.update(pattern.match_window(win, exclude_condition=exclude_condition))
                    queue = matched_windows
                # Any windows remaining in the queue at this point have 
                # matched all patterns.
                for win in queue:
                    win = self._check_constaints(win)
                    if win:
                        yield win
        elif self.operator == 'or':
            for pattern in self.patterns:
                for win in pattern.generate_windows(days=days, patients=patients, exclude_condition=exclude_condition):
                    win = self._check_constaints(win)
                    if win:
                        yield win
        else:
            raise 'Invalid self.operator -- WTF?!'
    
    def match_window(self, reference, exclude_condition=None):
        sorted_patterns = self.sorted_patterns()
        # Queue up the reference window to be checked against patterns.  We use 
        # a set instead of a list to avoid double-adding the reference window
        # when evaluating with 'or' operator.
        queue = set([reference]) 
        for pattern in sorted_patterns:
            # When operator is 'or', even if the previous pattern didn't match 
            # anything, we're still going to try matching the remaining patterns 
            # against the reference window.
            if self.operator == 'or':
                queue.update([reference])
            matched_windows = set()
            for win in queue:
                matched_windows.update(pattern.match_window(win, exclude_condition=exclude_condition))
            queue = matched_windows
        valid = set()
        for win in queue:
            win = self._check_constaints(win)
            if win:
                valid.add(win)
        return valid
    
    def _check_constaints(self, win):
        '''
        Checks a Window object against 'require_past', 'exclude', and
        'exclude_past' constraints.  Returns window if all constraints are
        passed; otherwise returns False.  If a 'require_past' constraint is
        passed, relevant past events are added to the Window object's
        past_events list.
        @param win: Window to check
        @type win:  Window instance
        '''
        if self.exclude_past:
            exclude_q = Q(patient=win.patient, heuristic_name__in=self.exclude_past, date__lt=win.start)
            query = HeuristicEvent.objects.filter(exclude_q)
            log_query('Check exclude_past', query)
            if  query.count() > 0:
                log.debug('Patient %s excluded by %s past events' % (win.patient, query.count()))
                return False
        if self.require_past:
            require_q = Q(patient=win.patient, heuristic_name__in=self.require_past, date__lt=win.start)
            query = HeuristicEvent.objects.filter(require_q)
            log_query('Check require_past', query)
            if query.count() == 0:
                log.debug('Patient %s excluded by lack of required past events' % win.patient)
                return False
            else:
                win.past_events += [e for e in HeuristicEvent.objects.filter(require_q)]
        #
        # Since self.exclude can include ComplexEventPatterns, it is by far the
        # most computationally expensive constraint check.  So we test it only 
        # after all other constraints have passed.
        #
        for pat in self.exclude:
            # If any pattern matches, this constraint fails
            if pat.match_window(win):
                log.debug('Patient %s excluded by pattern %s' % (win.patient, pat))
                return False
        #
        # If we made it this far, we have passed all constraints.  
        #
        log.debug('Patient %s passes constraint checks' % win.patient)
        return win
    
