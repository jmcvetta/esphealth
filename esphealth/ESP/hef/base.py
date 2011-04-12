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
HEF_CORE_URI = 'urn:x-esphealth:hef:core:3.0'
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import abc
import math
import re

from decimal import Decimal

from ESP.conf.models import LabTestMap
from ESP.emr.models import Encounter
from ESP.emr.models import LabOrder
from ESP.emr.models import LabResult
from ESP.emr.models import Prescription
from ESP.hef.models import Event
from ESP.static.models import Icd9
from ESP.utils import log, log_query
from ESP.utils.utils import queryset_iterator
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


class BaseHeuristic(object):
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
    
    def __str__(self):
        return smart_str(self.uri)
    
    __registered_heuristics = {}
    
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
        heuristics = set()
        for entry_point in iter_entry_points(group='esphealth', name='event_heuristics'):
            factory = entry_point.load()
            heuristics.update(factory())
        heuristics = list(heuristics)
        heuristics.sort(key = lambda h: h.short_name)
        return heuristics


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
        heuristics = set()
        for entry_point in iter_entry_points(group='esphealth', name='timespan_heuristics'):
            factory = entry_point.load()
            heuristics.update(factory())
        heuristics = list(heuristics)
        heuristics.sort(key = lambda h: h.short_name)
        return heuristics

    @abc.abstractproperty
    def timespan_names(self):
        '''
        A list of one or more strings naming all the possible 
        kinds of timespan this heuristic can generate
        '''
        

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
    
    @property
    def lab_results(self):
        testmaps = LabTestMap.objects.filter(test_name = self.name).filter( Q(record_type='result') | Q(record_type='both') )
        qs = LabResult.objects.filter(native_code__in=testmaps.values('native_code'))
        log_query('Lab Results for %s' % self.name, qs)
        return qs
    
    @property
    def lab_orders(self):
        testmaps = LabTestMap.objects.filter(test_name = self.name).filter( Q(record_type='order') | Q(record_type='both') )
        qs = LabOrder.objects.filter(native_code__in=testmaps.values('native_code'))
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
    def order_event_name(self):
        return u'lx:%s:order' % self.test_name
    
    @property
    def event_names(self):
        return [self.order_event_name]
    
    def generate(self):
        log.info('Generating events for %s' % self)
        alt = AbstractLabTest(self.test_name)
        unbound_orders = alt.lab_orders.exclude(tags__event_name=self.order_event_name)
        log_query('Unbound lab orders for %s' % self.uri, unbound_orders)
        unbound_count = unbound_orders.count()
        for order in queryset_iterator(unbound_orders):
            e = Event(
                name = self.order_event_name,
                source = self.uri,
                date = order.date,
                patient = order.patient,
                provider = order.provider,
                )
            e.save()
            e.tag(order)
            log.debug('Saved new event: %s' % e)
        log.info('Generated %s new %s events' % (unbound_count, self.uri))
        return unbound_count
    
    
class BaseLabResultHeuristic(BaseEventHeuristic):
    '''
    Parent for lab heuristics, supplying some convenience methods
    '''
    
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
        unbound_results = self.alt.lab_results.exclude(tags__event_name__in=self.event_names)
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
            return u'lx:%s:any-result' % (self.test_name, self.date_field)
        else:
            return u'lx:%s:any-result:%s-date' % (self.test_name, self.date_field)
    
    @property
    def event_names(self):
        return [self.any_result_event_name]
    
    def generate(self):
        log.debug('Generating events for "%s"' % self)
        unbound_count = self.unbound_results.count()
        for lab in queryset_iterator(self.unbound_results):
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            e = Event(
                name = self.any_result_event_name,
                source = self.uri,
                date = lab_date,
                patient = lab.patient,
                provider = lab.provider,
                )
            e.save()
            e.tag(lab)
            log.debug('Saved new event: %s' % e)
        log.info('Generated %s new %s events' % (unbound_count, self.uri))
        return unbound_count


