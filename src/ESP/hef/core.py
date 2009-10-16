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

    def __init__(self, name, def_name, def_version):
        '''
        @param heuristic: Name of this heuristic (could be shared by several instances)
        @type heuristic: String
        @param def_name: Name of the definition used (unique to instance)
        @type def_name: String
        @param def_version: Version of definition
        @type def_version: Integer
        '''
        assert name
        assert def_name
        assert def_version
        self.name = name
        self.def_name = def_name
        self.def_version = def_version
        #
        # Register this heuristic
        #
        registry = self.__registry # For convenience
        if name in registry:
            if self.def_name in [item.def_name for item in registry[name]]:
                log.error('Event definition "%s" is already registered for event type "%s".' % (self.def_name, name))
                raise HeuristicAlreadyRegistered('A BaseHeuristic instance is already registered with heuristic "%s".' % name)
            else:
                log.debug('Registering additional heuristic for heuristic "%s".' % name)
                registry[name] += [self]
        else:
            log.debug('Registering heuristic with heuristic "%s".' % name)
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
    def list_heuristics(cls, choices=False):
        '''
        Returns a sorted list of strings naming all registered BaseHeuristic instances
        @param choices: If true, return a list of two-tuples suitable for use with a form ChoiceField
        @type choices: Boolean
        '''
        names = cls.__registry.keys()
        names.sort()
        if choices:
            return [(n, n) for n in names]
        else:
            return names

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

    def generate_events(self, **kw):
        '''
        Generate Event records for each item returned by
        matches, if it does not already have one.
        @return: Integer number of new records created
        '''
        log.info('Generating events for "%s".' % self.def_name)
        counter = 0 # Counts how many new records have been created
        self.run = Run(def_name = self.def_name) # New Run object for this run
        self.run.save()
        log.debug('Generated new Run object for this run: %s' % self.run)
        for event in self.matches().select_related():
            content_type = ContentType.objects.get_for_model(event)
            obj, created = Event.objects.get_or_create(
                heuristic = self.name,
                definition = self.def_name,
                def_version = self.def_version,
                date = event.date,
                patient = event.patient,
                content_type = content_type,
                object_id = event.pk,
                )
            if created:
                log.info('Creating new heuristic event "%s" for %s #%s' % (self.name, event._meta.object_name, event.id))
                obj.save()
                counter += 1
            else:
                log.debug('Did not create heuristic event - found matching event #%s' % obj.id)
        log.info('Generated %s new events for "%s".' % (counter, self.name))
        # If we made it this far, run has succeeded
        log.debug('Setting run #%s status to "s" (success).' % self.run.pk)
        self.run.status = 's'
        self.run.save()
        return counter

    @classmethod
    def generate_all_events(cls, **kw):
        '''
        Generate Event records for every registered BaseHeuristic 
            instance.
        @return:           Integer number of new records created
        '''
        counter = 0 # Counts how many total new records have been created
        for heuristic in cls.get_all_heuristics():
            counter += heuristic.generate_events()
        log.info('Generated %s TOTAL new events.' % counter)
        return counter

    @classmethod
    def generate_events_by_name(cls, name):
        for heuristic in cls.get_heuristics_by_name(name):
            heuristic.generate_events()

    def get_events(self):
        '''
        Returns a QuerySet of all existing Event objects generated by
        this heuristic.
        '''
        log.debug('Getting all events for heuristic name %s' % self.name)
        return Event.objects.filter(name = self.name)

    def __repr__(self):
        return '<BaseHeuristic: %s>' % self.def_name


class LabHeuristic(BaseHeuristic):
    '''
    Abstract base class for lab test heuristics, concrete instances of which
    are used as components of DiseaseDefinitions
    '''

    def __init__(self, name, def_name, def_version):
        '''
        @param loinc_nums:   LOINC numbers for lab results this heuristic will examine
        @type loinc_nums:    [String, String, String, ...]
        '''
        BaseHeuristic.__init__(self,
            name = name,
            def_name = def_name,
            def_version = def_version,
            )

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


