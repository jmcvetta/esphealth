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
import string

from django.db import transaction
from django.db.models import Q
from django.db.models import F
from django.db.models import Sum
from django.db.models import Min
from django.db.models import Max
from django.db.models.query import QuerySet
from django.contrib.contenttypes.models import ContentType


from ESP.emr.models import LabResult
from ESP.emr.models import Encounter
from ESP.emr.models import Prescription
from ESP.conf.models import CodeMap
from ESP.static.models import Loinc
from ESP.static.models import Icd9
from ESP.hef.models import Event
from ESP.hef.models import Run
from ESP.hef.models import Pregnancy
from ESP import settings
from ESP.utils import utils as util
from ESP.utils.utils import log
from ESP.utils.utils import log_query


POSITIVE_STRINGS = ['reactiv', 'pos', 'detec', 'confirm']
NEGATIVE_STRINGS = ['non', 'neg', 'not', 'nr']



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

    def __init__(self, name, long_name):
        '''
        @param heuristic: Name of this heuristic (could be shared by several instances)
        @type heuristic: String
        @param def_name: Name of the definition used (unique to instance)
        @type def_name: String
        @param def_version: Version of definition
        @type def_version: Integer
        '''
        assert name
        assert long_name
        self.name = name
        self.long_name = long_name
        #
        # Register this heuristic
        #
        registry = self.__registry # For convenience
        if name in registry:
            log.error('Event %s is already registered.' % name)
            raise HeuristicAlreadyRegistered('A BaseHeuristic instance is already registered with heuristic "%s".' % name)
        else:
            log.debug('Registering heuristic: "%s".' % name)
            registry[name] = self

    @classmethod
    def all_heuristics(cls):
        '''
        Returns a list of all registered BaseHeuristic instances.
        '''
        result = []
        keys = cls.__registry.keys()
        keys.sort()
        [result.append(cls.__registry[key]) for key in keys]
        log.debug('All BaseHeuristic instances: %s')
        for item in result:
            log.debug('    %s' % item)
        return result

    @classmethod
    def get_heuristic(cls, name):
        '''
        Given a string naming a heuristic, returns the appropriate BaseHeuristic instance
        '''
        return cls.__registry[name]

    @classmethod
    def all_event_names(cls, choices=False):
        '''
        Returns a sorted list of strings naming all registered BaseHeuristic instances
        @param choices: If true, return a list of two-tuples suitable for use with a form ChoiceField
        @type choices: Boolean
        '''
        all_names = set()
        [all_names.update(set(cls.__registry[i].event_names)) for i in cls.__registry]
        all_names = list(all_names)
        all_names.sort()
        return all_names
    
    @classmethod
    def lab_heuristic_choices(cls):
        out = []
        for item in cls.__registry:
            heuristic = cls.__registry[item]
            if not isinstance(heuristic, BaseLabHeuristic):
                continue
            display = '%s --- %s' % (item, heuristic.long_name)
            out.append( (item, display) )
        out.sort()
        return out
    
    @classmethod
    def lab_heuristics(cls):
        out = set()
        for item in cls.__registry:
            heuristic = cls.__registry[item]
            if isinstance(heuristic, BaseLabHeuristic):
                out.add(heuristic)
        return out

    def matches(self, exclude_bound=True):
        '''
        Return a QuerySet of matches for this heuristic
        @param exclude_bound: Should we exclude labs that are already bound to 
            an event of this heuristic type?
        @type exclude_bound: Boolean
        '''
        raise NotImplementedError('This method MUST be implemented in concrete classes inheriting from BaseHeuristic.')

    def generate_events(self, run, name=None, date_field=None, **kw):
        '''
        Generate Event records for each item returned by self.matches().
        @param run: Current HEF run
        @type  run: Instance of ESP.hef.models.Run
        @param name: Use this heuristic name instead of self.name
        @type  name: String
        @param **kw: Keyword arguments are fed to self.matches()
        @return: Integer number of new records created
        '''
        counter = 0 # Counts how many new records have been created
        if not name:
            name = self.name
        for event in self.matches(**kw).select_related():
            event_date = event.date
            if date_field == 'result': # Lab Order
                event_date = event.result_date
            if date_field == 'order': # Lab Result
                event_date = event.date
            content_type = ContentType.objects.get_for_model(event)
            obj = Event(
                name = name,
                date = event_date,
                patient = event.patient,
                run = run,
                content_type = content_type,
                object_id = event.pk,
                )
            sid = transaction.savepoint()
            try:
                obj.save()
                counter += 1
                transaction.savepoint_commit(sid)
                log.info('Created new heuristic event "%s" for %s # %s' % (name, event._meta.object_name, event.id))
            except KeyboardInterrupt, e:
                # Allow keyboard interrupt to rise to next catch in main()
                raise e
            except BaseException, e:
                transaction.savepoint_rollback(sid)
                log.debug('Did not create heuristic event - found matching event #%s' % obj.id)
                log.debug('   name: %s' % obj.name)
                log.debug('   date: %s' % obj.date)
                log.debug('   patient #: %s' % obj.patient.pk)
                log.debug('   content_type: %s' % obj.content_type)
                log.debug('   object_id: %s' % obj.object_id)
        log.info('Generated %s new events for "%s".' % (counter, name))
        return counter

    @classmethod
    def generate_all_events(cls, run, **kw):
        '''
        Generate Event records for every registered BaseHeuristic 
            instance.
        @return:           Integer number of new records created
        '''
        counter = 0 # Counts how many total new records have been created
        for heuristic in cls.all_heuristics():
            counter += heuristic.generate_events(run)
        log.info('Generated %s TOTAL new events.' % counter)
        return counter

    @classmethod
    def generate_events_by_name(cls, name, run):
        cls.get_heuristic(name).generate_events(run)

    def __get_events(self):
        '''
        Returns a QuerySet of all existing Event objects generated by
        this heuristic.
        '''
        log.debug('Getting all events for heuristic name %s' % self.name)
        return Event.objects.filter(name = self.name)
    events = property(__get_events)
    
    def __get_event_names(self):
        return set([self.name])
    event_names = property(__get_event_names)
    
    @classmethod
    def get_heuristic_from_event_name(cls, event_name):
        '''
        Given an Event name, get the BaseHeuristic child instance that generates it.
        '''
        for i in cls.__registry:
            heuristic = cls.__registry[i]
            if event_name in heuristic.event_names:
                return heuristic

    def __repr__(self):
        return '<%s: %s>' % (type(self), self.name)
    
    def __get_relevant_labs(self):
        '''
        Return a QuerySet of LabResult objects relevant to this heuristic.  
        This is a null set for non-lab child classes.
        '''
        return LabResult.objects.none()
    relevant_labs = property(__get_relevant_labs)
    


