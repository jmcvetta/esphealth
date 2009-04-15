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


from ESP.esp.models import Lx, Enc, Rx
from ESP.conf.models import Rule
from ESP.hef.models import NativeToLoincMap, HeuristicEvent
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
            #raise HeuristicAlreadyRegistered('A BaseHeuristic instance is already registered with name "%s".' % name)
            log.warning('A BaseHeuristic instance is already registered with name "%s".' % name)
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
        Generate HeuristicEvent records for each item returned by
        matches, if it does not already have one.
        @return: Integer number of new records created
        '''
        log.info('Generating events for heuristic "%s".' % self.name)
        counter = 0 # Counts how many new records have been created
        # First we retrieve a list of object IDs for this 
        existing = HeuristicEvent.objects.filter(heuristic_name=self.name).values_list('object_id')
        existing = [int(item[0]) for item in existing] # Convert to a list of integers
        for event in self.matches(begin_date, end_date).select_related():
            if event.id in existing:
                log.debug('BaseHeuristic event "%s" already exists for %s #%s' % (self.name, event._meta.object_name, event.id))
                continue
            content_type = ContentType.objects.get_for_model(event)
            obj, created = HeuristicEvent.objects.get_or_create(heuristic_name=self.name,
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
        @param name:         Short name -- used internally to identify this heuristic's results
        @type name:          String
        @param verbose_name: Long name of this heuristic -- for display only
        @type verbose_name:  String
        @param loinc_nums:   LOINC numbers for lab results this heuristic will examine
        @type loinc_nums:    [String, String, String, ...]
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
        codes = NativeToLoincMap.objects.filter(loinc__in=self.loinc_nums).values_list('native_code', flat=True)
        if not codes: # Is length of codes == 0?
            log.critical('Could not generate events for heuristic "%s" because no LOINCs can be mapped to native codes' % self.name)
            return Q(pk__isnull=True) # Matches nothing
        lab_q = Q(native_code__in=codes)
        log.debug('lab_q for %s: %s' % (self.name, lab_q) )
        return lab_q
    lab_q = property(__get_lab_q)
        
    def relevant_labs(self, begin_date=None, end_date=None):
        '''
        Return all lab results relevant to this heuristic, whether or not they 
        indicate positive.
            @type begin_date: datetime.date
            @type end_date:   datetime.date
            @type patient:    Demog
            @type queryset:   QuerySet
        '''
        log.debug('Get lab results relevant to "%s".' % self.name)
        log.debug('Time window: %s to %s' % (begin_date, end_date))
        qs = Lx.objects.all()
        if begin_date:
            qs = qs.filter(date__gte=begin_date)
        if end_date:
            qs = qs.filter(date__lte=end_date)
        qs = qs.filter(self.lab_q)
        return qs


class HighNumericLabHeuristic(LabHeuristic):
    '''
    Matches labs results with high numeric scores, as determined by a ratio to 
    that result's reference high, with fall back to a default high value.
    '''
    
    def __init__(self, name, verbose_name=None, loinc_nums=[], ratio=None, default_high=None, **kwargs):
        '''
        @param name:         Name of this heuristic (short slug)
        @type name:          String
        @param verbose_name: Long name of this heuristic
        @type verbose_name:  String
        @param loinc_nums:   LOINC numbers relevant to this heuristic
        @type loinc_nums:    [String, String, String, ...]
        @param ratio:        Match on result > ratio * reference_high
        @type ratio:         Integer
        @param default_high: If no reference high, match on result > default_high
        @type default_high:  Integer
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
        @type begin_date: datetime.date
        @type end_date:   datetime.date
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
        result = relevant_labs.filter(pos_q)
        return result


class StringMatchLabHeuristic(LabHeuristic):
    '''
    Matches labs with results containing specified strings
    '''
    
    def __init__(self, name, verbose_name=None, loinc_nums=[], strings=[], 
        abnormal_flag=False, match_type='istartswith', exclude=False, **kwargs):
        '''
        @param name:          Name of this heuristic (short slug)
        @type name:           String
        @param verbose_name:  Long name of this heuristic
        @type verbose_name:   String
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
        self.name = name
        self.verbose_name = verbose_name
        self.loinc_nums = loinc_nums
        self.strings = strings
        self.abnormal_flag = abnormal_flag
        self.match_type = match_type
        self.exclude = exclude
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
    def __init__(self, name, icd9s, verbose_name=None, **kwargs):
        '''
        @type name:         String
        @type icd9s:        [String, String, String, ...]
        @type verbose_name: String
        @type match_style:  String (either 'icontains' or 'iexact')
        '''
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
            @type patient:    Demog
            @type queryset:   QuerySet
        '''
        log.debug('Get encounters relevant to "%s".' % self.name)
        qs = Enc.objects.all()
        if begin_date :
            begin = self.make_date_str(begin_date)
            qs = qs.filter(EncEncounter_Date__gte=begin)
        if end_date:
            end = self.make_date_str(end_date)
            qs = qs.filter(EncEncounter_Date__lte=end)
        elif begin_date or end_date:
            raise 'If you specify either begin_date or end_date, you must also specify the other.'
        qs = qs.filter(self.enc_q)
        return qs
    
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
            @type patient:    Demog
            @type queryset:   QuerySet
        '''
        log.debug('Get encounters matching "%s".' % self.name)
        qs = Enc.objects.all()
        if begin_date :
            begin = self.make_date_str(begin_date)
            qs = qs.filter(EncEncounter_Date__gte=begin)
        if end_date:
            end = self.make_date_str(end_date)
            qs = qs.filter(EncEncounter_Date__lte=end)
        # Either encounter has the 'fever' ICD9, or it records a high temp
        q_obj = self.enc_q | Q(EncTemperature__gt=100.4)
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
        matches = Lx.objects.filter(pk__isnull=True) # Lx QuerySet that matches nothing
        for item in vqs:
            matches = matches | relevant.filter(LxPatient__id=item['LxPatient'], LxOrderDate=item['LxOrderDate']) 
        return matches
