'''
                              ESP Health Project
                          Heuristic Events Framework
                                  Data Models

@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
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
from ESP.emr.models import Patient
from ESP.emr.models import Encounter
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
        verbose_name = 'Abstract Lab Test Type'
        ordering = ['name']
    
    def __unicode__(self):
        return u'%s' % self.verbose_name
    
    def __get_lab_results(self):
        result = LabResult.objects.none()
        result_q = Q(record_type='result') | Q(record_type='both')
        for cm in self.labtestmap_set.filter(result_q):
            result = result | cm.lab_results
        log_query('Lab Results for %s' % self.name, result)
        return result
    lab_results = property(__get_lab_results)
    
    def __get_lab_orders(self):
        result = LabOrder.objects.none()
        order_q = Q(record_type='order') | Q(record_type='both')
        for cm in self.labtestmap_set.filter(order_q):
            result = result | cm.lab_orders
        log_query('Lab Orders for %s' % self.name, result)
        return result
    lab_orders = property(__get_lab_orders)
    
    def generate_events(self):
        count = 0
        log.info('Generating events for abstract test: %s' % self)
        heuristic_set = set(self.laborderheuristic_set.all())
        heuristic_set |= set(self.labresultpositiveheuristic_set.all())
        heuristic_set |= set(self.labresultratioheuristic_set.all())
        heuristic_set |= set(self.labresultfixedthresholdheuristic_set.all())
        for heuristic in heuristic_set:
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


class LabTestMap(models.Model):
    '''
    Mapping object to associate an abstract lab test type with a concrete, 
    source-EMR-specific lab test type
    '''
    test = models.ForeignKey(AbstractLabTest, blank=False)
    code = models.CharField(max_length=100, verbose_name='Test Code', db_index=True,
        help_text='Native test code from source EMR system', blank=False)
    code_match_type = models.CharField(max_length=32, blank=False, choices=MATCH_TYPE_CHOICES, 
        help_text='Match type for test code', default='exact')
    record_type = models.CharField(max_length=8, blank=False, choices=ORDER_RESULT_RECORD_TYPES, 
        help_text='Does this map relate to lab orders, results, or both?', default='both')
    threshold = models.FloatField(help_text='Fallback positive threshold for tests without reference high', blank=True, null=True)
    extra_positive_strings = models.ManyToManyField(ResultString, blank=True, null=True, related_name='positive_set',
        limit_choices_to={'indicates': 'pos', 'applies_to_all': False})
    extra_negative_strings = models.ManyToManyField(ResultString, blank=True, null=True, related_name='negative_set',
        limit_choices_to={'indicates': 'neg', 'applies_to_all': False})
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
        verbose_name = 'Lab Test Code Map'
        unique_together = ['test', 'code']
    
    def __get_lab_results(self):
        if self.code_match_type == 'exact':
            return LabResult.objects.filter(native_code__exact=self.code)
        elif self.code_match_type == 'iexact':
            return LabResult.objects.filter(native_code__iexact=self.code)
        elif self.code_match_type == 'startswith':
            return LabResult.objects.filter(native_code__startswith=self.code)
        elif self.code_match_type == 'istartswith':
            return LabResult.objects.filter(native_code__istartswith=self.code)
        elif self.code_match_type == 'endswith':
            return LabResult.objects.filter(native_code__endswith=self.code)
        elif self.code_match_type == 'iendswith':
            return LabResult.objects.filter(native_code__iendswith=self.code)
        elif self.code_match_type == 'contains':
            return LabResult.objects.filter(native_code__contains=self.code)
        elif self.code_match_type == 'icontains':
            return LabResult.objects.filter(native_code__icontains=self.code)
    lab_results = property(__get_lab_results)
    
    def __get_lab_orders(self):
        #
        # 'procedure_master_num' is a crappy field name, and needs to be changed
        if self.code_match_type == 'exact':
            return LabOrder.objects.filter(procedure_master_num__exact=self.code)
        elif self.code_match_type == 'iexact':
            return LabOrder.objects.filter(procedure_master_num__iexact=self.code)
        elif self.code_match_type == 'startswith':
            return LabOrder.objects.filter(procedure_master_num__startswith=self.code)
        elif self.code_match_type == 'istartswith':
            return LabOrder.objects.filter(procedure_master_num__istartswith=self.code)
        elif self.code_match_type == 'endswith':
            return LabOrder.objects.filter(procedure_master_num__endswith=self.code)
        elif self.code_match_type == 'iendswith':
            return LabOrder.objects.filter(procedure_master_num__iendswith=self.code)
        elif self.code_match_type == 'contains':
            return LabOrder.objects.filter(procedure_master_num__contains=self.code)
        elif self.code_match_type == 'icontains':
            return LabOrder.objects.filter(procedure_master_num__icontains=self.code)
    lab_orders = property(__get_lab_orders)
    


class Heuristic(models.Model):
    '''
    Abstract base class for Django-model-based heuristics, concrete 
    instances of which may be used as components of disease definitions.
    '''
    name = models.SlugField(blank=False, unique=True)
    
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

    

class LabOrderHeuristic(Heuristic):
    '''
    A heuristic for detecting lab order events.
    
    Name is set programmatically for LabOrderHeuristic -- you do not need, and 
    in fact are not permitted, to set it manually

    Note that in some EMR systems (e.g. Atrius) lab orders may be less specific
    than lab results, and thus lab orders may require a different
    AbstractLabTest than required for lab results.
    '''
    test = models.ForeignKey(AbstractLabTest, blank=False, unique=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Lab Order Heuristic'
    
    def __unicode__(self):
        return u'%s' % self.verbose_name
    
    def __get_verbose_name(self):
        return '%s Order Heuristic' % self.test.verbose_name
    verbose_name = property(__get_verbose_name)
    
    def save(self, *args, **kwargs):
        name = '%s--order' % self.test.name
        if self.name and not self.name == name:
            log.warning('You tried to name a heuristic "%s", but it was automatically named "%s" instead.' % (self.name, name))
        self.name = name
        super(LabOrderHeuristic, self).save(*args, **kwargs) # Call the "real" save() method.
        obj, created = EventType.objects.get_or_create(
            name = self.name,
            heuristic = self,
            )
        if created:
            log.debug('Added %s for %s' % (obj, self))
    
    def generate_events(self):
        log.debug('Generating events for "%s"' % self.verbose_name)
        unbound_orders = self.test.lab_orders.exclude(events__event_type__heuristic=self)
        log_query('Unbound lab orders for %s' % self.name, unbound_orders)
        unbound_count = unbound_orders.count()
        event_type = EventType.objects.get(name=self.name)
        for order in unbound_orders:
            e = Event(
                event_type = event_type,
                date = order.date,
                patient = order.patient,
                content_object = order,
                )
            e.save()
            log.debug('Saved new event: %s' % e)
        log.info('Generated %s new %s events' % (unbound_count, self.name))
        return unbound_count


class LabResultPositiveHeuristic(Heuristic):
    '''
    A heuristic for detecting positive (& negative) lab result events
    '''
    test = models.ForeignKey(AbstractLabTest, blank=False, unique=True)
    titer = models.IntegerField(blank=True, null=True, choices=TITER_DILUTION_CHOICES, default=None,
        help_text='Titer value indicating positive result.  Leave blank if titer result is not anticipated.')
    date_field = models.CharField(max_length=32, blank=False, choices=DATE_FIELD_CHOICES, default='order')
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Lab Result Heuristic - Pos/Neg/Ind'
        ordering = ['test']
    
    def __unicode__(self):
        return u'%s' % self.verbose_name
    
    def __get_verbose_name(self):
        return '%s Positive Heuristic' % self.test.verbose_name
    verbose_name = property(__get_verbose_name)
    
    def save(self, *args, **kwargs):
        name = '%s--positive' % self.test.name
        if self.name and not self.name == name:
            log.warning('You tried to name a heuristic "%s", but it was automatically named "%s" instead.' % (self.name, name))
        self.name = name
        super(LabResultPositiveHeuristic, self).save(*args, **kwargs) # Call the "real" save() method.
        event_name_list = [
            self.name, 
            '%s--negative' % self.test.name,
            '%s--indeterminate' % self.test.name,
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
        unbound_labs = self.test.lab_results.exclude(events__event_type__heuristic=self)
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
        #
        # Build numeric comparison queries
        #
        for map in LabTestMap.objects.filter(test=self.test):
            num_res_q = Q(native_code=map.code, result_float__isnull=False)
            positive_q |= num_res_q & Q(ref_high_float__isnull=False, result_float__gte = F('ref_high_float'))
            negative_q |= num_res_q & Q(ref_high_float__isnull=False, result_float__lt = F('ref_high_float'))
            if map.threshold:
                positive_q |= num_res_q & Q(ref_high_float__isnull=True, result_float__gte=map.threshold)
                negative_q |= num_res_q & Q(ref_high_float__isnull=True, result_float__lt=map.threshold)
        #
        # Build string queries
        #
        pos_strings = list(POSITIVE_STRINGS)
        neg_strings = list(NEGATIVE_STRINGS)
        if self.titer:
            positive_titer_strings = ['1:%s' % 2**i for i in range(math.log(self.titer, 2), math.log(4096,2))]
            negative_titer_strings = ['1:%s' % 2**i for i in range(math.log(self.titer, 2))]
            pos_strings += positive_titer_strings
            neg_strings += negative_titer_strings
        pos_str_q = Q(result_string__istartswith=pos_strings[0])
        for s in pos_strings[1:]:
            pos_str_q |= Q(result_string__istartswith=s)
        positive_q |= pos_str_q
        #
        neg_str_q = Q(result_string__istartswith=neg_strings[0])
        for s in neg_strings[1:]:
            neg_str_q |= Q(result_string__istartswith=s)
        negative_q |= neg_str_q
        # Indeterminate events can ONLY be determined from string result
        indeterminate_q = Q(result_string__istartswith=INDETERMINATE_STRINGS[0])
        for s in INDETERMINATE_STRINGS[1:]:
            indeterminate_q |= Q(result_string__istartswith=s)
        #
        # Generate Events
        #
        positive_labs = unbound_labs.filter(positive_q)
        log_query('Positive labs for %s' % self.name, positive_labs)
        log.info('Generating positive events for %s' % self.test.name)
        pos_event_type = EventType.objects.get(name='%s--positive' % self.test.name)
        for lab in positive_labs:
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            new_event = Event(
                event_type = pos_event_type,
                patient = lab.patient,
                date = lab_date,
                content_object = lab,
                )
            new_event.save()
            log.debug('Saved new event: %s' % new_event)
        log.info('Generated %s new positive events for %s' % (positive_labs.count(), self.name))
        negative_labs = unbound_labs.filter(negative_q)
        log_query('Negative labs for %s' % self.name, negative_labs)
        log.info('Generating negative events for %s' % self.test.name)
        neg_event_type = EventType.objects.get(name='%s--negative' % self.test.name)
        for lab in negative_labs:
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            new_event = Event(
                event_type = neg_event_type,
                patient = lab.patient,
                date = lab_date,
                content_object = lab,
                )
            new_event.save()
            log.debug('Saved new event: %s' % new_event)
        log.info('Generated %s new negative events for %s' % (negative_labs.count(), self.name))
        indeterminate_labs = unbound_labs.filter(indeterminate_q)
        log_query('Indeterminate labs for %s' % self.name, indeterminate_labs)
        log.info('Generating indeterminate events for %s' % self.test.name)
        ind_event_type = EventType.objects.get(name='%s--indeterminate' % self.test.name)
        for lab in indeterminate_labs:
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            new_event = Event(
                event_type = ind_event_type,
                patient = lab.patient,
                date = lab_date,
                content_object = lab,
                )
            new_event.save()
            log.debug('Saved new event: %s' % new_event)
        log.info('Generated %s new indeterminate events for %s' % (indeterminate_labs.count(), self.name))
        return positive_labs.count() + negative_labs.count() + indeterminate_labs.count()


class LabResultRatioHeuristic(Heuristic):
    '''
    A heuristic for detecting ratio-based positive lab result events
    '''
    test = models.ForeignKey(AbstractLabTest, blank=False)
    ratio = models.FloatField(blank=False)
    date_field = models.CharField(max_length=32, blank=False, choices=DATE_FIELD_CHOICES, default='order')
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Lab Result Heuristic - Ratio'
        unique_together = ['test', 'ratio']
        ordering = ['test']
    
    def __unicode__(self):
        return u'%s' % self.verbose_name
    
    def __get_verbose_name(self):
        return '%s %s Ratio Heuristic' % (self.test.verbose_name, self.ratio)
    verbose_name = property(__get_verbose_name)
    
    def save(self, *args, **kwargs):
        name = '%s--ratio--%s' % (self.test.name, self.ratio)
        if self.name and not self.name == name:
            log.warning('You tried to name a heuristic "%s", but it was automatically named "%s" instead.' %  (self.name, name))
        self.name = name
        super(LabResultRatioHeuristic, self).save(*args, **kwargs) # Call the "real" save() method.
        obj, created = EventType.objects.get_or_create(
            name = self.name,
            heuristic = self,
            )
        if created:
            log.debug('Added %s for %s' % (obj, self))
    
    def generate_events(self):
        unbound_labs = self.test.lab_results.exclude(events__event_type__heuristic=self)
        log_query('Unbound lab results for %s' % self.name, unbound_labs)
        positive_labs = LabResult.objects.none()
        code_maps = LabTestMap.objects.filter(test=self.test)
        for map in code_maps:
            labs = unbound_labs.filter(native_code=map.code)
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
        for lab in positive_labs:
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            new_event = Event(
                event_type = event_type,
                patient = lab.patient,
                date = lab_date,
                content_object = lab,
                )
            new_event.save()
            log.debug('Saved new event: %s' % new_event)
        log.info('Generated %s new events for %s' % (positive_labs.count(), self.name))
        return positive_labs.count()


class LabResultFixedThresholdHeuristic(Heuristic):
    '''
    A heuristic for detecting fixed-threshold-based positive lab result events
    '''
    test = models.ForeignKey(AbstractLabTest, blank=False)
    threshold = models.FloatField(blank=False, 
        help_text='Events are generated for lab results greater than or equal to this value')
    date_field = models.CharField(max_length=32, blank=False, choices=DATE_FIELD_CHOICES, default='order')
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Lab Result Heuristic - Fixed Threshold'
        unique_together = ['test', 'threshold']
        ordering = ['test']
    
    def __unicode__(self):
        return u'%s' % self.verbose_name
    
    def __get_verbose_name(self):
        return '%s %s Threshold Heuristic' % (self.test.verbose_name, self.threshold)
    verbose_name = property(__get_verbose_name)
    
    def save(self, *args, **kwargs):
        name = '%s--threshold--%s' % (self.test.name, self.threshold)
        if self.name and not self.name == name:
            log.warning('You tried to name a heuristic "%s", but it was automatically named "%s" instead.' % (self.name, name))
        self.name = name
        super(LabResultFixedThresholdHeuristic, self).save(*args, **kwargs) # Call the "real" save() method.
        obj, created = EventType.objects.get_or_create(
            name = self.name,
            heuristic = self,
            )
        if created:
            log.debug('Added %s for %s' % (obj, self))
    
    def generate_events(self):
        unbound_labs = self.test.lab_results.exclude(events__event_type__heuristic=self)
        log_query('Unbound lab results for %s' % self.name, unbound_labs)
        positive_labs = unbound_labs.filter(result_float__isnull=False, result_float__gte=self.threshold)
        log_query(self.name, positive_labs)
        log.info('Generating events for "%s"' % self.verbose_name)
        event_type = EventType.objects.get(name=self.name)
        for lab in positive_labs:
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            new_event = Event(
                event_type = event_type,
                patient = lab.patient,
                date = lab_date,
                content_object = lab,
                )
            new_event.save()
            log.debug('Saved new event: %s' % new_event)
        log.info('Generated %s new events for %s' % (positive_labs.count(), self.name))
        return positive_labs.count() 


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
    drugs = models.CharField(max_length=256, blank=False, help_text='Drug names, separated by commas.')
    dose = models.ManyToManyField(Dose, blank=True, null=True)
    min_quantity = models.IntegerField(blank=True, null=True, default=None)
    require = models.CharField(max_length=128, blank=True, null=True, 
        help_text='Prescription must include one or more of these strings.  Separate strings with commas.')
    exclude = models.CharField(max_length=128, blank=True, null=True, 
        help_text='Prescription may not include any of these strings.  Separate strings with commas.')
    
    class Meta:
        verbose_name = 'Prescription Heuristic'
        ordering = ['name']
        
    def __unicode__(self):
        return u'%s' % self.verbose_name
    
    def __get_verbose_name(self):
        return '%s Prescription Heuristic' % self.name
    verbose_name = property(__get_verbose_name)
    
    def save(self, *args, **kwargs):
        super(PrescriptionHeuristic, self).save(*args, **kwargs) # Call the "real" save() method.
        obj, created = EventType.objects.get_or_create(
            name = self.name,
            heuristic = self,
            )
        if created:
            log.debug('Added %s for %s' % (obj, self))
    
    def generate_events(self):
        unbound = Prescription.objects.exclude(events__event_type__heuristic=self)
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
            prescriptions |= unbound.filter(name__icontains=drug_name)
        if self.dose.all():
            rxs_by_dose = Prescription.objects.none()
            for dose_obj in self.dose.all():
                for dose_string in dose_obj.string_variants:
                    rxs_by_dose |= unbound.filter(name__icontains=dose_string)
                    rxs_by_dose |= unbound.filter(dose__icontains=dose_string)
            prescriptions &= rxs_by_dose
        if self.min_quantity:
            prescriptions = prescriptions.filter(quantity__gte=self.min_quantity)
        for required_string in require:
            prescriptions &= unbound.filter(name__icontains=required_string)
        for excluded_string in exclude:
            prescriptions &= prescriptions.exclude(name__icontains=excluded_string)
        log_query('Prescriptions for %s' % self.name, prescriptions)
        log.info('Generating events for "%s"' % self.verbose_name)
        event_type = EventType.objects.get(name=self.name)
        for rx in prescriptions:
            new_event = Event(
                event_type = event_type,
                patient = rx.patient,
                date = rx.date,
                content_object = rx,
                )
            new_event.save()
            log.debug('Saved new event: %s' % new_event)
        return prescriptions.count()


class EncounterHeuristic(Heuristic):
    '''
    A heuristic for detecting encounter ICD9 code based events
    '''
    icd9_codes = models.CharField(max_length=128, blank=False, 
        help_text='Encounter must include one or more of these ICD9 codes.  Separate codes with commas.')
    code_match_type = models.CharField(max_length=32, blank=False, choices=MATCH_TYPE_CHOICES, db_index=True, 
        help_text='Match type for ICD9 code', default='exact')
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Encounter Heuristic'
        ordering = ['name']
        unique_together = ['icd9_codes', 'code_match_type']
    
    def __unicode__(self):
        return u'%s' % self.verbose_name
    
    def __get_verbose_name(self):
        return '%s Encounter Heuristic' % self.name
    verbose_name = property(__get_verbose_name)
    
    def save(self, *args, **kwargs):
        super(EncounterHeuristic, self).save(*args, **kwargs) # Call the "real" save() method.
        obj, created = EventType.objects.get_or_create(
            name = self.name,
            heuristic = self,
            )
        if created:
            log.debug('Added %s for %s' % (obj, self))
    
    def generate_events(self):
        codes = [c.strip() for c in self.icd9_codes.split(',')]
        unbound = Encounter.objects.exclude(events__event_type__heuristic=self)
        encounters = Encounter.objects.none()
        for c in codes:
            if self.code_match_type == 'exact':
                encounters |= unbound.filter(icd9_codes__code__exact=c)
            elif self.code_match_type == 'iexact':
                encounters |= unbound.filter(icd9_codes__code__iexact=c)
            elif self.code_match_type == 'startswith':
                encounters |= unbound.filter(icd9_codes__code__startswith=c)
            elif self.code_match_type == 'istartswith':
                encounters |= unbound.filter(icd9_codes__code__istartswith=c)
            elif self.code_match_type == 'endswith':
                encounters |= unbound.filter(icd9_codes__code__endswith=c)
            elif self.code_match_type == 'iendswith':
                encounters |= unbound.filter(icd9_codes__code__iendswith=c)
            elif self.code_match_type == 'contains':
                encounters |= unbound.filter(icd9_codes__code__contains=c)
            elif self.code_match_type == 'icontains':
                encounters |= unbound.filter(icd9_codes__code__icontains=c)
        log_query('Encounters for %s' % self.name, encounters)
        log.info('Generating events for "%s"' % self.verbose_name)
        event_type = EventType.objects.get(name=self.name)
        for enc in encounters:
            new_event = Event(
                event_type = event_type,
                patient = enc.patient,
                date = enc.date,
                content_object = enc,
                )
            new_event.save()
            log.debug('Saved new event: %s' % new_event)
        log.info('Generated %s new events for %s' % (encounters.count(), self.name))
        return encounters.count()


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
    timestamp = models.DateTimeField('Time event was created in db', blank=False, auto_now_add=True)
    #
    # Standard generic relation support
    #    http://docs.djangoproject.com/en/dev/ref/contrib/contenttypes/
    #
    content_type = models.ForeignKey(ContentType, db_index=True)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return u'Event # %s (%s %s)' % (self.pk, self.event_type.name, self.date)


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
        return u'Timespan %s, patient %s, %s - %s' % (self.name, self.patient.name, self.start_date, self.end_date)
