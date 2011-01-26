'''
                              ESP Health Project
                          Heuristic Events Framework
                                  Data Models

@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@contact: http://esphealth.org
@copyright: (c) 2009-2010 Channing Laboratory
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''

import math
import pprint

from django.db import models
from django.db.models import Q
from django.db.models import F
from django.db.models import Sum
from django.db.models import Min
from django.db.models import Max
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from ESP.utils import log
from ESP.utils import log_query
from ESP.utils.utils import queryset_iterator
from ESP.emr.models import Patient
from ESP.emr.models import Provider
from ESP.emr.models import Encounter
from ESP.emr.models import Icd9
from ESP.emr.models import LabResult
from ESP.emr.models import LabOrder
from ESP.emr.models import Prescription


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


class AbstractLabTest(models.Model):
    '''
    Represents an abstract type of lab test
    '''
    name = models.SlugField(primary_key=True)
    verbose_name = models.CharField(max_length=128, blank=False, unique=True, db_index=True)
    #
    # Reporting
    # 
    reportable = models.BooleanField('Is test reportable?', default=True, db_index=True)
    output_code = models.CharField('Test code for template output', max_length=100, blank=True, null=True, db_index=True)
    output_name = models.CharField('Test name for template output', max_length=255, blank=True, null=True)
    snomed_pos = models.CharField('SNOMED positive code', max_length=255, blank=True, null=True)
    snomed_neg = models.CharField('SNOMED neg code', max_length=255, blank=True, null=True)
    snomed_ind = models.CharField('SNOMED indeterminate code', max_length=255, blank=True, null=True)
    #
    notes = models.TextField(blank=True, null=True)
    class Meta:
        verbose_name = 'Abstract Lab Test'
        ordering = ['name']
    
    def __unicode__(self):
        return u'Abstract Lab Test - %s - %s' % (self.name, self.verbose_name)
    
    def __get_lab_results(self):
        result = LabResult.objects.none()
        for cm in self.labtestmap_set.filter( Q(record_type='result') | Q(record_type='both') ):
            result |= LabResult.objects.filter(cm.lab_results_q_obj)
        return result
    lab_results = property(__get_lab_results)
    
    def __get_lab_orders(self):
        result = LabOrder.objects.none()
        for cm in self.labtestmap_set.filter( Q(record_type='order') | Q(record_type='both') ):
            result |= LabOrder.objects.filter(cm.lab_orders_q_obj)
        log_query('Lab Orders for %s' % self.name, result)
        return result
    lab_orders = property(__get_lab_orders)
    
    def __get_heuristic_set(self):
        heuristic_set = set(self.laborderheuristic_set.all())
        heuristic_set |= set(self.labresultanyheuristic_set.all())
        heuristic_set |= set(self.labresultpositiveheuristic_set.all())
        heuristic_set |= set(self.labresultratioheuristic_set.all())
        heuristic_set |= set(self.labresultrangeheuristic_set.all())
        heuristic_set |= set(self.labresultfixedthresholdheuristic_set.all())
        return heuristic_set
    heuristic_set = property(__get_heuristic_set)

    def generate_events(self):
        count = 0
        log.info('Generating events for %s' % self)
        for heuristic in self.heuristic_set:
            count += heuristic.generate_events()
        return count


class ResultString(models.Model):
    '''
    A string indicating a positive, negative, or indeterminate lab result
    '''
    value = models.CharField(max_length=128, blank=False)
    indicates = models.CharField(max_length=8, blank=False, choices=POS_NEG_IND)
    match_type = models.CharField(max_length=32, blank=False, choices=MATCH_TYPE_CHOICES, 
        help_text='Match type for string', default='istartswith')
    applies_to_all = models.BooleanField(blank=False, default=False, 
        help_text='Match this string for ALL tests.  If not checked, string must be explicitly specified in Lab Test Map')
    
    class Meta:
        ordering = ['value']
        verbose_name = 'Result String'
    
    def __get_q_obj(self):
        '''
        Returns a Q object to search for this result string
        '''
        if self.match_type == 'exact':
            return Q(result_string__exact=self.value)
        elif self.match_type == 'iexact':
            return Q(result_string__iexact=self.value)
        elif self.match_type == 'startswith':
            return Q(result_string__startswith=self.value)
        elif self.match_type == 'istartswith':
            return Q(result_string__istartswith=self.value)
        elif self.match_type == 'endswith':
            return Q(result_string__endswith=self.value)
        elif self.match_type == 'iendswith':
            return Q(result_string__iendswith=self.value)
        elif self.match_type == 'contains':
            return Q(result_string__contains=self.value)
        elif self.match_type == 'icontains':
            return Q(result_string__icontains=self.value)
    q_obj = property(__get_q_obj)


class LabTestMap(models.Model):
    '''
    Mapping object to associate an abstract lab test type with a concrete, 
    source-EMR-specific lab test type
    '''
    test = models.ForeignKey(AbstractLabTest, blank=False)
    native_code = models.CharField(max_length=100, verbose_name='Test Code', db_index=True,
        help_text='Native test code from source EMR system', blank=False)
    code_match_type = models.CharField(max_length=32, blank=False, choices=MATCH_TYPE_CHOICES, 
        help_text='Match type for test code', default='exact')
    record_type = models.CharField(max_length=8, blank=False, choices=ORDER_RESULT_RECORD_TYPES, 
        help_text='Does this map relate to lab orders, results, or both?', default='both')
    threshold = models.FloatField(help_text='Fallback positive threshold for tests without reference high', blank=True, null=True)
    extra_positive_strings = models.ManyToManyField(ResultString, blank=True, null=True, related_name='extra_positive_set',
        limit_choices_to={'indicates': 'pos', 'applies_to_all': False})
    excluded_positive_strings = models.ManyToManyField(ResultString, blank=True, null=True, related_name='excluded_positive_set',
        limit_choices_to={'indicates': 'pos', 'applies_to_all': True})
    extra_negative_strings = models.ManyToManyField(ResultString, blank=True, null=True, related_name='extra_negative_set',
        limit_choices_to={'indicates': 'neg', 'applies_to_all': False})
    excluded_negative_strings = models.ManyToManyField(ResultString, blank=True, null=True, related_name='excluded_negative_set',
        limit_choices_to={'indicates': 'neg', 'applies_to_all': True})
    extra_indeterminate_strings = models.ManyToManyField(ResultString, blank=True, null=True, related_name='extra_indeterminate_set',
        limit_choices_to={'indicates': 'ind', 'applies_to_all': False})
    excluded_indeterminate_strings = models.ManyToManyField(ResultString, blank=True, null=True, related_name='excluded_indeterminate_set',
        limit_choices_to={'indicates': 'ind', 'applies_to_all': True})
    #
    # Reporting
    # 
    reportable = models.BooleanField('Is test reportable?', default=True, db_index=True)
    output_code = models.CharField('Test code for template output', max_length=100, blank=True, null=True)
    output_name = models.CharField('Test name for template output', max_length=255, blank=True, null=True)
    snomed_pos = models.CharField('SNOMED positive code', max_length=255, blank=True, null=True)
    snomed_neg = models.CharField('SNOMED neg code', max_length=255, blank=True, null=True)
    snomed_ind = models.CharField('SNOMED indeterminate code', max_length=255, blank=True, null=True)
    #
    # Notes
    #
    notes = models.TextField(blank=True, null=True)
    class Meta:
        verbose_name = 'Lab Test Map'
        unique_together = ['test', 'native_code']
    
    def __get_lab_results_q_obj(self):
        if self.code_match_type == 'exact':
            return Q(native_code__exact=self.native_code)
        elif self.code_match_type == 'iexact':
            return Q(native_code__iexact=self.native_code)
        elif self.code_match_type == 'startswith':
            return Q(native_code__startswith=self.native_code)
        elif self.code_match_type == 'istartswith':
            return Q(native_code__istartswith=self.native_code)
        elif self.code_match_type == 'endswith':
            return Q(native_code__endswith=self.native_code)
        elif self.code_match_type == 'iendswith':
            return Q(native_code__iendswith=self.native_code)
        elif self.code_match_type == 'contains':
            return Q(native_code__contains=self.native_code)
        elif self.code_match_type == 'icontains':
            return Q(native_code__icontains=self.native_code)
    lab_results_q_obj = property(__get_lab_results_q_obj)
    
    def __get_lab_orders_q_obj(self):
        #
        # 'procedure_master_num' is a crappy field name, and needs to be changed
        if self.code_match_type == 'exact':
            return Q(procedure_master_num__exact=self.native_code)
        elif self.code_match_type == 'iexact':
            return Q(procedure_master_num__iexact=self.native_code)
        elif self.code_match_type == 'startswith':
            return Q(procedure_master_num__startswith=self.native_code)
        elif self.code_match_type == 'istartswith':
            return Q(procedure_master_num__istartswith=self.native_code)
        elif self.code_match_type == 'endswith':
            return Q(procedure_master_num__endswith=self.native_code)
        elif self.code_match_type == 'iendswith':
            return Q(procedure_master_num__iendswith=self.native_code)
        elif self.code_match_type == 'contains':
            return Q(procedure_master_num__contains=self.native_code)
        elif self.code_match_type == 'icontains':
            return Q(procedure_master_num__icontains=self.native_code)
    lab_orders_q_obj = property(__get_lab_orders_q_obj)
    
    def __get_positive_string_q_obj(self):
        # Build pos q for this lab test based on q_obj for each result string object
        pos_rs = ResultString.objects.filter(indicates='pos', applies_to_all=True)
        pos_rs |= self.extra_positive_strings.all()
        if self.excluded_positive_strings.all():
            pos_rs = pos_rs.exclude(self.excluded_positive_strings.all())
        q_obj = pos_rs[0].q_obj
        for rs in pos_rs[1:]:
            q_obj |= rs.q_obj
        return q_obj
    positive_string_q_obj = property(__get_positive_string_q_obj)
    
    def __get_negative_string_q_obj(self):
        neg_rs = ResultString.objects.filter(indicates='neg', applies_to_all=True)
        neg_rs |= self.extra_negative_strings.all()
        if self.excluded_negative_strings.all():
            neg_rs = neg_rs.exclude(self.excluded_negative_strings.all())
        q_obj = neg_rs[0].q_obj
        for rs in neg_rs[1:]:
            q_obj |= rs.q_obj
        return q_obj
    negative_string_q_obj = property(__get_negative_string_q_obj)
    
    def __get_indeterminate_string_q_obj(self):
        rs_set = ResultString.objects.filter(indicates='ind', applies_to_all=True)
        rs_set |= self.extra_indeterminate_strings.all()
        if self.excluded_indeterminate_strings.all():
            rs_set = rs_set.exclude(self.excluded_indeterminate_strings.all())
        q_obj = rs_set[0].q_obj
        for rs in rs_set[1:]:
            q_obj |= rs.q_obj
        return q_obj
    indeterminate_string_q_obj = property(__get_indeterminate_string_q_obj)


class Heuristic(models.Model):
    '''
    Base model for heuristics
    '''
    notes = models.TextField(blank=True, null=True)
    
    def generate_events(self):
        raise NotImplementedError
    
    def __unicode__(self):
        return u'Heuristic # %s' % self.pk
    
    def _update_event_types(self):
        '''
        Save EventType objects that relate to this heuristic.
        '''
        # Noop for base Heuristic class.
        return
    
    #-------------------------------------------------------------------------------
    # Backwards Compatiblity w/ old HEF 
    #-------------------------------------------------------------------------------
    
    @classmethod
    def all_event_names(self):
        return EventType.objects.values_list('name', flat=True)

    
class LabHeuristicBase(Heuristic):
    '''
    Abstract base class for all lab heuristics
    '''
    test = models.ForeignKey(AbstractLabTest, blank=False)
    
    class Meta:
        abstract = True

    
class LabOrderHeuristic(LabHeuristicBase):
    '''
    A heuristic for detecting lab order events.
    
    Name is set programmatically for LabOrderHeuristic -- you do not need, and 
    in fact are not permitted, to set it manually

    Note that in some EMR systems (e.g. Atrius) lab orders may be less specific
    than lab results, and thus lab orders may require a different
    AbstractLabTest than required for lab results.
    '''
    
    class Meta:
        verbose_name = 'Heuristic - Lab - Order'
        verbose_name_plural = 'Heuristic - Lab - Order'
        unique_together = ['test']
    
    def __unicode__(self):
        return u'%s' % self.verbose_name
    
    def __get_name(self):
        return u'lx--%s--order' % self.test.name
    name = property(__get_name)
    
    def __get_verbose_name(self):
        return 'Heuristic - Lab - Order - %s' % self.test.name
    verbose_name = property(__get_verbose_name)
    
    def save(self, *args, **kwargs):
        super(LabOrderHeuristic, self).save(*args, **kwargs) # Call the "real" save() method.
        obj, created = EventType.objects.get_or_create(
            name = self.name,
            heuristic = self,
            )
        if created:
            log.debug('Added %s for %s' % (obj, self))
    
    def generate_events(self):
        log.info('Generating events for %s' % self)
        unbound_orders = self.test.lab_orders.exclude(tags__event__event_type__heuristic=self)
        log_query('Unbound lab orders for %s' % self.name, unbound_orders)
        unbound_count = unbound_orders.count()
        event_type = EventType.objects.get(name=self.name)
        for order in queryset_iterator(unbound_orders):
            e = Event(
                event_type = event_type,
                date = order.date,
                patient = order.patient,
                provider = order.provider,
                )
            e.save()
            e.tag_object(order)
            log.debug('Saved new event: %s' % e)
        log.info('Generated %s new %s events' % (unbound_count, self.name))
        return unbound_count


class LabResultHeuristicBase(LabHeuristicBase):
    '''
    Abstract base class for all lab heuristics
    '''
    date_field = models.CharField(max_length=32, blank=False, choices=DATE_FIELD_CHOICES, default='order')
    
    class Meta:
        abstract = True
    

class LabResultAnyHeuristic(LabResultHeuristicBase): 
    '''
    A heuristic for detecting positive (& negative) lab result events
    '''
    
    class Meta:
        verbose_name = 'Heuristic - Lab - Any Result'
        verbose_name_plural = 'Heuristic - Lab - Any Result'
        ordering = ['test']
        unique_together = ['test']
    
    def __get_name(self):
        return u'lx--%s--any_result' % self.test.name
    name = property(__get_name)
    
    def __get_verbose_name(self):
        return 'Heuristic - Lab - Any Result - %s' % self.test.name
    verbose_name = property(__get_verbose_name)
    
    def __unicode__(self):
        return self.verbose_name
    
    def save(self, *args, **kwargs):
        super(LabResultAnyHeuristic, self).save(*args, **kwargs) # Call the "real" save() method.
        obj, created = EventType.objects.get_or_create(
            name = self.name,
            heuristic = self,
            )
        if created:
            log.debug('Added %s for %s' % (obj, self))
    
    def generate_events(self):
        log.debug('Generating events for "%s"' % self)
        unbound_results = self.test.lab_results.exclude(tags__event__event_type__heuristic=self)
        log_query('Unbound lab results for %s' % self.name, unbound_results)
        unbound_count = unbound_results.count()
        event_type = EventType.objects.get(name=self.name)
        for lab in queryset_iterator(unbound_results):
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            e = Event(
                event_type = event_type,
                date = lab_date,
                patient = lab.patient,
                provider = lab.provider,
                )
            e.save()
            e.tag_object(lab)
            log.debug('Saved new event: %s' % e)
        log.info('Generated %s new %s events' % (unbound_count, self.name))
        return unbound_count


class LabResultPositiveHeuristic(LabResultHeuristicBase): 
    '''
    A heuristic for detecting positive (& negative) lab result events
    '''
    titer = models.IntegerField(blank=True, null=True, choices=TITER_DILUTION_CHOICES, default=None,
        help_text='Titer value indicating positive result.  Leave blank if titer result is not anticipated.')
    
    class Meta:
        verbose_name = 'Heuristic - Lab - Positive/Negative'
        verbose_name_plural = 'Heuristic - Lab - Positive/Negative'
        ordering = ['test']
        unique_together = ['test']
    
    def __get_name(self):
        return  u'lx--%s--positive' % self.test.name
    name = property(__get_name)
    
    def __get_verbose_name(self):
        return 'Heuristic - Lab - Positive/Negative - %s' % self.test.name
    verbose_name = property(__get_verbose_name)
    
    def __unicode__(self):
        return self.verbose_name
    
    def save(self, *args, **kwargs):
        super(LabResultPositiveHeuristic, self).save(*args, **kwargs) # Call the "real" save() method.
        event_name_list = [
            self.name, 
            'lx--%s--negative' % self.test.name,
            'lx--%s--indeterminate' % self.test.name,
            ]
        for event_name in event_name_list:
            obj, created = EventType.objects.get_or_create(
                name = event_name,
                heuristic = self,
                )
            if created:
                log.debug('Added %s for %s' % (obj, self))
    
    def generate_events(self):
        #
        # TODO:  The negative and indeterminate querysets should be generated 
        # *after* creating of preceding queries' events, so that labs bound to 
        # those events are ignored.  This will allow negative lab query to much
        # simpler.
        #
        log.debug('Generating events for "%s"' % self.verbose_name)
        unbound_labs = self.test.lab_results.exclude(tags__event__event_type__heuristic=self)
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
        pos_event_type = EventType.objects.get(name='lx--%s--positive' % self.test.name)
        for lab in queryset_iterator(positive_labs):
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            new_event = Event(
                event_type = pos_event_type,
                patient = lab.patient,
                date = lab_date,
                provider = lab.provider,
                )
            new_event.save()
            new_event.tag_object(lab)
            log.debug('Saved new event: %s' % new_event)
        log.info('Generated %s new positive events for %s' % (positive_labs.count(), self.name))
        negative_labs = unbound_labs.filter(negative_q)
        log_query('Negative labs for %s' % self.name, negative_labs)
        log.info('Generating negative events for %s' % self)
        neg_event_type = EventType.objects.get(name='lx--%s--negative' % self.test.name)
        for lab in queryset_iterator(negative_labs):
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
            new_event.save()
            new_event.tag_object(lab)
            log.debug('Saved new event: %s' % new_event)
        log.info('Generated %s new negative events for %s' % (negative_labs.count(), self.name))
        indeterminate_labs = unbound_labs.filter(indeterminate_q)
        log_query('Indeterminate labs for %s' % self.name, indeterminate_labs)
        log.info('Generating indeterminate events for %s' % self)
        ind_event_type = EventType.objects.get(name='lx--%s--indeterminate' % self.test.name)
        for lab in queryset_iterator(indeterminate_labs):
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            new_event = Event(
                event_type = ind_event_type,
                patient = lab.patient,
                date = lab_date,
                provider = lab.provider,
                )
            new_event.save()
            new_event.tag_object(lab)
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
            new_event.tag_object(lab)
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
            new_event.tag_object(lab)
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
            new_event.tag_object(lab)
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
            new_event.tag_object(rx)
            log.debug('Saved new event: %s' % new_event)
        return prescriptions.count()


class DiagnosisHeuristic(Heuristic):
    '''
    A heuristic for detecting events based on one or more ICD9 diagnosis codes
    from a physician encounter.  Formerly called EncounterHeuristic.
    '''
    name = models.SlugField(blank=False, unique=True)
    
    class Meta:
        verbose_name = 'Heuristic - Diagnosis'
        verbose_name_plural = 'Heuristic - Diagnosis'
        ordering = ['name']

    def __unicode__(self):
        return u'%s' % self.verbose_name
    
    def __get_verbose_name(self):
        return 'Heuristic - Diagnosis - %s' % self.name
    verbose_name = property(__get_verbose_name)
    
    def save(self, *args, **kwargs):
        super(DiagnosisHeuristic, self).save(*args, **kwargs) # Call the "real" save() method.
        obj, created = EventType.objects.get_or_create(
            name = 'dx--%s' % self.name,
            heuristic = self,
            )
        if created:
            log.debug('Added %s for %s' % (obj, self))
    
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
            
    
    def generate_events(self):
        icd9s = Icd9.objects.filter(self.icd9_q_obj)
        encounters = Encounter.objects.filter(icd9_codes__in=icd9s)
        encounters = encounters.exclude(tags__event__event_type__heuristic=self)
        log_query('Encounters for %s' % self.name, encounters)
        log.info('Generating events for "%s"' % self.verbose_name)
        event_type = EventType.objects.get(name='dx--%s' % self.name)
        for enc in queryset_iterator(encounters):
            new_event = Event(
                event_type = event_type,
                patient = enc.patient,
                date = enc.date,
                provider = enc.provider,
                )
            new_event.save()
            new_event.tag_object(enc)
            log.debug('Saved new event: %s' % new_event)
        log.info('Generated %s new events for %s' % (encounters.count(), self.name))
        return encounters.count()



class Icd9Query(models.Model):
    '''
    A query for selecting encounters based on ICD9 codes
    '''
    heuristic = models.ForeignKey(DiagnosisHeuristic, blank=False)
    # Let's hope we never need to deal with case-sensitive ICD9 codes.
    icd9_exact = models.CharField(max_length=128, blank=True, null=True,
        help_text='Encounter must include this exact ICD9 code')
    # We use "starts_with" instead of Django-style "startswith", to prevent 
    # people from thinking this field is case-sensistive, like a Django startswith
    # query would be.
    icd9_starts_with = models.CharField(max_length=128, blank=True, null=True,
        help_text='Encounter must include an ICD9 code starting with this string')
    icd9_ends_with = models.CharField(max_length=128, blank=True, null=True,
        help_text='Encounter must include an ICD9 code ending with this string')
    icd9_contains = models.CharField(max_length=128, blank=True, null=True,
        help_text='Encounter must include an ICD9 code containing this string')
    
    def __get_icd9_q_obj(self):
        '''
        Returns a Q object suitable for selecting ICD9 objects that match this query
        '''
        if not (self.icd9_exact or self.icd9_starts_with or self.icd9_ends_with or self.icd9_contains):
            log.error('%s does not contain any ICD9 search terms, and will not be processed.' % self)
            return
        q_obj = Q() # Null Q object
        if self.icd9_exact:
            q_obj &= Q(code__iexact=self.icd9_exact)
        if self.icd9_starts_with:
            q_obj &= Q(code__istartswith=self.icd9_starts_with)
        if self.icd9_ends_with:
            q_obj &= Q(code__iendswith=self.icd9_ends_with)
        if self.icd9_contains:
            q_obj &= Q(code__icontains=self.icd9_contains)
        return q_obj
    icd9_q_obj = property(__get_icd9_q_obj)
    
    def __get_encounters(self):
        codes = Icd9.objects.filter(self.icd9_q_obj)
        return Encounter.objects.filter(icd9_codes__in=codes)
    encounters = property(__get_encounters)

    class Meta:
        verbose_name = 'ICD9 Query'
        verbose_name_plural = 'ICD9 Queries'
        ordering = ['heuristic']
        unique_together = ['heuristic', 'icd9_exact', 'icd9_starts_with', 'icd9_ends_with', 'icd9_contains'],
    
    def __unicode__(self):
        return u'%s' % self.verbose_name
    
    def __get_verbose_name(self):
        return 'ICD9 Query: %s | %s | %s | %s | %s' % (self.heuristic.name, self.icd9_exact, self.icd9_starts_with, self.icd9_ends_with, self.icd9_contains),
    verbose_name = property(__get_verbose_name)
    

class CalculatedBilirubinHeuristic(Heuristic):
    '''
    A heuristic to detect high calculated 
    '''
    threshold = models.FloatField(blank=False, 
        help_text='Events are generated for calculated bilirubin levels greater than or equal to this value')
    
    def __get_name(self):
        return 'lx--bilirubin_calculated--threshold--%s' % self.threshold
    name = property(__get_name)
    
    def __get_verbose_name(self):
        return u'Heuristic - Calculated Bilirubin - Threshold - %s' % self.threshold
    verbose_name = property(__get_verbose_name)
    
    def __unicode__(self):
        return u'%s' % self.verbose_name
    
    def save(self, *args, **kwargs):
        super(CalculatedBilirubinHeuristic, self).save(*args, **kwargs) # Call the "real" save() method.
        obj, created = EventType.objects.get_or_create(
            name = self.name,
            heuristic = self,
            )
        if created:
            log.debug('Added %s for %s' % (obj, self))


class EventType(models.Model):
    '''
    A distinct, named type of medical event, associated with a the heuristic 
    which generated it.
    '''
    name = models.SlugField(max_length=128, primary_key=True)
    heuristic = models.ForeignKey(Heuristic, blank=False)
    
    def __unicode__(self):
        return u'Event Type %s' % self.name
    
    def __str__(self):
        return u'Event Type %s' % self.name


class Event(models.Model):
    '''
    A medical event
    '''
    event_type = models.ForeignKey(EventType, blank=True, null=True)
    date = models.DateField('Date event occured', blank=False, db_index=True)
    patient = models.ForeignKey(Patient, blank=False, db_index=True)
    provider = models.ForeignKey(Provider, blank=False, db_index=True)
    timestamp = models.DateTimeField('Time event was created in db', blank=False, auto_now_add=True)
    
    def __unicode__(self):
        return u'Event # %s (%s %s)' % (self.pk, self.event_type.name, self.date)
    
    def tag_object(self, obj):
        '''
        Tags a medical record with this event. 
        '''
        ert = EventRecordTag(
            event=self,
            content_object=obj,
            )
        ert.save()
        return ert


class EventRecordTag(models.Model):
    '''
    A tag associating an Event instance with a medical record
    '''
    event = models.ForeignKey(Event, blank=False, related_name='tag_set')
    #
    # Standard generic relation support
    #    http://docs.djangoproject.com/en/dev/ref/contrib/contenttypes/
    #
    content_type = models.ForeignKey(ContentType, db_index=True)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    def __unicode__(self):
        return u'%s --> %s' % (self.event, self.content_object)
    
    class Meta:
        unique_together = [('event', 'content_type', 'object_id')]
        

class Timespan(models.Model):
    '''
    A condition, such as pregnancy, which occurs over a defined span of time.  
    '''   
    name = models.SlugField(max_length=128, null=False, blank=False, db_index=True)
    patient = models.ForeignKey(Patient, blank=False)
    start_date = models.DateField(blank=False, db_index=True)
    end_date = models.DateField(blank=False, db_index=True)
    timestamp = models.DateTimeField('Time this event was created in db', blank=False, auto_now_add=True)
    pattern = models.SlugField(blank=False)
    # 
    # The 'encounters' field is a short-term hack for generating gdm pregnancy timespans, and should be 
    # replaced (soon) with a fully generic solution.
    #
    encounters = models.ManyToManyField(Encounter)

    def __unicode__(self):
        return u'Timespan #%s | %s | patient %s | %s - %s' % (self.pk, self.name, self.patient.name, self.start_date, self.end_date)
