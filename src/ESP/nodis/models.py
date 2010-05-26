'''
                                  ESP Health
                         Notifiable Diseases Framework
                                  Data Models
'''

CACHE_WARNING_THRESHOLD = 100 # Log warning when cache exceeds this many patients
EXCLUDE_XB_NAMES = False # Exclude patients whose names start with 'Xb' -- test patients


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
from django.db.models import Model
from django.db.models import Count
from django.db.models.query import QuerySet
from django.contrib.contenttypes.models import ContentType


from ESP import settings
from ESP.hef import events # Ensure events are loaded
from ESP.utils import utils as util
from ESP.utils.utils import log
from ESP.utils.utils import log_query
from ESP.static.models import Icd9
from ESP.conf.models import STATUS_CHOICES
from ESP.conf.models import CodeMap
from ESP.conf.models import ReportableLab
from ESP.conf.models import ReportableIcd9
from ESP.conf.models import ReportableMedication
from ESP.conf.models import IgnoredCode
from ESP.emr.models import LabResult
from ESP.emr.models import Encounter
from ESP.emr.models import Prescription
from ESP.emr.models import Immunization
from ESP.emr.models import Patient
from ESP.emr.models import Provider
from ESP.hef import events
from ESP.hef.core import BaseHeuristic
from ESP.hef.core import EncounterHeuristic
from ESP.hef.core import MedicationHeuristic
from ESP.hef.core import TimespanHeuristic
from ESP.hef.models import Timespan
from ESP.hef.models import Event
from ESP.conf.models import ConditionConfig

import datetime

from django.db import models
from django.db.models import Q

from ESP.emr.models import Encounter
from ESP.emr.models import Immunization
from ESP.emr.models import LabResult
from ESP.emr.models import Patient
from ESP.emr.models import Prescription
from ESP.emr.models import Provider
from ESP.hef.models import Event

from ESP.utils.utils import log
from ESP.utils.utils import log_query


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

