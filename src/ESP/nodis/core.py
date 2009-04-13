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


from ESP.hef.models import NativeToLoincMap, HeuristicEvent
from ESP import settings
from ESP.utils import utils as util
from ESP.utils.utils import log



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


class DiseaseCriterion(object):
    '''
    One set of rules for algorithmically defining a disease.  Satisfying a 
    single disease criterion is sufficient to indicate a case of that disease, 
    but a given disease may have arbitrarily many criteria.
    '''
    def __init__(self,  name, version, window, require, require_past = None, require_past_window = None,
        exclude = None, exclude_past = None):
        '''
        @param name: Name of this criterion
        @type name: String
        @param version: Definition version
        @type version: Integer
        @param window: Time window in days
        @type window: Integer
        @param require: Events that must have occurred within 'window' days of one another
        @type require:  List of tuples of HeuristicEvent instances.  The tuples 
            are AND'ed together, and each item in a tuple is OR'ed.
        @param require_past: Events that must have occurred in the past, but 
            not within this criterion's time window
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
        self.name = name
        self.version = version
        self.window = datetime.timedelta(window)
        self.require = require
        self.require_past = require_past
        self.require_past_window = require_past_window
        self.exclude = exclude
        self.exclude_past = exclude_past
    
    def matches(self, begin_date=None, end_date=None):
        #
        # Examine only the time slice specified
        #
        all_events = HeuristicEvent.objects.all()
        if begin_date:
            begin = self.make_date_str(begin_date)
            all_events = all_events.filter(LxDate_of_result__gte=begin)
        if end_date:
            end = self.make_date_str(end_date)
            all_events = all_events.filter(LxDate_of_result__lte=end)
        #
        # Do we match all required events?
        #
        first_req = self.require[0] # Doesn't matter which tuple is considered first, since they are AND'ed
        names = [e.name for e in first_req]
        #events = all_events.filter(heuristic_name__in=names).values_list('patient', flat=True)
        events = all_events.filter(heuristic_name__in=names)
        p_e = {} # {patient: [event, event, ...]}  
        for e in events:
            try:
                p_e[e.patient].append(e)
            except KeyError:
                p_e[e.patient] = [e]
        for patient in p_e.keys():
            for req in self.require[1:]:
                known_events = p_e[patient]
                known_events.sort(lambda x, y: x.date-y.date)
                window_end = known_events[0].date + self.window
                names = [e.name for e in req]
                events = all_events.filter(patient=patient, heuristic_name__in=names)
                if events:
                    p_e[patient].extend( list(events))
                else:
                    del p_e[patient] # This patient does not match this criterion
                    break # Move on to the next patient
        #
        # Now p_e is a dict whose keys are valid patients, and whose values are the validating events for
        # the respective patients.
        #
            
            


 
class DiseaseDefinition(object):
    def __init__(self, **kwargs):
        pass
        

class BaseDiseaseDefinition(object):
    '''
    Abstract base class for disease definitions
    '''
    
    def __init__(self, 
        name, 
        time_window = 0,
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
        self.time_window = time_window
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
        self.condition = Rule.objects.get(ruleName=self.name)
        self._register()
    
    __registry = {} # Class variable
    def _register(self):
        if self.name in self.__registry:
            raise DiseaseDefinitionAlreadyRegistered('A disease definition with the name "%s" is already registered.' % self.name)
        else:
            self.__registry[self.name] = self
    
    @classmethod
    def get_all_definitions(cls):
        '''
        Returns a list of all registered disease definitions.
        '''
        result = []
        keys = cls.__registry.keys()
        keys.sort()
        [result.extend([cls.__registry[k]]) for k in keys]
        log.debug('All Disease Definition instances: %s' % result)
        return result
    
    def find_events(self):
        '''
        Finds heuristic events that, taken together, constitute a disease case.  
            Returns a list of HeuristicEvent instances, usually ordered by 
            date.  For each patient, the first event that is not bound to an
            existing case, and does not fall within an existing case's time 
            window, will be used as the primary event for dating a new case.
        @return: [HeuristicEvent, HeuristicEvent, HeuristicEvent, ...]  
        '''
        raise NotImplementedError('This method MUST be implemented in concrete classes inheriting from BaseDiseaseDefinition.')
        
    def new_case(self, primary_event, all_events):
        '''
        Creates, saves, and returns a new Case object.  Case variables like 
            provider and date are set based on primary_event.  The set of 
            primary_event | all_events  are attached as the Case's events 
            member.
        @param primary_event: Event on which the case's date, provider, etc are based
        @type primary_event:  HeuristicEvent
        @param all_events:    All events that together establish this case
        @type all_events:     [HeuristicEvent, HeuristicEvent, ...]
        '''
        log.info('Creating a new %s case based on event:\n    %s' % (self.condition, primary_event))
        case = Case()
        case.patient = primary_event.patient
        case.provider = primary_event.content_object.provider
        case.date = primary_event.date
        case.condition = self.condition
        case.workflow_state = self.condition.ruleInitCaseStatus
        case.save()
        events = set([primary_event]) | set(all_events)
        case.events = events
        case = self.update_reportable_events(case)
        case.save()
        return case
    
    def generate_cases(self, new_only=False):
        '''
        Calls the user-supplied case factory with appropriate arguments
        '''
        case_window = datetime.timedelta(days=self.time_window) # Group events occurring within case_window into single case
        counter = 0            # Number of new cases generated
        log.info('Generating cases for %s' % self.condition)
        existing_cases = Case.objects.filter(condition=self.condition)
        print existing_cases
        # Primary keys of events already bound to a Case object:
        bound_event_pks = HeuristicEvent.objects.filter(case__in=existing_cases).values_list('pk') # ValuesListQuerySet
        bound_event_pks = [item[0] for item in bound_event_pks]
        log.debug('number of bound_events: %s' % len(bound_event_pks))
        for event in self.find_events():
            if event.pk in bound_event_pks: 
                log.debug('Event #%s is already bound to a case' % event.pk) 
                continue # Event is already attached to a case
            patient = event.patient
            begin = event.date - case_window
            end = event.date
            if self.time_window > 0:
                previous = existing_cases.filter(patient=patient, date__gte=begin, date__lte=end)
            else:
                previous = existing_cases.filter(patient=patient)
            if previous: # This event should be attached to an existing case
                print previous
                assert len(previous) == 1 # Sanity check
                primary_case = previous[0]
                if new_only:
                    log.debug('Event #%s belongs to existing case #%s, but new_only flag is set to True.  Skipping.' % (event.id, primary_case.id) )
                    continue # Don't update case
                else:
                    log.debug('Attaching event:\n    %s\nto existing case\n    %s' % (event, primary_case))
                    primary_case.events.add(event)
                    primary_case.save()
                    bound_event_pks.extend([event.pk])
            else: # A new case should be created for this event
                self.new_case(event, [])
                counter += 1 # Increment new case count
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
        for definition in cls.get_all_definitions():
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
            enc_q = Q(EncICD9_Codes__icontains=self.icd9s[0])
            for code in self.icd9s[1:]:
                enc_q = enc_q | Q(EncICD9_Codes__icontains=code)
            if self.fever: 
                enc_q = enc_q | Q(EncTemperature__gte=100.4)
            enc_q = enc_q & Q(EncPatient=patient)
            enc_q = enc_q & Q(EncEncounter_Date__gte=util.str_from_date(date - self.icd9_days_before))
            enc_q = enc_q & Q(EncEncounter_Date__lte=util.str_from_date(date + self.icd9_days_after))
            log.debug('enc_q: %s' % enc_q)
            encounters = Enc.objects.filter(enc_q)
            case.encounters = sets.Set(case.encounters.all()) | sets.Set(encounters)
        if self.lab_loinc_nums:
            lab_q = Q(LxLoinc__in=self.lab_loinc_nums)
            lab_q = lab_q & Q(LxPatient=patient)
            lab_q = lab_q & Q(LxOrderDate__gte=util.str_from_date(date - self.lab_days_before))
            lab_q = lab_q & Q(LxOrderDate__lte=util.str_from_date(date + self.lab_days_after))
            log.debug('lab_q: %s' % lab_q)
            labs = Lx.objects.filter(lab_q)
            # Some of these lab results will be for the same test (ie same 
            # LOINC code), but Mike only wants to see one result per test.  
            # It's probably better to handle that in the case management UI,
            # where we could potentially show a history for each test, than 
            # here.
            case.lab_results = sets.Set(case.lab_results.all()) | sets.Set(labs)
        if self.med_names:
            med_q = Q(RxDrugName__icontains=self.med_names[0])
            for name in self.med_names[1:]:
                med_q = med_q | Q(RxDrugName__icontains=name)
            med_q = med_q & Q(RxPatient=patient)
            med_q = med_q & Q(RxOrderDate__gte=util.str_from_date(date - self.med_days_before))
            med_q = med_q & Q(RxOrderDate__lte=util.str_from_date(date + self.med_days_after))
            log.debug('med_q: %s' % med_q)
            medications = Rx.objects.filter(med_q)
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
        for definition in cls.get_all_definitions():
            q_obj = Q(condition=definition.condition)
            if begin_date:
                q_obj = q_obj & Q(date__gte=begin_date)
            if end_date:
                q_obj = q_obj & Q(date__lte=end_date)
            existing_cases = Case.objects.filter(q_obj)
            for case in existing_cases:
                definition.update_reportable_events(case)