class BaseLabHeuristic(BaseHeuristic):
    '''
    Abstract base class for lab test heuristics, concrete instances of which
    are used as components of DiseaseDefinitions
    '''

    def __get_relevant_labs(self):
        '''
        Return all lab results relevant to this heuristic, whether or not they 
        indicate positive.
        @param exclude_bound: Should we exclude labs that are already bound to 
            an event of this heuristic type?
        @type exclude_bound: Boolean
        '''
        log.debug('Get lab results relevant to "%s".' % self.name)
        native_codes = CodeMap.objects.filter(heuristic=self.name).values('native_code')
        qs = LabResult.objects.filter(native_code__in=native_codes)
        return qs
    relevant_labs = property(__get_relevant_labs)


class LabResultHeuristic(BaseLabHeuristic):
    '''
    All-singing, all-dancing heuristic for most lab types.
    '''

    def __init__(self, name, long_name,  positive_events = True, negative_events=False, 
        order_events=False, ratio_events=[], fixed_threshold_events=[], 
        extra_positive_strings=[], extra_negative_strings=[], date_field='order',):
        '''
        @param name: Short name of this heuristic.  Should be suitable for use in a SlugField.
        @type  name: String
        @param long_name: Long display name for this heuristic
        @type  long_name: String
        @param ratio: Match on result_float >= (ref_high_float * ratio)
        @type  ratio: Integer
        @param negative_events: Should we also generate events for negative results?
        @type  negative_events: Boolean
        @param order_events: Should we also generate events for lab orders, regardless of result?
        @type  order_events: Boolean
        @param fixed_threshold_events: Generates events based on a fixed threshold, regardless of reference high 
        @type fixed_threshold_events:  [Float, Float, ...]
        @param extra_positive_strings: Additional strings indicating positive test
        @type extra_positive_strings:  [String, String, ...]
        @param extra_negative_strings: Additional strings indicating negative test
        @type extra_negative_strings:  [String, String, ...]
        @param date_field: Which field, order date or result date, should event's date be based upon?
        @type date_field:  String (either 'order' or 'result')
        '''
        assert (positive_events or negative_events or order_events or ratio_events or fixed_threshold_events)
        assert date_field in ['order', 'result']
        self.positive_events = positive_events
        self.negative_events = negative_events
        self.order_events = order_events
        self.ratio_events = ratio_events
        self.fixed_threshold_events = fixed_threshold_events
        self.extra_positive_strings = extra_positive_strings
        self.extra_negative_strings = extra_negative_strings
        self.date_field = date_field
        for ratio in ratio_events:
            assert isinstance(ratio, int) or isinstance(ratio, float)
        for threshold in fixed_threshold_events:
            assert isinstance(threshold, int) or isinstance(threshold, float)
        BaseLabHeuristic.__init__(self,
            name = name,
            long_name = long_name,
            )
    
    def ratio_matches(self, ratio, exclude_bound=True):
        '''
        Return labs where result_float > ref_high_float * ratio
        @param ratio: Ratio used to generate this type of event
        @type  ratio: Int or Float
        '''
        has_ref_high = Q(ref_high_float__isnull=False) # Record does NOT have NULL value for ref_high_float
        null_ref_high = Q(ref_high_float__isnull=True) # Record has NULL value for ref_high_float
        ratio_q = has_ref_high & Q(result_float__gt = F('ref_high_float') * float(ratio))
        fallback_q = None # Fallback to comparison with 
        for map in CodeMap.objects.filter(heuristic=self.name).filter(threshold__isnull=False):
            q_obj = Q(native_code=map.native_code) & null_ref_high & Q(result_float__gt = map.threshold * float(ratio))
            if fallback_q:
                fallback_q |= q_obj
            else:
                fallback_q = q_obj
        if fallback_q:
            result = self.relevant_labs.filter(ratio_q | fallback_q)
        else:
            result = self.relevant_labs.filter(ratio_q)
        if exclude_bound:
            q_obj = ~Q(events__name=self.ratio_name(ratio))
            result = result.filter(q_obj)
        log_query('Matches query for %s' % self.ratio_name(ratio), result)
        return result
    
    def order_matches(self, exclude_bound=True):
        '''
        Return all matching labs, regardless of 
        '''
        result = self.relevant_labs
        if exclude_bound:
            q_obj = ~Q(events__name=self.order_name)
            result = result.filter(q_obj)
        log_query('Query for heuristic %s' % self.order_name, result)
        return result
    
    def fixed_threshold_matches(self, threshold, exclude_bound=True):
        '''
        Return labs where result_float > threshold
        @param ratio: Ratio used to generate this type of event
        @type  ratio: Int or Float
        '''
        qs = self.relevant_labs
        if exclude_bound:
            q_obj = ~Q(events__name=self.fixed_threshold_name(threshold))
            qs = qs.filter(q_obj)
        qs = qs.filter(result_float__gt=float(threshold))
        log_query('Query for %s' % self.fixed_threshold_name(threshold), qs)
        return qs

    def matches(self, exclude_bound=True, result_type='positive', ratio=None, threshold=None):
        '''
        If record has a reference high, and a ratio has been specified, compare
        test result against that reference.  If a record does not have a
        reference high, and a default_high has been specified, compare result
        against that default 'high' value.
        '''
        assert result_type in ['positive', 'negative', 'order', 'ratio', 'threshold']
        if result_type == 'positive':
            event_name = self.pos_name
        elif result_type == 'negative':
            event_name = self.neg_name
        elif result_type == 'order':
            return self.order_matches(exclude_bound=exclude_bound)
        elif result_type == 'ratio':
            assert ratio
            return self.ratio_matches(ratio=ratio, exclude_bound=exclude_bound)
        elif result_type == 'threshold':
            assert threshold
            return self.fixed_threshold_matches(threshold=threshold, exclude_bound=exclude_bound)
        else:
            raise RuntimeError('This should never happen.  Consult the developers.')
        ################################################################################
        # 
        # Everything below this point assumes we are looking for pos or neg match
        #
        log.info('Finding matches for heuristic %s' % event_name)
        code_maps = CodeMap.objects.filter(heuristic=self.name)
        native_codes = code_maps.values_list('native_code')
        has_ref_high = Q(ref_high_float__isnull=False) # Record does NOT have null value for ref_high_float
        log.debug('Code maps: %s' % pprint.pformat(code_maps))
        #
        # Build numeric query
        #
        #
        # Not doing abnormal flag yet, because many values are not null but a blank string
        #
        #if result_type == 'positive':
            #pos_q = Q(abnormal_flag__isnull=False)
        #else:
            #pos_q = None
        pos_q = None
        for map in code_maps:
            #
            # Build numeric comparison queries
            #
            thresh_q = None
            ratio_q = None
            if result_type == 'positive':
                if map.threshold:
                    thresh_q = Q(result_float__gt = float(map.threshold))
                ratio_q = has_ref_high & Q(result_float__gt = F('ref_high_float'))
            else: # result_type == 'negative'
                if map.threshold:
                    thresh_q = Q(result_float__lte = float(map.threshold))
                ratio_q = has_ref_high & Q(result_float__lte = F('ref_high_float'))
            # 
            # Combine restrict numeric comparison(s) to relevant native_code.
            #
            q_obj = Q(native_code=map.native_code)
            if thresh_q:
                q_obj &= (thresh_q | ratio_q)
            else:
                q_obj &= ratio_q
            if pos_q:
                pos_q |= q_obj
            else:
                pos_q = q_obj
        #
        # Build string query
        #
        # When using ratio, we cannot rely on a test being "POSITIVE" from 
        # lab, since we may be looking for higher value.
        strings_q = None
        if result_type == 'positive':
            strings = POSITIVE_STRINGS + self.extra_positive_strings
        else:
            strings = NEGATIVE_STRINGS + self.extra_negative_strings
        assert strings
        for s in strings:
            q_obj = Q(result_string__istartswith = s)
            if strings_q: 
                strings_q |= q_obj
            else:
                strings_q = q_obj
        if pos_q:
            pos_q |= strings_q
        else:
            pos_q = strings_q
        #
        # Only look at relevant labs.  We do this for both numeric & string 
        # subqueries, for faster overall query performance.
        #
        pos_q &= Q(native_code__in=native_codes)
        #
        # Exclude labs that are already bound to an event
        #
        if exclude_bound:
            pos_q &= ~Q(events__name=event_name)
        labs = LabResult.objects.filter(pos_q)
        log_query('Query for heuristic %s' % event_name, labs)
        return labs
    
    def generate_events(self, run):
        '''
        Generate positive, and if defined negative, events
        '''
        counter = 0
        if self.positive_events:
            counter += BaseHeuristic.generate_events(self, run, name=self.pos_name, date_field=self.date_field, result_type='positive')
        if self.negative_events:
            counter += BaseHeuristic.generate_events(self, run, name=self.neg_name, date_field=self.date_field, result_type='negative')
        if self.order_events:
            counter += BaseHeuristic.generate_events(self, run, name=self.order_name, date_field=self.date_field, result_type='order')
        for ratio in self.ratio_events:
            counter += BaseHeuristic.generate_events(self, run, name=self.ratio_name(ratio), date_field=self.date_field, result_type='ratio', ratio=ratio)
        for threshold in self.fixed_threshold_events:
            counter += BaseHeuristic.generate_events(self, run, name=self.fixed_threshold_name(threshold), date_field=self.date_field, result_type='threshold', threshold=threshold)
        return counter
    
    ################################################################################
    #
    # Event Names  
    #
    # This heuristic generates events with different names, depending on 
    # whether the event indicates a positive test result, a negative test 
    # result, or a test order.
    #
    ################################################################################
    
    def __get_pos_name(self):
        ''' Returns name for negative lab result heuristic event '''
        return self.name + '_pos'
    pos_name = property(__get_pos_name)
    
    def __get_neg_name(self):
        ''' Returns name for positive lab result heuristic event '''
        return self.name + '_neg'
    neg_name = property(__get_neg_name)
    
    def __get_order_name(self):
        ''' Returns name for lab order heuristic event '''
        return self.name + '_order'
    order_name = property(__get_order_name)
    
    def fixed_threshold_name(self, threshold):
        '''
        Return the event name for specified threshold
        @param ratio: Ratio used to generate this type of event
        @type  ratio: Int or Float
        '''
        return '%s_%s' % (self.name, threshold)
    
    def ratio_name(self, ratio):
        '''
        Return the event name for specified ratio
        @param ratio: Ratio used to generate this type of event
        @type  ratio: Int or Float
        '''
        return '%s_%sx' % (self.name, ratio)
    
    def __get_event_names(self):
        l = [self.pos_name]
        if self.negative_events:
            l.append(self.neg_name)
        if self.order_events:
            l.append(self.order_name)
        for ratio in self.ratio_events:
            l.append(self.ratio_name(ratio))
        for threshold in self.fixed_threshold_events:
            l.append(self.fixed_threshold_name(threshold))
        return set(l)
    event_names = property(__get_event_names)
    
    