class OutOfWindow(NodisException):
    '''
    Raised when attempting to add an event to EventTimeWindow, where the 
    event's date falls outside the window.
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




class Window(object):
    '''
    A time window containing one or more events
    '''
    
    def __init__(self, days, events):
        '''
        @param days: Max number of days between events
        @type days:  Int
        @param events: Events to populate window
        @type events:  List of Event instances
        '''
        assert isinstance(days, int)
        self.delta = datetime.timedelta(days=days)
        self.__events = []
        self.__patient = None
        for e in events:
            assert isinstance(e, Event)
            if not self.__patient:
                self.__patient = e.patient
            self._check_event(e)
            self.__events += [e]
        self.events_after = None
        self.events_before = None
        self.events_ever = None
        win_size = self.end - self.start
        assert win_size.days >= 0
        log.debug('Initialized %s day window # %s with %s events' % (win_size.days, id(self), len(events)))
        for e in events:
            log.debug('    %s' % e)
    
    def _check_event(self, event):
        '''
        Raises OutOfWindow exception if event does not fit within this window
        @type event:  Event instance
        '''
        out = False
        if self.__events: # Cannot check date range if window has no events
            if (event.date < self.start) or (event.date > self.end):
                out = 'Date outside window'
        if not self.__patient == event.patient:
            out = 'Patient does not match'
        if out:
            log.debug('Out of window: %s' % out)
            raise OutOfWindow(out)
        
    def _get_start_date(self):
        '''Start of the time window'''
        self.__events.sort(lambda x, y: (x.date - y.date).days) # Sort by date
        return self.__events[-1].date - self.delta
    start = property(_get_start_date)

    def _get_end_date(self):
        '''End of the time window'''
        self.__events.sort(lambda x, y: (x.date - y.date).days) # Sort by date
        return self.__events[0].date + self.delta
    end = property(_get_end_date)
    
    def __get_date(self):
        '''Return date of earliest event in window'''
        return self.__events[0].date
    date = property(__get_date)

    def _get_events(self):
        return self.__events
    events = property(_get_events)
    
    def _get_patient(self):
        return self.__patient
    patient = property(_get_patient)

    def fit(self, event):
        '''
        Try to fit a new event into the window.  If it fits, a *new* Window 
            instance containing new + old events is returned.  If window does
            not fit, OutOfWindow exception is raised.
        @param event: Try to fit event into window
        @type event:  Event
        '''
        log.debug('Fitting %s to %s' % (event, self))
        log.debug('  Events already in this window:')
        for e in self.__events:
            log.debug('    %s' % e)
        self._check_event(event)
        new_events = self.events + [event]
        log.debug('Returning new window:')
        return Window(days=self.delta.days, events=new_events)
    
    def __repr__(self):
        return 'Window %s (%s events %s - %s patient %s)' % (id(self), len(self.__events), self.start, self.end, self.patient.pk)
        
    def overlaps(self, dates, recurance_interval):
        '''
        Test whether window overlaps a set of reference dates.  If the window
        occurs on or after a date in the set, but before the recurance interval
        has passed, then it is considered to overlap.  
        @param reference: Dates to check for overlap
        @type reference: Iterable set of datetime.date objects
        @param recurance_interval: Number of days from case until a condition can recur
        @type recurance_interval:  Integer
        @return: Boolean -- True if window overlaps reference dates
        '''
        log.debug('Checking window %s for overlap' % self)
        log.debug('Reference dates: %s' % dates)
        delta = datetime.timedelta(days=recurance_interval)
        for ref_date in dates:
            recur_date = ref_date + delta
            if (self.date >= ref_date) and (self.date <= recur_date):
                return True
        return False
    
    def __cmp__(self, other):
        '''
        Sort first by date.  If both windows have the same date, then sort by descending number of events
        '''
        if self.date == other.date:
            return len(other.events) - len(self.events)
        else:
            return (self.date - other.date).days



class BaseEventPattern(object):
    '''
    A pattern of one or more heuristic events occurring within a specified 
    time window
    '''
    
    def plausible_patients(self, exclude_condition=None):
        '''
        Returns a QuerySet of Patient records which may plausibly match this pattern
        @param exclude_condition: Exclude events already bound to cases of this condition
        @type exclude_condition:  String naming a Condition
        '''
        raise NotImplementedError
        
    def plausible_events(self, patients=None, exclude_condition=None):
        '''
        Returns a QuerySet of Event records which may plausibly match this pattern
        '''
        raise NotImplementedError
        
    def generate_windows(self, days, patients=None, exclude_condition=None):
        '''
        Iterator yielding Window instances matching this pattern.  Matches can 
        be constrained to a given set of patients.  Events already bound to 
        exclude model are excluded.
        @param days: Length of match window
        @type days:  Integer
        @param patients: Generate windows for specified patients only
        @type patients:  ESP.emr.models.Patient QuerySet
        @param exclude_condition: Exclude events already bound to cases of this condition
        @type exclude_condition:  String naming a Condition
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
            events = models.ManyToManyField(Event)
        @return: set of Window instances
        '''
        raise NotImplementedError
    
    def __get_string_hash(self):
        '''
        Returns a string that uniquely represents this pattern.  Cf the integer 
        returned by __hash__().
        '''
        raise NotImplementedError
    
    def __get_event_names(self):
        '''
        Returns the set of heuristics Event names required by any component of this pattern
        '''
        raise NotImplementedError


class SimpleEventPattern(BaseEventPattern):
    '''
    An event pattern consisting of only a single heuristic event type.  
    Instances of this class typically will be created internally by 
    ComplexEventPattern instances.
    '''
    
    # Class variables
    #
    # {heuristic: {condition: event_pk_set}}
    __excluded_events_cache = {}
    
    def __init__(self, event_name, require_timespan=[], exclude_timespan=[]):
        self.__events_cache = {}
        #
        # Sanity Checks
        #
        if not event_name in BaseHeuristic.all_event_names():
            raise InvalidHeuristic('Unknown heuristic Event: %s' % event_name)
        for tspan_name in require_timespan + exclude_timespan:
            if not tspan_name in TimespanHeuristic.all_event_names():
                raise InvalidHeuristic('Unknown TimespanHeuristic: %s' % tspan_name)
        #
        #
        self.event_name = event_name
        self.require_timespan = require_timespan
        self.exclude_timespan = exclude_timespan
            
    
    def plausible_patients(self, exclude_condition=None):
        q_obj = Q(event__name=self.event_name)
        if exclude_condition:
            q_obj = q_obj & ~Q(case__condition=exclude_condition)
        for tspan_name in self.require_timespan:
            q_obj = q_obj & Q(timespan__name=tspan_name)
        qs = Patient.objects.filter(q_obj).distinct()
        log_query('Plausible patients for %s, exclude %s' % (self, exclude_condition), qs)
        return qs
    
    def plausible_events(self, patients=None, exclude_condition=None):
        log.debug('Building plausible events query for %s' % self)
        q_obj = Q(name=self.event_name)
        if patients:
            q_obj = q_obj & Q(patient__in=patients)
        if exclude_condition:
            q_obj = q_obj & ~Q(case__condition=exclude_condition)
        events = Event.objects.filter(q_obj)
        for tspan in self.require_timespan:
            events = events.extra(
                tables = ['hef_timespan'],
                select = {
                    'ts_name': 'hef_timespan.name',
                    },
                where = [
                    'hef_timespan.patient_id = hef_event.patient_id',
                    'hef_timespan.start_date <= hef_event.date',
                    'hef_timespan.end_date >= hef_event.date',
                    'hef_timespan.name = %s',
                    ],
                params = [tspan],
                ).distinct()
        for tspan in self.exclude_timespan:
            raise NotImplementedError()
        log_query('Querying plausible events for %s' % self, events)
        return events

    def generate_windows(self, days, patients=None, exclude_condition=None):
        log.debug('Generating windows for %s' % self)
        events = self.plausible_events(patients=patients, exclude_condition=exclude_condition)
        for e in events:
            for tspan in self.require_timespan:
                if not Timespan.objects.filter(patient=e.patient, start_date__lte=e.date, end_date__gte=e.date).count():
                    continue # Event does not fall within required timespans
            for tspan in self.exclude_timespan:
                if Timespan.objects.filter(patient=e.patient, start_date__lte=e.date, end_date__gte=e.date).count():
                    continue # Event falls within an excluded timespan
            yield Window(days=days, events=[e])
                
    def match_window(self, reference, exclude_condition=None):
        assert isinstance(reference, Window)
        patient = reference.patient
        cache = self.__events_cache
        key = (patient, exclude_condition)
        if not key in cache:
            q_obj = Q(patient=patient)
            q_obj &= Q(name=self.event_name)
            if exclude_condition:
                q_obj &= ~Q(case__condition=exclude_condition)
            qs = Event.objects.filter(q_obj)
            log_query('Events for heuristic event %s, patient %s, excluding %s' % (self.event_name, patient, exclude_condition), qs)
            cache[key] = qs
        matched_windows = set()
        event_qs = cache[key]
        for e in event_qs:
            for tspan in self.require_timespan:
                if not Timespan.objects.filter(patient=e.patient, start_date__lte=e.date, end_date__gte=e.date).count():
                    continue # Event does not fall within required timespans
            for tspan in self.exclude_timespan:
                if Timespan.objects.filter(patient=e.patient, start_date__lte=e.date, end_date__gte=e.date).count():
                    continue # Event falls within an excluded timespan
            try:
                win = reference.fit(e)
                matched_windows.add(win)
            except OutOfWindow:
                continue
        return matched_windows
    
    def __get_string_hash(self):
        return '%s' % self.event_name
    string_hash = property(__get_string_hash)
    
    def __repr__(self):
        return 'SimpleEventPattern: %s' % self.event_name
    
    def __get_event_names(self):
        return set([self.event_name])
    event_names = property(__get_event_names)
        
class TimespanPattern(object):
    '''
    A pattern matching a Timespan instance.  
    
    Note, this is NOT a child of BaseEventPattern, because it does not relate
    to Event instances.
    '''
    def __init__(self, timespans):
        raise NotImplementedError
        
    def plausible_patients(self, exclude_condition=None):
        q_obj = Q(timespan__pk__isnull=False)
        if exclude_condition:
            q_obj = q_obj & ~Q(case__condition=exclude_condition)
        qs = Patient.objects.filter(q_obj)
        log_query('Plausible patients for %s, exclude %s' % (self, exclude_condition), qs)
        return qs
            
    def plausible_events(self, patients=None, exclude_condition=None):
        '''
        NOTE: This function returns Timespan instances, not Event instances!
        '''
        # Not sure if this should be implemented this way, since we're dealing 
        # with Timespan instances, not Event instances.
        q_obj = Q(name=self.event_name)
        if patients:
            q_obj = q_obj & Q(patient__in=patients)
        if exclude_condition:
            q_obj = q_obj & ~Q(case__condition=exclude_condition)
        events = Timespan.objects.filter(q_obj)
        log_query('Querying plausible events for %s' % self, events)
        return events
    
    def generate_windows(self, days, patients=None, exclude_condition=None):
        log.debug('Generating windows for %s' % self)
        events = self.plausible_events(patients=patients, exclude_condition=exclude_condition)
        for e in events:
            yield Window(days=days, events=[e])
                
    def match_window(self, reference, exclude_condition=None):
        raise NotImplementedError
    
    def __get_string_hash(self):
        raise NotImplementedError
    string_hash = property(__get_string_hash)
    
    def __repr__(self):
        raise NotImplementedError
    
    def __get_event_names(self):
        raise NotImplementedError
    event_names = property(__get_event_names)

    

class MultipleEventPattern(BaseEventPattern):
    '''
    An event pattern that matches when a patient has a specified number of 
    positive results from a pool of potential tests.
    @param events: List of heuristic 
    '''
    
    def __init__(self, events, count,  require_timespan=[], exclude_timespan=[]):
        #self.__events_cache = {}
        for event_name in events:
            if not event_name in BaseHeuristic.all_event_names():
                raise InvalidHeuristic('Unknown heuristic Event: %s' % event_name)
        self.events = events
        if not isinstance(count, int):
            raise TypeError('count must be an integer, but you supplied: "%s"' % count)
        self.count = count
        #
        # TODO: What kind of sanity checking do we need for Timespans??
        #
        self.require_timespan = require_timespan
        self.exclude_timespan = exclude_timespan
    
    def plausible_patients(self, exclude_condition=None):
        '''
        Returns a QuerySet of Patient records which may plausibly match this pattern
        @param exclude_condition: Exclude events already bound to cases of this condition
        @type exclude_condition:  String naming a Condition
        '''
        q_obj = Q(event__name__in=self.events)
        qs = Patient.objects.filter(q_obj).distinct()
        log_query('Plausible patients for %s, exclude %s' % (self, exclude_condition), qs)
        return qs
        
    def plausible_events(self, patients=None, exclude_condition=None):
        '''
        Returns a QuerySet of Event records which may plausibly match this pattern
        '''
        log.debug('Building plausible events query for %s' % self)
        q_obj = Q(name__in=self.events)
        if patients:
            q_obj = q_obj & Q(patient__in=patients)
        if exclude_condition:
            q_obj = q_obj & ~Q(case__condition=exclude_condition)
        events = Event.objects.filter(q_obj)
        log_query('Querying plausible events for %s' % self, events)
        return events
        
    def generate_windows(self, days, patients=None, exclude_condition=None):
        '''
        Iterator yielding Window instances matching this pattern.  Matches can 
        be constrained to a given set of patients.  Events already bound to 
        exclude model are excluded.
        @param days: Length of match window
        @type days:  Integer
        @param patients: Generate windows for specified patients only
        @type patients:  ESP.emr.models.Patient QuerySet
        @param exclude_condition: Exclude events already bound to cases of this condition
        @type exclude_condition:  String naming a Condition
        '''
        log.debug('Generating windows for %s' % self)
        events = self.plausible_events(patients=patients, exclude_condition=exclude_condition)
        patient_dates = events.values('patient', 'date').distinct().annotate(count=Count('name')).filter(count__gte=2)
        for pd in patient_dates:
            patient = pd['patient']
            event_date = pd['date']
            pd_events = self.plausible_events(exclude_condition=exclude_condition).filter(patient=patient, date=event_date)
            if pd_events: yield Window(days=days, events=pd_events)

    def match_window(self, reference, exclude_condition=None):
        '''
        Returns set of zero or more windows, falling within a reference window,
        that match this pattern.
        @param reference: Reference window
        @type reference: Window instance
        @param exclude: Exclude events already bound to this model instance
        @type exclude: django.db.models.Model instance, which has this field:
            events = models.ManyToManyField(Event)
        @return: set of Window instances
        '''
        assert isinstance(reference, Window)
        patient = reference.patient
        events = self.plausible_events(patients=[patient], exclude_condition=exclude_condition)
        valid_dates = events.values('date').distinct().annotate(count=Count('name')).filter(count__gte=2)
        # 
        # Not sure if we should do caching here, as in SimpleEventPattern.match_window()
        #
        matched_windows = set()
        for date in valid_dates:
            dated_events = events.filter(date=date)
            win = reference
            try:
                for event in dated_events:
                    win = win.fit(event)
            except OutOfWindow:
                continue
            matched_windows.add(win)
        return matched_windows
    
    def __get_string_hash(self):
        '''
        Returns a string that uniquely represents this pattern.  Cf the integer 
        returned by __hash__().
        '''
        events_string = ', '.join(self.events)
        h = '(AT LEAST %s OF %s)' % (self.count, events_string)
        return h
    string_hash = property(__get_string_hash)
    
    def __get_event_names(self):
        '''
        Returns the set of heuristics Event names required by any component of this pattern
        '''
        raise NotImplementedError



class ComplexEventPattern(BaseEventPattern):
    '''
    An event pattern composed of one or more SimpleEventPattern or 
    ComplexEventPattern instances.  
    '''
    def __init__(self, operator, patterns, name=None, 
        require_before=[], require_before_window=None, 
        require_after=[], require_after_window=None, 
        require_ever=[], require_timespan=[],
        exclude=[], exclude_past=[], exclude_timespan=[],
        ):
        '''
        @param operator: Logical operator for combining patterns 
        @type operator:  String ('and' or 'or')
        @param patterns: Patterns to search for
        @type patterns:  Dict of Strings naming heuristic Event, or ComplexEventPattern instance
        @param name: Name of this pattern (optional)
        @type name:  String
        @param require_before:         Require these events in past
        @type require_before:          Dict of Strings naming a heuristic Event that must have occurred before event window
        @param require_before_window:  Limit require_before look back to this many days before event window
        @type require_before_window:   Integer (number of days)
        @param require_after:          Require these events in past
        @type require_after:           Dict of Strings naming heuristic Event that must have occurred after event window
        @param require_after_window:   Limit require_after look back to this many days after event window
        @type require_after_window:    Integer (number of days)
        @param require_ever:           Dict of Strings naming event that must have occurred at some point, irrelevant of when
        @type require_ever:            Integer (number of days)
        @type require_timespan:        Events matching thsi pattern must have occurred within these timespans
        @param require_timespan:       Dict of strings naming timespans during which pattern match is valid
        @param exclude:                Exclude this pattern within match window
        @type exclude:                 Dict of String naming heuristic Event, or ComplexEventPattern instance
        @param exclude_past:           Exclude these events in past
        @type exclude_past:            Dict Strings naming a heuristic Event
        @type exclude_timespan:        Events matching thsi pattern must have occurred within these timespans
        @param exclude_timespan:       Dict of strings naming timespans during which pattern match is valid
        '''
        operator = operator.lower()
        self.__sorted_pattern_cache = None
        assert operator in ('and', 'or')
        self.operator = operator
        valid_event_names = BaseHeuristic.all_event_names()
        self.patterns = []
        self.name = name # Optional name
        self.exclude = []
        for pat in patterns:
            if isinstance(pat, (ComplexEventPattern, MultipleEventPattern)):
                self.patterns.append(pat)
            elif pat in valid_event_names: # Implies req is a string
                pat_obj = SimpleEventPattern(event_name=pat, require_timespan=require_timespan, exclude_timespan=exclude_timespan)
                self.patterns.append(pat_obj)
            else:
                raise InvalidPattern('%s [%s]' % (pat, type(pat)))
        for pat in exclude:
            if isinstance(pat, ComplexEventPattern):
                self.exclude.append(pat)
            elif pat in valid_event_names: # Implies req is a string
                pat_obj = SimpleEventPattern(event_name=pat, require_timespan=require_timespan, exclude_timespan=exclude_timespan)
                self.exclude.append(pat_obj)
            else:
                raise InvalidPattern('%s [%s]' % (pat, type(pat)))
        count = {} # Count of plausible events per req
        for name in require_before + require_after + require_ever + exclude_past:
            if not name in  valid_event_names:
                log.error('"%s" not in valid heuristic Event names:' % name)
                log.error('\t%s' % valid_event_names)
                raise InvalidPattern('%s [%s]' % (name, type(name)))
        self.require_before = require_before
        self.require_after = require_after
        self.require_ever = require_ever
        if require_before_window:
            self.require_before_window = datetime.timedelta(days=require_before_window)
        else:
            self.require_before_window = None
        if require_after_window:
            self.require_after_window = datetime.timedelta(days=require_after_window)
        else:
            self.require_after_window = None
        self.exclude_past = exclude_past
        #
        # TODO: What kind of sanity checking do we need for Timespans??
        #
        self.require_timespan = require_timespan
        self.exclude_timespan = exclude_timespan
        #
        self.__pattern_obj = None # Cache 
        log.debug('Initializing new ComplexEventPattern instance')
        log.debug('    operator:    %s' % operator)
        log.debug('    patterns:    %s' % patterns)
        log.debug('    require_before:  %s' % require_before)
        log.debug('    require_before_window:  %s' % require_before_window)
        log.debug('    require_after:  %s' % require_after)
        log.debug('    require_after_window:  %s' % require_after_window)
        log.debug('    require_ever:  %s' % require_ever)
        log.debug('    exclude:  %s' % exclude)
        log.debug('    exclude_past:  %s' % exclude_past)
    
    def __get_string_hash(self):
        op_delim = ' %s ' % self.operator
        h = op_delim.join([pat.string_hash for pat in self.patterns])
        if self.exclude:
            h += ' EXCLUDE '
            if len(self.exclude) > 1:
                h += '(%s)' % ' or '.join([pat.string_hash for pat in self.exclude])
            else:
                h += '%s' % self.exclude[0].string_hash
        if self.require_before:
            h += ' REQUIRE BEFORE '
            if len(self.require_before) > 1:
                h += '(%s)' % op_delim.join([str(pat) for pat in self.require_before])
            else:
                h += '%s' % self.require_before[0]
            if self.require_before_window:
                h += ' WITHIN %s DAYS ' % self.require_before_window.days
        if self.require_after:
            h += ' REQUIRE AFTER '
            if len(self.require_after) > 1:
                h += '(%s)' % op_delim.join([str(pat) for pat in self.require_after])
            else:
                h += '%s' % self.require_after[0]
            if self.require_after_window:
                h += ' WITHIN %s DAYS ' % self.require_after_window.days
        if self.require_ever:
            h += ' REQUIRE EVER '
            if len(self.require_ever) > 1:
                h += '(%s)' % op_delim.join([str(pat) for pat in self.require_ever])
            else:
                h += '%s' % self.require_ever[0]
        if self.exclude_past:
            h += ' EXCLUDE PAST '
            if len(self.exclude_past) > 1:
                h += '(%s)' % ' or '.join([str(pat) for pat in self.exclude_past])
            else:
                h += '%s' % self.exclude_past[0]
        if self.require_timespan:
            h += ' WITHIN TIMESPAN '
            if len(self.exclude_past) > 1:
                h += '(%s)' % ' or '.join([str(ts) for ts in self.require_timespan])
            else:
                h += '%s' % self.require_timespan[0]
        if self.exclude_timespan:
            h += ' NOT WITHIN TIMESPAN '
            if len(self.exclude_past) > 1:
                h += '(%s)' % ' or '.join([str(ts) for ts in self.exclude_timespan])
            else:
                h += '%s' % self.exclude_timespan[0]
        h = '(%s)' % h
        return h
    string_hash = property(__get_string_hash)
    
    def plausible_patients(self, exclude_condition=None):
        plausible = None
        for pat in self.patterns:
            if not plausible:
                plausible = pat.plausible_patients(exclude_condition)
                continue
            if self.operator == 'and':
                plausible = plausible & pat.plausible_patients(exclude_condition)
            else: # 'or'
                plausible = plausible | pat.plausible_patients(exclude_condition)
        all_required_events = (self.require_before + self.require_after + self.require_ever)
        if all_required_events:
            q_obj = Q(event__name=all_required_events[0])
            for name in all_required_events[1:]:
                q_obj = q_obj | Q(event__name=name)
            plausible = plausible & Patient.objects.filter(q_obj).distinct()
        for tspan in self.require_timespan:
            plausible = plausible & Patient.objects.filter(timespan__name=tspan).distinct()
        log_query('Plausible patients for ComplexEventPattern "%s", exclude %s' % (self, exclude_condition), plausible)
        if EXCLUDE_XB_NAMES:
            #
            # DEBUG:  Remove me when done debugging!!!!!
            #
            last_name_q = ~Q(last_name__istartswith='xb')
            plausible = plausible.filter(last_name_q)
        return plausible
    
    def plausible_events(self, patients=None, exclude_condition=None):
        log.debug('Building plausible events query for %s' % self)
        patients = self.plausible_patients(exclude_condition)
        plausible = None
        for pat in self.patterns:
            if not plausible:
                plausible = pat.plausible_events(patients=patients, exclude_condition=exclude_condition)
                continue
            if self.operator == 'and':
                plausible = plausible & pat.plausible_events(patients=patients, exclude_condition=exclude_condition)
            else: # 'or'
                plausible = plausible | pat.plausible_events(patients=patients, exclude_condition=exclude_condition)
        purpose = 'Querying plausible events for %s' % self
        log_query(purpose, plausible)
        return plausible
    
    def sorted_patterns(self, exclude_condition=None):
        '''
        Returns the patterns composing this ComplexEventPattern sorted from 
        lowest to highest number of plausible patients
        '''
        if not self.__sorted_pattern_cache:
            #
            # FIXME: The sorted pattern cache doesn't take into account that
            # exclude_condition may be different on different calls to this 
            # method.
            #
            #log.debug('Sorting patterns by plausible event count')
            log.debug('Sorting patterns by plausible patient count')
            plausible = self.plausible_patients(exclude_condition)
            count = {}
            for pat in self.patterns:
                #count[pat] = pat.plausible_events(patients=plausible).count()
                count[pat] = pat.plausible_patients(exclude_condition).count()
            #log.debug('Plausible events by pattern: \n%s' % pprint.pformat(count))
            log.debug('Plausible patients by pattern: \n%s' % pprint.pformat(count))
            self.__sorted_pattern_cache = [i[0] for i in sorted(count.items(), key=itemgetter(1))]
        return self.__sorted_pattern_cache

    def generate_windows(self, days, patients=None, exclude_condition=None):
        if not patients:
            patients = self.plausible_patients(exclude_condition)
        if self.operator == 'and':
            # Order does not matter with 'or' operator, so only 'and' operator 
            # needs to perform expensive pattern sort.
            sorted_patterns = self.sorted_patterns(exclude_condition)
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
                    log.debug('Queue: %s' % queue)
                    matched_windows = set() # Windows matching both a window from queue, and current pattern
                    for win in queue:
                        new_matches = pattern.match_window(win, exclude_condition=exclude_condition)
                        matched_windows.update(new_matches)
                        if not new_matches:
                            log.debug('%s excluded, does not match pattern:' % win)
                            log.debug('    %s' % pattern)
                            log.debug('  Events in window:')
                            [log.debug('    %s' % e) for e in win.events]
                    queue = matched_windows
                log.debug('Complete unconstrained queue: %s' % queue)
                # Any windows remaining in the queue at this point have 
                # matched all patterns.
                queue = list(queue)
                queue.sort()
                for win in queue:
                    new_win = self._check_constaints(win)
                    if new_win:
                        log.debug('Yielding %s' % new_win)
                        yield new_win
                    else:
                        log.debug('Window %s failed constraint checks' % win)
        elif self.operator == 'or':
            for pattern in self.patterns:
                for win in pattern.generate_windows(days=days, patients=patients, exclude_condition=exclude_condition):
                    win = self._check_constaints(win)
                    if win:
                        yield win
        else:
            raise 'Invalid self.operator -- WTF?!'
    
    def match_window(self, reference, exclude_condition=None):
        '''
        Returns set of zero or more windows, falling within a reference window,
        that match this pattern.
        '''
        # Order matters with 'and' operator, because any pattern that does not 
        # match, causes the entire complex pattern not to match.  So we start
        # with that pattern which has the fewest possible matches, and thus is
        # least likely to match.  With 'or' operator, order of patterns does not
        # matter at all, so we don't waste DB resources counting their possible
        # matches.
        if self.operator == 'and':
            sorted_patterns = self.sorted_patterns(exclude_condition)
        else:
            sorted_patterns = self.patterns
        queue = set() # Windows that we will TRY to match.  
        matched_windows = set() # Windows that DO match this complex pattern, before checking constraints
        queue.add(reference) # Start by checking the reference window
        for pattern in sorted_patterns:
            new_matches = set() # New matches for this pattern
            for win in queue:
                this_win_matches = pattern.match_window(win, exclude_condition=exclude_condition)
                new_matches.update(this_win_matches)
            if self.operator == 'and':
                # Only windows that have matched everything so far will be considered for the next pass
                queue = matched_windows = new_matches
                if not new_matches:
                    log.debug('%s excluded, does not match pattern:' % win)
                    log.debug('    %s' % pattern)
            else: # operator == 'or'
                # The original reference window, as well as any windows that 
                # have matched so far, will be considered for next pass
                matched_windows |= new_matches
                queue = matched_windows.copy()
                queue.add(reference)
        valid = set()
        for win in matched_windows:
            win = self._check_constaints(win)
            if win:
                valid.add(win)
        return valid
    
    def _check_constaints(self, win):
        '''
        Checks a Window object against 'require_before', 'exclude', and
        'exclude_past' constraints.  Returns window if all constraints are
        passed; otherwise returns False.  If a 'require_before' constraint is
        passed, relevant past events are added to the Window object's
        events_before list.  Likewise 'require_after'.
        @param win: Window to check
        @type win:  Window instance
        '''
        log.debug('Checking constraints on %s' % win)
        #
        # Exclude Past
        #
        if self.exclude_past:
            exclude_q = Q(patient=win.patient, name__in=self.exclude_past, date__lt=win.start)
            past_events = Event.objects.filter(exclude_q)
            log_query('Check exclude_past', past_events)
            if  past_events.count() > 0:
                log.debug('%s excluded by past events:' % win)
                for e in past_events:
                    log.debug('    %s' % e)
                return False
            else:
                log.debug('Patient %s was not excluded by past events' % win.patient)
        #
        # Required Before
        #
        if self.require_before:
            require_q = Q(patient=win.patient, name__in=self.require_before, date__lt=win.start)
            if self.require_before_window:
                lookback_start = win.start - self.require_before_window
                require_q &= Q(date__gte=lookback_start)
            required_events = Event.objects.filter(require_q)
            log_query('Check require_before', required_events)
            if required_events.count() == 0:
                log.debug('%s excluded by lack of require_before events:' % win)
                for e in self.require_before:
                    log.debug('    %s' % e)
                return False
            else:
                log.debug('Patient %s has require_before events' % win.patient)
                log.debug('Adding events to window %s' % id(win))
                if win.events_before:
                    win.events_before = win.events_before | required_events
                else:
                    win.events_before = required_events
        #
        # Required After
        #
        if self.require_after:
            require_q = Q(patient=win.patient, name__in=self.require_after, date__gt=win.end)
            if self.require_before_window:
                lookahead_start = win.end + self.require_before_window
                require_q &= Q(date__gte=lookahead_start)
            required_events = Event.objects.filter(require_q)
            log_query('Check require_after', required_events)
            if required_events.count() == 0:
                log.debug('%s excluded by lack of require_after events:' % win)
                for e in self.require_after:
                    log.debug('    %s' % e)
                return False
            else:
                log.debug('Patient %s has require_after events' % win.patient)
                log.debug('Adding events to window %s' % id(win))
                if win.events_after:
                    win.events_after = win.events_after | required_events
                else:
                    win.events_after = required_events
        #
        # Required Ever
        #
        if self.require_ever:
            require_q = Q(patient=win.patient, name__in=self.require_ever)
            required_events = Event.objects.filter(require_q)
            log_query('Check require_ever', required_events)
            if required_events.count() == 0:
                log.debug('%s excluded by lack of require_ever events:' % win)
                for e in self.require_ever:
                    log.debug('    %s' % e)
                return False
            else:
                log.debug('Patient %s has require_ever events' % win.patient)
                log.debug('Adding events to window %s' % id(win))
                if win.events_ever:
                    win.events_ever = win.events_ever | required_events
                else:
                    win.events_ever = required_events
        #
        # Since self.exclude can include ComplexEventPatterns, it is by far the
        # most computationally expensive constraint check.  So we test it only 
        # after all other constraints have passed.
        #
        log.debug('Check exclude')
        for pat in self.exclude:
            # If any pattern matches, this constraint fails
            exclude_match = pat.match_window(win)
            if exclude_match:
                log.debug('%s excluded by pattern' % win)
                log.debug('    Exclusion match: %s' % exclude_match)
                return False
        #
        # If we made it this far, we have passed all constraints.  
        #
        log.debug('%s passes constraint checks' % win)
        return win
    
    def __get_pattern_object(self):
        '''
        Returns a Pattern model instance representing this pattern.
        '''
        if not self.__pattern_obj:
            hash = hashlib.sha224(self.string_hash).hexdigest()
            try: 
                pat = Pattern.objects.get(hash=hash)
            except Pattern.DoesNotExist:
                pat = Pattern(pattern=self.string_hash, hash=hash, name=self.name)
                pat.save()
            self.__pattern_obj = pat
        return self.__pattern_obj
    pattern_obj = property(__get_pattern_object)
    
    def __repr__(self):
        if self.name:
            return self.name
        else:
            return self.string_hash
    
    def __get_relevant_loincs(self):
        loincs = set()
        for pat in self.patterns:
            loincs |= pat.relevant_loincs
        return loincs
    relevant_loincs = property(__get_relevant_loincs)
        
    def __get_event_names(self):
        events = set()
        for pat in self.patterns:
            events |= pat.event_names
        for pat in self.exclude:
            events |= pat.event_names
        events |= set(self.require_before)
        events |= set(self.require_after)
        events |= set(self.require_ever)
        events |= set(self.exclude_past)
        return events
    event_names = property(__get_event_names)
    
    def _is_in_timespan(self, event, timespan):
        Timespan.objects


class TuberculosisDefC(BaseEventPattern):
    '''
    TB definition (c).  
    This is something of an ugly hack, and does not fully support the Nodis API.  
    Can't say how much work it would be, to make it possible to use this as a 
    regular BaseEventPattern child.
    '''
    
    SECONDARY_MED_EVENTS = [
        'isoniazid',
        'ethambutol', 
        'rifampin', 
        'rifabutin', 
        'rifapentine', 
        'pyrazinamide',
        'streptomycin', 
        'para_aminosalicyclic_acid', 
        'kanamycin', 
        'capreomycin', 
        'cycloserine', 
        'ethionamide', 
        'moxifloxacin', 
        ]
    
    def __init__(self):
        self.name = 'tb_def_c'
        self.string_hash = '(%s)' % self.name
        self.event_names = set(['tb_diagnosis'] + self.SECONDARY_MED_EVENTS)
        hash = hashlib.sha224(self.string_hash).hexdigest()
        try: 
            pat = Pattern.objects.get(hash=hash)
        except Pattern.DoesNotExist:
            pat = Pattern(pattern=self.string_hash, hash=hash, name=self.name)
            pat.save()
        self.pattern_obj = pat
    
    def generate_windows(self, days, patients=None, exclude_condition=None):
        if not patients:
            patients = Patient.objects.filter(event__name='tb_diagnosis').exclude(case__condition='tb').distinct().order_by('pk')
        for pat in patients:
            q_obj = Q(name='tb_diagnosis') & ~Q(case__condition='tb') & Q(patient=pat)
            for diagnosis in Event.objects.filter(q_obj).order_by('date'):
                start = diagnosis.date - datetime.timedelta(days=60)
                end = diagnosis.date + datetime.timedelta(days=60)
                med_events = Event.objects.filter(patient=pat, date__gte=start, date__lte=end, 
                    name__in=self.SECONDARY_MED_EVENTS)
                cnt = med_events.values_list('name', flat=True).distinct().count()
                if not cnt >= 2:
                    continue
                else:
                    yield Window(121, med_events)
                    break

    def plausible_patients(self, exclude_condition=None):
        q_obj_1 = Q(event__name='tb_diagnosis') & ~Q(case__condition='tb')
        q_obj_2 = Q(event__name__in=self.SECONDARY_MED_EVENTS) & ~Q(case__condition='tb')
        qs = Patient.objects.filter(q_obj_1).distinct() & Patient.objects.filter(q_obj_2).distinct()
        log_query('Plausible patients for tb', qs)
        return qs
    

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
            raise NodisException('A condition with the name "%s" is already registered.' % self.name)
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
        for name in self.heuristics:
            heuristic_obj = BaseHeuristic.get_heuristic(name)
            if isinstance(heuristic_obj, EncounterHeuristic):
                icd9_objs |= heuristic_obj.icd9_objects
        return icd9_objs.distinct()
    icd9s = property(__get_icd9s)
    
    def __get_medications(self):
        '''
        Returns set of medication names used in this condition's definition.
        '''
        med_names = set()
        for name in self.heuristics:
            heuristic_obj = BaseHeuristic.get_heuristic(name)
            if isinstance(heuristic_obj, MedicationHeuristic):
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
        case.provider = window.events[0].content_object.provider
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
            h = BaseHeuristic.get_heuristic_from_event_name(event_name)
            assert h, 'No heuristic found for "%s".' % event_name
            heuristics.add(h)
        heuristic_names = [h.name for h in heuristics]
        codes = CodeMap.objects.filter(heuristic__in=heuristic_names).values('native_code')
        return LabResult.objects.filter(native_code__in=codes)
    relevant_labs = property(__get_relevant_labs)
    
    @classmethod
    def all_test_name_search_strings(cls):
        '''
        Returns a list of all suspicious strings to search for in lab names.
        '''
        all_strings = set()
        for c in Condition.all_conditions():
            for string in c.test_name_search:
                all_strings.add(string)
        all_strings = list(all_strings)
        log.debug('all test name strings: %s' % all_strings)
        return all_strings
        
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
    events = models.ManyToManyField(Event, blank=False) # The events that caused this case to be generated
    # TODO: rename to events_before
    events_before = models.ManyToManyField(Event, blank=False, related_name='case_before') # The events that caused this case to be generated, but occured before the event window
    events_after = models.ManyToManyField(Event, blank=False, related_name='case_after') # The events that caused this case to be generated, but occurred after the event window
    events_ever = models.ManyToManyField(Event, blank=False, related_name='case_ever') # The events that caused this case to be generated, but occurred after the event window
    
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
        return self.events.all().order_by('date')[0].content_object.provider
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
    
    class Meta:
        permissions = [ ('view_phi', 'Can view protected health information'), ]
        unique_together = ['patient', 'condition', 'date']
        ordering = ['id']
    
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


#-------------------------------------------------------------------------------
#
#--- Development
#
#-------------------------------------------------------------------------------




class Gdm(models.Model):
    '''
    Introspected model to work with 'gdm' view until GDM algos are fully 
    integrated into Nodis.
    '''
    date = models.DateField()
    alogrithm = models.TextField()
    patient_id = models.IntegerField()
    mrn = models.CharField(max_length=20)
    last_name = models.CharField(max_length=199)
    first_name = models.CharField(max_length=199)
    native_code = models.CharField(max_length=30)
    native_name = models.CharField(max_length=255)
    result_string = models.TextField()
    event_id = models.IntegerField()
    event_name = models.CharField(max_length=128)
    class Meta:
        db_table = u'gdm'
