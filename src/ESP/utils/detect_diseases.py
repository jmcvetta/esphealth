#!/usr/bin/env python
'''
Detect cases of (reportable) disease
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
from ESP.esp import models
from ESP.utils import utils as util
from ESP.utils.utils import log





#===============================================================================
#
#--- ~~~ Exceptions ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HeuristicAlreadyRegistered(BaseException):
    '''
    A BaseHeuristic instance has already been registered with the same name 
    as the instance you are trying to register.
    '''
    pass

class DiseaseDefinitionAlreadyRegistered(BaseException):
    '''
    A BaseDiseaseDefinition instance has already been registered with the same 
    name as the instance you are trying to register.
    '''
    pass

class CaseAlreadyExists(BaseException):
    '''
    A case already exists for this disease + patient.
    '''
    pass


#===============================================================================
#
#--- ~~~ Heuristics Framework ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BaseHeuristic:
    '''
    Abstract interface class for heuristics, concrete instances of which are
    used as components of disease definitions.
    '''
    
    def __init__(self, name, verbose_name=None):
        raise NotImplementedError('This method MUST be implemented in concrete classes inheriting from BaseHeuristic.')
    
    __registry = {} # Class variable
    def _register(self, allow_duplicate_name=False):
        '''
        Add this instance to the BaseHeuristic registry
        '''
        name = self.name
        registry = self.__registry
        if allow_duplicate_name and name in registry:
            if not self in registry[name]:
                log.debug('Registering additional heuristic for name "%s".' % name)
                registry[name] += [self]
        elif name in registry:
            raise HeuristicAlreadyRegistered('A BaseHeuristic instance is already registered with name "%s".' % name)
        else:
            log.debug('Registering heuristic with name "%s".' % name)
            registry[name] = [self]
    
    @classmethod
    def get_all_heuristics(cls):
        '''
        Returns a list of all registered BaseHeuristic instances.
        '''
        result = []
        keys = cls.__registry.keys()
        keys.sort()
        [result.extend(cls.__registry[key]) for key in keys]
        log.debug('All BaseHeuristic instances: %s' % result)
        return result
    
    def matches(self, begin_date=None, end_date=None):
        '''
        Return a QuerySet of matches for this heuristic
        '''
        raise NotImplementedError('This method MUST be implemented in concrete classes inheriting from BaseHeuristic.')
        
    def generate_events(self, begin_date=None, end_date=None):
        '''
        Generate models.HeuristicEvent records for each item returned by
        matches, if it does not already have one.
        @return: Integer number of new records created
        '''
        log.info('Generating events for heuristic "%s".' % self.name)
        counter = 0 # Counts how many new records have been created
        # First we retrieve a list of object IDs for this 
        existing = models.HeuristicEvent.objects.filter(heuristic_name=self.name).values_list('object_id')
        existing = [int(item[0]) for item in existing] # Convert to a list of integers
        for event in self.matches(begin_date, end_date).select_related():
            if event.id in existing:
                log.debug('BaseHeuristic event "%s" already exists for %s #%s' % (self.name, event._meta.object_name, event.id))
                continue
            content_type = ContentType.objects.get_for_model(event)
            obj, created = models.HeuristicEvent.objects.get_or_create(heuristic_name=self.name,
                                                         date=event.date,
                                                         patient=event.patient,
                                                         content_type=content_type,
                                                         object_id=event.pk,
                                                         )
            if created:
                log.info('Creating new heuristic event "%s" for %s #%s' % (self.name, event._meta.object_name, event.id))
                obj.save()
                counter += 1
            else:
                log.debug('Did not create heuristic event - found matching event #%s' % obj.id)
        log.info('Generated %s new events for "%s".' % (counter, self.name))
        return counter
    
    @classmethod
    def generate_all_events(cls, begin_date=None, end_date=None):
        '''
        Generate HeuristicEvent records for every registered BaseHeuristic 
            instance.
        @param begin_date: Beginning of time window to examine
        @type begin_date:  datetime.date
        @param end_date:   End of time window to examine
        @type end_date:    datetime.date
        @return:           Integer number of new records created
        '''
        counter = 0 # Counts how many total new records have been created
        for heuristic in cls.get_all_heuristics():
            counter += heuristic.generate_events()
        log.info('Generated %s TOTAL new events.' % counter)
        return counter
    
    
    
    def make_date_str(self, date):
        '''
        Returns a string representing a datetime.date object (kludge for old 
        ESP data model)
        '''
        if type(date) == types.StringType:
            log.debug('String given as date -- no conversion')
            return date
        return util.str_from_date(date)
    
    def __repr__(self):
        return '<BaseHeuristic: %s>' % self.name
    
    
class LabHeuristic(BaseHeuristic):
    '''
    Abstract base class for lab test heuristics, concrete instances of which
    are used as components of DiseaseDefinitions
    '''
    def __init__(self, name, verbose_name=None, loinc_nums=[], **kwargs):
        '''
        @param lookback: Include encounters/lab results occurring no more 
            than this many days before today.  If lookback is 0 or None, all 
            records are examined.
        @type lookback: Integer
        '''
        self.name = name
        self.verbose_name = verbose_name
        self.loinc_nums = loinc_nums
        assert self.name # Concrete class must define this!
        self._register(**kwargs)
    
    def __get_lab_q(self):
        '''
        Returns a Q object that selects all labs identified by self.loinc_nums.
        '''
        lab_q = Q(LxLoinc='%s' % self.loinc_nums[0])
        for num in self.loinc_nums[1:]:
            lab_q = lab_q | Q(LxLoinc='%s' % num)
        return lab_q
    lab_q = property(__get_lab_q)
        
    def relevant_labs(self, begin_date=None, end_date=None):
        '''
        Return all lab results relevant to this heuristic, whether or not they 
        indicate positive.
            @type begin_date: datetime.date
            @type end_date:   datetime.date
            @type patient:    models.Demog
            @type queryset:   QuerySet
        '''
        log.debug('Get lab results relevant to "%s".' % self.name)
        log.debug('Time window: %s to %s' % (begin_date, end_date))
        qs = models.Lx.objects.all()
        if begin_date:
            begin = self.make_date_str(begin_date)
            qs = qs.filter(LxDate_of_result__gte=begin)
        if end_date:
            end = self.make_date_str(end_date)
            qs = qs.filter(LxDate_of_result__lte=end)
        #
        # Build Q object
        #
        lab_q = Q(LxLoinc='%s' % self.loinc_nums[0])
        for num in self.loinc_nums[1:]:
            lab_q = lab_q | Q(LxLoinc='%s' % num)
        log.debug('lab_q: %s' % lab_q)
        return qs.filter(self.lab_q)


class HighNumericLabHeuristic(LabHeuristic):
    '''
    Matches labs with high numeric scores, as determined by a ratio to 
    '''
    
    def __init__(self, name, verbose_name=None, loinc_nums=[], ratio=None, default_high=None, **kwargs):
        '''
        @param name: Name of this heuristic (short slug)
        @type name: String
        @param verbose_name: Long name of this heuristic
        @type verbose_name: String
        @param loinc_nums: LOINC numbers relevant to this heuristic
        @type loinc_nums: List of strings
        @param ratio: Match on result > ratio * reference_high
        @type ratio: Integer
        @param default_high: If no reference high, match on result > default_high
        @type default_high: Integer
        '''
        self.name = name
        self.verbose_name = verbose_name
        self.loinc_nums = loinc_nums
        self.ratio = ratio
        self.default_high = default_high
        assert self.name # Sanity check
        # Should we sanity check verbose_name?
        assert self.loinc_nums # Sanity check
        assert self.ratio or self.default_high # Sanity check -- one or the other or both required
        self._register(kwargs)
    
    def matches(self, begin_date=None, end_date=None):
        '''
        If record has a reference high, and a ratio has been specified, compare
        test result against that reference.  If a record does not have a
        reference high, and a default_high has been specified, compare result
        against that default 'high' value.
        '''
        relevant_labs = self.relevant_labs(begin_date, end_date)
        no_ref_q = Q(LxReference_High=None) | Q(LxReference_High='')
        if self.default_high:
            static_comp_q = no_ref_q & Q(LxTest_results__gt=self.default_high)
            pos_q = static_comp_q
        if self.ratio:
            ref_comp_q = ~no_ref_q & Q(LxTest_results__gt=F('LxReference_High') * self.ratio)
            pos_q = ref_comp_q
        if self.default_high and self.ratio:
            pos_q = (ref_comp_q | static_comp_q)
        log.debug('pos_q: %s' % pos_q)
        return relevant_labs.filter(pos_q)


class StringMatchLabHeuristic(LabHeuristic):
    '''
    Matches labs with results containing specified strings
    '''
    
    def __init__(self, name, verbose_name=None, loinc_nums=[], strings=[], 
        abnormal_flag=False, match_type='istartswith', **kwargs):
        '''
        @param name:          Name of this heuristic (short slug)
        @type name:           String
        @param verbose_name:  Long name of this heuristic
        @type verbose_name:   String
        @param strings:       Strings to match against
        @type strings:        List of strings
        @param abnormal_flag: If true, a lab result with its 'abnormal' flag
            set will count as a match
        @type abnormal_flag:  Boolean
        @param match_type:    Right now, only 'istartswith'
        @type match_type:     String
        '''
        self.name = name
        self.verbose_name = verbose_name
        self.loinc_nums = loinc_nums
        self.strings = strings
        self.abnormal_flag = abnormal_flag
        self.match_type = match_type
        assert self.name # Sanity check
        # Should we sanity check verbose_name?
        assert self.loinc_nums # Sanity check
        assert self.strings # Sanity check
        assert self.match_type # Sanity check
        self._register(**kwargs)
    
    def matches(self, begin_date=None, end_date=None):
        '''
        Compare record's result field against strings.
            #
        @param begin_date: Beginning of time window to examine
        @type begin_date:  datetime.date
        @param end_date:   End of time window to examine
        @type end_date:    datetime.date
        '''
        if self.match_type == 'istartswith':
            pos_q = Q(LxTest_results__istartswith=self.strings[0])
            for s in self.strings[1:]:
                pos_q = pos_q | Q(LxTest_results__istartswith=s)
            if self.abnormal_flag:
                msg = 'IMPORTANT: Support for abnormal-flag-based queries has not yet been implemented!\n'
                msg += '    Our existing data has only nulls for that field, so I am not sure what the query should look like.'
                log.critical(msg)
        else:
            raise NotImplementedError('The only match type supported at this time is "istartswith".')
        log.debug('pos_q: %s' % pos_q)
        return self.relevant_labs(begin_date, end_date).filter(pos_q)



class EncounterHeuristic(BaseHeuristic):
    '''
    Abstract base class for encounter heuristics, concrete instances of which
    are used as components of DiseaseDefinitions
    '''
    def __init__(self, name, verbose_name=None, icd9s=[], **kwargs):
        self.name = name
        self.verbose_name = verbose_name
        self.icd9s = icd9s
        assert self.name # The name of this kind of encounter
        self._register(kwargs)
    
    def __get_enc_q(self):
        '''
        Returns a Q object to select all Encounters indicated by self.icd9s
        '''
        enc_q = Q()
        for code in self.icd9s:
            enc_q = enc_q | Q(EncICD9_Codes__icontains=code)
        return enc_q
    enc_q = property(__get_enc_q)

    def encounters(self, begin_date=None, end_date=None):
        '''
        Return all lab results relevant to this heuristic, whether or not they 
        indicate positive.
            @type begin_date: datetime.date
            @type end_date:   datetime.date
            @type patient:    models.Demog
            @type queryset:   QuerySet
        '''
        log.debug('Get encounters relevant to "%s".' % self.name)
        qs = models.Enc.objects.all()
        if begin_date :
            begin = self.make_date_str(begin_date)
            qs = qs.filter(EncEncounter_Date__gte=begin)
        if end_date:
            end = self.make_date_str(end_date)
            qs = qs.filter(EncEncounter_Date__lte=end)
        elif begin_date or end_date:
            raise 'If you specify either begin_date or end_date, you must also specify the other.'
        return qs.filter(self.enc_q)
    
    def matches(self, begin_date=None, end_date=None):
        return self.encounters(begin_date, end_date)


class FeverHeuristic(EncounterHeuristic):
    '''
    Abstract base class for encounter heuristics, concrete instances of which
    are used as components of DiseaseDefinitions
    '''
    def __init__(self, **kwargs):
        self.name = 'fever'
        self.verbose_name = 'Fever'
        self.icd9s = ['780.6A',]
        self._register(kwargs)
    
    def encounters(self, begin_date=None, end_date=None):
        '''
        Return all encounters indicating fever.
            @type begin_date: datetime.date
            @type end_date:   datetime.date
            @type patient:    models.Demog
            @type queryset:   QuerySet
        '''
        log.debug('Get encounters matching "%s".' % self.name)
        qs = models.Enc.objects.all()
        if begin_date :
            begin = self.make_date_str(begin_date)
            qs = qs.filter(EncEncounter_Date__gte=begin)
        if end_date:
            end = self.make_date_str(end_date)
            qs = qs.filter(EncEncounter_Date__lte=end)
        # Either encounter has the 'fever' ICD9, or it records a high temp
        q_obj = self.enc_q | Q(EncTemperature__gt=100.4)
        log.debug('q_obj: %s' % q_obj)
        return qs.filter(q_obj)

class CalculatedBilirubinHeuristic(LabHeuristic):
    '''
    Special heuristic to detect high calculated bilirubin values.  Since the
    value of calculated bilirubin is the sum of results of two seperate tests
    (w/ separate LOINCs), it cannot be handled by a generic heuristic class.
    '''
    def __init__(self):
        self.name = 'high_calc_bilirubin'
        self.verbose_name = 'Calculated Bilirubin = (direct bilirubin + indirect bilirubin) > 1.5'
        self.loinc_nums = ['29760-6', '14630-8']
        self._register()
        
    def matches(self, begin_date=None, end_date=None):
        log.debug('Looking for high calculated bilirubin scores')
        # First, we return a list of patient & order date pairs, where the sum
        # of direct and indirect bilirubin tests ordered on the same day is 
        # greater than 1.5.
        relevant = self.relevant_labs(begin_date, end_date)
        vqs = relevant.values('LxPatient', 'LxOrderDate') # returns ValueQuerySet
        vqs = vqs.annotate(calc_bil=Sum('LxTest_results'))
        vqs = vqs.filter(calc_bil__gt=1.5)
        # Next we loop thru the patient/order-date list, fetch the relevant 
        # (direct + indirect) > 1.5, just in case there is a funky situation
        # where, e.g., the patient has had two indirect bilirubin tests ordered
        # on the same day.
        matches = []
        for item in vqs:
            matches += [i for i in relevant.filter(LxPatient__id=item['LxPatient'], LxOrderDate=item['LxOrderDate']) ]
        return matches
            

#===============================================================================
#
#--- ~~~ Disease Definition Framework ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BaseDiseaseDefinition:
    '''
    Abstract base class for disease definitions
    '''
    
    def __init__(self, 
        name, 
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
        self.condition = models.Rule.objects.get(ruleName=self.name)
        self._register()
    
    def generate_cases(self, new_only=False):
        '''
        Calls the user-supplied case factory with appropriate arguments
        '''
        raise NotImplementedError('This method MUST be implemented in concrete classes inheriting from BaseDiseaseDefinition.')
    
    __registry = {} # Class variable
    def _register(self):
        if self.name in self.__registry:
            raise DiseaseDefinitionAlreadyRegistered('A disease definition with the name "%s" is already registered.' % self.name)
        else:
            self.__registry[self.name] = self
    
    @classmethod
    def get_all_definitions(cls):
        '''
        Returns a list of all registered BaseHeuristic instances.
        '''
        result = []
        keys = cls.__registry.keys()
        keys.sort()
        [result.extend([cls.__registry[k]]) for k in keys]
        log.debug('All Disease Definition instances: %s' % result)
        return result
    
    @classmethod
    def generate_all_cases(cls, begin_date=None, end_date=None):
        '''
        Generate HeuristicEvent records for every registered BaseHeuristic 
            instance.
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
    
    def new_case(self, primary_event, all_events):
        '''
        Creates, saves, and returns a new Case object.  Case variables like 
            provider and date are set based on primary_event.  The set of 
            primary_event + all_events  are attached as the Case's events 
            member.
        @param primary_event: Event on which this case is based
        @type primary_event:  HeuristicEvent
        @param all_events:    All events that together establish this case
        @type all_events:     [HeuristicEvent, HeuristicEvent, ...]
        '''
        log.info('Creating a new %s case based on event:\n    %s' % (self.condition, primary_event))
        case = models.Case()
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
    
    def update_reportable_events(self, case):
        '''
        Updates the reportable events for a given case, based on rules defined
            when at BaseDiseaseDefinition instantiation.  
        @param case: The case to update
        @type case:  models.Case
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
            encounters = models.Enc.objects.filter(enc_q)
            case.encounters = sets.Set(case.encounters.all()) | sets.Set(encounters)
        if self.lab_loinc_nums:
            lab_q = Q(LxLoinc__in=self.lab_loinc_nums)
            lab_q = lab_q & Q(LxPatient=patient)
            lab_q = lab_q & Q(LxOrderDate__gte=util.str_from_date(date - self.lab_days_before))
            lab_q = lab_q & Q(LxOrderDate__lte=util.str_from_date(date + self.lab_days_after))
            log.debug('lab_q: %s' % lab_q)
            labs = models.Lx.objects.filter(lab_q)
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
            medications = models.Rx.objects.filter(med_q)
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
            existing_cases = models.Case.objects.filter(q_obj)
            for case in existing_cases:
                definition.update_reportable_events(case)


class BaseCaseDemarcator:
    '''
    Concrete instances of this abstract base class divide a set of heuristic 
    events into one or more cases.
    '''
    
    def demarcate(self, event_dict):
        raise NotImplementedError('This method MUST be implemented in concrete classes inheriting from BaseCaseDemarcator.')
        
        

class SingleHeuristicTimeWindowCaseMaker:
    '''
    Instances of this class, initialized with the name of a heuristic and a 
    time window (number of days), are suitable for use as make_cases_func in 
    a BaseDiseaseDefinition.  When called the instance generates and saves new 
    Case objects based on the named heuristic event.  All events occuring 
    within the specified time window will be grouped into a single case.
    Existing cases will be updated with any new events found, unless the
    new_only flag is set to True.
    '''
    
    def __init__(self, heuristic_name, time_window):
        self.heuristic_name = heuristic_name
        self.time_window = time_window
        assert self.heuristic_name
        assert self.time_window
        
    def __call__(self, disease, new_only=False):
        '''
        @param disease:  The BaseDiseaseDefinition calling this method
        @type disease:   BaseDiseaseDefinition
        @param new_only: Only create new cases, don't update existing cases
        @type new_only:  Boolean
        '''
        case_window = datetime.timedelta(days=self.time_window) # Group events occurring within case_window into single case
        counter = 0            # Number of new cases generated
        #bound_events = []      # Events already bound to a Case object
        #existing_cases = models.Case.objects.filter(condition=disease.condition).select_related('events')
        existing_cases = models.Case.objects.filter(condition=disease.condition)
        # 
        # Next statement causes huge number of very similar queries
        #
        #[bound_events.extend(case.events.all()) for case in existing_cases]
        #
        # Events already bound to a Case object
        bound_events = models.HeuristicEvent.objects.filter(case__in=existing_cases).select_related()
        log.debug('number of bound_events: %s' % len(bound_events))
        for event in models.HeuristicEvent.objects.filter(heuristic_name=self.heuristic_name).order_by('date').select_related():
            if event in bound_events:
                log.debug('Event #%s is already bound to a case' % event.id)
                continue # Event is already attached to a case
            patient = event.patient
            begin = event.date - case_window
            end = event.date
            primary = existing_cases.filter(patient=patient, date__gte=begin, date__lte=end)
            if primary: # This event should be attached to an existing case
                assert len(primary) == 1 # Sanity check
                primary_case = primary[0]
                if new_only:
                    log.debug('Event #%s belongs to existing case #%s, but new_only flag is set to True.  Skipping.' % (event.id, primary_case.id) )
                    continue # Don't update case
                log.debug('Attaching event:\n    %s\nto existing case\n    %s' % (event, primary_case))
                primary_case.events.add(event)
                primary_case.save()
            else: # A new case should be created for this event
                disease.new_case(event, [])
                counter += 1 # Increment new case count
        return counter
    

            
#===============================================================================
#
#--- ~~~ Encounter Heuristics ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

fever_enc = FeverHeuristic()

jaundice_enc = EncounterHeuristic(name='jaundice', 
                              verbose_name='Jaundice, not of newborn',
                              icd9s=['782.4'],
                              )

chronic_hep_b_enc = EncounterHeuristic(name='chronic_hep_b',
                                   verbose_name='Chronic Hepatitis B',
                                   icd9s=['070.32'],
                                   )

#===============================================================================
#
#--- ~~~ Lab Test Heuristics ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

alt_2x = HighNumericLabHeuristic(
    name='alt_2x',
    verbose_name='Alanine aminotransferase (ALT) >2x upper limit of normal',
    loinc_nums=['1742-6'],
    ratio=2,
    default_high=132,
    )

alt_5x = HighNumericLabHeuristic(
    name='alt_5x',
    verbose_name='Alanine aminotransferase (ALT) >5x upper limit of normal',
    loinc_nums=['1742-6'],
    ratio=5,
    default_high=330,
    )

ast_2x = HighNumericLabHeuristic(
    name='ast_2x',
    verbose_name='Aspartate aminotransferase (ALT) >2x upper limit of normal',
    loinc_nums=['1920-8'],
    ratio=2,
    default_high=132,
    )

ast_5x = HighNumericLabHeuristic(
    name='ast_5x',
    verbose_name='Aspartate aminotransferase (ALT) >5x upper limit of normal',
    loinc_nums=['1920-8'],
    ratio=5,
    default_high=330,
    )

hep_a_igm_ab = StringMatchLabHeuristic(
    name='hep_a_igm_ab',
    verbose_name='IgM antibody to Hepatitis A = "REACTIVE" (may be truncated)',
    loinc_nums=['22314-9'],
    strings=['reactiv'],
    )

hep_b_igm_ab = StringMatchLabHeuristic(
    name='hep_b_igm_ab',
    verbose_name='IgM antibody to Hepatitis B Core Antigen = "REACTIVE" (may be truncated)',
    loinc_nums = ['31204-1'],
    strings=['reactiv'],
    )

hep_b_surface = StringMatchLabHeuristic(
    name='hep_b_surface',
    verbose_name='Hepatitis B Surface Antigen = "REACTIVE" (may be truncated)',
    loinc_nums = ['5195-3'],
    strings=['reactiv'],
    )

hep_b_e_antigen = StringMatchLabHeuristic(
    name = 'hep_b_e_antigen',
    verbose_name = 'Hepatitis B "e" Antigen = "REACTIVE" (may be truncated)',
    loinc_nums = ['13954-3'],
    strings=['reactiv'],
    )

#
# Hep B Viral DNA
#
# There are three different heuristics here, a string match and a two numeric
# comparisons, all of which indicate the same condition.  Thus I have assigned
# them all the same name, so they will be identical in searches of heuristic
# events.  I think this is an okay scheme, but it doesn't quite feel elegant;
# so let me know if you can think of a better way to do it
#
#
# NOTE:  See note in Hep B google doc about "HEPATITIS B DNA, QN, IU/COPIES" 
# portion of algorithm
#
hep_b_viral_dna_str = StringMatchLabHeuristic(
    name = 'hep_b_viral_dna',
    verbose_name = 'Hepatitis B Viral DNA',
    loinc_nums = ['13126-8', '16934', '5009-6'],
    strings = ['positiv', 'detect'],
    )
hep_b_viral_dna_num1 = HighNumericLabHeuristic(
    name = 'hep_b_viral_dna',
    verbose_name = 'Hepatitis B Viral DNA',
    loinc_nums = ['16934-2'],
    default_high = 100,
    allow_duplicate_name=True,
    )
hep_b_viral_dna_num2 = HighNumericLabHeuristic(
    name = 'hep_b_viral_dna',
    verbose_name = 'Hepatitis B Viral DNA',
    loinc_nums = ['5009-6'],
    default_high = 160,
    allow_duplicate_name=True,
    )


hep_e_ab = StringMatchLabHeuristic(
    name = 'hep_a_ab',
    verbose_name = 'Hepatitis E antibody',
    loinc_nums = ['14212-5'],
    strings = ['reactiv'],
    )

hep_c_ab = StringMatchLabHeuristic(
    name = 'hep_c_ab',
    verbose_name = 'Hepatitis C antibody = "REACTIVE" (may be truncated)',
    loinc_nums = ['16128-1'],
    strings = ['reactiv'],
    )

total_bilirubin_high = HighNumericLabHeuristic(
    name = 'total_bilirubin_high',
    verbose_name = 'Total bilirubin > 1.5',
    loinc_nums = ['33899-6'],
    default_high = 1.5,
    )

high_calc_bilirubin = CalculatedBilirubinHeuristic()

GONORRHEA_LOINCS = ['691-6', '23908-7', '24111-7', '36902-5'] # Re-used in disease definition
gonorrhea = StringMatchLabHeuristic(
    name =          'gonorrhea', 
    verbose_name =  'Gonorrhea', 
    loinc_nums =    GONORRHEA_LOINCS,
    strings =       ['positiv', 'detect'], 
    abnormal_flag = True, 
    match_type =    'istartswith',
    )

CHLAMYDIA_LOINCS = ['4993-2', '6349-5', '16601-7', '20993-2', '21613-5', '36902-5', ] # Re-used in disease definition
chlamydia = StringMatchLabHeuristic(
    name =          'chlamydia', 
    verbose_name =  'Chlamydia', 
    loinc_nums =    CHLAMYDIA_LOINCS,
    strings =       ['positiv', 'detect'], 
    abnormal_flag = True, 
    match_type =    'istartswith',
    )




#===============================================================================
#
#--- ~~~ Disease Definitions ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        
def make_acute_hep_a_cases(disease, new_only=False):
    '''
    Only one Hep A case per lifetime -- so return one case, with all relevant 
        events attached.
    @param disease:  The BaseDiseaseDefinition calling this method
    @type disease:   BaseDiseaseDefinition
    @param new_only: Only create new cases, don't update existing cases
    @type new_only:  Boolean
        '''
    result = {} # {Patient: Case}
    count = 0 # New case counter
    igm_events = models.HeuristicEvent.objects.filter(heuristic_name='hep_a_igm_ab')
    for event in igm_events:
        patient = event.patient
        fourteen = datetime.timedelta(days=14)
        begin = event.date - fourteen
        end = event.date + fourteen
        other_names = ('jaundice', 'alt_2x', 'ast_2x')
        q_obj = Q(patient=patient, heuristic_name__in=other_names, date__gte=begin, date__lte=end)
        other_events = models.HeuristicEvent.objects.filter(q_obj)
        if not other_events:
            continue # Not a case
        all_events = [event] + [e for e in other_events]
        msg = '\n'
        msg += '    Acute Hepatitis A case detected for:\n'
        msg += '        %s\n' % patient
        msg += '    Components:\n'
        for e in all_events:
            msg += '        %s\n' % e.content_object
        log.info(msg)
        #
        # Case established -- but a patient can have only one Acute Hep A 
        # diagnosis per lifetime, so let's check and see if he already has 
        # one.
        #
        if patient in result: # First, have we seen it in this detection run:
            log.debug('Result list already contains case for %s.  Updating its events and continuing.' % patient)
            case = result[patient]
            case.events = sets.Set(case.events) + sets.Set(all_events)
            continue
        # Now check the db:
        # FIXME: This will need to be updated when we go to new Case model
        existing = models.Case.objects.filter(patient=patient, condition=disease.condition)
        if existing and new_only:
            log.debug('Existing case found for %s.  Flag new_only is set, so skipping & continuing.' % patient)
            continue
        elif existing:
            log.debug('Existing case found for %s.  Updating its events (not saving), putting it in result list, and continuing.' % patient)
            case = existing[0] # should be only one hep A case
            case.events = sets.Set(case.events.all()) | sets.Set(all_events)
            result[patient] = case
        else:
            # No case --
            log.debug('Creating new case for %s' % patient)
            result[patient] = disease.new_case(primary_event=event, all_events=all_events)
            count += 1
    return count

acute_hep_a = BaseDiseaseDefinition(
    name = 'Acute Hepatitis A', 
    make_cases_func = make_acute_hep_a_cases,
    icd9s = settings.DEFAULT_REPORTABLE_ICD9S,
    icd9_days_before = 14,
    icd9_days_after = 14,
    fever = True,
    lab_loinc_nums = ['1742-6', '1920-8', '22314-9', '14212-5', '16128-1'],
    lab_days_before = 30,
    lab_days_after = 30,
    )


make_chlamydia_cases = SingleHeuristicTimeWindowCaseMaker(
    heuristic_name = 'chlamydia', 
    time_window = 365
    )


class make_acute_hep_b_cases:
    '''
    Acute Hepatitis B definitions:
    1)  (jaundice OR alt_5x OR ast_5x) 
        AND hep_b_igm_ab 
        WITHIN 14 days
    2)  (jaundice OR alt_5x OR ast_5x) 
        AND (total_bilirubin_high OR high_calc_bilirubin)
        AND (hep_b_surface OR hep_b_viral_dna)
        WITHIN 21 days
        AND NOT chronic_hep_b AT THIS TIME
        AND NOT (chronic_hep_b OR hep_b_surface OR hep_b_viral_dna) EVER IN PAST
    3)  hep_b_surface
        AND NOT (hep_b_surface OR hep_b_viral_dna OR jaundice) EVER IN PAST
    '''
    
    '''
    Def 1:
    
    select e3.*
    from esp_heuristic_event e1 
    join esp_heuristic_event e2 
        on e1.patient_id = e2.patient_id 
    join esp_heuristic_event e3
        on (e3.id = e1.id) or (e3.id = e2.id)
    where e1.heuristic_name = 'hep_b_igm_ab' 
    and e2.heuristic_name in ('alt_5x', 'ast_5x', 'jaundice') 
    and e2.date > e1.date - interval 14 day
    and e2.date < e1.date + interval 14 day
    order by e3.patient_id, e3.date
    '''

    def foo(self):
        jaa = Q(heuristic_name__in=['jaundice_enc', 'alt_5x_lab', 'ast_5x_lab'])
        plus14 = Q(date)
        
    def __init__(self):
        # This is used by several definitions:
        q_obj = Q(heuristic_name__in=['jaundice_enc', 'alt_5x_lab', 'ast_5x_lab'])
        self.jaundice_alt_ast = models.Case.objects.filter(q_obj)
    
    def definition_a(self):
        result = []
        for event in models.Case.objects.filter(heuristic_name='hep_b_igm_ab_lab'):
            patient = event.patient
            fourteen = datetime.timedelta(days=14)
            begin = event.date - fourteen
            end = event.date + fourteen
            other_events = self.jaundice_alt_ast.filter(patient=patient, date__gte=begin, date__lte=end)
            all_events = [event] + [e for e in other_events]
            if not other_events:
                continue # Not a case
            ################################################################################
            # Here we should return (patient, all_events) to a calling method, which will 
            # assemble the results list.
            ################################################################################
            result += [(patient, all_events)]
        return result
    
    def __call__(self, disease, new_only):
        '''
        @param disease:  The BaseDiseaseDefinition calling this method
        @type disease:   BaseDiseaseDefinition
        @param new_only: Only create new cases, don't update existing cases
        @type new_only:  Boolean
        '''
        count = 0
        candidates = []
        for func in [self.definition_a, ]:
            candidates += func()
        result = {} # {Patient: Case}
        for patient, events in candidates:
            #
            # Case established -- but a patient can have only one Acute Hep A 
            # diagnosis per lifetime, so let's check and see if he already has 
            # one.
            #
            if patient in result: # First, have we seen it in this detection run:
                log.debug('Result list already contains case for %s.  Updating its events and continuing.' % patient)
                case = result[patient]
                case.events = sets.Set(case.events) + sets.Set(events)
                continue
            # Now check the db:
            existing = models.Case.objects.filter(patient=patient, condition=disease.condition)
            if existing and new_only:
                log.debug('Existing case found for %s.  Flag new_only is set, so skipping & continuing.' % patient)
                continue
            elif existing:
                log.debug('Existing case found for %s.  Updating its events (not saving), putting it in result list, and continuing.' % patient)
                case = existing[0] # should be only one hep A case
                case.events = sets.Set(case.events.all()) | sets.Set(events)
                result[patient] = case
            else:
                # No existing case -- let's create one
                #
                # TODO: Primary date is date of first event
                log.debug('Creating new case for %s' % patient)
                result[patient] = disease.new_case(primary_event=event, all_events=all_events)
                count += 1
        return count
            


chlamydia = BaseDiseaseDefinition(
    name = 'Chlamydia',
    make_cases_func = make_chlamydia_cases,
    icd9s = [
        '788.7',
        '099.40',
        '597.80',
        '780.6A',
        '616.0',
        '616.10',
        '623.5',
        '789.07',
        '789.04',
        '789.09',
        '789.03',
        '789.00',
        ],
    icd9_days_before = 14,
    icd9_days_after = 14,
    fever = True,
    med_names = [
        'azithromycin',
        'levofloxacin',
        'ofloxacin',
        'ciprofloxacin',
        'doxycycline',
        'eryrthromycin',
        'amoxicillin',
        'EES',
        ],
    med_days_before = 7,
    med_days_after = 14,
    # Report both Chlamydia and Gonorrhea labs
    lab_loinc_nums = CHLAMYDIA_LOINCS + GONORRHEA_LOINCS,
    lab_days_before = 30,
    lab_days_after = 30,
    )

make_gonorrhea_cases = SingleHeuristicTimeWindowCaseMaker(
    heuristic_name = 'gonorrhea', 
    time_window = 365
    )

gonorrhea = BaseDiseaseDefinition(
    name = 'Gonorrhea',
    make_cases_func = make_gonorrhea_cases,
    icd9s = [
        '788.7',
        '099.40',
        '597.80',
        '616.0',
        '616.10',
        '623.5',
        '789.07',
        '789.04',
        '789.09',
        '789.03',
        '789.00',
        ],
    icd9_days_before = 14,
    icd9_days_after = 14,
    fever = True,
    lab_loinc_nums = GONORRHEA_LOINCS, 
    lab_days_before = 28,
    lab_days_after = 28,
    med_names = [
        'amoxicillin',
        'cefixime',
        'cefotaxime',
        'cefpodoxime',
        'ceftizoxime',
        'ceftriaxone',
        'gatifloxacin',
        'levofloxacin',
        'ofloxacin',
        'spectinomycin',
        'moxifloxacin',
        ],
    med_days_before = 7,
    med_days_after = 14
    )

    
USAGE_MSG = '''\
%prog [options]

    One or more of '-e', '-c', '-u', or '-a' must be specified.
    
    DATE variables are specified in this format: '17-Mar-2009'\