class EncounterHeuristic(BaseHeuristic):
    '''
    Abstract base class for encounter heuristics, concrete instances of which
    are used as components of DiseaseDefinitions
    '''
    def __init__(self, name, long_name, icd9s, match_style='exact'):
        '''
        @type name:         String
        @type icd9s:        [String, String, String, ...]
        @type match_style:  String (see assertion below)
        '''
        assert icd9s
        self.icd9s = icd9s
        assert match_style in ['exact', 'startswith', 'iexact', 'istartswith']
        self.match_style = match_style
        super(EncounterHeuristic, self).__init__(
            name = name,
            long_name = long_name,
            )

    def __get_icd9_objects(self):
        '''
        Returns the actual Icd9 objects for which this heuristic is looking 
        for linked encounters .
        '''
        q_obj = Q()
        for code in self.icd9s:
            if self.match_style == 'exact':
                q_obj |= Q(code__exact = code)
            elif self.match_style == 'iexact':
                q_obj |= Q(code__iexact = code)
            elif self.match_style == 'startswith':
                q_obj |= Q(code__startswith = code)
            elif self.match_style == 'istartswith':
                q_obj |= Q(code__istartswith = code)
        return Icd9.objects.filter(q_obj)
    icd9_objects = property(__get_icd9_objects)
    
    def __get_enc_q(self):
        '''
        Returns a Q object to select all Encounters indicated by self.icd9s
        '''
        return Q(icd9_codes__in=self.icd9_objects)
    enc_q = property(__get_enc_q)

    def encounters(self, exclude_bound=True):
        '''
        Return all encounters relevant to this heuristic
            @type patient:    Demog
            @type queryset:   QuerySet
        '''
        log.debug('Get encounters relevant to "%s".' % self.name)
        qs = Encounter.objects.all()
        if exclude_bound:
            q_obj = ~Q(events__name=self.name)
            qs = qs.filter(q_obj)
        qs = qs.filter(self.enc_q)
        log_query('Encounters for %s' % self, qs )
        return qs

    def matches(self, exclude_bound=True):
        qs = self.encounters(exclude_bound=exclude_bound)
        log_query('Query for heuristic %s' % self.name, qs)
        return qs
        

