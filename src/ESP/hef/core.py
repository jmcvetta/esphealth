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
from django.db.models import Max
from django.db.models.query import QuerySet
from django.contrib.contenttypes.models import ContentType


from ESP.emr.models import LabResult
from ESP.emr.models import Encounter
from ESP.emr.models import Prescription
from ESP.conf.models import NativeCode
from ESP.conf.models import CodeMap
from ESP.static.models import Loinc
from ESP.hef.models import Event
from ESP.hef.models import Run
from ESP import settings
from ESP.utils import utils as util
from ESP.utils.utils import log
from ESP.utils.utils import log_query


POSITIVE_STRINGS = ['reactiv', 'pos', 'detec']
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
            log.error('Event definition "%s" is already registered for event type "%s".' % (self.def_name, name))
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
    def all_heuristic_names(cls, choices=False):
        '''
        Returns a sorted list of strings naming all registered BaseHeuristic instances
        @param choices: If true, return a list of two-tuples suitable for use with a form ChoiceField
        @type choices: Boolean
        '''
        all_names = set()
        [all_names.update(set(cls.__registry[i].name_list)) for i in cls.__registry]
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
    def get_all_loincs(cls, choices=False):
        '''
        Returns a list of all LOINC numbers for registered heuristics
        @param choices: If true, return a list of two-tuples suitable for use with a form ChoiceField
        @type choices: Boolean
        '''
        loincs = set()
        for heuristic in cls.get_all_heuristics():
            try:
                loincs = loincs | set(heuristic.loinc_nums)
            except AttributeError:
                pass # Skip heuristics w/ no LOINCs defined
        loincs = list(loincs)
        loincs.sort()
        if choices:
            out = []
            for loinc in loincs:
                try:
                    name = Loinc.objects.get(loinc_num=loinc).name[:100]
                except Loinc.DoesNotExist:
                    name = ''
                label = '%-7s: %s' % (loinc, name)
                out.append((loinc, label))
            return out
        else:
            return loincs

    @classmethod
    def get_required_loincs(cls):
        '''
        Returns a dictionary associated each LOINC number required by 
        registered heuristics, with the heuristic(s) that require it.
        '''
        required_loincs = {}
        for heuristic in cls.get_all_heuristics():
            if not hasattr(heuristic, 'loinc_nums'):
                continue # Skip heuristics w/ no LOINCs defined
            for loinc in heuristic.loinc_nums:
                if loinc in required_loincs:
                    required_loincs[loinc].add(heuristic)
                else:
                    required_loincs[loinc] = set([heuristic])
        return required_loincs 

    def matches(self, exclude_bound=True):
        '''
        Return a QuerySet of matches for this heuristic
        @param exclude_bound: Should we exclude labs that are already bound to 
            an event of this heuristic type?
        @type exclude_bound: Boolean
        '''
        raise NotImplementedError('This method MUST be implemented in concrete classes inheriting from BaseHeuristic.')

    def generate_events(self, run, name=None, **kw):
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
            content_type = ContentType.objects.get_for_model(event)
            obj = Event(
                heuristic = name,
                date = event.date,
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
                log.debug('   heuristic: %s' % obj.heuristic)
                log.debug('   date: %s' % obj.date)
                log.debug('   patient: %s' % obj.patient)
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

    def get_events(self):
        '''
        Returns a QuerySet of all existing Event objects generated by
        this heuristic.
        '''
        log.debug('Getting all events for heuristic name %s' % self.name)
        return Event.objects.filter(name = self.name)
    
    def __get_name_list(self):
        return [self.name]
    name_list = property(__get_name_list)

    def __repr__(self):
        return '<BaseHeuristic: %s>' % self.name


class BaseLabHeuristic(BaseHeuristic):
    '''
    Abstract base class for lab test heuristics, concrete instances of which
    are used as components of DiseaseDefinitions
    '''

    def relevant_labs(self, exclude_bound=True):
        '''
        Return all lab results relevant to this heuristic, whether or not they 
        indicate positive.
        @param exclude_bound: Should we exclude labs that are already bound to 
            an event of this heuristic type?
        @type exclude_bound: Boolean
        '''
        log.debug('Get lab results relevant to "%s".' % self.name)
        log.debug('    Exclude Bound: %s' % exclude_bound)
        native_codes = CodeMap.objects.filter(heuristic=self.name).values('native_code')
        qs = LabResult.objects.filter(native_code__in=native_codes)
        if exclude_bound:
            q_obj = ~Q(events__heuristic=self.name)
            qs = qs.filter(q_obj)
        return qs


class LabResultHeuristic(BaseLabHeuristic):
    '''
    Matches labs results with high numeric scores, as determined by a ratio to 
    that result's reference high, with fall back to a default high value.
    '''

    def __init__(self, name, long_name,  ratio = 1, negative_events=False, order_events=False):
        '''
        @param name: Short name of this heuristic.  Should be suitable for use in a SlugField.
        @type  name: String
        @param long_name: Long display name for this heuristic
        @type  long_name: String
        @param ratio: Match on result_float >= (ref_high * ratio)
        @type  ratio: Integer
        @param negative_events: Should we also generate events for negative results?
        @type  negative_events: Boolean
        @param order_events: Should we also generate events for lab orders, regardless of result?
        @type  order_events: Boolean
        '''
        self.ratio = ratio
        self.negative_events = negative_events
        self.order_events = order_events
        BaseLabHeuristic.__init__(self,
            name = name,
            long_name = long_name,
            )

    def matches(self, exclude_bound=True, result_type='positive'):
        '''
        If record has a reference high, and a ratio has been specified, compare
        test result against that reference.  If a record does not have a
        reference high, and a default_high has been specified, compare result
        against that default 'high' value.
        '''
        assert result_type in ['positive', 'negative', 'order']
        if result_type == 'positive':
            event_name = self.pos_name
        elif result_type == 'negative':
            event_name = self.neg_name
        else: # result_type == 'order'
            event_name = self.order_name
            q_obj = ~Q(events__heuristic=event_name)
            result = self.relevant_labs(exclude_bound=False).filter(q_obj)
            log_query('Query for heuristic %s' % event_name, result)
            return result
        log.info('Finding matches for heuristic %s' % event_name)
        has_ref_high = Q(ref_high__isnull=False) # Record does NOT have null value for ref_high
        code_maps = CodeMap.objects.filter(heuristic=self.name)
        native_codes = code_maps.values_list('native_code')
        log.debug('Code maps: %s' % pprint.pformat(code_maps))
        #
        # Build numeric query
        #
        num_q = None
        for map in code_maps:
            #
            # Build numeric comparison queries
            #
            thresh_q = None
            ratio_q = None
            if result_type == 'positive':
                if map.threshold:
                    thresh_q = Q(result_float__gt = float(map.threshold))
                if self.ratio == 1:
                    ratio_q = has_ref_high & Q(result_float__gt = F('ref_high'))
                elif self.ratio:
                    ratio_q = has_ref_high & Q(result_float__gt = F('ref_high') * self.ratio)
            else: # result_type == 'negative'
                if map.threshold:
                    thresh_q = Q(result_float__lte = float(map.threshold))
                if self.ratio:
                    ratio_q = has_ref_high & Q(result_float__lte = F('ref_high') * self.ratio)
            # 
            # Combine restrict numeric comparison(s) to relevant native_code.
            #
            q_obj = Q(native_code=map.native_code)
            if thresh_q and ratio_q:
                q_obj &= (thresh_q | ratio_q)
            elif thresh_q:
                q_obj &= thresh_q
            elif ratio_q:
                q_obj &= ratio_q
            else:
                continue # No query to build here
            if num_q:
                num_q |= q_obj
            else:
                num_q = q_obj
        pos_q = num_q
        #
        # Build string query
        #
        # When using ratio, we cannot rely on a test being "POSITIVE" from 
        # lab, since we may be looking for higher value.
        if (not self.ratio) or (self.ratio == 1):
            strings_q = None
            if result_type == 'positive':
                strings = POSITIVE_STRINGS
            else:
                strings = NEGATIVE_STRINGS
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
            pos_q &= ~Q(events__heuristic=event_name)
        labs = LabResult.objects.filter(pos_q)
        log_query('Query for heuristic %s' % event_name, labs)
        return labs
    
    def generate_events(self, run):
        '''
        Generate positive, and if defined negative, events
        '''
        counter = BaseHeuristic.generate_events(self, run, name=self.pos_name, result_type='positive')
        if self.negative_events:
            counter += BaseHeuristic.generate_events(self, run, name=self.neg_name, result_type='negative')
        if self.order_events:
            counter += BaseHeuristic.generate_events(self, run, name=self.order_name, result_type='order')
        return counter
    
    def __get_name_list(self):
        l = [self.pos_name]
        if self.negative_events:
            l.append(self.neg_name)
        if self.order_events:
            l.append(self.order_name)
        return l
    name_list = property(__get_name_list)
    
    #
    # Event Names  
    #
    # This heuristic generates events with different names, depending on 
    # whether the event indicates a positive test result, a negative test 
    # result, or a test order.
    #
    
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


class LabOrderedHeuristic(BaseLabHeuristic):
    '''
    Matches any *order* for a lab test with specified LOINC(s)
    '''

    def matches(self, exclude_bound=True):
        result = self.relevant_labs(exclude_bound=exclude_bound)
        log_query('Query for heuristic %s' % self.name, result)
        return result


class EncounterHeuristic(BaseHeuristic):
    '''
    Abstract base class for encounter heuristics, concrete instances of which
    are used as components of DiseaseDefinitions
    '''
    def __init__(self, name, long_name, icd9s, match_style='exact'):
        '''
        @type name:         String
        @type icd9s:        [String, String, String, ...]
        @type match_style:  String (either 'iexact' or 'istartswith')
        '''
        assert icd9s
        self.icd9s = icd9s
        assert match_style in ['exact', 'startswith', 'iexact', 'istartswith']
        self.match_style = match_style
        BaseHeuristic.__init__(self,
            name = name,
            long_name = long_name,
            )

    def __get_enc_q(self):
        '''
        Returns a Q object to select all Encounters indicated by self.icd9s
        '''
        enc_q = Q()
        for code in self.icd9s:
            if self.match_style == 'exact':
                enc_q |= Q(icd9_codes__code__exact = code)
            elif self.match_style == 'iexact':
                enc_q |= Q(icd9_codes__code__iexact = code)
            elif self.match_style == 'startswith':
                enc_q |= Q(icd9_codes__code__startswith = code)
            elif self.match_style == 'istartswith':
                enc_q |= Q(icd9_codes__code__istartswith = code)
            else:
                raise RuntimeError('Match style "%s" requested.  This should never happen.  Contact developers.' % self.match_style)
        return enc_q
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
            q_obj = ~Q(events__heuristic=self.name)
            qs = qs.filter(q_obj)
        qs = qs.filter(self.enc_q)
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
            q_obj = ~Q(events__heuristic=self.name)
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
        relevant = self.relevant_labs(exclude_bound=exclude_bound)
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

    def __init__(self, name, long_name, drugs, exclude=[]):
        '''
        @param drugs:  Generate events when drug(s) are prescribed
        @type drugs:   [String, String, ...]
        @param drugs:  Exclude drugs that contain these strings
        @type drugs:   [String, String, ...]
        '''
        assert drugs
        assert isinstance(exclude, list)
        self.drugs = drugs
        self.exclude = exclude
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
            q_obj = ~Q(events__heuristic=self.name)
            qs = qs.filter(q_obj)
        q_obj = Q(name__icontains = self.drugs[0])
        for drug_name in self.drugs[1:]:
            q_obj |= Q(name__icontains = drug_name)
        for string in self.exclude:
            q_obj &= ~Q(name__icontains=string)
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
        relevant_labs = self.relevant_labs(exclude_bound=exclude_bound)
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