'''


def main():
    # 
    # TODO: We need a lockfile or some othermeans to prevent multiple 
    # instances running at once.
    #
    parser = optparse.OptionParser(usage=USAGE_MSG)
    parser.add_option('-e', '--events', action='store_true', dest='events',
        help='Generate heuristic events')
    parser.add_option('-c', '--cases', action='store_true', dest='cases',
        help='Generate new cases')
    parser.add_option('-u', '--update-cases', action='store_true', dest='update',
        help='Update cases')
    parser.add_option('-a', '--all', action='store_true', dest='all', 
        help='Generate heuristic events, generate new cases, and update existing cases')
    parser.add_option('--begin', action='store', dest='begin', type='string', 
        metavar='DATE', help='Analyze time window beginning at DATE')
    parser.add_option('--end', action='store', dest='end', type='string', 
        metavar='DATE', help='Analyze time window ending at DATE')
    (options, args) = parser.parse_args()
    log.debug('options: %s' % options)
    #
    # Date Parser
    #
    date_format = '%d-%b-%Y'
    if options.begin:
        options.begin = datetime.datetime.strptime(options.begin, date_format).date()
    if options.end:
        options.end = datetime.datetime.strptime(options.end, date_format).date()
    #
    # Main Control block
    #
    if options.all: # '--all' is exactly equivalent to '--events --cases --update-cases'
        options.events = True
        options.cases = True
        options.update = True
    if options.events:
        BaseHeuristic.generate_all_events(begin_date=options.begin, end_date=options.end)
    if options.cases:
        BaseDiseaseDefinition.generate_all_cases(begin_date=options.begin, end_date=options.end)
    if options.update:
        BaseDiseaseDefinition.update_all_cases(begin_date=options.begin, end_date=options.end)
    if not (options.events or options.cases or options.update):
        parser.print_help()
    

def experiment():
    fever_enc.generate_events()

if __name__ == '__main__':
    #main()
    experiment()
    print 'Total Number of DB Queries: %s' % len(connection.queries)
    #pprint.pprint(connection.queries)