class FeverHeuristic(BaseHeuristic):
    '''
    Abstract base class for encounter heuristics, concrete instances of which
    are used as components of DiseaseDefinitions
    '''
    def __init__(self, name, long_name, temperature = None, icd9s = []):
        assert (icd9s or temperature)
        self.temperature = temperature
        self.icd9s = icd9s
        BaseHeuristic.__init__(self,
            name = name,
            long_name = long_name,
            )

    def matches(self, queryset=None, exclude_bound=True):
        '''
        Return all encounters indicating fever.
            @type queryset:   QuerySet
        '''
        log.debug('Get encounters matching "%s".' % self.name)
        enc_q = None
        for code in self.icd9s:
            if enc_q:
                enc_q |= Q(icd9_codes__code = code)
            else:
                enc_q = Q(icd9_codes__code = code)
        qs = Encounter.objects.all()
        if exclude_bound:
            q_obj = ~Q(events__name=self.name)
            qs = qs.filter(q_obj)
        # Either encounter has the 'fever' ICD9, or it records a high temp
        q_obj = enc_q | Q(temperature__gt = self.temperature)
        log.debug('q_obj: %s' % q_obj)
        qs = qs.filter(q_obj)
        log_query('Query for heuristic %s' % self.name, qs)
        return qs


class CalculatedBilirubinHeuristic(BaseLabHeuristic):
    '''
    Special heuristic to detect high calculated bilirubin values.  Since the
    value of calculated bilirubin is the sum of results of two seperate tests
    (w/ separate LOINCs), it cannot be handled by a generic heuristic class.
    '''
    def __init__(self):
        self.loinc_nums = ['29760-6', '14630-8']
        BaseHeuristic.__init__(self,
            name = 'high_calc_bilirubin',
            long_name = 'High bilirubin (calculated)'
            )

    def matches(self, exclude_bound=True):
        log.debug('Looking for high calculated bilirubin scores')
        # First, we return a list of patient & order date pairs, where the sum
        # of direct and indirect bilirubin tests ordered on the same day is 
        # greater than 1.5.
        q_obj = ~Q(events__name=self.name)
        relevant = self.relevant_labs.filter(q_obj)
        vqs = relevant.values('patient', 'date') # returns ValueQuerySet
        vqs = vqs.annotate(calc_bil = Sum('result_float'))
        vqs = vqs.filter(calc_bil__gt = 1.5)
        #
        # Now, instead of returning a QuerySet -- which would require a hugely
        # complex, slow query -- we go and fetch the individual matches into a 
        # set.  
        #
        # FIXME:  This looks slow & cumbersome -- we should do a big complex 
        # query instead, as postgres handles those efficiently
        match_ids = set()
        for item in vqs:
            match_ids = match_ids | set(relevant.filter(patient = item['patient'], 
                date = item['date']).values_list('id', flat = True))
        log.debug('Number of match IDs: %s' % len(match_ids))
        matches = relevant.filter(id__in = match_ids)
        #log_query('Query for heuristic %s' % self.name, matches)
        return matches


