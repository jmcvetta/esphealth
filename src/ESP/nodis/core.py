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

from django.db import connection
from django.db.models import Q
from django.db.models import F
from django.db.models import Sum
from django.db.models.query import QuerySet
from django.contrib.contenttypes.models import ContentType


from ESP import settings
from ESP.utils import utils as util
from ESP.utils.utils import log
from ESP.emr.models import LabResult
from ESP.emr.models import Encounter
from ESP.emr.models import Prescription
from ESP.emr.models import Immunization
from ESP.emr.models import Patient
from ESP.emr.models import Provider
from ESP.hef.models import HeuristicEvent
from ESP.conf.models import Rule
from ESP.nodis.models import Case



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


class EventTimeWindow(object):
    '''
    A potential case.
    '''
    def __init__(self, window, definition, def_version, events=[]):
        '''
        @param window: Number of days in this time window
        @type window: Int
        @param definition: Name of disease definition that generated this window
        @type definition: String
        @param def_version: Version of disease definition that generated this window
        @type def_version: Int
        @param events: Events that defined this window
        @type events: List of HeuristicEvent objects
        '''
        assert isinstance(window, datetime.timedelta)
        self.__window = window
        self.__events = events
        self.definition = definition # Name of definition that generated this ETW
        self.def_version = def_version
        self.past_events = [] # Past events that validate this windo
    
    def _get_start_date(self):
        return self.__events[-1].date - self.__window
    start = property(_get_start_date)
    
    def _get_end_date(self):
        return self.__events[0].date + self.__window
    end = property(_get_end_date)
    
    def _get_events(self):
        return self.__events
    events = property(_get_events)
    
    def add_event(self, event):
        if len(self.__events) == 0:
            self.__events = [event]
        elif (event.date >= self.start) and (event.date <= self.end):
            self.__events += [event]
            self.__events.sort(lambda x,y: (x.date-y.date).days) # Sort by date
        else:
            raise OutOfWindow
    
    def all_events(self):
        return self.events + self.past_events
        
    def __repr__(self):
        return 'Window %s - %s (%s events)' % (self.start, self.end, len(self.all_events()))
 