class LabResultPositiveHeuristic(BaseLabResultHeuristic): 
    '''
    A heuristic for detecting positive (& negative) lab result events
    '''
    
    def __init__(self, test_name, date_field='order', titer_dilution=None):
        assert test_name
        self.test_name = test_name
        self.date_field = date_field
        if titer_dilution:
            self.titer_dilution = Decimal('%.2g' % titer_dilution)
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
        positive_q = Q(pk__isnull=True)
        negative_q = Q(pk__isnull=True)
        indeterminate_q = Q(pk__isnull=True)
        #
        # Build queries from LabTestMaps
        #
        for map in LabTestMap.objects.filter(test_name=self.test_name):
            lab_q = map.lab_results_q_obj
            ref_float_q = Q(ref_high_float__isnull=False)
            num_res_q = lab_q & ref_float_q & Q(result_float__isnull=False)
            positive_q |= num_res_q & Q(result_float__gte = F('ref_high_float'))
            negative_q |= num_res_q & Q(result_float__lt = F('ref_high_float'))
            if map.threshold:
                positive_q |= num_res_q & Q(result_float__gte=map.threshold)
                negative_q |= num_res_q & Q(result_float__lt=map.threshold)
            # Greater than ref high -- result string begins with '>' and ref_high_float is not null
            positive_q |= lab_q & ref_float_q & Q(result_string__istartswith='>')
            negative_q |= lab_q & ref_float_q & Q(result_string__istartswith='<')
            # String queries
            positive_q |= (map.positive_string_q_obj & map.lab_results_q_obj)
            negative_q |= (map.negative_string_q_obj & map.lab_results_q_obj)
            indeterminate_q |= (map.indeterminate_string_q_obj & map.lab_results_q_obj)
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
        #
        # Generate Events
        #
        positive_labs = self.unbound_labs.filter(positive_q)
        log_query('Positive labs for %s' % self.uri, positive_labs)
        log.info('Generating positive events for %s' % self)
        for lab in queryset_iterator(positive_labs):
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            new_event = Event(
                name = self.positive_event_name,
                source = self.uri,
                patient = lab.patient,
                date = lab_date,
                provider = lab.provider,
                )
            new_event.save()
            new_event.tag(lab)
            log.debug('Saved new event: %s' % new_event)
        log.info('Generated %s new positive events for %s' % (positive_labs.count(), self))
        negative_labs = self.unbound_labs.filter(negative_q)
        log_query('Negative labs for %s' % self, negative_labs)
        log.info('Generating negative events for %s' % self)
        for lab in queryset_iterator(negative_labs):
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            new_event = Event(
                name = self.negative_event_name,
                source = self.uri,
                patient = lab.patient,
                date = lab_date,
                provider = lab.provider,
                )
            new_event.save()
            new_event.tag(lab)
            log.debug('Saved new event: %s' % new_event)
        log.info('Generated %s new negative events for %s' % (negative_labs.count(), self))
        indeterminate_labs = self.unbound_labs.filter(indeterminate_q)
        log_query('Indeterminate labs for %s' % self, indeterminate_labs)
        log.info('Generating indeterminate events for %s' % self)
        for lab in queryset_iterator(indeterminate_labs):
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            new_event = Event(
                name = self.indeterminate_event_name,
                source = self.uri,
                patient = lab.patient,
                date = lab_date,
                provider = lab.provider,
                )
            new_event.save()
            new_event.tag(lab)
            log.debug('Saved new event: %s' % new_event)
        log.info('Generated %s new indeterminate events for %s' % (indeterminate_labs.count(), self))
        return positive_labs.count() + negative_labs.count() + indeterminate_labs.count()