class MedicationHeuristic(BaseHeuristic):

    def __init__(self, name, long_name, drugs, exclude=[], require=[], min_quantity=None):
        '''
        @param drugs:  Generate events when drug(s) are prescribed
        @type drugs:   [String, String, ...]
        @param exclude:  Exclude drugs that contain these strings
        @type exclude:   [String, String, ...]
        @param exclude:  Require that drug name contain at least one of these strings
        @type exclude:   [String, String, ...]
        @param min_quantity: Quantity value on prescription must be >= this amount
        @type min_quantity:  Integer
        '''
        assert drugs
        assert isinstance(exclude, list)
        assert isinstance(require, list)
        if min_quantity:
            assert isinstance(min_quantity, int)
        self.drugs = drugs
        self.exclude = exclude
        self.require = require
        self.min_quantity = min_quantity
        BaseHeuristic.__init__(self,
            name = name,
            long_name = long_name,
            )

    def matches(self, exclude_bound=True):
        log.debug('Finding matches for following drugs:')
        [log.debug('    %s' % d) for d in self.drugs]
        [log.debug('    Exclude string: %s' % s) for s in self.exclude]
        qs = Prescription.objects.all()
        if exclude_bound:
            q_obj = ~Q(events__name=self.name)
            qs = qs.filter(q_obj)
        q_obj = Q(name__icontains = self.drugs[0])
        for drug_name in self.drugs[1:]:
            q_obj |= Q(name__icontains = drug_name)
        for s in self.exclude:
            q_obj &= ~Q(name__icontains=s)
        req_q = None
        for s in self.require:
            this_req_q = Q(name__icontains=s) 
            if req_q:
                req_q |= this_req_q
            else:
                req_q = this_req_q
        if req_q:
            q_obj &= req_q
        if self.min_quantity:
            q_obj &= Q(quantity_float__gte=self.min_quantity)
        qs = qs.filter(q_obj)
        log_query('Query for heuristic %s' % self.name, qs)
        return qs


