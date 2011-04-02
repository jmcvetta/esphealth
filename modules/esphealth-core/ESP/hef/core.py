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
HEF_CORE_URI = 'https://esphealth.org/reference/hef/core/1.0'
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


import abc
import re
import math

from pkg_resources import iter_entry_points

from django.db.models import Q
from django.db.models import F
from django.utils.encoding import force_unicode
from django.utils.encoding import smart_str

from ESP.utils import log
from ESP.utils import log_query
from ESP.utils.utils import queryset_iterator
from ESP.static.models import Icd9
from ESP.conf.models import LabTestMap
from ESP.emr.models import Encounter
from ESP.emr.models import LabResult
from ESP.emr.models import LabOrder
from ESP.hef.models import Event


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

GT_CHOICES = [
    ('gte', 'Greater Than or Equal To: >='),
    ('gt', 'Greater Than: >'),
    ]

LT_CHOICES = [
    ('lte', 'Less Than or Equal To: <='),
    ('lt', 'Less Than: <'),
    ]

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



class EventType(object):
    '''
    A distinct type of medical event
    '''
    
    def __init__(self, name, uri):
        assert name
        assert uri
        self.__name = name
        self.__uri = uri
    
    def __get_name(self):
        '''
        Common English name for this kind of event
        '''
        return self.__name
    name = property(__get_name)
    
    def __get_uri(self):
        '''
        URI which uniquely describes this kind of event
        '''
        return self.__uri
    uri = property(__get_uri)
    
    def create_event(self, patient, provider, date, heuristic_uri):
        '''
        Creates an event of this type
        @param patient: Patient to whom this event relates
        @type patient:  ESP.emr.models.Patient
        @param provider: Medical service provider for this event
        @type provider:  ESP.emr.models.Provider
        @param date: Date of this event
        @type date:  datetime.date
        @param heuristic_uri: URI for the heuristic that created this event
        @type heuristic_uri:  String
        '''
        new_event = Event(
            name = self.name,
            uri = self.uri,
            heuristic_uri = heuristic_uri,
            patient = patient,
            provider = provider,
            date = date, 
            )
        new_event.save()
        log.debug('Created new event: %s' % new_event)
        return new_event


