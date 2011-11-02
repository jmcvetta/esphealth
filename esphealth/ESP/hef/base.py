'''
                              ESP Health Project
                          Heuristic Events Framework
                                  Core Logic

@author: Jason McVetta <jason.mcvetta@heliotropi.cc>
@organization: Channing Laboratory http://www.channing.harvard.edu
@contact: http://esphealth.org
@copyright: (c) 2009-2011 Channing Laboratory
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# The HEF_CORE_URI string uniquely describes this version of HEF core.  
# It MUST be incremented whenever any core functionality is changed!
HEF_CORE_URI = 'urn:x-esphealth:hef:core:v1'
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import abc
import math
import re
import threading
import Queue
import time
import sys
from concurrent import futures

from decimal import Decimal

from ESP.settings import HEF_THREAD_COUNT
from ESP.conf.models import LabTestMap
from ESP.conf.models import ResultString
from ESP.emr.models import Encounter
from ESP.emr.models import LabOrder
from ESP.emr.models import LabResult
from ESP.emr.models import Prescription
from ESP.hef.models import Event
from ESP.static.models import Icd9
from ESP.utils import log, log_query
from ESP.utils.utils import queryset_iterator
from ESP.utils.utils import wait_for_threads
from ESP.utils.utils import EquivalencyMixin
from django.db.models import F, Q
from django.utils.encoding import force_unicode, smart_str
from pkg_resources import iter_entry_points





POSITIVE_STRINGS = ['reactiv', 'pos', 'detec', 'confirm']
NEGATIVE_STRINGS = ['non', 'neg', 'not det', 'nr']
INDETERMINATE_STRINGS = ['indeterminate', 'not done', 'tnp']

POS_NEG_IND = [
    ('pos', 'Positive'),
    ('neg', 'Negative'),
    ('ind', 'Indeterminate'),
    ]

DATE_FIELD_CHOICES = [
    ('order', 'Order'),
    ('result', 'Result')
    ]

DOSE_UNIT_CHOICES = [
    ('ml', 'Milliliters'),
    ('mg', 'Milligrams'),
    ('g', 'Grams'),
    ('ug', 'Micrograms'),
    ]

DOSE_UNIT_VARIANTS = {
    'ml': ['milliliter', 'ml'],
    'g': ['gram', 'g', 'gm'],
    'mg': ['milligram', 'mg'],
    'ug': ['microgram', 'mcg', 'ug'],
    }

TITER_DILUTION_CHOICES = [
    (1, '1:1'),  
    (2, '1:2'),
    (4, '1:4'),
    (8, '1:8'),
    (16, '1:16'),
    (32, '1:32'),
    (64, '1:64'),
    (128, '1:128'),
    (256, '1:256'),
    (512, '1:512'),
    (1024, '1:1024'),
    (2048, '1:2048'),
    ]

MATCH_TYPE_CHOICES = [
    ('exact', 'Exact Match (case sensitive)'),
    ('iexact', 'Exact Match (NOT case sensitive)'),
    ('startswith', 'Starts With (case sensitive)'),
    ('istartswith', 'Starts With (NOT case sensitive)'),
    ('endswith', 'Ends With (case sensitive)'),
    ('iendswith', 'Ends With (NOT case sensitive)'),
    ('contains', 'Contains (case sensitive)'),
    ('icontains', 'Contains (NOT case sensitive)'),
    ]

ORDER_RESULT_RECORD_TYPES = [
    ('order', 'Lab Test Orders'),
    ('result', 'Lab Test Results'),
    ('both', 'Both Lab Test Orders and Results'),
    ]


class BaseHeuristic(EquivalencyMixin):
    '''
    A heuristic for generating Events from raw medical records
    (Abstract base class)
    '''
    
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractproperty
    def short_name(self):
        '''
        Short name (SlugField-compatible) for this instance.  Name should
        reflect any arguments used to instantiate the heuristic.
        '''
        
    @abc.abstractproperty
    def uri(self):
        '''
        URI which uniquely describes this heuristic, including its version.  
        This should describe the heuristic itself, regardless of any 
        arguments with which it may be instantiated.
        '''
    
    @abc.abstractproperty
    def core_uris(self):
        '''
        A list of one or more URIs indicating the version(s) of HEF core with 
        which this heuristic is compatible
        '''
    
    @abc.abstractmethod
    def generate(self):
        '''
        Examine data and generate new objects
        @return: Count of new objects generated
        @rtype:  Integer
        '''
    
    __registered_heuristics = {}
    
    def __str__(self):
        return smart_str(self.short_name)
    
    @classmethod
    def get_all(cls):
        '''
        @return: All known heuristics of any type
        @rtype:  List
        '''
        heuristics = set()
        heuristics.update(BaseEventHeuristic.get_all())
        heuristics.update(BaseTimespanHeuristic.get_all())
        heuristics = list(heuristics)
        heuristics.sort(key = lambda h: h.short_name)
        return heuristics
    
    @classmethod
    def generate_all(cls, heuristic_list=None, thread_count=HEF_THREAD_COUNT):
        counter = 0
        counter += BaseEventHeuristic.generate_all(heuristic_list=heuristic_list, thread_count=thread_count)
        counter += BaseTimespanHeuristic.generate_all(heuristic_list=heuristic_list, thread_count=thread_count)
        return counter
    
    @classmethod
    def get_heuristic_by_name(cls, short_name):
        '''
        Returns the named heuristic
        '''
        class UnknownHeuristicException(Exception):
            '''
            Exception raised no heuristic can be found matching the requested name
            '''
            pass
        heuristics = {}
        for h in cls.get_all():
            heuristics[h.short_name] = h
        if not short_name in heuristics:
            raise UnknownHeuristicException('Could not get heuristic for name: "%s"' % short_name)
        return heuristics[short_name]
    
    @classmethod
    def generate_by_name(cls, name_list, thread_count=HEF_THREAD_COUNT):
        '''
        Run heuristic(s) specified by name as arguments
        '''
        class UnknownHeuristicException(Exception):
            '''
            Exception raised no heuristic can be found matching the requested name
            '''
            pass
        selected_heuristics = set()
        for short_name in name_list:
            selected_heuristics.add( cls.get_heuristic_by_name(short_name) )
        return cls.generate_all(heuristic_list=selected_heuristics, thread_count=thread_count)
    

class BaseEventHeuristic(BaseHeuristic):
    '''
    A heuristic for generating Events from raw medical records
    (Abstract base class)
    '''
    
    @abc.abstractproperty
    def event_names(self):
        '''
        A list of one or more strings naming all the possible 
        kinds of event this heuristic can generate
        '''
        
    @classmethod
    def get_all(cls):
        '''
        @return: All known event heuristics
        @rtype:  List
        '''
        available_heuristics = set()
        for entry_point in iter_entry_points(group='esphealth', name='event_heuristics'):
            factory = entry_point.load()
            available_heuristics.update(factory())
        valid_heuristics = []
        for heuristic in available_heuristics:
            if HEF_CORE_URI in heuristic.core_uris:
                valid_heuristics.append(heuristic)
            else:
                log.warning('Core version error.  Could not load %s' % heuristic.uri)
                log.warning('    Running core version: %s' % HEF_CORE_URI)
                log.warning('    Heuristic requires: %s' % heuristic.core_uris)
        valid_heuristics.sort(key = lambda h: h.short_name)
        return valid_heuristics
    
    @classmethod
    def generate_all(cls, heuristic_list=None, thread_count=HEF_THREAD_COUNT):
        '''
        Generate events all specified heuristics.  If event_heuristic_list is None, then
        use all known EventHeuristic instances.
        '''
        if heuristic_list:
            relevant_heuristics = set()
            for item in heuristic_list:
                if isinstance(item, cls):
                    relevant_heuristics.add(item)
            heuristic_list = relevant_heuristics
            if not heuristic_list:
                return 0
        else:
            heuristic_list = cls.get_all()
        counter = 0
        if thread_count == 0:
            #
            # No threads
            # 
            for heuristic in heuristic_list:
                log.info('Running %s' % heuristic)
                counter += heuristic.generate()
        else:
            #
            # Threaded
            #
            funcs = [heuristic.generate for heuristic in heuristic_list]
            counter = wait_for_threads(funcs, max_workers=thread_count)
        log.info('Generated %20s events' % counter)
        return counter


class BaseTimespanHeuristic(BaseHeuristic):
    '''
    A heuristic for generating Timespans from Events
    (Abstract base class)
    '''
    
    @classmethod
    def get_all(cls):
        '''
        @return: All known timespan heuristics
        @rtype:  List
        '''
        available_heuristics = set()
        for entry_point in iter_entry_points(group='esphealth', name='timespan_heuristics'):
            factory = entry_point.load()
            available_heuristics.update(factory())
        valid_heuristics = []
        for heuristic in available_heuristics:
            if HEF_CORE_URI in heuristic.core_uris:
                valid_heuristics.append(heuristic)
            else:
                log.warning('Mismatched core version error.  Could not load %s' % heuristic.uri)
                log.warning('    Running core version: %s' % HEF_CORE_URI)
                log.warning('    Heuristic requires: %s' % heuristic.core_uris)
        valid_heuristics.sort(key = lambda h: h.short_name)
        return valid_heuristics

    @abc.abstractproperty
    def timespan_names(self):
        '''
        A list of one or more strings naming all the possible 
        kinds of timespan this heuristic can generate
        '''
    
    @classmethod
    def generate_all(cls, heuristic_list=None, thread_count=HEF_THREAD_COUNT):
        '''
        Generate events all specified heuristics.  If heuristic_list is None, then
        use all known TimespanHeuristic instances.
        '''
        if heuristic_list:
            relevant_heuristics = set()
            for item in heuristic_list:
                if isinstance(item, cls):
                    relevant_heuristics.add(item)
            heuristic_list = relevant_heuristics
            if not heuristic_list:
                return 0
        else:
            heuristic_list = cls.get_all()
        log.debug('heuristic list: %s' % heuristic_list)
        if thread_count == 0:
            #
            # No threads
            # 
            for heuristic in heuristic_list:
                log.info('Running %s' % heuristic)
                counter = heuristic.generate() 
        else:
            #
            # Threaded
            #
            funcs = [heuristic.generate for heuristic in heuristic_list]
            counter = wait_for_threads(funcs, max_workers=thread_count)
        log.info('Generated %20s timespans' % counter)
        return counter


class AbstractLabTest(object):
    '''
    Represents an abstract type of lab test
    '''
    
    def __init__(self, name):
        '''
        An abstract type of lab test.  Any given abstract test may take several
            functionally equivalent, yet perhaps chemically dissimilar, concrete 
            forms.
        @param name:  Unique name of this test
        @type name:   String in Django slug format
        
        '''
        # Sanity check - is this a slug?
        assert re.match('[\w\d]+', name) 
        assert len(name) <= 50 
        #
        self.name = name
    
    def __unicode__(self):
        return u'Abstract Lab Test - %s' % self.name
    
    @classmethod
    def get_all_names(cls):
        '''
        Returns the set of all known Abstract Lab Test names
        '''
        names = set()
        for heuristic in BaseLabResultHeuristic.get_all():
            names.add(heuristic.alt.name)
        return names
    
    @property
    def lab_results(self):
        testmaps = LabTestMap.objects.filter(test_name = self.name).filter( Q(record_type='result') | Q(record_type='both') )
        qs = LabResult.objects.filter(native_code__in=testmaps.values('native_code'))
        log_query('Lab Results for %s' % self.name, qs)
        return qs
    
    @property
    def lab_orders(self):
        testmaps = LabTestMap.objects.filter(test_name = self.name).filter( Q(record_type='order') | Q(record_type='both') )
        qs = LabOrder.objects.filter(procedure_master_num__in=testmaps.values('native_code'))
        log_query('Lab Orders for %s' % self.name, qs)
        return qs
    
    @property
    def uri(self):
        '''
        URI describing this kind of abstract lab test
        '''
        return u'urn:x-esphealth:abstractlabtest:%s' % self.name


class LabOrderHeuristic(BaseEventHeuristic):
    '''
    A heuristic for detecting lab order events.
    
    Note that in some EMR systems (e.g. Atrius) lab orders may be less specific
    than lab results, and thus lab orders may require a different
    AbstractLabTest than required for lab results.
    '''
    
    def __init__(self, test_name):
        assert test_name
        self.test_name = test_name
    
    @property
    def short_name(self):
        return 'laborder:%s' % self.test_name
    
    uri = 'urn:x-esphealth:heuristic:channing:laborder:v1'
    
    @property
    def core_uris(self):
        # Only this version of HEF is supported
        return [HEF_CORE_URI]
    
    @property
    def order_event_name(self):
        return u'lx:%s:order' % self.test_name
    
    @property
    def event_names(self):
        return [self.order_event_name]
    
    def generate(self):
        log.info('Generating events for %s' % self)
        alt = AbstractLabTest(self.test_name)
        unbound_orders = alt.lab_orders.exclude(events__name=self.order_event_name)
        log_query('Unbound lab orders for %s' % self.uri, unbound_orders)
        unbound_count = unbound_orders.count()
        for order in queryset_iterator(unbound_orders):
            Event.create(
                name = self.order_event_name,
                source = self.uri,
                date = order.date,
                patient = order.patient,
                provider = order.provider,
                emr_record = order,
                )
        log.info('Generated %s new %s events' % (unbound_count, self.uri))
        return unbound_count
    
    
class BaseLabResultHeuristic(BaseEventHeuristic):
    '''
    Parent for lab heuristics, supplying some convenience methods
    '''
    
    @classmethod
    def get_all(cls):
        '''
        Returns the set of all lab result heuristics
        '''
        lab_heuristics = set()
        for h in BaseEventHeuristic.get_all():
            if isinstance(h, cls):
                lab_heuristics.add(h)
        return lab_heuristics
    
    @property
    def core_uris(self):
        # Only this version of HEF is supported
        return [HEF_CORE_URI]
    
    @property
    def alt(self):
        '''
        Returns the abstract lab test for this heuristic
        '''
        return AbstractLabTest(self.test_name)
    
    @property
    def unbound_labs(self):
        '''
        Returns a qs of LabResult objects that are not currently bound to any 
        event that can be generated by this heuristic.
        '''
        unbound_results = self.alt.lab_results
        unbound_results = unbound_results.exclude(events__name__in=list(self.event_names))
        return unbound_results
    


class LabResultAnyHeuristic(BaseLabResultHeuristic): 
    '''
    A heuristic for generating events on ANY result from specified lab test
    '''
    
    def __init__(self, test_name, date_field='order'):
        assert test_name
        assert date_field in ['order', 'result']
        self.test_name = test_name
        self.date_field = date_field
    
    @property
    def short_name(self):
        name = 'labresult:%s:any-result' % self.test_name
        if not self.date_field == 'order':
            name += ':%s-date' % self.date_field
        return name
    
    uri = 'urn:x-esphealth:heuristic:channing:labresult:any-result:v1'
    
    @property
    def any_result_event_name(self):
        # Order date is default
        if self.date_field == 'order':
            return u'lx:%s:any-result' % (self.test_name)
        else:
            return u'lx:%s:any-result:%s-date' % (self.test_name, self.date_field)
    
    @property
    def event_names(self):
        return [self.any_result_event_name]
    
    def generate(self):
        log.debug('Generating events for "%s"' % self)
        unbound_count = self.unbound_labs.count()
        for lab in queryset_iterator(self.unbound_labs):
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            Event.create(
                name = self.any_result_event_name,
                source = self.uri,
                date = lab_date,
                patient = lab.patient,
                provider = lab.provider,
                emr_record = lab,
                )
        log.info('Generated %s new %s events' % (unbound_count, self))
        return unbound_count


class LabResultPositiveHeuristic(BaseLabResultHeuristic): 
    '''
    A heuristic for detecting positive (& negative) lab result events
    '''
    
    def __init__(self, test_name, date_field='order', titer_dilution=None):
        '''
        @param titer_dilution: The demoninator showing titer dilution
        @type  titer_dilution: Integer
        '''
        assert test_name
        self.test_name = test_name
        self.date_field = date_field
        if titer_dilution:
            assert isinstance(titer_dilution, int)
            self.titer_dilution = titer_dilution
        else:
            self.titer_dilution = None
    
    @property
    def short_name(self):
        name = 'labresult:%s:positive' % self.test_name
        if not self.date_field == 'order':
            name += ':%s-date' % self.date_field
        if self.titer_dilution:
            name += ':titer:%s' % self.titer_dilution
        return name
    
    uri = 'urn:x-esphealth:heuristic:channing:labresult:positive:v1'
    
    @property
    def positive_event_name(self):
        # Order date is default
        if self.date_field == 'order':
            return u'lx:%s:positive' % self.test_name
        else:
            return u'lx:%s:positive:%s-date' % (self.test_name, self.date_field)
    
    @property
    def negative_event_name(self):
        # Order date is default
        if self.date_field == 'order':
            return u'lx:%s:negative' % self.test_name
        else:
            return u'lx:%s:negative:%s-date' % (self.test_name, self.date_field)
    
    @property
    def indeterminate_event_name(self):
        # Order date is default
        if self.date_field == 'order':
            return u'lx:%s:indeterminate' % self.test_name
        else:
            return u'lx:%s:indeterminate:%s-date' % (self.test_name, self.date_field)
    
    @property
    def event_names(self):
        return [self.positive_event_name, self.negative_event_name, self.indeterminate_event_name]
    
    def generate(self):
        #
        # TODO:  The negative and indeterminate querysets should be generated 
        # *after* creating of preceding queries' events, so that labs bound to 
        # those events are ignored.  This will allow negative lab query to much
        # simpler.
        #
        log.debug('Generating events for "%s"' % self)
        #
        # Build numeric query
        #
        #--------------------------------------------------------------------------------
        # Not doing abnormal flag yet, because many values are not null but a blank string
        #
        #if result_type == 'positive':
            #pos_q = Q(abnormal_flag__isnull=False)
        #else:
            #pos_q = None
        #--------------------------------------------------------------------------------
        map_qs = LabTestMap.objects.filter(test_name=self.test_name)
        if not map_qs:
            log.warning('No tests mapped for "%s", cannot generate events.' % self.test_name)
            return 0
        #
        # All labs can be classified pos/neg if they have reference high and 
        # numeric result
        #
        ref_high_float_q = Q(ref_high_float__isnull=False)
        result_float_q = Q(result_float__isnull=False)
        numeric_q = ref_high_float_q & result_float_q
        positive_q = ( numeric_q & Q(result_float__gte = F('ref_high_float')) )
        negative_q = ( numeric_q & Q(result_float__lt = F('ref_high_float')) )
        indeterminate_q = None
        all_labs_q = None
        #
        # Build queries with custom result strings or fallback thresholds
        #
        simple_strings_lab_q = None
        for map in map_qs:
            lab_q = map.lab_results_q_obj
            if all_labs_q:
                all_labs_q |= lab_q
            else:
                all_labs_q = lab_q
            #
            # Labs mapped with extra result strings need to be handled specially
            #
            if map.extra_positive_strings.all() \
                or map.extra_negative_strings.all() \
                or map.extra_indeterminate_strings.all() \
                or map.excluded_positive_strings.all() \
                or map.excluded_negative_strings.all() \
                or map.excluded_indeterminate_strings.all():
                positive_q |= (map.positive_string_q_obj & lab_q)
                negative_q |= (map.negative_string_q_obj & lab_q)
                if indeterminate_q:
                    indeterminate_q |= (map.indeterminate_string_q_obj & lab_q)
                else:
                    indeterminate_q = (map.indeterminate_string_q_obj & lab_q)
                continue
            # Threshold criteria is *in addition* to reference high
            if map.threshold:
                num_lab_q = (lab_q & result_float_q)
                positive_q |= ( num_lab_q & Q(result_float__gte=map.threshold) )
                negative_q |= ( num_lab_q & Q(result_float__lt=map.threshold) )
            if simple_strings_lab_q:
                simple_strings_lab_q |= lab_q
            else:
                simple_strings_lab_q = lab_q
        #
        # All labs in the simple_strings_lab_q can be queried using the standard
        # set of result strings
        #
        if simple_strings_lab_q:
            pos_rs_q = ResultString.get_q_by_indication('pos')
            neg_rs_q = ResultString.get_q_by_indication('neg')
            ind_rs_q = ResultString.get_q_by_indication('ind')
            positive_q |= (simple_strings_lab_q & pos_rs_q)
            negative_q |= (simple_strings_lab_q & neg_rs_q)
            if indeterminate_q:
                indeterminate_q |= (simple_strings_lab_q & ind_rs_q)
            else:
                indeterminate_q = (simple_strings_lab_q & ind_rs_q)
        #
        # Add titer string queries
        #
        if self.titer_dilution:
            positive_titer_strings = ['1:%s' % 2**i for i in range(math.log(self.titer_dilution, 2), math.log(4096,2))]
            negative_titer_strings = ['1:%s' % 2**i for i in range(math.log(self.titer_dilution, 2))]
            log.debug('positive_titer_strings: %s' % positive_titer_strings)
            log.debug('negative_titer_strings: %s' % negative_titer_strings)
            for s in positive_titer_strings:
                positive_q |= Q(result_string__istartswith=s)
            for s in negative_titer_strings:
                negative_q |= Q(result_string__istartswith=s)
        positive_q = all_labs_q & positive_q
        negative_q = all_labs_q & negative_q
        indeterminate_q = all_labs_q & indeterminate_q
        #
        # Generate Events
        #
        pos_counter = 0
        positive_labs = self.unbound_labs.filter(positive_q)
        log_query('Positive labs for %s' % self.uri, positive_labs)
        log.info('Generating positive events for %s' % self)
        for lab in queryset_iterator(positive_labs):
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            Event.create(
                name = self.positive_event_name,
                source = self.uri,
                patient = lab.patient,
                date = lab_date,
                provider = lab.provider,
                emr_record = lab,
                )
            pos_counter += 1
        log.info('Generated %s new positive events for %s' % (positive_labs.count(), self))
        negative_labs = self.unbound_labs.filter(negative_q)
        log_query('Negative labs for %s' % self, negative_labs)
        log.info('Generating negative events for %s' % self)
        neg_counter = 0
        for lab in queryset_iterator(negative_labs):
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            Event.create(
                name = self.negative_event_name,
                source = self.uri,
                patient = lab.patient,
                date = lab_date,
                provider = lab.provider,
                emr_record = lab,
                )
            neg_counter += 1
        log.info('Generated %s new negative events for %s' % (negative_labs.count(), self))
        indeterminate_labs = self.unbound_labs.filter(indeterminate_q)
        log_query('Indeterminate labs for %s' % self, indeterminate_labs)
        log.info('Generating indeterminate events for %s' % self)
        ind_counter = 0
        for lab in queryset_iterator(indeterminate_labs):
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            Event.create(
                name = self.indeterminate_event_name,
                source = self.uri,
                patient = lab.patient,
                date = lab_date,
                provider = lab.provider,
                emr_record = lab,
                )
            ind_counter += 1
        log.info('Generated %s new indeterminate events for %s' % (ind_counter, self))
        return pos_counter + neg_counter + ind_counter


class LabResultRatioHeuristic(BaseLabResultHeuristic):
    '''
    A heuristic for detecting ratio-based positive lab result events
    '''
    
    def __init__(self, test_name, ratio, date_field='order'):
        '''
        @param ratio: Result must be greater than ref_high * ratio to generate
            an event.
        @type  ratio: Decimal
        '''
        assert test_name and date_field
        assert isinstance(ratio, Decimal)
        self.test_name = test_name
        self.ratio = ratio
        self.date_field = date_field
    
    @property
    def short_name(self):
        name = 'labresult:%s:ratio:%s' % (self.test_name, self.ratio)
        if not self.date_field == 'order':
            name += ':%s-date' % self.date_field
        return name
    
    uri = 'urn:x-esphealth:heuristic:channing:labresult:ratio:v1'
    
    @property
    def ratio_event_name(self):
        name = u'lx:%s:ratio:%s' % (self.test_name, self.ratio)
        if not self.date_field == 'order':
            name += ':%s-date' % self.date_field
        return name
    
    @property
    def event_names(self):
        return [self.ratio_event_name]
    
    def generate(self):
        positive_labs = LabResult.objects.none()
        code_maps = LabTestMap.objects.filter(test=self.test)
        for map in code_maps:
            labs = self.unbound_labs.filter(map.lab_results_q_obj)
            #
            # Build numeric comparison queries
            #
            num_res_labs = labs.filter(result_float__isnull=False)
            positive_labs |= num_res_labs.filter(ref_high_float__isnull=False, result_float__gte = (self.ratio * F('ref_high_float')))
            if map.threshold:
                positive_labs |= num_res_labs.filter(ref_high_float__isnull=True, result_float__gte = (self.ratio * map.threshold))
        log_query(self, positive_labs)
        log.info('Generating new events for %s' % self)
        for lab in queryset_iterator(positive_labs):
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            Event.create(
                name = self.ratio_event_name,
                source = self.uri,
                patient = lab.patient,
                date = lab_date,
                provider = lab.provider,
                emr_record = lab,
                )
        log.info('Generated %s new events for %s' % (positive_labs.count(), self))
        return positive_labs.count()


class LabResultFixedThresholdHeuristic(BaseLabResultHeuristic):
    '''
    A heuristic for detecting fixed-threshold-based positive lab result events
    '''
    def __init__(self, test_name, threshold, match_type='gte', date_field='order'):
        '''
        @param threshold: Events are generated for lab results greater than or equal to this value
        @type threshold:  Decimal
        '''
        assert test_name and date_field
        assert isinstance(threshold, Decimal)
        assert match_type in ['gt', 'gte', 'lt', 'lte']
        self.test_name = test_name
        self.threshold = threshold
        self.match_type = match_type
        self.date_field = date_field
    
    @property
    def short_name(self):
        name = 'labresult:%s:threshold:%s:%s' % (self.test_name, self.match_type, self.threshold)
        if not self.date_field == 'order':
            name += ':%s-date' % self.date_field
        return name
    
    uri = 'urn:x-esphealth:heuristic:channing:labresult:threshold:v1'
    
    @property
    def threshold_event_name(self):
        name = u'lx:%s:threshold:%s:%s' % (self.test_name, self.match_type, self.threshold)
        if not self.date_field == 'order':
            name += ':%s-date' % self.date_field
        return name
    
    @property
    def event_names(self):
        return [self.threshold_event_name]
    
    def generate(self):
        lab_qs = self.unbound_labs.filter(result_float__isnull=False)
        if self.match_type == 'lt':
            lab_qs = lab_qs.filter(result_float__lt=self.threshold)
        elif self.match_type == 'lte':
            lab_qs = lab_qs.filter(result_float__lte=self.threshold)
        elif self.match_type == 'gt':
            lab_qs = lab_qs.filter(result_float__gt=self.threshold)
        else: # 'gte'
            lab_qs = lab_qs.filter(result_float__gte=self.threshold)
        log_query(self, lab_qs)
        counter = 0
        for lab in queryset_iterator(lab_qs):
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            Event.create(
                name = self.threshold_event_name,
                source = self.uri,
                patient = lab.patient,
                date = lab_date,
                provider = lab.provider,
                emr_record = lab,
                )
            counter += 1
        log.info('Generated %s new events for %s' % (counter, self.uri))
        return counter


class LabResultRangeHeuristic(BaseLabResultHeuristic):
    '''
    A heuristic for detecting lab results falling within a certain fixed range
    '''
    
    def __init__(self, test_name, min, max, min_match='gte', max_match='lte', date_field='order'):
        '''
        Generates events for lab results with numeric values falling within a specified range.
        @param min: Minimum result value to generate an event
        @type min:  Decimal
        @param max: Maximum result value to generate an event
        @type max:  Decimal
        @param min_match: Match type for min value 
        @type min_match:  String, either 'gt' or 'gte'
        @param max_match: Match type for max value 
        @type max_match:  String, either 'lt' or 'lte'
        '''
        assert test_name and date_field
        assert isinstance(min, Decimal)
        assert isinstance(max, Decimal)
        assert min_match in ['gt', 'gte']
        assert max_match in ['lt', 'lte']
        self.test_name = test_name
        self.date_field = date_field
        self.min = min
        self.max = max
        self.min_match = min_match
        self.max_match = max_match
    
    @property
    def short_name(self):
        name = 'labresult:%s:range:%s:%s:%s:%s' % (self.test_name, 
            self.min_match, self.min, self.max_match, self.max)
        if not self.date_field == 'order':
            name += ':%s-date' % self.date_field
        return name
    
    uri = 'urn:x-esphealth:heuristic:channing:labresult:range:v1'
    
    @property
    def ratio_event_name(self):
        name = 'lx:%s:range:%s:%s:%s:%s' % (self.test_name, self.min_match, self.min, self.max_match, self.max)
        if not self.date_field == 'order':
            name += ':%s-date' % self.date_field
        return name
    
    @property
    def event_names(self):
        return [self.ratio_event_name]
    
    def generate(self):
        qs = self.unbound_labs.filter(
            result_float__isnull=False, 
            )
        if self.min_match == 'gte':
            qs = qs.filter(result_float__gte=self.min)
        elif self.min_match == 'gt':
            qs = qs.filter(result_float__gt=self.min)
        if self.max_match == 'lte':
            qs = qs.filter(result_float__lte=self.max)
        elif self.max_match == 'lt':
            qs = qs.filter(result_float__lt=self.max)
        log_query(self.uri, qs)
        log.info('Generating events for "%s"' % self)
        for lab in queryset_iterator(qs):
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            Event.create(
                name = self.ratio_event_name,
                source = self.uri,
                patient = lab.patient,
                date = lab_date,
                provider = lab.provider,
                emr_record = lab,
                )
        log.info('Generated %s new events for %s' % (qs.count(), self))
        return qs.count() 


class LabResultWesternBlotHeuristic(BaseLabResultHeuristic):
    '''
    Generates events from western blot test results.
    http://en.wikipedia.org/wiki/Western_blot
    '''
    def __init__(self, test_name, bands, date_field='order'):
        '''
        Generates events for Western Blot lab results
        @param bands: List of interesting bands for this western blot
        @type bands:  List of strings
        '''
        assert test_name and date_field and bands
        self.test_name = test_name
        self.date_field = date_field
        self.bands = ['%s'.strip() %b for b in bands]
    
    @property
    def bands_str(self):
        '''
        Printable string of self.bands
        '''
        return '|'.join(self.bands)
    
    @property
    def short_name(self):
        name = 'labresult:%s:westernblot:%s' % (self.test_name, self.bands_str)
        if not self.date_field == 'order':
            name += ':%s-date' % self.date_field
        return name
    
    uri = 'urn:x-esphealth:heuristic:channing:labresult:westernblot:v1'
    
    @property
    def positive_event_name(self):
        name = 'lx:%s:westernblot:%s:positive' % (self.test_name, self.bands_str)
        if not self.date_field == 'order':
            name += ':%s-date' % self.date_field
        return name
    
    @property
    def negative_event_name(self):
        name = 'lx:%s:westernblot:%s:negative' % (self.test_name, self.bands_str)
        if not self.date_field == 'order':
            name += ':%s-date' % self.date_field
        return name
    
    @property
    def event_names(self):
        return [self.positive_event_name, self.negative_event_name]
    
    def generate_events(self):
        log.debug('Generating events for "%s"' % self)
        counter = 0
        # Find potential positives -- tests whose results contain at least one 
        # of the interesting band numbers.
        q_obj = Q(result_string__icontains = self.bands[0])
        for band in self.bands[1:]:
            q_obj = q_obj | Q(result_string__icontains = band)
        potential_positives = self.unbound_labs.filter(q_obj)
        log.debug('Found %s potential positive lab results.' % potential_positives.count())
        # Examine result strings of each potential positive.  If it has enough 
        # interesting bands, add its pk to the match list
        match_pks = []
        for item in potential_positives.values('pk', 'result_string'):
            # We might need smarter splitting logic if we ever get differently
            # formatted result strings.
            band_count = 0 # Counter of interesting bands in this result
            result_bands = item['result_string'].replace(' ', '').split(',')
            pk = item['pk']
            for band in result_bands:
                try:
                    band = int(band)
                except ValueError:
                    log.warning('Could not cast band "%s" from lab # %s into an integer.' % (band, pk))
                    continue
                if band in self.interesting_bands:
                    band_count += 1
                # If we reach the band_count threshold, we have a positive result.  No need to look further.
                if band_count >= self.band_count:
                    match_pks.append(pk)
                    break
        log.debug('Found %s actual positive lab results.' % len(match_pks))
        for lab in LabResult.objects.filter(pk__in = match_pks):
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            Event.create(
                name = self.positive_event_name,
                source = self.uri,
                patient = lab.patient,
                date = lab_date,
                provider = lab.provider,
                emr_record = lab,
                )
            counter += 1
        for lab in queryset_iterator(self.unbound_labs.exclude(pk__in = match_pks)):
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            Event.create(
                name = self.negative_event_name,
                source = self.uri,
                patient = lab.patient,
                date = lab_date,
                provider = lab.provider,
                emr_record = lab,
                )
            counter += 1
        return counter


class Dose(object):
    '''
    A measurement of dose for a prescription
    '''
    
    def __init__(self, quantity, units):
        assert quantity and units
        assert units in [i[0] for i in DOSE_UNIT_CHOICES]
        self.quantity = quantity
        self.units = units
    
    def __unicode__(self):
        return u'%s %s' % (self.quantity, self.units)
    
    @property
    def string_variants(self):
        '''
        Returns the various different strings that can represent this dose
        '''
        # Represent quantity as an integer ('2' vs '2.0') if appropriate
        if int(self.quantity) == self.quantity:
            quantity = int(self.quantity)
        else:
            quantity = self.quantity
        variants = DOSE_UNIT_VARIANTS[self.units]
        result = ['%s%s' % (quantity, i) for i in variants]   # Without space
        result += ['%s %s' % (quantity, i) for i in variants] # With space
        return result
        

class PrescriptionHeuristic(BaseEventHeuristic):
    '''
    A heuristic for detecting prescription events
    '''
    
    def __init__(self, name, drugs, doses=[], min_quantity=None, require=[], exclude=[]):
        '''
        @param name: Name of event to be generated
        @type name:  String
        @param drugs: Generate event if one of these drugs was prescribed
        @type drugs:  List of strings
        @param doses: Only generate events if this doses was prescribed
        @type doses:  List of Dose objects
        @param min_quanity: Minimum value for quantity field
        @type min_quanity:  Integer
        @param require: Prescription must include one or more of these strings.
        @type require:  List of strings
        @param exclude: Prescription may not include any of these strings.
        @type exclude:  List of strings
        '''
        assert name and drugs
        self.name = name
        self.drugs = [d.strip() for d in drugs]
        for dose_obj in doses:
            assert isinstance(dose_obj, Dose)
        self.doses = doses
        self.min_quantity = min_quantity
        self.require = require
        self.exclude = exclude
        
    @property
    def short_name(self):
        return 'prescription:%s' % self.name
    
    uri = 'urn:x-esphealth:heuristic:channing:prescription:v1'
    
    @property
    def core_uris(self):
        # Only this version of HEF is supported
        return [HEF_CORE_URI]
    
    @property
    def rx_event_name(self):
        return 'rx:%s' % self.name
    
    @property
    def event_names(self):
        return [self.rx_event_name]
    
    
    def generate(self):
        prescriptions = Prescription.objects.none()
        for drug_name in self.drugs:
            prescriptions |= Prescription.objects.filter(name__icontains=drug_name)
        if self.doses:
            rxs_by_dose = Prescription.objects.none()
            for dose_obj in self.doses:
                for dose_string in dose_obj.string_variants:
                    rxs_by_dose |= Prescription.objects.filter(name__icontains=dose_string)
                    rxs_by_dose |= Prescription.objects.filter(dose__icontains=dose_string)
            prescriptions &= rxs_by_dose
        if self.min_quantity:
            prescriptions = prescriptions.filter(quantity__gte=self.min_quantity)
        for required_string in self.require:
            prescriptions = prescriptions.filter(name__icontains=required_string)
        for excluded_string in self.exclude:
            prescriptions = prescriptions.exclude(name__icontains=excluded_string)
        # Exclude prescriptions already bound to this heuristic
        prescriptions = prescriptions.exclude(events__name__in=self.event_names)
        prescriptions = prescriptions.order_by('date')
        log_query('Prescriptions for %s' % self, prescriptions)
        log.info('Generating events for "%s"' % self)
        for rx in queryset_iterator(prescriptions):
            Event.create(
                name = self.rx_event_name,
                source = self.uri,
                patient = rx.patient,
                date = rx.date,
                provider = rx.provider,
                emr_record = rx,
                )
        return prescriptions.count()


class Icd9Query(object):
    '''
    A query for selecting encounters based on ICD9 codes
    '''
    
    def __init__(self, exact=None, starts_with=None, ends_with=None, contains=None):
        '''
        @param exact: Encounter must include this exact ICD9 code
        @type exact:  String
        #
        # We use "starts_with" instead of Django-style "startswith", to
        # discourage people from thinking this argument is case-sensistive,
        # like a Django startswith query would be.
        #
        # Let's hope we never need to deal with case-sensitive ICD9 codes.
        #
        @param starts_with: Encounter must include an ICD9 code starting with this string
        @type exact:  String
        @param ends_with: Encounter must include an ICD9 code ending with this string
        @type exact:  String
        @param contains: Encounter must include an ICD9 code containing this string
        @type exact:  String
        '''
        assert (exact or starts_with or ends_with or contains) # Sanity check
        self.exact = exact
        self.starts_with = starts_with
        self.ends_with = ends_with
        self.contains = contains
        
    
    @property
    def icd9_q_obj(self):
        '''
        Returns a Q object suitable for selecting ICD9 objects that match this query
        '''
        q_list = []
        if self.exact:
            q_list.append( Q(code__iexact=self.exact) )
        if self.starts_with:
            q_list.append( Q(code__istartswith=self.starts_with) )
        if self.ends_with:
            q_list.append( Q(code__iendswith=self.ends_with) )
        if self.contains:
            q_list.append( Q(code__icontains=self.contains) )
        assert q_list # This should not be empty
        q_obj = q_list[0]
        for another_q_obj in q_list[1:]:
            q_obj &= another_q_obj
        return q_obj
    
    @property
    def encounter_q_obj(self):
        '''
        Returns a Q object suitable for selecting ICD9 objects that match this query
        '''
        q_list = []
        if self.exact:
            q_list.append( Q(icd9_codes__code__iexact=self.exact) )
        if self.starts_with:
            q_list.append( Q(icd9_codes__code__istartswith=self.starts_with) )
        if self.ends_with:
            q_list.append( Q(icd9_codes__code__iendswith=self.ends_with) )
        if self.contains:
            q_list.append( Q(icd9_codes__code__icontains=self.contains) )
        assert q_list # This should not be empty
        q_obj = q_list[0]
        for another_q_obj in q_list[1:]:
            q_obj &= another_q_obj
        return q_obj
    
    def __unicode__(self):
        return u'%s' % self.verbose_name
    
    @property
    def verbose_name(self):
        return 'ICD9 Query: %s | %s | %s | %s' % (self.exact, self.starts_with, self.ends_with, self.contains),


class DiagnosisHeuristic(BaseEventHeuristic):
    '''
    A heuristic for detecting events based on one or more ICD9 diagnosis codes
    from a physician encounter.
    '''
    
    def __init__(self, name, icd9_queries):
        '''
        @param name: Name of this heuristic
        @type name:  String
        @param icd9_queries: Generate event for records matching one of these queries
        @type icd9_queries:  List of Icd9Query objects
        '''
        assert name and icd9_queries
        self.name = name
        self.icd9_queries = icd9_queries

    @property
    def short_name(self):
        sn = u'diagnosis:%s' % self.name
        return sn
    
    uri = u'urn:x-esphealth:heuristic:channing:diagnosis:v1'
    
    # Only this version of HEF is supported
    core_uris = [HEF_CORE_URI]
    
    def __str__(self):
        return self.short_name
    
    @property
    def encounters(self):
        enc_q = self.icd9_queries[0].encounter_q_obj
        for query in self.icd9_queries[1:]:
            enc_q |= query.encounter_q_obj
        return Encounter.objects.filter(enc_q)
    
    @property
    #def icd9_q_obj(self):
    def junk(self):
        q_obj = None
        for icd9_query in self.icd9_queries:
            if q_obj:
                q_obj |= icd9_query.icd9_q_obj
            else:
                q_obj = icd9_query.icd9_q_obj
        return q_obj
    
    @property
    def dx_event_name(self):
        return 'dx:%s' % self.name
    
    @property
    def event_names(self):
        return [self.dx_event_name]
    
    def generate(self):
        enc_qs = self.encounters
        enc_qs = enc_qs.exclude(events__name__in=self.event_names)
        enc_qs = enc_qs.order_by('date').distinct()
        log.info('Generating events for "%s"' % self)
        log_query('Encounters for %s' % self, enc_qs)
        counter = 0
        for enc in queryset_iterator(enc_qs):
            Event.create(
                name = self.dx_event_name,
                source = self.uri,
                patient = enc.patient,
                date = enc.date,
                provider = enc.provider,
                emr_record = enc,
                )
            counter += 1
        log.info('Generated %s new events for %s' % (counter, self))
        return counter


class CalculatedBilirubinHeuristic(object):
    '''
    A heuristic to detect high calculated 
    '''
    #
    # Write me!
    #