class WesternBlotHeuristic(BaseLabHeuristic):
    '''
    Generates events from western blot test results.
    http://en.wikipedia.org/wiki/Western_blot
    '''

    def __init__(self, name, long_name, interesting_bands, band_count):
        '''
        @param interesting_bands: Which (numbered) bands are interesting for this test?
        @type interesting_bands: [Int, Int, ...]
        @param band_count: Minimum count of interesting bands for test to be positive?
        @type band_count: Int
        '''
        assert len(interesting_bands) > 0
        assert band_count
        self.interesting_bands = interesting_bands
        self.band_count = band_count
        BaseLabHeuristic.__init__(self,
            name = name,
            long_name = long_name,
            )

    def matches(self, exclude_bound=True):
        # Find potential positives -- tests whose results contain at least one 
        # of the interesting band numbers.
        q_obj = ~Q(events__name=self.name)
        relevant_labs = self.relevant_labs.filter(q_obj)
        q_obj = Q(result_string__icontains = str(self.interesting_bands[0]))
        for band in self.interesting_bands[1:]:
            q_obj = q_obj | Q(result_string__icontains = str(band))
        potential_positives = relevant_labs.filter(q_obj)
        log.debug('Found %s potential positive lab results.' % potential_positives.count())
        # Examine result strings of each potential positive.  If it has enough 
        # interesting bands, add its pk to the match list
        match_pks = []
        for item in potential_positives.values('pk', 'result_string'):
            # We might need smarter splitting logic if we ever get differently
            # formatted result strings.
            count = 0 # Counter of interesting bands in this result
            result_bands = item['result_string'].replace(' ', '').split(',')
            pk = item['pk']
            for band in result_bands:
                try:
                    band = int(band)
                except ValueError:
                    log.warning('Could not cast band "%s" from lab # %s into an integer.' % (band, pk))
                    continue
                if band in self.interesting_bands:
                    count += 1
                # If we reach the band_count threshold, we have a positive result.  No need to look further.
                if count >= self.band_count:
                    match_pks.append(pk)
                    break
        log.debug('Found %s actual positive lab results.' % len(match_pks))
        return LabResult.objects.filter(pk__in = match_pks)


