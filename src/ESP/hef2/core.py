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

from django.db import connection
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
from ESP.hef2.models import HeuristicEvent
from ESP.hef2.models import Run
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
        log.debug('All BaseHeuristic instances: %s')
        for item in result:
            log.debug('    %s' % item)
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

    def matches(self, begin_timestamp = None):
        '''
        Return a QuerySet of matches for this heuristic
        '''
        raise NotImplementedError('This method MUST be implemented in concrete classes inheriting from BaseHeuristic.')

    def generate_events(self, incremental = True, **kw):
        '''
        Generate HeuristicEvent records for each item returned by
        matches, if it does not already have one.
        @return: Integer number of new records created
        '''
        log.info('Generating events for "%s".' % self.def_name)
        counter = 0 # Counts how many new records have been created
        #
        # Incremental processing
        #
        if incremental:
            log.debug('Incremental processing requested.')
            runs = Run.objects.filter(def_name = self.def_name, status = 's')
            begin_timestamp = runs.aggregate(ts = Max('timestamp'))['ts'] # aggregate() returns dict
        else:
            log.debug('Incremental processing NOT requested.')
            begin_timestamp = None
        log.debug('begin_timestamp: %s' % begin_timestamp)
        self.run = Run(def_name = self.def_name) # New Run object for this run
        self.run.save()
        log.debug('Generated new Run object for this run: %s' % self.run)
        #
        #
        # First we retrieve a list of object IDs for this 
        existing = HeuristicEvent.objects.filter(definition = self.def_name).values_list('object_id')
        existing = [int(item[0]) for item in existing] # Convert to a list of integers
        #
        # Disabled select_related() because matches will most often be in 
        # existing list, and thus discarded not saved.
        #
        for event in self.matches(begin_timestamp):
            if event.id in existing:
                log.debug('BaseHeuristic event "%s" already exists for %s #%s' % (self.heuristic_name, event._meta.object_name, event.id))
                continue
            content_type = ContentType.objects.get_for_model(event)
            obj, created = HeuristicEvent.objects.get_or_create(
                heuristic_name = self.heuristic_name,
                definition = self.def_name,
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
        # If we made it this far, run has succeeded
        log.debug('Setting run #%s status to "s" (success).' % self.run.pk)
        self.run.status = 's'
        self.run.save()
        return counter

    @classmethod
    def generate_all_events(cls, incremental = True, **kw):
        '''
        Generate HeuristicEvent records for every registered BaseHeuristic 
            instance.
        @param begin_timestamp: Beginning of time window to examine
        @type begin_timestamp:  datetime.datetime
        @return:           Integer number of new records created
        '''
        counter = 0 # Counts how many total new records have been created
        for heuristic in cls.get_all_heuristics():
            counter += heuristic.generate_events(incremental = incremental)
        log.info('Generated %s TOTAL new events.' % counter)
        return counter

    @classmethod
    def generate_events_by_name(cls, name, incremental = True):
        for heuristic in cls.get_heuristics_by_name(name):
            heuristic.generate_events(incremental = incremental)

    def get_events(self):
        '''
        Returns a QuerySet of all existing HeuristicEvent objects generated by
        this heuristic.
        '''
        log.debug('Getting all events for heuristic name %s' % self.heuristic_name)
        return HeuristicEvent.objects.filter(heuristic_name = self.heuristic_name)

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

    def relevant_labs(self, begin_timestamp = None, loinc_nums = None):
        '''
        Return all lab results relevant to this heuristic, whether or not they 
        indicate positive.
            @type loinc_nums: [String, String, ...]
            @type begin_timestamp: datetime.datedatetime
            @type end_date:   datetime.date
        '''
        log.debug('Get lab results relevant to "%s".' % self.heuristic_name)
        log.debug('Beginning timestamp: %s' % begin_timestamp)
        if not loinc_nums:
            loinc_nums = self.loinc_nums
        qs = LabResult.objects.filter_loincs(loinc_nums)
        if begin_timestamp:
            qs = qs.filter(updated_timestamp__gte = begin_timestamp)
        return qs


class NumericLabHeuristic(LabHeuristic):
    '''
    Matches labs results with high numeric scores, as determined by a ratio to 
    that result's reference high, with fall back to a default high value.
    '''

    def __init__(self, heuristic_name, def_name, def_version, loinc_nums,
        comparison, ratio = None, default_high = None, exclude = False):
        '''
        @param comparison:   Operator to use for numerical comparison (currently only '>' and '>=' supported)
        @type comparison:    String
        @param ratio:        Match on result > ratio * reference_high
        @type ratio:         Integer
        @param default_high: If no reference high, match on result > default_high
        @type default_high:  Integer
        '''
        assert ratio or default_high
        comparison = comparison.strip()
        assert comparison in ['>', '>=', '<', '<=']
        self.default_high = default_high
        self.ratio = ratio
        self.comparison = comparison.strip()
        self.exclude = exclude
        LabHeuristic.__init__(self,
            heuristic_name = heuristic_name,
            def_name = def_name,
            def_version = def_version,
            loinc_nums = loinc_nums,
            )

    def matches(self, begin_timestamp = None):
        '''
        If record has a reference high, and a ratio has been specified, compare
        test result against that reference.  If a record does not have a
        reference high, and a default_high has been specified, compare result
        against that default 'high' value.
        '''
        relevant_labs = self.relevant_labs(begin_timestamp)
        no_ref_q = Q(ref_high = None) # Record has null value for ref_high
        comparison = self.comparison.strip()
        if self.default_high:
            # Query to compare result_float against self.default_high
            if comparison == '>':
                def_high_q = Q(result_float__gt = self.default_high)
            elif comparison == '>=':
                def_high_q = Q(result_float__gte = self.default_high)
            elif comparison == '<':
                def_high_q = Q(result_float__lt = self.default_high)
            elif comparison == '<=':
                def_high_q = Q(result_float__lte = self.default_high)
            else:
                raise RuntimeError('Invalid comparison operator: %s' % self.comparison)
            pos_q = def_high_q
        if self.ratio:
            # Query to compare non-null ref_high against self.ratio
            if comparison == '>':
                ref_comp_q = ~no_ref_q & Q(result_float__gt = F('ref_high') * self.ratio)
            elif comparison == '>=':
                ref_comp_q = ~no_ref_q & Q(result_float__gte = F('ref_high') * self.ratio)
            elif comparison == '<':
                ref_comp_q = ~no_ref_q & Q(result_float__lt = F('ref_high') * self.ratio)
            elif comparison == '<=':
                ref_comp_q = ~no_ref_q & Q(result_float__lte = F('ref_high') * self.ratio)
            else:
                raise RuntimeError('Invalid comparison operator: %s' % self.comparison)
            pos_q = ref_comp_q
        if self.default_high and self.ratio:
            # Query to compare records with non-null ref_high against 
            # self.ratio, and records with null ref_high against self.default
            static_comp_q = no_ref_q & def_high_q
            pos_q = (ref_comp_q | static_comp_q)
        log.debug('pos_q: %s' % pos_q)
        if self.exclude:
            result = relevant_labs.exclude(pos_q)
        else:
            result = relevant_labs.filter(pos_q)
        return result


class StringMatchLabHeuristic(LabHeuristic):
    '''
    Matches labs with results containing specified strings
    '''

    def __init__(self, heuristic_name, def_name, def_version, loinc_nums, strings = [],
        abnormal_flag = False, match_type = 'istartswith', exclude = False):
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

    def matches(self, begin_timestamp = None):
        '''
        Compare record's result field against strings.
        '''
        if self.match_type == 'istartswith':
            pos_q = Q(result_string__istartswith = self.strings[0])
            for s in self.strings[1:]:
                pos_q = pos_q | Q(result_string__istartswith = s)
            if self.abnormal_flag:
                msg = 'IMPORTANT: Support for abnormal-flag-based queries has not yet been implemented!\n'
                msg += '    Our existing data has only nulls for that field, so I am not sure what the query should look like.'
                log.critical(msg)
        else:
            raise NotImplementedError('The only match type supported at this time is "istartswith".')
        log.debug('pos_q: %s' % pos_q)
        if self.exclude:
            result = self.relevant_labs(begin_timestamp).exclude(pos_q)
        else:
            result = self.relevant_labs(begin_timestamp).filter(pos_q)
        return result


class LabOrderedHeuristic(LabHeuristic):
    '''
    Matches any *order* for a lab test with specified LOINC(s)
    '''

    def matches(self, begin_timestamp = None):
        return self.relevant_labs(begin_timestamp = begin_timestamp)


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
            enc_q = enc_q | Q(icd9_codes__code = code)
        return enc_q
    enc_q = property(__get_enc_q)

    def encounters(self, begin_timestamp):
        '''
        Return all lab results relevant to this heuristic, whether or not they 
        indicate positive.
            @type patient:    Demog
            @type queryset:   QuerySet
        '''
        log.debug('Get encounters relevant to "%s".' % self.heuristic_name)
        qs = Encounter.objects.all()
        if begin_timestamp :
            qs = qs.filter(updated_timestamp__gte = begin_timestamp)
        qs = qs.filter(self.enc_q)
        return qs

    def matches(self, begin_timestamp = None):
        return self.encounters(begin_timestamp)


class FeverHeuristic(BaseHeuristic):
    '''
    Abstract base class for encounter heuristics, concrete instances of which
    are used as components of DiseaseDefinitions
    '''
    def __init__(self, heuristic_name, def_name, def_version, temperature = None, icd9s = []):
        assert (icd9s or temperature)
        self.temperature = temperature
        self.icd9s = icd9s
        BaseHeuristic.__init__(self,
            heuristic_name = heuristic_name,
            def_name = def_name,
            def_version = def_version,
            )

    def matches(self, begin_timestamp = None, queryset = None):
        '''
        Return all encounters indicating fever.
            @type queryset:   QuerySet
        '''
        log.debug('Get encounters matching "%s".' % self.heuristic_name)
        enc_q = Q()
        for code in self.icd9s:
            enc_q = enc_q | Q(icd9_codes__code = code)
        qs = Encounter.objects.all()
        if begin_timestamp:
            qs = qs.filter(updated_timestamp__gte = begin_timestamp)
        # Either encounter has the 'fever' ICD9, or it records a high temp
        q_obj = enc_q | Q(temperature__gt = self.temperature)
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
            heuristic_name = 'high_calc_bilirubin',
            def_name = 'High Calculated Bilirubin Event Definition 1',
            def_version = 1,
            )

    def old_matches(self, begin_timestamp = None):
        log.debug('Looking for high calculated bilirubin scores')
        # First, we return a list of patient & order date pairs, where the sum
        # of direct and indirect bilirubin tests ordered on the same day is 
        # greater than 1.5.
        relevant = self.relevant_labs(begin_timestamp)
        vqs = relevant.values('patient', 'date') # returns ValueQuerySet
        vqs = vqs.annotate(calc_bil = Sum('result_float'))
        vqs = vqs.filter(calc_bil__gt = 1.5)
        # Now we retrieve the matches -- this is a huuuuuuge query: it takes a 
        # long time just for Django to build it, and even longer for the DB to 
        # execute it.  But is there a better solution?  
        matches = LabResult.objects.filter(pk__isnull = True) # QuerySet that matches nothing
        for item in vqs:
            matches = matches | relevant.filter(patient = item['patient'], date = item['date'])
        return matches

    def matches(self, begin_timestamp = None):
        log.debug('Looking for high calculated bilirubin scores')
        # First, we return a list of patient & order date pairs, where the sum
        # of direct and indirect bilirubin tests ordered on the same day is 
        # greater than 1.5.
        relevant = self.relevant_labs(begin_timestamp = begin_timestamp)
        vqs = relevant.values('patient', 'date') # returns ValueQuerySet
        vqs = vqs.annotate(calc_bil = Sum('result_float'))
        vqs = vqs.filter(calc_bil__gt = 1.5)
        # Now, instead of returning a QuerySet -- which would require a hugely
        # complex, slow query -- we go and fetch the individual matches into a 
        match_ids = set()
        for item in vqs:
            match_ids = match_ids | set(relevant.filter(patient = item['patient'], date = item['date']).values_list('id', flat = True))
        log.debug('Number of match IDs: %s' % len(match_ids))
        matches = relevant.filter(id__in = match_ids)
        return matches

    def newer_matches(self, begin_timestamp = None):
        log.debug('Looking for high calculated bilirubin scores')
        direct_loinc = ['29760-6']
        indirect_loinc = ['14630-8']
        # {patient: {date: [result, pk]}}
        d = self.relevant_labs(begin_timestamp = begin_timestamp, loinc_nums = direct_loinc)
        d_patients = d.values_list('patient', flat = True)
        i = self.relevant_labs(begin_timestamp = begin_timestamp, loinc_nums = direct_loinc)
        i_patients = i.values_list('patient', flat = True)
        plausible_patients = d_patients.filter(patient__in = i_patients)
        print plausible_patients[0]