class DiseaseDefinition(object):
    '''
    One set of rules for algorithmically defining a disease.  Satisfying a 
    single disease definition is sufficient to indicate a case of that disease, 
    but a given disease may have arbitrarily many definitions.
    '''
    def __init__(self,  name, version, window, require, require_past = [], require_past_window = None,
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
    
    def __match_plausible_patient(self, patient_pk):
        '''
        For a given plausible (meeting match()'s screening definitions) patient, 
        identified by db primary key, return EventTimeWindow objects matching
        disease requirements.
        '''
        t_windows = [] # [EventTimeWindow, EventTimeWindow, ...]
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Create all possible time windows from first set of required events
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        for h in self.require[0]: # Create EventTimeWindows for first req
            for event in h.get_events().filter(patient__pk=patient_pk):
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
                    win = EventTimeWindow(self.window, definition=self.name, 
                        def_version=self.version, events=[event])
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
                events = h.get_events().filter(patient__pk=patient_pk)
                for win in t_windows:
                    found_event = False # Did we find event that fits this window?
                    for e in events:
                        try:
                            win.add_event(e)
                            log.debug('Event %s fits in %s' % (e, win))
                            found_event = True
                        except OutOfWindow:
                            continue
                    if found_event:
                        new_windows.append(win)
            t_windows = list(new_windows)
            log.debug('Remaining valid time windows: %s' % t_windows)
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Exclude if we match exclude_past
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        for req in self.exclude_past:
            valid_windows = [] # EventWindows matching all requirements
            for h in req: # h is HeuristicEvent type
                for win in t_windows:
                    events = h.get_events().filter(patient__pk=patient_pk, date__lt=win.start)
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
                    events = h.get_events().filter(patient__pk=patient_pk, date__gte=start, date__lt=end)
                    if events:
                        win.past_events += events
                        log.debug('Window %s matches require_past %s' % (win, h))
                        valid_windows.append(win)
                    t_windows = list(valid_windows)
            log.debug('Remaining valid time windows: %s' % t_windows)
        # DEBUG:
        #for win in t_windows:
            #print '+' * 80
            #print win
            #for e in win.events:
                #print '\t%s' % e
        # /DEBUG
        return t_windows
            
    def matches(self, begin_date=None, end_date=None, matches={}):
        '''
        @param matches: A match dictionary, in the same format as this 
            function returns.  New matches are added to this dictionary, and 
            the combined dict returned.
        @type matches:  {Demog: [EventTimeWindow, EventTimeWindow, ...], ...}
        @return:        {Demog: [EventTimeWindow, EventTimeWindow, ...], ...}
        '''
        log.info('Finding matches for %s' % self.name)
        #
        # Examine only the time slice specified
        #
        all_events = HeuristicEvent.objects.all()
        if begin_date:
            all_events = all_events.filter(date__gte=begin_date)
        if end_date:
            all_events = all_events.filter(date__lte=end_date)
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # First we do some simple queries and set arithmetic to generate a list
        # of patients who *could* have the disease.
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #
        # 'pids' are patient IDs -- db primary keys
        for req in (self.require + self.require_past):
            pids_this_req = set()
            for h in req: # One or more BaseHeuristic instances
                s = set(h.get_events().values_list('patient_id', flat=True))
                pids_this_req = pids_this_req | s 
                log.debug('%50s: %s' % (h, len(pids_this_req)) )
            try:
                pids = pids & pids_this_req
            except UnboundLocalError:
                pids = pids_this_req
        for item in self.exclude:
            pids_this_item = set()
            for h in item: # One or more BaseHeuristic instances
                s = set(h.get_events().values_list('patient_id', flat=True))
                pids_this_item = pids_this_item | s 
                log.debug('%50s: %s' % (h, len(pids_this_item)) )
            pids = pids - pids_this_item
        log.debug('Plausible %50s: %s' % (self.name, len(pids)) )
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Now that we have screened for patients who are plausible disease
        # candidates, we individually examine them to see if they match the 
        # full battery of requirements.
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        for pid in list(pids):
            wins = self.__match_plausible_patient(pid)
            if wins:
                try:
                    matches[pid] += wins
                except KeyError:
                    matches[pid] = wins
        return matches
    
        
            
            


 
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
        self.name = name
        self.definitions = definitions
        self.icd9s = icd9s
        self.icd9_days_before = datetime.timedelta(days=icd9_days_before)
        self.icd9_days_after = datetime.timedelta(days=icd9_days_after)
        self.fever = fever
        self.lab_loinc_nums = lab_loinc_nums
        self.lab_days_before = datetime.timedelta(days=lab_days_before)
        self.lab_days_after = datetime.timedelta(days=lab_days_after)
        self.med_names = med_names
        self.med_days_before = datetime.timedelta(days=med_days_before)
        self.med_days_after = datetime.timedelta(days=med_days_after)
        #
        # Sanity checks
        #
        assert self.name 
        assert self.icd9_days_before
        assert self.icd9_days_after
        assert self.lab_days_before
        assert self.lab_days_after
        assert self.med_days_before
        assert self.med_days_after
        #self.condition = Rule.objects.get(ruleName=self.name)
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
    def get_disease_by_name(cls, name):
        '''
        Returns a Disease object matching the specified name, or None if no
        match is found.
        '''
        return cls.__registry.get(name, None)
    
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
        '''
        Calls the user-supplied case factory with appropriate arguments
        '''
        counter = 0            # Number of new cases generated
        log.info('Generating cases for %s' % self.name)
        existing_cases = Case.objects.filter(condition=self.name)
        # Primary keys of events already bound to a Case object:
        bound_event_pks = HeuristicEvent.objects.filter(case__in=existing_cases).values_list('pk') # ValuesListQuerySet
        bound_event_pks = [item[0] for item in bound_event_pks]
        log.debug('number of bound_events: %s' % len(bound_event_pks))
        matches = {}
        for d in self.definitions:
            matches = d.matches(matches=matches)
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
    
    
    @classmethod
    def generate_all_cases(cls, begin_date=None, end_date=None):
        '''
        Generates cases for all registered disease definitions.
            #
        @param begin_date: Beginning of time window to examine
        @type begin_date:  datetime.date
        @param end_date:   End of time window to examine
        @type end_date:    datetime.date
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
            enc_q = Q(icd9_codes__code=self.icd9s[0])
            for code in self.icd9s[1:]:
                enc_q = enc_q | Q(icd9_codes__code=code)
            if self.fever: 
                enc_q = enc_q | Q(temperature__gte=100.4)
            enc_q = enc_q & Q(patient=patient)
            enc_q = enc_q & Q(date__gte=(date - self.icd9_days_before))
            enc_q = enc_q & Q(date__lte=(date + self.icd9_days_after))
            log.debug('enc_q: %s' % enc_q)
            encounters = Encounter.objects.filter(enc_q)
            case.encounters = sets.Set(case.encounters.all()) | sets.Set(encounters)
        if self.lab_loinc_nums:
            lab_q = Q(patient=patient)
            lab_q = lab_q & Q(date__gte=(date - self.lab_days_before))
            lab_q = lab_q & Q(date__lte=(date + self.lab_days_after))
            log.debug('lab_q: %s' % lab_q)
            labs = LabResult.objects.filter_loincs(self.lab_loinc_nums).filter(lab_q)
            # Some of these lab results will be for the same test (ie same 
            # LOINC code), but Mike only wants to see one result per test.  
            # It's probably better to handle that in the case management UI,
            # where we could potentially show a history for each test, than 
            # here.
            case.lab_results = sets.Set(case.lab_results.all()) | sets.Set(labs)
        if self.med_names:
            med_q = Q(name__icontains=self.med_names[0])
            for name in self.med_names[1:]:
                med_q = med_q | Q(name__icontains=name)
            med_q = med_q & Q(patient=patient)
            med_q = med_q & Q(date__gte=(date - self.med_days_before))
            med_q = med_q & Q(date__lte=(date + self.med_days_after))
            log.debug('med_q: %s' % med_q)
            medications = Prescription.objects.filter(med_q)
            case.medications = sets.Set(case.medications.all()) | sets.Set(medications)
        # Support for reporting immunizations has not yet been implemented
        case.save()
        return case
    
    @classmethod
    def update_all_cases(cls, begin_date=None, end_date=None):
        '''
        Updates reportable events for all existing cases
        @param begin_date: Analyze cases with dates greater than begin_date
        @type begin_date:  datetime.date
        @param end_date:   Analyze cases with dates less than end_date
        @type end_date:    datetime.date
        '''
        log.info('Updating reportable events for existing cases.')
        for definition in cls.get_all_diseases():
            q_obj = Q(condition=definition.name)
            if begin_date:
                q_obj = q_obj & Q(date__gte=begin_date)
            if end_date:
                q_obj = q_obj & Q(date__lte=end_date)
            existing_cases = Case.objects.filter(q_obj)
            for case in existing_cases:
                definition.update_reportable_events(case)