class LabResultHeuristic(LabHeuristic):
    '''
    Matches labs results with high numeric scores, as determined by a ratio to 
    that result's reference high, with fall back to a default high value.
    '''

    def __init__(self, name, def_name, def_version, result_type, ratio = 1):
        '''
        @param strings:       Strings to match against
        @type strings:          [String, String, String, ...]
        @param comparison:   Operator to use for numerical comparison (currently only '>' and '>=' supported)
        @type comparison:    String
        @param ratio:        Match on result > ratio * reference_high
        @type ratio:         Integer
        '''
        result_type = result_type.strip()
        assert result_type in ['positive', 'negative']
        self.result_type = result_type
        self.ratio = ratio
        LabHeuristic.__init__(self,
            name = name,
            def_name = def_name,
            def_version = def_version,
            )

    def matches(self, exclude_bound=True):
        '''
        If record has a reference high, and a ratio has been specified, compare
        test result against that reference.  If a record does not have a
        reference high, and a default_high has been specified, compare result
        against that default 'high' value.
        '''
        has_ref_high = Q(ref_high__isnull=False) # Record does NOT have null value for ref_high
        code_maps = CodeMap.objects.filter(heuristic=self.name)
        native_codes = code_maps.values_list('native_code')
        #
        # Build numeric query
        #
        num_q = None
        for map in code_maps.filter(threshold__isnull=False):
            if self.result_type == 'positive':
                q_obj = Q(result_float__gt = float(map.threshold))
                if self.ratio:
                    q_obj |= has_ref_high & Q(result_float__gt = F('ref_high') * self.ratio)
            else: # result_type == 'negative'
                q_obj = Q(result_float__lte = float(map.threshold))
                if self.ratio:
                    q_obj |= has_ref_high & Q(result_float__lte = F('ref_high') * self.ratio)
            q_obj &= Q(native_code=map.native_code)
            if num_q:
                num_q |= q_obj
            else:
                num_q = q_obj
        pos_q = num_q
        #
        # Build string query
        #
        # When using ratio, we cannot rely on a test being "POSITIVE" from 
        # lab, since we may be looking for higher value
        if self.ratio != 1:
            strings_q = None
            if self.result_type == 'positive':
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
            print strings_q       
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
            pos_q &= ~Q(events__heuristic=self.name)
        labs = LabResult.objects.filter(pos_q)
        log_query('Query for heuristic %s' % self.name, labs)
        return labs


class StringMatchLabHeuristic(LabHeuristic):
    '''
    Matches labs with results containing specified strings
    '''

    def __init__(self, name, def_name, def_version, loinc_nums, strings = [],
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
            name = name,
            def_name = def_name,
            def_version = def_version,
            loinc_nums = loinc_nums,
            )

    def matches(self, exclude_bound=True):
        '''
        Compare record's result field against strings.
        '''
        labs = self.relevant_labs(exclude_bound=exclude_bound)
        if self.match_type == 'istartswith':
            q_obj = Q(result_string__istartswith = self.strings[0])
            for s in self.strings[1:]:
                q_obj = q_obj | Q(result_string__istartswith = s)
            if self.abnormal_flag:
                msg = 'IMPORTANT: Support for abnormal-flag-based queries has not yet been implemented!\n'
                msg += '    Our existing data has only nulls for that field, so I am not sure what the query should look like.'
                log.critical(msg)
            labs = labs.filter(q_obj)
        else:
            raise NotImplementedError('The only match type supported at this time is "istartswith".')
        log_query('Query for heuristic %s' % self.name, labs)
        return labs


class LabOrderedHeuristic(LabHeuristic):
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
    def __init__(self, name, def_name, def_version, icd9s, match_style='iexact'):
        '''
        @type name:         String
        @type icd9s:        [String, String, String, ...]
        @type match_style:  String (either 'iexact' or 'istartswith')
        '''
        assert icd9s
        self.icd9s = icd9s
        assert match_style in ['iexact', 'istartswith']
        self.match_style = match_style
        BaseHeuristic.__init__(self,
            name = name,
            def_name = def_name,
            def_version = def_version,
            )

    def __get_enc_q(self):
        '''
        Returns a Q object to select all Encounters indicated by self.icd9s
        '''
        enc_q = Q()
        for code in self.icd9s:
            if self.match_style == 'iexact':
                enc_q |= Q(icd9_codes__code__iexact = code)
            elif self.match_style == 'istartswith':
                enc_q |= Q(icd9_codes__code__istartswith = code)
            else:
                raise 'This should never happen.  Contact developers.'
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
    def __init__(self, name, def_name, def_version, temperature = None, icd9s = []):
        assert (icd9s or temperature)
        self.temperature = temperature
        self.icd9s = icd9s
        BaseHeuristic.__init__(self,
            name = name,
            def_name = def_name,
            def_version = def_version,
            )

    def matches(self, queryset=None, exclude_bound=True):
        '''
        Return all encounters indicating fever.
            @type queryset:   QuerySet
        '''
        log.debug('Get encounters matching "%s".' % self.name)
        enc_q = Q()
        for code in self.icd9s:
            enc_q = enc_q | Q(icd9_codes__code = code)
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


class CalculatedBilirubinHeuristic(LabHeuristic):
    '''
    Special heuristic to detect high calculated bilirubin values.  Since the
    value of calculated bilirubin is the sum of results of two seperate tests
    (w/ separate LOINCs), it cannot be handled by a generic heuristic class.
    '''
    def __init__(self):
        self.loinc_nums = ['29760-6', '14630-8']
        BaseHeuristic.__init__(self,
            name = 'high_calc_bilirubin',
            def_name = 'High Calculated Bilirubin Event Definition 1',
            def_version = 1,
            )

    def old_matches(self, begin_timestamp = None):
        #
        # WTF: Why did I save this?
        #
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

    def newer_matches(self, begin_timestamp = None):
        #
        # WTF: Why did I save this?
        #
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

    def __init__(self, name, def_name, def_version, drugs, exclude=[]):
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
            def_name = def_name,
            def_version = def_version,
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


class WesternBlotHeuristic(LabHeuristic):
    '''
    Generates events from western blot test results.
        http://en.wikipedia.org/wiki/Western_blot
    '''

    def __init__(self, name, def_name, def_version, 
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
            name = name,
            def_name = def_name,
            def_version = def_version,
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