class MedicationHeuristic(BaseHeuristic):

    def __init__(self, heuristic_name, def_name, def_version, drugs):
        '''
        @param drugs:  Generate events when drug(s) are prescribed
        @type drugs:   [String, String, ...]
        '''
        assert drugs
        self.drugs = drugs
        BaseHeuristic.__init__(self,
            heuristic_name = heuristic_name,
            def_name = def_name,
            def_version = def_version,
            )

    def matches(self, begin_timestamp = None):
        log.debug('Finding matches for following drugs:')
        [log.debug('    %s' % d) for d in self.drugs]
        qs = Prescription.objects.all()
        if begin_timestamp:
            qs = qs.filter(updated_timestamp__gte = begin_timestamp)
        q_obj = Q(name__icontains = self.drugs[0])
        for drug_name in self.drugs[1:]:
            q_obj = q_obj | Q(name__icontains = drug_name)
        return qs.filter(q_obj)


class WesternBlotHeuristic(LabHeuristic):
    '''
    Generates events from western blot test results.
        http://en.wikipedia.org/wiki/Western_blot
    '''

    def __init__(self, heuristic_name, def_name, def_version, loinc_nums,
        interesting_bands, band_count):
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
        LabHeuristic.__init__(self,
            heuristic_name = heuristic_name,
            def_name = def_name,
            def_version = def_version,
            loinc_nums = loinc_nums,
            )

    def matches(self, begin_timestamp = None):
        # Find potential positives -- tests whose results contain at least one 
        # of the interesting band numbers.
        relevant_labs = self.relevant_labs(begin_timestamp)
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
