#!/usr/bin/env python
'''
                                  ESP Health
                          Heuristic Events Framework
                                Core Components


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''

import datetime
import pprint
import types
import sys
import optparse
import re

from django.db import connection
from django.db.models import Q
from django.db.models import F
from django.db.models import Sum
from django.db.models.query import QuerySet
from django.contrib.contenttypes.models import ContentType


from ESP.emr.models import LabResult
from ESP.emr.models import Encounter
from ESP.emr.models import Prescription
from ESP.conf.models import NativeCode
#from ESP.conf.models import Rule
from ESP.hef.models import HeuristicEvent
from ESP import settings
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

class BaseHeuristic(object):
    '''
    Abstract interface class for heuristics, concrete instances of which are
    used as components of disease definitions.
    '''
    
    __registry = {} # Class variable
    
    def __init__(self, heuristic_name, def_name, def_version):
        '''
        @param heuristic_name: Name of this heuristic (could be shared by several instances)
        @type heuristic_name: String
        @param def_name: Name of the definition used (unique to instance)
        @type def_name: String
        @param def_version: Version of definition
        @type def_version: Integer
        '''
        assert heuristic_name
        assert def_name
        assert def_version
        self.heuristic_name = heuristic_name
        self.def_name = def_name
        self.def_version = def_version
        #
        # Register this heuristic
        #
        registry = self.__registry # For convenience
        if heuristic_name in registry:
            if self.def_name in [item.def_name for item in registry[heuristic_name]]:
                log.error('Event definition "%s" is already registered for event type "%s".' % (self.def_name, heuristic_name))
                raise HeuristicAlreadyRegistered('A BaseHeuristic instance is already registered with heuristic_name "%s".' % heuristic_name)
            else:
                log.debug('Registering additional heuristic for heuristic_name "%s".' % heuristic_name)
                registry[heuristic_name] += [self]
        else:
            log.debug('Registering heuristic with heuristic_name "%s".' % heuristic_name)
            registry[heuristic_name] = [self]
    
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
    
    @classmethod
    def get_heuristics_by_name(cls, name):
        '''
        Given a string naming a heuristic, returns the appropriate BaseHeuristic instance
        '''
        return cls.__registry[name]
    
    @classmethod
    def list_heuristic_names(cls):
        '''
        Returns a sorted list of strings naming all registered BaseHeuristic instances
        '''
        names = cls.__registry.keys()
        names.sort()
        return names
    
    
    @classmethod
    def get_all_loincs(cls):
        '''
        Returns a list of all LOINC numbers for registered heuristics
        '''
        loincs = set()
        for heuristic in cls.get_all_heuristics():
            try:
                loincs = loincs | set(heuristic.loinc_nums)
            except AttributeError:
                pass # Skip heuristics w/ no LOINCs defined
        return loincs
    
    @classmethod
    def get_all_loincs_by_event(cls):
        '''
        Returns a list of all LOINC numbers for registered heuristics
        '''
        loincs = {}
        for heuristic in cls.get_all_heuristics():
            try:
                try:
                    loincs[heuristic] += set(heuristic.loinc_nums)
                except KeyError:
                    loincs[heuristic] = set(heuristic.loinc_nums)
            except AttributeError:
                pass # Skip heuristics w/ no LOINCs defined
        return loincs
    
    def matches(self, begin_date=None, end_date=None):
        '''
        Return a QuerySet of matches for this heuristic
        '''
        raise NotImplementedError('This method MUST be implemented in concrete classes inheriting from BaseHeuristic.')
        
    def generate_events(self, incremental=True, begin_date=None, end_date=None):
        '''
        Generate HeuristicEvent records for each item returned by
        matches, if it does not already have one.
        @return: Integer number of new records created
        '''
        log.info('Generating events for heuristic "%s".' % self.heuristic_name)
        counter = 0 # Counts how many new records have been created
        # First we retrieve a list of object IDs for this 
        existing = HeuristicEvent.objects.filter(heuristic_name=self.heuristic_name).values_list('object_id')
        existing = [int(item[0]) for item in existing] # Convert to a list of integers
        #
        # Disabled select_related() because matches will most often be in 
        # existing list, and thus discarded not saved.
        #
        for event in self.matches(begin_date, end_date):
        #for event in self.matches(begin_date, end_date).select_related():
            if event.id in existing:
                log.debug('BaseHeuristic event "%s" already exists for %s #%s' % (self.heuristic_name, event._meta.object_name, event.id))
                continue
            content_type = ContentType.objects.get_for_model(event)
            obj, created = HeuristicEvent.objects.get_or_create(
                heuristic_name = self.heuristic_name,
                definition  = self.def_name,
                def_version = self.def_version,
                date = event.date,
                patient = event.patient,
                content_type = content_type,
                object_id = event.pk,
                )
            if created:
                log.info('Creating new heuristic event "%s" for %s #%s' % (self.heuristic_name, event._meta.object_name, event.id))
                obj.save()
                counter += 1
            else:
                log.debug('Did not create heuristic event - found matching event #%s' % obj.id)
        log.info('Generated %s new events for "%s".' % (counter, self.heuristic_name))
        for item in connection.queries:
            log.debug('\n\t%8s    %s' % (item['time'], item['sql']))
        connection.queries = []
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
    
    @classmethod
    def generate_events_by_name(cls, name, begin_date=None, end_date=None):
        for heuristic in cls.get_heuristics_by_name(name):
            heuristic.generate_events(begin_date, end_date)
    
    def get_events(self):
        '''
        Returns a QuerySet of all existing HeuristicEvent objects generated by
        this heuristic.
        '''
        return HeuristicEvent.objects.filter(heuristic_name=self.heuristic_name)
    
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
        return '<BaseHeuristic: %s>' % self.def_name
    
    
class LabHeuristic(BaseHeuristic):
    '''
    Abstract base class for lab test heuristics, concrete instances of which
    are used as components of DiseaseDefinitions
    '''
    
    def __init__(self, heuristic_name, def_name, def_version, loinc_nums):
        '''
        @param loinc_nums:   LOINC numbers for lab results this heuristic will examine
        @type loinc_nums:    [String, String, String, ...]
        '''
        assert loinc_nums
        self.loinc_nums = loinc_nums
        BaseHeuristic.__init__(self,
            heuristic_name = heuristic_name,
            def_name = def_name,
            def_version = def_version,
            )
    
    def relevant_labs(self, begin_date=None, end_date=None):
        '''
        Return all lab results relevant to this heuristic, whether or not they 
        indicate positive.
            @type begin_date: datetime.date
            @type end_date:   datetime.date
        '''
        log.debug('Get lab results relevant to "%s".' % self.heuristic_name)
        log.debug('Time window: %s to %s' % (begin_date, end_date))
        qs = LabResult.objects.filter_loincs(self.loinc_nums)
        if begin_date:
            qs = qs.filter(date__gte=begin_date)
        if end_date:
            qs = qs.filter(date__lte=end_date)
        return qs


class HighNumericLabHeuristic(LabHeuristic):
    '''
    Matches labs results with high numeric scores, as determined by a ratio to 
    that result's reference high, with fall back to a default high value.
    '''
    
    def __init__(self, heuristic_name, def_name, def_version, loinc_nums, 
        ratio=None, default_high=None, exclude=False):
        '''
        @param ratio:        Match on result > ratio * reference_high
        @type ratio:         Integer
        @param default_high: If no reference high, match on result > default_high
        @type default_high:  Integer
        '''
        assert ratio or default_high
        self.default_high = default_high
        self.ratio = ratio
        LabHeuristic.__init__(self,
            heuristic_name = heuristic_name,
            def_name = def_name,
            def_version = def_version,
            loinc_nums = loinc_nums,
            )
    
    def matches(self, begin_date=None, end_date=None):
        '''
        If record has a reference high, and a ratio has been specified, compare
        test result against that reference.  If a record does not have a
        reference high, and a default_high has been specified, compare result
        against that default 'high' value.
        @type begin_date: datetime.date
        @type end_date:   datetime.date
        '''
        relevant_labs = self.relevant_labs(begin_date, end_date)
        no_ref_q = Q(ref_high=None)
        if self.default_high:
            static_comp_q = no_ref_q & Q(result_float__gt=self.default_high)
            pos_q = static_comp_q
        if self.ratio:
            ref_comp_q = ~no_ref_q & Q(result_float__gt=F('ref_high') * self.ratio)
            pos_q = ref_comp_q
        if self.default_high and self.ratio:
            pos_q = (ref_comp_q | static_comp_q)
        log.debug('pos_q: %s' % pos_q)
        result = relevant_labs.filter(pos_q)
        return result


class StringMatchLabHeuristic(LabHeuristic):
    '''
    Matches labs with results containing specified strings
    '''
    
    def __init__(self, heuristic_name, def_name, def_version, loinc_nums, strings=[], 
        abnormal_flag=False, match_type='istartswith', exclude=False):
        '''
        @param strings:       Strings to match against
        @type strings:          [String, String, String, ...]
        @param abnormal_flag: If true, a lab result with its 'abnormal' flag
            set will count as a match
        @type abnormal_flag:  Boolean
        @param match_type:    Right now, only 'istartswith'
        @type match_type:     String
        @param exclude:       Returns relevant labs where the string does NOT match
        @type  exclude:       Boolean
        '''
        assert strings or abnormal_flag
        assert match_type
        self.strings = strings
        self.abnormal_flag = abnormal_flag
        self.match_type = match_type
        self.exclude = exclude
        LabHeuristic.__init__(self,
            heuristic_name = heuristic_name,
            def_name = def_name,
            def_version = def_version,
            loinc_nums = loinc_nums,
            )
    
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
            pos_q = Q(result_string__istartswith=self.strings[0])
            for s in self.strings[1:]:
                pos_q = pos_q | Q(result_string__istartswith=s)
            if self.abnormal_flag:
                msg = 'IMPORTANT: Support for abnormal-flag-based queries has not yet been implemented!\n'
                msg += '    Our existing data has only nulls for that field, so I am not sure what the query should look like.'
                log.critical(msg)
        else:
            raise NotImplementedError('The only match type supported at this time is "istartswith".')
        log.debug('pos_q: %s' % pos_q)
        if self.exclude:
            result = self.relevant_labs(begin_date, end_date).exclude(pos_q)
        else:
            result = self.relevant_labs(begin_date, end_date).filter(pos_q)
        return result



class EncounterHeuristic(BaseHeuristic):
    '''
    Abstract base class for encounter heuristics, concrete instances of which
    are used as components of DiseaseDefinitions
    '''
    def __init__(self, heuristic_name, def_name, def_version, icd9s):
        '''
        @type name:         String
        @type icd9s:        [String, String, String, ...]
        @type verbose_name: String
        @type match_style:  String (either 'icontains' or 'iexact')
        '''
        assert icd9s
        self.icd9s = icd9s
        BaseHeuristic.__init__(self,
            heuristic_name = heuristic_name,
            def_name = def_name,
            def_version = def_version,
            )
    
    def __get_enc_q(self):
        '''
        Returns a Q object to select all Encounters indicated by self.icd9s
        '''
        enc_q = Q()
        for code in self.icd9s:
            enc_q = enc_q | Q(icd9_codes__code=code)
        return enc_q
    enc_q = property(__get_enc_q)

    def encounters(self, begin_date=None, end_date=None):
        '''
        Return all lab results relevant to this heuristic, whether or not they 
        indicate positive.
            @type begin_date: datetime.date
            @type end_date:   datetime.date
            @type patient:    Demog
            @type queryset:   QuerySet
        '''
        log.debug('Get encounters relevant to "%s".' % self.heuristic_name)
        qs = Encounter.objects.all()
        if begin_date :
            begin = self.make_date_str(begin_date)
            qs = qs.filter(date__gte=begin)
        if end_date:
            end = self.make_date_str(end_date)
            qs = qs.filter(date__lte=end)
        elif begin_date or end_date:
            raise 'If you specify either begin_date or end_date, you must also specify the other.'
        qs = qs.filter(self.enc_q)
        return qs
    
    def matches(self, begin_date=None, end_date=None):
        return self.encounters(begin_date, end_date)


class FeverHeuristic(BaseHeuristic):
    '''
    Abstract base class for encounter heuristics, concrete instances of which
    are used as components of DiseaseDefinitions
    '''
    def __init__(self, heuristic_name, def_name, def_version, temperature=None,  icd9s=[]):
        assert (icd9s or temperature)
        self.temperature = temperature
        self.icd9s = icd9s
        BaseHeuristic.__init__(self,
            heuristic_name = heuristic_name,
            def_name = def_name,
            def_version = def_version,
            )
    
    def matches(self, begin_date=None, end_date=None, queryset=None):
        '''
        Return all encounters indicating fever.
            @type begin_date: datetime.date
            @type end_date:   datetime.date
            @type queryset:   QuerySet
        '''
        log.debug('Get encounters matching "%s".' % self.heuristic_name)
        enc_q = Q()
        for code in self.icd9s:
            enc_q = enc_q | Q(icd9_codes__code=code)
        qs = Encounter.objects.all()
        if begin_date :
            begin = self.make_date_str(begin_date)
            qs = qs.filter(date__gte=begin)
        if end_date:
            end = self.make_date_str(end_date)
            qs = qs.filter(date__lte=end)
        # Either encounter has the 'fever' ICD9, or it records a high temp
        q_obj = enc_q | Q(temperature__gt=self.temperature)
        log.debug('q_obj: %s' % q_obj)
        qs = qs.filter(q_obj)
        return qs


class CalculatedBilirubinHeuristic(LabHeuristic):
    '''
    Special heuristic to detect high calculated bilirubin values.  Since the
    value of calculated bilirubin is the sum of results of two seperate tests
    (w/ separate LOINCs), it cannot be handled by a generic heuristic class.
    '''
    def __init__(self):
        self.loinc_nums = ['29760-6', '14630-8']
        BaseHeuristic.__init__(self, 
            heuristic_name='high_calc_bilirubin', 
            def_name = 'High Calculated Bilirubin Event Definition 1',
            def_version = 1,
            )
        
    def matches(self, begin_date=None, end_date=None):
        log.debug('Looking for high calculated bilirubin scores')
        # First, we return a list of patient & order date pairs, where the sum
        # of direct and indirect bilirubin tests ordered on the same day is 
        # greater than 1.5.
        relevant = self.relevant_labs(begin_date, end_date)
        vqs = relevant.values('patient', 'date') # returns ValueQuerySet
        vqs = vqs.annotate(calc_bil=Sum('result_float'))
        vqs = vqs.filter(calc_bil__gt=1.5)
        # Now we retrieve the matches -- this is a huuuuuuge query: it takes a 
        # long time just for Django to build it, and even longer for the DB to 
        # execute it.  But is there a better solution?  
        matches = LabResult.objects.filter(pk__isnull=True) # QuerySet that matches nothing
        for item in vqs:
            matches = matches | relevant.filter(patient=item['patient'], date=item['date']) 
        return matches
    
    def newmatches(self, begin_date=None, end_date=None):
        log.debug('Looking for high calculated bilirubin scores')
        # First, we return a list of patient & order date pairs, where the sum
        # of direct and indirect bilirubin tests ordered on the same day is 
        # greater than 1.5.
        relevant = self.relevant_labs(begin_date, end_date).filter(date__isnull=False)
        vqs = relevant.values('patient', 'date') # returns ValueQuerySet
        vqs = vqs.annotate(calc_bil=Sum('result_float'))
        vqs = vqs.filter(calc_bil__gt=1.5)
        # Now, instead of returning a QuerySet -- which would require a hugely
        # complex, slow query -- we go and fetch the individual matches into a 
        match_ids = set()
        for item in vqs:
            match_ids = match_ids | set(relevant.filter(patient=item['patient'], date=item['date']).values_list('id', flat=True))
            print len(match_ids)
        #return matches
    