class LabResultRatioHeuristic(BaseLabResultHeuristic):
    '''
    A heuristic for detecting ratio-based positive lab result events
    '''
    
    def __init__(self, test_name, ratio, date_field='order'):
        assert test_name and ratio and date_field
        self.test_name = test_name
        self.ratio = Decimal('%.2g' % ratio)
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
            new_event = Event(
                name = self.ratio_event_name,
                source = self.uri,
                patient = lab.patient,
                date = lab_date,
                provider = lab.provider,
                )
            new_event.save()
            new_event.tag(lab)
            log.debug('Saved new event: %s' % new_event)
        log.info('Generated %s new events for %s' % (positive_labs.count(), self))
        return positive_labs.count()


class LabResultFixedThresholdHeuristic(BaseLabResultHeuristic):
    '''
    A heuristic for detecting fixed-threshold-based positive lab result events
    '''
    def __init__(self, test_name, threshold, date_field='order'):
        '''
        @param threshold: Events are generated for lab results greater than or equal to this value
        @type threshold:  Float
        '''
        assert test_name and date_field
        self.test_name = test_name
        self.threshold = Decimal('%.2g' % threshold)
        self.date_field = date_field
    
    @property
    def short_name(self):
        name = 'labresult:%s:threshold:%s' % (self.test_name, self.threshold)
        if not self.date_field == 'order':
            name += ':%s-date' % self.date_field
        return name
    
    uri = 'urn:x-esphealth:heuristic:channing:labresult:threshold:v1'
    
    @property
    def threshold_event_name(self):
        name = u'lx:%s:threshold:%s' % (self.test_name, self.threshold)
        if not self.date_field == 'order':
            name += ':%s-date' % self.date_field
        return name
    
    @property
    def event_names(self):
        return [self.threshold_event_name]
    
    def generate(self):
        positive_labs = self.unbound_labs.filter(result_float__isnull=False, result_float__gte=self.threshold)
        log_query(self.uri, positive_labs)
        log.info('Generating events for "%s"' % self)
        for lab in queryset_iterator(positive_labs):
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            new_event = Event(
                name = self.threshold_event_name,
                source = self.uri,
                patient = lab.patient,
                date = lab_date,
                provider = lab.provider,
                )
            new_event.save()
            new_event.tag(lab)
            log.debug('Saved new event: %s' % new_event)
        log.info('Generated %s new events for %s' % (positive_labs.count(), self.uri))
        return positive_labs.count() 


class LabResultRangeHeuristic(BaseLabResultHeuristic):
    '''
    A heuristic for detecting lab results falling within a certain fixed range
    '''
    
    def __init__(self, test_name, min, max, min_match='gte', max_match='lte', date_field='order'):
        '''
        Generates events for lab results with numeric values falling within a specified range.
        @param min: Minimum result value to generate an event
        @type min:  Float
        @param max: Maximum result value to generate an event
        @type max:  Float
        @param min_match: Match type for min value 
        @type min_match:  String, either 'gt' or 'gte'
        @param max_match: Match type for max value 
        @type max_match:  String, either 'lt' or 'lte'
        '''
        assert test_name and date_field
        assert min_match in ['gt', 'gte']
        assert max_match in ['lt', 'lte']
        self.test_name = test_name
        self.date_field = date_field
        self.min = Decimal('%.2g' % min)
        self.max = Decimal('%.2g' % max)
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
            new_event = Event(
                name = self.ratio_event_name,
                source = self.uri,
                patient = lab.patient,
                date = lab_date,
                provider = lab.provider,
                )
            new_event.save()
            new_event.tag(lab)
            log.debug('Saved new event: %s' % new_event)
        log.info('Generated %s new events for %s' % (qs.count(), self.uri))
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
            new_event = Event(
                name = self.positive_event_name,
                source = self.uri,
                patient = lab.patient,
                date = lab_date,
                provider = lab.provider,
                )
            new_event.save()
            new_event.tag(lab)
            counter += 1
        for lab in queryset_iterator(self.unbound_labs.exclude(pk__in = match_pks)):
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            new_event = Event(
                name = self.negative_event_name,
                source = self.uri,
                patient = lab.patient,
                date = lab_date,
                provider = lab.provider,
                )
            new_event.save()
            new_event.tag(lab)
            counter += 1
        return counter