class PregnancyHeuristic(BaseHeuristic):
    '''
    Heuristic to infer periods of known pregnancy from EDC values and ICD9 codes
    '''
    
    def __init__(self):
        BaseHeuristic.__init__(self,
            name = 'pregnancy',
            long_name = 'Pregnancy',
            )
    
    def generate_events(self, run, **kwargs):
        #
        # EDC
        #
        log.info('Generating pregnancy events from EDC')
        q_obj = Q(edc__isnull=False)
        q_obj &= ~Q(pregnancy__pk__isnull=False)
        edc_encounters = Encounter.objects.filter(q_obj)
        log_query('Pregnancy encounters by EDC', edc_encounters)
        for enc in edc_encounters.iterator():
            start_date = enc.edc - datetime.timedelta(days=280)
            p = Pregnancy(
                run = run,
                patient = enc.patient,
                start_date = start_date,
                end_date = enc.edc,
                content_object = enc,
                )
            p.save()
            log.debug('Added pregnancy record: %s (%s - %s)' % (enc.patient, start_date, enc.edc))
        del q_obj
        #
        # ICD9s
        #
        log.info('Generating pregnancy events from ICD9s')
        q_obj = Q(icd9_codes__code__startswith='V22.') | Q(icd9_codes__code__startswith='V23.')
        q_obj &= Q(edc__isnull=True)
        ignore_bound_q = ~Q(pregnancy__pk__isnull=False)
        encs = Encounter.objects.filter(q_obj)
        encs_unbound = encs.filter(ignore_bound_q)
        log_query('Pregnancy encounters by ICD9', encs_unbound)
        for e in encs_unbound.iterator():
            # Find previous pregnant encounters.  250 day range, because start_date will be 30 days earlier
            range_encs = encs.filter(
                patient=e.patient,
                date__gte=(e.date - datetime.timedelta(days=250) ),
                date__lte=(e.date + datetime.timedelta(days=266) ),
                )
            # Start is 30 days before first encounter in the range
            date_range = range_encs.aggregate(start=Min('date'), end=Max('date'))
            start_date = date_range['start'] - datetime.timedelta(days=30)
            # End is 14 days after last encounter in the range
            end_date = date_range['end'] + datetime.timedelta(days=14)
            p = Pregnancy(
                run = run,
                patient = e.patient,
                start_date = start_date,
                end_date = end_date,
                content_object = e,
                )
            p.save()
            log.debug('Added pregnancy record: %s (%s - %s)' % (enc.patient, start_date, enc.edc))
        new_pregnancy_count = Pregnancy.objects.filter(run=run).count()
        log.info('Generated %s new pregnancy events' % new_pregnancy_count)
        return new_pregnancy_count