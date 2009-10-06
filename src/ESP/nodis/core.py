'''
                                  ESP Health
                         Notifiable Diseases Framework
                                Core Components


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL - http://www.gnu.org/licenses/lgpl-3.0.txt
'''


CACHE_WARNING_THRESHOLD = 100 # Log warning when cache exceeds this many patients


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
from django.db.models import Count
from django.db.models.query import QuerySet
from django.contrib.contenttypes.models import ContentType


from ESP import settings
from ESP.hef import events # Ensure events are loaded
from ESP.utils import utils as util
from ESP.utils.utils import log
from ESP.utils.utils import log_query
from ESP.conf.models import NativeCode
from ESP.conf.models import IgnoredCode
from ESP.emr.models import LabResult
from ESP.emr.models import Encounter
from ESP.emr.models import Prescription
from ESP.emr.models import Immunization
from ESP.emr.models import Patient
from ESP.emr.models import Provider
from ESP.hef import events
from ESP.hef.core import BaseHeuristic
from ESP.hef.models import Event
from ESP.nodis.models import Case
from ESP.nodis.models import Pattern

HEAPY = False
HEAPFILE = '/tmp/heapy.dat'

if HEAPY:
    from guppy import hpy
    HEAP = hpy().heap()


def monitor_heap():
    if HEAPY:
        HEAP.stat.dump(HEAPFILE)


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
            self.__events.sort(lambda x, y: (x.date - y.date).days) # Sort by date
        self.past_events = None
        win_size = (days * 2) + 1
        log.debug('Initialized %s day window with %s events' % (win_size, len(events)))
    
    def _check_event(self, event):
        '''
        Raises OutOfWindow exception if event does not fit within this window
        @type event:  Event instance
        '''
        if self.__events: # Cannot check date range if window has no events
            if not (event.date >= self.start) and (event.date <= self.end):
                raise OutOfWindow('Date outside window')
        if not self.__patient == event.patient:
            raise OutOfWindow('Patient does not match')
        
    def _get_start_date(self):
        '''Start of the time window'''
        return self.__events[-1].date - self.delta
    start = property(_get_start_date)

    def _get_end_date(self):
        '''End of the time window'''
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
        self._check_event(event)
        new_events = self.events + [event]
        return Window(days=self.delta.days, events=new_events)
    
    def merge(self, other):
        '''
        Try to merge all events another window into this window.  If window 
            does not fit, OutOfWindow exception is raised.
        @param other: Window to be merged with this one
        @type other:  Window instance
        '''
        win = other
        for event in other.events:
            win = self.fit(event)
        return win
        
    def __repr__(self):
        return 'Window %s (%s events %s - %s)' % (id(self), len(self.__events), self.start, self.end)
        
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
        
    def plausible_events(self, patients=None):
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
    
    def __get_relevant_loincs(self):
        '''
        Returns the set of LOINC numbers required any component of this pattern
        '''
        raise NotImplementedError
    
    def __get_relevant_heuristics(self):
        '''
        Returns the set of heuristics required by any component of this pattern
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
    
    def __init__(self, heuristic):
        self.__dated_events_cache = {} 
        if not heuristic in BaseHeuristic.list_heuristics():
            raise InvalidHeuristic('Unknown heuristic: %s' % heuristic)
        self.heuristic = heuristic
    
    def plausible_patients(self, exclude_condition=None):
        q_obj = Q(event__heuristic=self.heuristic)
        if exclude_condition:
            q_obj = q_obj & ~Q(event__case__condition=exclude_condition)
        qs = Patient.objects.filter(q_obj).distinct()
        log_query('Plausible patients for %s, exclude %s' % (self, exclude_condition), qs)
        monitor_heap()
        return qs
    
    def plausible_events(self, patients=None, exclude_condition=None):
        log.debug('Building plausible events query for %s' % self)
        q_obj = Q(heuristic=self.heuristic)
        if patients:
            q_obj = q_obj & Q(patient__in=patients)
        if exclude_condition:
            q_obj = q_obj & ~Q(case__condition=exclude_condition)
        events = Event.objects.filter(q_obj)
        log_query('Querying plausible events for %s' % self, events)
        monitor_heap()
        return events
    
    def generate_windows(self, days, patients=None, exclude_condition=None):
        log.debug('Generating windows for %s' % self)
        events = self.plausible_events(patients=patients, exclude_condition=exclude_condition)
        for e in events:
            yield Window(days=days, events=[e])
                
    def match_window(self, reference, exclude_condition=None):
        assert isinstance(reference, Window)
        #
        # Get dated events
        #
        patient = reference.patient
        cache = self.__dated_events_cache
        if patient not in cache:
            values = Event.objects.filter(heuristic=self.heuristic, patient=patient).values('pk', 'date')
            if exclude_condition:
                q_obj = ~Q(case__condition=exclude_condition)
                values = values.filter()
            log_query('get dated events for patient %s exclude condition %s' % (patient, exclude_condition), values)
            patient_dates = {}
            for val in values:
                patient_dates[val['date']] = val['pk']
            cache[patient] = patient_dates
            if len(cache) >= CACHE_WARNING_THRESHOLD:
                log.warning('More than %s patients cached:  %s' % (CACHE_WARNING_THRESHOLD, len(cache)))
        dated_events = cache[patient]
        matched_windows = set()
        for event_date in dated_events:
            # If date is outside window, skip it
            if (event_date > reference.end) or (event_date < reference.start):
                continue
            event_pk = dated_events[event_date]
            event = Event.objects.get(pk=event_pk)
            win = reference.fit(event)
            matched_windows.add(win)
        return matched_windows
        
    def __get_string_hash(self):
        return '%s' % self.heuristic
    string_hash = property(__get_string_hash)
    
    def __repr__(self):
        return 'SimpleEventPattern: %s' % self.heuristic
    
    def __get_relevant_loincs(self):
        loincs = set()
        for h in BaseHeuristic.get_heuristics_by_name(self.heuristic):
            if not hasattr(h, 'loinc_nums'):
                continue
            loincs |= set(h.loinc_nums)
        return loincs
    relevant_loincs = property(__get_relevant_loincs)
    
    def __get_relevant_heuristics(self):
        return set([self.heuristic])
    relevant_heuristics = property(__get_relevant_heuristics)


class ComplexEventPattern(BaseEventPattern):
    '''
    An event pattern composed of one or more SimpleEventPattern or 
    ComplexEventPattern instances.  
    '''
    def __init__(self, operator, patterns, name=None, require_past=[], require_past_window=None, exclude=[], exclude_past=[]):
        '''
        @param operator: Logical operator for combining patterns 
        @type operator:  String ('and' or 'or')
        @param patterns: Patterns to search for
        @type patterns:  String naming heuristic event, or ComplexEventPattern instance
        @param name: Name of this pattern (optional)
        @type name:  String
        @param require_past: Require these events in past
        @type require_past:  String naming a heuristic event
        @param require_past_window: Optionally limit require_past look back to this many days before event window
        @type require_past_window:  Integer (number of days)
        @param exclude: Exclude this pattern within match window
        @type exclude:  String naming heuristic event, or ComplexEventPattern instance
        @param exclude_past: Exclude these events in past
        @type exclude_past:  String naming a heuristic event
        '''
        operator = operator.lower()
        self.__sorted_pattern_cache = None
        assert operator in ('and', 'or')
        self.operator = operator
        valid_heuristic_names = BaseHeuristic.list_heuristics()
        self.patterns = []
        self.name = name # Optional name
        self.exclude = []
        for pat in patterns:
            if isinstance(pat, ComplexEventPattern):
                self.patterns.append(pat)
            elif pat in valid_heuristic_names: # Implies req is a string
                pat_obj = SimpleEventPattern(heuristic=pat)
                self.patterns.append(pat_obj)
            else:
                raise InvalidPattern('%s [%s]' % (pat, type(pat)))
        for pat in exclude:
            if isinstance(pat, ComplexEventPattern):
                self.exclude.append(pat)
            elif pat in valid_heuristic_names: # Implies req is a string
                pat_obj = SimpleEventPattern(heuristic=pat)
                self.exclude.append(pat_obj)
            else:
                raise InvalidPattern('%s [%s]' % (pat, type(pat)))
        count = {} # Count of plausible events per req
        for name in require_past + exclude_past:
            if not name in valid_heuristic_names:
                log.error('"%s" not in valid hueristic names:' % name)
                log.error('\t%s' % valid_heuristic_names)
                raise InvalidPattern('%s [%s]' % (name, type(name)))
        self.require_past = require_past
        if require_past_window:
            self.require_past_window = datetime.timedelta(days=require_past_window)
        else:
            self.require_past_window = None
        self.exclude_past = exclude_past
        self.__pattern_obj = None # Cache 
        log.debug('Initializing new ComplexEventPattern instance')
        log.debug('    operator:    %s' % operator)
        log.debug('    patterns:    %s' % patterns)
        log.debug('    require_past:  %s' % require_past)
        log.debug('    require_past_window:  %s' % require_past_window)
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
        if self.require_past:
            h += ' REQUIRE PAST '
            if len(self.require_past) > 1:
                h += '(%s)' % op_delim.join([pat.string_hash for pat in self.require_past])
            else:
                h += '%s' % self.require_past[0]
        if self.require_past_window:
            h += ' WITHIN %s DAYS ' % self.require_past_window.days
        if self.exclude_past:
            h += ' EXCLUDE PAST '
            if len(self.exclude_past) > 1:
                h += '(%s)' % ' or '.join([str(pat) for pat in self.exclude_past])
            else:
                h += '%s' % self.exclude_past[0]
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
        for heuristic in self.require_past:
            plausible = plausible & Patient.objects.filter(event__heuristic=heuristic).distinct()
        log_query('Plausible patients for ComplexEventPattern "%s", exclude %s' % (self, exclude_condition), plausible)
        monitor_heap()
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
        monitor_heap()
        return plausible
    
    def sorted_patterns(self, exclude_condition=None):
        '''
        Returns the patterns composing this ComplexEventPattern sorted from 
        lowest to highest number of plausible patients
        '''
        if not self.__sorted_pattern_cache:
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
        sorted_patterns = self.sorted_patterns(exclude_condition)
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
            exclude_q = Q(patient=win.patient, heuristic__in=self.exclude_past, date__lt=win.start)
            query = Event.objects.filter(exclude_q)
            log_query('Check exclude_past', query)
            if  query.count() > 0:
                log.debug('Patient %s excluded by %s past events' % (win.patient, query.count()))
                return False
            else:
                log.debug('Patient %s was not excluded by past events' % win.patient)
        if self.require_past:
            require_q = Q(patient=win.patient, heuristic__in=self.require_past, date__lt=win.start)
            if self.require_past_window:
                lookback_start = win.start - self.require_past_window
                require_q = Q(date__gte=lookback_start)
            query = Event.objects.filter(require_q)
            log_query('Check require_past', query)
            if query.count() == 0:
                log.debug('Patient %s excluded by lack of required past events' % win.patient)
                return False
            else:
                log.debug('Patient %s has required past events' % win.patient)
                log.debug('Adding events to window')
                if win.past_events:
                    win.past_events = win.past_events | Event.objects.filter(require_q)
                else:
                    win.past_events = Event.objects.filter(require_q)
        #
        # Since self.exclude can include ComplexEventPatterns, it is by far the
        # most computationally expensive constraint check.  So we test it only 
        # after all other constraints have passed.
        #
        log.debug('Check exclude')
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
    
    def __get_pattern_object(self):
        '''
        Returns a Pattern model instance representing this pattern.
        '''
        if not self.__pattern_obj:
            hash = self.string_hash
            try: 
                pat = Pattern.objects.get(hash=hash)
            except Pattern.DoesNotExist:
                pat = Pattern(hash=hash, name=self.name)
                pat.save()
            self.__pattern_obj = pat
        return self.__pattern_obj
    pattern_obj = property(__get_pattern_object)
    
    def __str__(self):
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
        
    def __get_relevant_heuristics(self):
        heuristics = set()
        for pat in self.patterns:
            heuristics |= pat.relevant_heuristics
        return heuristics
    relevant_heuristics = property(__get_relevant_heuristics)


class Condition(object):
    '''
    A medical condition, defined by matching at least one event pattern.
    '''

    def __init__(self,
        name,
        patterns,
        recur_after,
        test_name_search,
        # Reporting
        icd9s = [],
        icd9_days_before = 14,
        fever = True,
        lab_loinc_nums = [],
        lab_days_before = 14,
        med_names = [],
        med_days_before = 14,
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
        @param lab_loinc_nums:   Report lab results matching these LOINCs
        @type lab_loinc_nums:    List of strings
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
        assert icd9_days_before
        assert lab_days_before
        assert med_days_before
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
        self.icd9s = icd9s
        self.icd9_days_before = datetime.timedelta(days = icd9_days_before)
        self.fever = fever
        self.lab_loinc_nums = lab_loinc_nums
        self.lab_days_before = datetime.timedelta(days = lab_days_before)
        self.med_names = med_names
        self.med_days_before = datetime.timedelta(days = med_days_before)
        self.__existing = {} # Cache 
        self._register()

    __registry = {} # Class variable
    def _register(self):
        if self.name in self.__registry:
            raise NodisException('A disease definition with the name "%s" is already registered.' % self.name)
        else:
            self.__registry[self.name] = self

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
        return cls.__registry.keys()
    
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

    def get_all_event_names(self):
        '''
        Return list of names of all heuristic events included in this 
        disease's definition(s).
        '''
        # 
        # DEBUG: This is probably broken since change to BaseEventPattern
        #
        names = []
        for d in self.definitions:
            names.extend(d.get_all_event_names())
        return set(names)

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
        case.save()
        case.events = window.events
        case.save()
        log.info('Created new %s case #%s for patient #%s based on %s' % (self.name, case.pk, case.patient.pk, window))
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
            log.debug('Patient #%s: %s' % (patient.pk, patient))
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
                    monitor_heap()
                    if window.overlaps(existing_case_dates, self.recur_after):
                        log.debug('Window overlaps with existing case')
                        continue # 
                    else:
                        log.debug('Window added to queue')
                        queue.append(window)
                        window_patterns[window] = pattern
            if not queue:
                continue # no windows for this patient
            queue.sort(lambda x, y: (x.date - y.date).days) # Sort by date
            log.debug('sorted queue: %s' % queue)
            log.debug('sorted queue dates: %s' % [win.date for win in queue])
            if self.recur_after == -1:
                log.debug('Disease cannot recur, so limiting queue to the earliest window')
                queue = [queue[0]]
            else:
                log.debug('Examining queue')
            #
            # Now we have a queue of cases that do not overlap existing (in db) 
            # cases.  Let's winnow down that queue to a list of valid windows.
            #
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
        log.WARNING('update_case() is deprecated')
        return
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
            new_encounters = sets.Set(case.encounters.all()) | sets.Set(encounters)
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
            new_labs = sets.Set(case.lab_results.all()) | sets.Set(labs)
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
            new_meds = sets.Set(case.medications.all()) | sets.Set(medications)
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
    
    def __get_relevant_loincs(self):
        '''
        Returns the set of LOINC numbers required by any pattern defining this 
        condition
        '''
        loincs = set()
        for pat in self.patterns:
            loincs |= pat.relevant_loincs
        return loincs
    relevant_loincs = property(__get_relevant_loincs)
        

    def __get_relevant_heuristics(self):
        '''
        Returns the set of heuristics required by any pattern defining this 
        condition
        '''
        heuristics = set()
        for pat in self.patterns:
            heuristics |= pat.relevant_heuristics
        return heuristics
    relevant_heuristics = property(__get_relevant_heuristics)
    
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
        return all_strings
        
    @classmethod
    def find_unmapped_labs(cls):
        '''
        Returns a QuerySet of unmapped lab tests whose native name contains
        a suspicious string.
        '''
        all_strings = self.all_test_name_search_strings()
        mapped_codes = NativeCode.objects.values('native_code').distinct()
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
        