class Dose(object):
    '''
    A measurement of dose for a prescription
    '''
    
    def __init__(self, quantity, units):
        assert quantity and units
        assert units in DOSE_UNIT_CHOICES
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
    
    def __init__(self, name, drugs, doses=[], min_quantity=None, require=None, exclude=None):
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
            assert isinstance(Dose, dose_obj)
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
        if self.require:
            require = [s.strip() for s in self.require.split(',')]
        else:
            require = []
        if self.exclude:
            exclude = [s.strip() for s in self.exclude.split(',')]
        else:
            exclude = []
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
        for required_string in require:
            prescriptions = prescriptions.filter(name__icontains=required_string)
        for excluded_string in exclude:
            prescriptions = prescriptions.exclude(name__icontains=excluded_string)
        # Exclude prescriptions already bound to this heuristic
        prescriptions = prescriptions.exclude(tags__event_name__in=self.event_names)
        log_query('Prescriptions for %s' % self, prescriptions)
        log.info('Generating events for "%s"' % self)
        for rx in queryset_iterator(prescriptions):
            new_event = Event(
                name = self.rx_event_name,
                source = self.uri,
                patient = rx.patient,
                date = rx.date,
                provider = rx.provider,
                )
            new_event.save()
            new_event.tag(rx)
            log.debug('Saved new event: %s' % new_event)
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
        
    
    def __get_icd9_q_obj(self):
        '''
        Returns a Q object suitable for selecting ICD9 objects that match this query
        '''
        q_obj = Q() # Null Q object
        if self.exact:
            q_obj &= Q(code__iexact=self.exact)
        if self.starts_with:
            q_obj &= Q(code__istartswith=self.starts_with)
        if self.ends_with:
            q_obj &= Q(code__iendswith=self.ends_with)
        if self.contains:
            q_obj &= Q(code__icontains=self.contains)
        return q_obj
    icd9_q_obj = property(__get_icd9_q_obj)
    
    def __get_encounters(self):
        codes = Icd9.objects.filter(self.icd9_q_obj)
        return Encounter.objects.filter(icd9_codes__in=codes)
    encounters = property(__get_encounters)

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
        sn = 'diagnosis:%s' % self.name
        return sn
    
    uri = 'urn:x-esphealth:heuristic:channing:diagnosis:v1'
    
    # Only this version of HEF is supported
    core_uris = [HEF_CORE_URI]
    
    def __str__(self):
        return self.uri
    
    @property
    def encounters(self):
        encs = Encounter.objects.none()
        for icd9_query in self.icd9_queries:
            encs |= icd9_query.encounters
        log_query('Encounters for %s' % self, encs)
        return encs
    
    @property
    def icd9_q_obj(self):
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
    
    event_names = [dx_event_name]
    
    def generate(self):
        icd9s = Icd9.objects.filter(self.icd9_q_obj)
        enc_qs = Encounter.objects.filter(icd9_codes__in=icd9s)
        enc_qs = enc_qs.exclude(tags__event_name__in=self.event_names)
        log_query('Encounters for %s' % self, enc_qs)
        log.info('Generating events for "%s"' % self)
        for enc in queryset_iterator(enc_qs):
            new_event = Event(
                name = self.dx_event_name,
                source = self.uri,
                patient = enc.patient,
                date = enc.date,
                provider = enc.provider,
                )
            new_event.save()
            new_event.tag(enc)
            log.debug('Saved new event: %s' % new_event)
        log.info('Generated %s new events for %s' % (enc_qs.count(), self))
        return enc_qs.count()


class CalculatedBilirubinHeuristic(object):
    '''
    A heuristic to detect high calculated 
    '''
    #
    # Write me!
    #