class BaseHeuristic(object):
    '''
    A heuristic for generating Events from raw medical records
    (Abstract base class)
    '''
    
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractproperty
    def name(self):
        '''
        Common English name for this heuristic
        '''
    
    @abc.abstractproperty
    def uri(self):
        '''
        URI which uniquely describes this heuristic, including its version
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
        heuristics.sort(key = lambda h: h.name)
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
        heuristics.sort(key = lambda h: h.name)
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
        heuristics.sort(key = lambda h: h.name)
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
    def uri(self):
        return 'urn:x-esphealth:heuristic:laborder:%s' % self.test_name
    
    @property
    def order_event_name(self):
        return u'%s:order' % self.test_name
    
    @property
    def event_names(self):
        return [self.order_event_name]
    
    def generate(self):
        log.info('Generating events for %s' % self)
        alt = AbstractLabTest(self.test_name)
        unbound_orders = alt.lab_orders.exclude(tags__event_name=self.order_event_name)
        log_query('Unbound lab orders for %s' % self.name, unbound_orders)
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
        log.info('Generated %s new %s events' % (unbound_count, self.name))
        return unbound_count


class LabResultAnyHeuristic(BaseEventHeuristic): 
    '''
    A heuristic for generating events on ANY result from specified lab test
    '''
    
    def __init__(self, test_name, date_field='order'):
        assert test_name
        assert date_field in ['order', 'result']
        self.test_name = test_name
        self.date_field = date_field
    
    @property
    def uri(self):
        return 'urn:x-esphealth:heuristic:labresult:%s:any-result' % self.test_name
    
    @property
    def any_result_event_name(self):
        # Order date is default
        if self.date_field == 'order':
            return u'%s:any-result' % (self.test_name, self.date_field)
        else:
            return u'%s:any-result:%s-date' % (self.test_name, self.date_field)
    
    @property
    def event_names(self):
        return [self.any_result_event_name]
    
    def generate(self):
        log.debug('Generating events for "%s"' % self)
        alt = AbstractLabTest(self.test_name)
        unbound_results = alt.lab_results.exclude(tags__event_name=self.any_result_event_name)
        log_query('Unbound lab results for %s' % self, unbound_results)
        unbound_count = unbound_results.count()
        for lab in queryset_iterator(unbound_results):
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
        log.info('Generated %s new %s events' % (unbound_count, self.name))
        return unbound_count


class LabResultPositiveHeuristic(BaseEventHeuristic): 
    '''
    A heuristic for detecting positive (& negative) lab result events
    '''
    
    def __init__(self, test_name, date_field='order', titer=None):
        assert test_name
        self.test_name = test_name
        self.date_field = date_field
        self.titer = titer
    
    @property
    def uri(self):
        uri = 'urn:x-esphealth:heuristic:labresult:%s:positive' % self.test_name
        if not self.date_field == 'order':
            uri += ':%s-date' % self.date_field
        if self.titer:
            uri += ':titer:%s' % self.titer
        return uri
    
    @property
    def positive_event_name(self):
        # Order date is default
        if self.date_field == 'order':
            return u'%s:positive' % (self.test_name, self.date_field)
        else:
            return u'%s:positive:%s-date' % (self.test_name, self.date_field)
    
    @property
    def negative_event_name(self):
        # Order date is default
        if self.date_field == 'order':
            return u'%s:negative' % (self.test_name, self.date_field)
        else:
            return u'%s:negative:%s-date' % (self.test_name, self.date_field)
    
    @property
    def indeterminate_event_name(self):
        # Order date is default
        if self.date_field == 'order':
            return u'%s:indeterminate' % (self.test_name, self.date_field)
        else:
            return u'%s:indeterminate:%s-date' % (self.test_name, self.date_field)
    
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
        log.debug('Generating events for "%s"' % self.verbose_name)
        alt = AbstractLabTest(self.test_name)
        unbound_labs = alt.lab_results.exclude(tags__event_name__in=self.event_names)
        log_query('Unbound lab results for %s' % self.name, unbound_labs)
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
        for map in LabTestMap.objects.filter(test=self.test):
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
        if self.titer:
            positive_titer_strings = ['1:%s' % 2**i for i in range(math.log(self.titer, 2), math.log(4096,2))]
            negative_titer_strings = ['1:%s' % 2**i for i in range(math.log(self.titer, 2))]
            log.debug('positive_titer_strings: %s' % positive_titer_strings)
            log.debug('negative_titer_strings: %s' % negative_titer_strings)
            for s in positive_titer_strings:
                positive_q |= Q(result_string__istartswith=s)
            for s in negative_titer_strings:
                negative_q |= Q(result_string__istartswith=s)
        #
        # Generate Events
        #
        positive_labs = unbound_labs.filter(positive_q)
        log_query('Positive labs for %s' % self.name, positive_labs)
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
        log.info('Generated %s new positive events for %s' % (positive_labs.count(), self.name))
        negative_labs = unbound_labs.filter(negative_q)
        log_query('Negative labs for %s' % self.name, negative_labs)
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
        log.info('Generated %s new negative events for %s' % (negative_labs.count(), self.name))
        indeterminate_labs = unbound_labs.filter(indeterminate_q)
        log_query('Indeterminate labs for %s' % self.name, indeterminate_labs)
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
        log.info('Generated %s new indeterminate events for %s' % (indeterminate_labs.count(), self.name))
        return positive_labs.count() + negative_labs.count() + indeterminate_labs.count()


class LabResultRatioHeuristic(LabResultHeuristicBase):
    '''
    A heuristic for detecting ratio-based positive lab result events
    '''
    ratio = models.FloatField(blank=False)
    
    class Meta:
        verbose_name = 'Heuristic - Lab - Ratio'
        verbose_name_plural = 'Heuristic - Lab - Ratio'
        unique_together = ['test', 'ratio']
        ordering = ['test']
        unique_together = ['test', 'ratio']
    
    def __get_name(self):
        # explicit cast to float to work around django FloatField pre/post save quirk
        return  u'lx--%s--ratio--%s' % (self.test.name, float(self.ratio))
    name = property(__get_name)
    
    def __get_verbose_name(self):
        return 'Heuristic - Lab - Ratio - %s' % self.test.name
    verbose_name = property(__get_verbose_name)
    
    def __unicode__(self):
        return u'%s' % self.verbose_name
    
    def save(self, *args, **kwargs):
        super(LabResultRatioHeuristic, self).save(*args, **kwargs) # Call the "real" save() method.
        obj, created = EventType.objects.get_or_create(
            name = self.name,
            heuristic = self,
            )
        if created:
            log.debug('Added %s for %s' % (obj, self))
    
    def generate_events(self):
        unbound_labs = self.test.lab_results.exclude(tags__event__event_type__heuristic=self)
        log_query('Unbound lab results for %s' % self.name, unbound_labs)
        positive_labs = LabResult.objects.none()
        code_maps = LabTestMap.objects.filter(test=self.test)
        for map in code_maps:
            labs = unbound_labs.filter(map.lab_results_q_obj)
            #
            # Build numeric comparison queries
            #
            num_res_labs = labs.filter(result_float__isnull=False)
            positive_labs |= num_res_labs.filter(ref_high_float__isnull=False, result_float__gte = (self.ratio * F('ref_high_float')))
            if map.threshold:
                positive_labs |= num_res_labs.filter(ref_high_float__isnull=True, result_float__gte = (self.ratio * map.threshold))
        log_query(self.name, positive_labs)
        log.info('Generating new events for %s' % self.name)
        event_type = EventType.objects.get(name=self.name)
        for lab in queryset_iterator(positive_labs):
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            new_event = Event(
                event_type = event_type,
                patient = lab.patient,
                date = lab_date,
                provider = lab.provider,
                )
            new_event.save()
            new_event.tag(lab)
            log.debug('Saved new event: %s' % new_event)
        log.info('Generated %s new events for %s' % (positive_labs.count(), self.name))
        return positive_labs.count()


class LabResultFixedThresholdHeuristic(LabResultHeuristicBase):
    '''
    A heuristic for detecting fixed-threshold-based positive lab result events
    '''
    threshold = models.FloatField(blank=False, 
        help_text='Events are generated for lab results greater than or equal to this value')
    
    class Meta:
        verbose_name = 'Heuristic - Lab - Fixed Threshold'
        verbose_name_plural = verbose_name
        ordering = ['test']
        unique_together = ['test', 'threshold']
    
    def __get_name(self):
        return  u'lx--%s--threshold--%s' % (self.test.name, float(self.threshold))
    name = property(__get_name)
    
    def __get_verbose_name(self):
        return 'Heuristic - Lab - Fixed Threshold - %s - %s' % (self.test.name, self.threshold)
    verbose_name = property(__get_verbose_name)
    
    def __unicode__(self):
        return u'%s' % self.verbose_name
    
    def save(self, *args, **kwargs):
        super(LabResultFixedThresholdHeuristic, self).save(*args, **kwargs) # Call the "real" save() method.
        obj, created = EventType.objects.get_or_create(
            name = self.name,
            heuristic = self,
            )
        if created:
            log.debug('Added %s for %s' % (obj, self))
    
    def generate_events(self):
        unbound_labs = self.test.lab_results.exclude(tags__event__event_type__heuristic=self)
        log_query('Unbound lab results for %s' % self.name, unbound_labs)
        positive_labs = unbound_labs.filter(result_float__isnull=False, result_float__gte=self.threshold)
        log_query(self.name, positive_labs)
        log.info('Generating events for "%s"' % self.name)
        event_type = EventType.objects.get(name=self.name)
        for lab in queryset_iterator(positive_labs):
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            new_event = Event(
                event_type = event_type,
                patient = lab.patient,
                date = lab_date,
                provider = lab.provider,
                )
            new_event.save()
            new_event.tag(lab)
            log.debug('Saved new event: %s' % new_event)
        log.info('Generated %s new events for %s' % (positive_labs.count(), self.name))
        return positive_labs.count() 


class LabResultRangeHeuristic(LabResultHeuristicBase):
    '''
    A heuristic for detecting lab results falling within a certain fixed range
    '''
    minimum = models.FloatField(blank=False)
    minimum_match_type = models.CharField(max_length=3, choices=GT_CHOICES)
    maximum = models.FloatField(blank=False)
    maximum_match_type = models.CharField(max_length=3, choices=LT_CHOICES)
    
    
    class Meta:
        verbose_name = 'Heuristic - Lab - Range'
        verbose_name_plural = verbose_name
        ordering = ['test']
        unique_together = ['test', 'minimum', 'maximum']
    
    def __get_name(self):
        return  u'lx--%s--range--%s-%s' % (self.test.name, float(self.minimum), float(self.maximum))
    name = property(__get_name)
    
    def __get_verbose_name(self):
        return 'Heuristic - Lab - Range - %s - %s <> %s' % (self.test.name, self.minimum, self.maximum)
    verbose_name = property(__get_verbose_name)
    
    def __unicode__(self):
        return u'%s' % self.verbose_name
    
    def save(self, *args, **kwargs):
        super(LabResultRangeHeuristic, self).save(*args, **kwargs) # Call the "real" save() method.
        obj, created = EventType.objects.get_or_create(
            name = self.name,
            heuristic = self,
            )
        if created:
            log.debug('Added %s for %s' % (obj, self))
    
    def generate_events(self):
        qs = self.test.lab_results.filter(
            result_float__isnull=False, 
            )
        if self.minimum_match_type == 'gte':
            qs = qs.filter(result_float__gte=self.minimum)
        elif self.minimum_match_type == 'gt':
            qs = qs.filter(result_float__gt=self.minimum)
        if self.maximum_match_type == 'lte':
            qs = qs.filter(result_float__lte=self.maximum)
        elif self.maximum_match_type == 'lt':
            qs = qs.filter(result_float__lt=self.maximum)
        qs = qs.exclude(tags__event__event_type__heuristic=self)
        log_query(self.name, qs)
        log.info('Generating events for "%s"' % self.name)
        event_type = EventType.objects.get(name=self.name)
        for lab in queryset_iterator(qs):
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            new_event = Event(
                event_type = event_type,
                patient = lab.patient,
                date = lab_date,
                provider = lab.provider,
                )
            new_event.save()
            new_event.tag(lab)
            log.debug('Saved new event: %s' % new_event)
        log.info('Generated %s new events for %s' % (qs.count(), self.name))
        return qs.count() 


class LabResultWesternBlotHeuristic(LabResultHeuristicBase):
    '''
    Generates events from western blot test results.
    http://en.wikipedia.org/wiki/Western_blot
    '''
    bands = models.CharField('Interesting Bands', max_length=256, blank=False, 
        help_text='Comma-separated list of interesting bands for this western blot')
    
    # Making this model unique on test means we assume there is only one way 
    # to interpret a western blot test -- however, I do not actually know that 
    # this is true.
    class Meta:
        verbose_name = 'Heuristic - Lab - Western Blot'
        verbose_name_plural = 'Heuristic - Lab - Western Blot'
        unique_together = ['test', ]
        ordering = ['test']
    
    def __get_name(self):
        return  u'lx--%s--western_blot' % self.test.name
    name = property(__get_name)
    
    def __get_verbose_name(self):
        return 'Heuristic - Lab -  Western Blot - %s' % self.test.name
    verbose_name = property(__get_verbose_name)
    
    def __unicode__(self):
        return u'%s' % self.verbose_name
    
    def save(self, *args, **kwargs):
        super(LabResultWesternBlotHeuristic, self).save(*args, **kwargs) # Call the "real" save() method.
        event_name_list = [
            '%s--positive' % self.name,
            '%s--negative' % self.name,
            ]
        for event_name in event_name_list:
            obj, created = EventType.objects.get_or_create(
                name = event_name,
                heuristic = self,
                )
            if created:
                log.debug('Added %s for %s' % (obj, self))
   
    def __get_band_list(self):
        return [i.strip() for i in self.bands.split(',')]
    band_list = property(__get_band_list)

    def generate_events(self):
        log.debug('Generating events for "%s"' % self.verbose_name)
        unbound_labs = self.test.lab_results.exclude(tags__event__event_type__heuristic=self)
        log_query('Unbound lab results for %s' % self.name, unbound_labs)
        # Find potential positives -- tests whose results contain at least one 
        # of the interesting band numbers.
        q_obj = Q(result_string__icontains = self.band_list[0])
        for band in self.band_list[1:]:
            q_obj = q_obj | Q(result_string__icontains = band)
        potential_positives = unbound_labs.filter(q_obj)
        negatives = unbound_labs.exclude(potential_positives)
        neg_event_type = EventType.objects.get(name='%s--negative' % self.name)
        for lab in queryset_iterator(negatives):
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            new_event = Event(
                event_type = neg_event_type,
                patient = lab.patient,
                date = lab_date,
                provider = lab.provider,
                )
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
        qs = LabResult.objects.filter(pk__in = match_pks)
        return qs


class Dose(models.Model):
    '''
    A measurement of dose for a prescription
    '''
    quantity = models.FloatField(blank=False)
    units = models.CharField(max_length=8, blank=False, choices=DOSE_UNIT_CHOICES)
    
    class Meta:
        unique_together = ['quantity', 'units']
        ordering = ['units', 'quantity']
    
    def __unicode__(self):
        return u'%s %s' % (self.quantity, self.units)
    
    def __get_string_variants(self):
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
    string_variants = property(__get_string_variants)
        


class PrescriptionHeuristic(Heuristic):
    '''
    A heuristic for detecting prescription events
    '''
    name = models.SlugField(blank=False, unique=True)
    drugs = models.CharField(max_length=256, blank=False, help_text='Drug names, separated by commas.')
    dose = models.ManyToManyField(Dose, blank=True, null=True)
    min_quantity = models.IntegerField(blank=True, null=True, default=None)
    require = models.CharField(max_length=128, blank=True, null=True, 
        help_text='Prescription must include one or more of these strings.  Separate strings with commas.')
    exclude = models.CharField(max_length=128, blank=True, null=True, 
        help_text='Prescription may not include any of these strings.  Separate strings with commas.')
    
    class Meta:
        verbose_name = 'Heuristic - Prescription'
        verbose_name_plural = 'Heuristic - Prescription'
        ordering = ['name']
        
    def __unicode__(self):
        return u'%s' % self.verbose_name
    
    def __get_verbose_name(self):
        return 'Heuristic - Prescription - %s' % self.name
    verbose_name = property(__get_verbose_name)
    
    def save(self, *args, **kwargs):
        super(PrescriptionHeuristic, self).save(*args, **kwargs) # Call the "real" save() method.
        obj, created = EventType.objects.get_or_create(
            name = 'rx--%s' % self.name,
            heuristic = self,
            )
        if created:
            log.debug('Added %s for %s' % (obj, self))
    
    def generate_events(self):
        drugs = [s.strip() for s in self.drugs.split(',')]
        if self.require:
            require = [s.strip() for s in self.require.split(',')]
        else:
            require = []
        if self.exclude:
            exclude = [s.strip() for s in self.exclude.split(',')]
        else:
            exclude = []
        prescriptions = Prescription.objects.none()
        for drug_name in drugs:
            prescriptions |= Prescription.objects.filter(name__icontains=drug_name)
        if self.dose.all():
            rxs_by_dose = Prescription.objects.none()
            for dose_obj in self.dose.all():
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
        prescriptions = prescriptions.exclude(tags__event__event_type__heuristic=self)
        log_query('Prescriptions for %s' % self.name, prescriptions)
        log.info('Generating events for "%s"' % self.verbose_name)
        event_type = EventType.objects.get(name='rx--%s' % self.name)
        for rx in queryset_iterator(prescriptions):
            new_event = Event(
                event_type = event_type,
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
    
    def __init__(self, exact, starts_with, ends_with, contains):
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
    
    def __get_verbose_name(self):
        return 'ICD9 Query: %s | %s | %s | %s' % (self.exact, self.starts_with, self.ends_with, self.contains),
    verbose_name = property(__get_verbose_name)


class DiagnosisHeuristic(BaseEventHeuristic):
    '''
    A heuristic for detecting events based on one or more ICD9 diagnosis codes
    from a physician encounter.
    '''

    def __get_encounters(self):
        encs = Encounter.objects.none()
        for icd9_query in self.icd9query_set.all():
            encs |= icd9_query.encounters
        log_query('Encounters for %s' % self, encs)
        return encs
    encounters = property(__get_encounters)
    
    def __get_icd9_q_obj(self):
        q_obj = self.icd9query_set.all()[0].icd9_q_obj
        for icd9_query in self.icd9query_set.all()[1:]:
            q_obj |= icd9_query.icd9_q_obj
        return q_obj
    icd9_q_obj = property(__get_icd9_q_obj)
    
    def generate(self):
        icd9s = Icd9.objects.filter(self.icd9_q_obj)
        encounters = Encounter.objects.filter(icd9_codes__in=icd9s)
        encounters = encounters.exclude(tags__event__event_type__heuristic=self)
        log_query('Encounters for %s' % self.name, encounters)
        log.info('Generating events for "%s"' % self.verbose_name)
        event_type = EventType.objects.get(name='dx--%s' % self.name)
        for enc in queryset_iterator(encounters):
            new_event = Event(
                name = self.name,
                uri = self.uri,
                patient = enc.patient,
                date = enc.date,
                provider = enc.provider,
                )
            new_event.save()
            new_event.tag(enc)
            log.debug('Saved new event: %s' % new_event)
        log.info('Generated %s new events for %s' % (encounters.count(), self.name))
        return encounters.count()


class CalculatedBilirubinHeuristic(Heuristic):
    '''
    A heuristic to detect high calculated 
    '''
    #
    # Write me!
    #


