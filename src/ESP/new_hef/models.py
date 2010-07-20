'''
                              ESP Health Project
                          Heuristic Events Framework
                                  Data Models

@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''

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


POSITIVE_STRINGS = ['reactiv', 'pos', 'detec', 'confirm']
NEGATIVE_STRINGS = ['non', 'neg', 'not det', 'nr']
INDETERMINATE_STRINGS = ['indeterminate', 'not done', 'tnp']
DATE_FIELD_CHOICES = [
    ('order', 'Order'),
    ('result', 'Result')
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
    
    def __str__(self):
        return self.name
    
    def __get_lab_results(self):
        result = LabResult.objects.none()
        for cm in self.labtestmap_set.all():
            result = result | cm.lab_results
        log_query('Lab Results for %s' % self.name, result)
        return result
    lab_results = property(__get_lab_results)
    
    def __get_lab_orders(self):
        result = LabOrder.objects.none()
        for cm in self.labtestmap_set.all():
            result = result | cm.lab_orders
        log_query('Lab Orders for %s' % self.name, result)
        return result
    lab_orders = property(__get_lab_orders)
    

class LabTestMap(models.Model):
    '''
    Mapping object to associate an abstract lab test type with a concrete, 
    EMR-specific lab test type
    '''
    test = models.ForeignKey(AbstractLabTest, blank=False, db_index=True)
    code = models.CharField(max_length=100, verbose_name='Test Code',
        help_text='Native test code from source EMR system', blank=False, db_index=True)
    code_match_type = models.CharField(max_length=32, blank=False, choices=MATCH_TYPE_CHOICES, db_index=True, 
        help_text='Match type for test code', default='exact')
    threshold = models.FloatField(help_text='Fallback positive threshold for tests without reference high', blank=True, null=True)
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
    
    def generate_events(self):
        raise NotImplementedError
    
    def __str__(self):
        return 'Heuristic # %s' % self.pk
    

class LabOrderHeuristic(Heuristic):
    '''
    A heuristic for detecting lab order events.

    Note that in some EMR systems (e.g. Atrius) lab orders may be less specific
    than lab results, and thus lab orders may require a different
    AbstractLabTest than required for lab results.
    '''
    test = models.ForeignKey(AbstractLabTest, blank=False, unique=True)
    
    class Meta:
        verbose_name = 'Lab Order Heuristic'
    
    def __str__(self):
        return self.verbose_name
    
    def __get_name(self):
        return '%s--order' % self.test.name
    name = property(__get_name)
    
    def __get_verbose_name(self):
        return '%s Order Heuristic' % self.test.verbose_name
    verbose_name = property(__get_verbose_name)
    
    def __get_event_names(self):
        return [self.name]
    event_names = property(__get_event_names)
    
    def generate_events(self):
        log.debug('Generating events for "%s"' % self.verbose_name)
        unbound_orders = self.test.lab_orders.exclude(events__heuristic=self)
        log_query('Unbound lab orders for %s' % self.name, unbound_orders)
        unbound_count = unbound_orders.count()
        for order in unbound_orders:
            e = Event(
                name = self.name,
                heuristic = self,
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
    date_field = models.CharField(max_length=32, blank=False, choices=DATE_FIELD_CHOICES, default='order')
    
    class Meta:
        verbose_name = 'Positive/Negative Lab Result Heuristic'
    
    def __str__(self):
        return self.verbose_name
    
    def __get_name(self):
        return '%s--positive' % self.test.name
    name = property(__get_name)
    
    def __get_verbose_name(self):
        return '%s Positive Heuristic' % self.test.verbose_name
    verbose_name = property(__get_verbose_name)
    
    def __get_event_names(self):
        return [
            self.name, 
            '%s--negative' % self.test.name,
            '%s--indeterminate' % self.test.name,
            ]
    
    def generate_events(self):
        log.debug('Generating events for "%s"' % self.verbose_name)
        unbound_labs = self.test.lab_results.exclude(new_events__heuristic=self)
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
        positive_labs = LabResult.objects.none()
        negative_labs = LabResult.objects.none()
        code_maps = LabTestMap.objects.filter(test=self.test)
        for map in code_maps:
            labs = unbound_labs.filter(native_code=map.code)
            #
            # Build numeric comparison queries
            #
            num_res_labs = labs.filter(result_float__isnull=False)
            positive_labs |= num_res_labs.filter(ref_high_float__isnull=False, result_float__gte = F('ref_high_float'))
            negative_labs |= num_res_labs.filter(ref_high_float__isnull=False, result_float__lt = F('ref_high_float'))
            if map.threshold:
                positive_labs |= num_res_labs.filter(ref_high_float__isnull=True, result_float__gte=map.threshold)
                negative_labs |= num_res_labs.filter(ref_high_float__isnull=True, result_float__lt=map.threshold)
        #
        # Build string queries
        #
        #
        pos_str_q = Q(result_string__istartswith=POSITIVE_STRINGS[0])
        for s in POSITIVE_STRINGS[1:]:
            pos_str_q |= Q(result_string__istartswith=s)
        positive_labs |= unbound_labs.filter(pos_str_q)
        #
        neg_str_q = Q(result_string__istartswith=NEGATIVE_STRINGS[0])
        for s in NEGATIVE_STRINGS[1:]:
            neg_str_q |= Q(result_string__istartswith=s)
        negative_labs |= unbound_labs.filter(neg_str_q)
        # Indeterminate events can ONLY be determined from string result
        ind_str_q = Q(result_string__istartswith=INDETERMINATE_STRINGS[0])
        for s in INDETERMINATE_STRINGS[1:]:
            ind_str_q |= Q(result_string__istartswith=s)
        indeterminate_labs = unbound_labs.filter(ind_str_q)
        #--------------------------------------------------------------------------------
        # REMOVED -- is this still necessary/useful?
        #
        # Only look at relevant labs.  We do this for both numeric & string 
        # subqueries, for faster overall query performance.   
        #
        #pos_q &= Q(native_code__in=native_codes)
        #--------------------------------------------------------------------------------
        #
        # If a lab is positive, then it definitionally is not negative
        #
        pos_pks = positive_labs.values('pk')
        negative_labs = negative_labs.exclude(pk__in=pos_pks)
        #
        # Generate Events
        #
        log_query('Positive labs for %s' % self.name, positive_labs)
        log.info('Generating positive events for %s' % self.name)
        for lab in positive_labs:
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            new_event = Event(
                name = '%s--positive' % self.test.name,
                heuristic = self,
                patient = lab.patient,
                date = lab_date,
                content_object = lab,
                )
            new_event.save()
            log.debug('Saved new event: %s' % new_event)
        log.info('Generated %s new positive events for %s' % (positive_labs.count(), self.name))
        log_query('Negative labs for %s' % self.name, negative_labs)
        log.info('Generating negative events for %s' % self.name)
        for lab in negative_labs:
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            new_event = Event(
                name = '%s--negative' % self.test.name,
                heuristic = self,
                patient = lab.patient,
                date = lab_date,
                content_object = lab,
                )
            new_event.save()
            log.debug('Saved new event: %s' % new_event)
        log.info('Generated %s new negative events for %s' % (negative_labs.count(), self.name))
        log_query('Indeterminate labs for %s' % self.name, indeterminate_labs)
        log.info('Generating indeterminate events for %s' % self.name)
        for lab in indeterminate_labs:
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            new_event = Event(
                name = '%s--indeterminate' % self.test.name,
                heuristic = self,
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
    
    class Meta:
        verbose_name = 'Ratio Lab Result Heuristic'
        unique_together = ['test', 'ratio']
    
    def __str__(self):
        return self.verbose_name
    
    def __get_name(self):
        return '%s--ratio--%s' % (self.test.name, self.ratio)
    name = property(__get_name)
    
    def __get_verbose_name(self):
        return '%s %s Ratio Heuristic' % (self.test.verbose_name, self.ratio)
    verbose_name = property(__get_verbose_name)
    
    def __get_event_names(self):
        return [self.name,]
    
    def generate_events(self):
        log.debug('Generating events for "%s"' % self.verbose_name)
        unbound_labs = self.test.lab_results.exclude(new_events__heuristic=self)
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
        for lab in positive_labs:
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            new_event = Event(
                name = self.name,
                heuristic = self,
                patient = lab.patient,
                date = lab_date,
                content_object = lab,
                )
            new_event.save()
            log.debug('Saved new event: %s' % new_event)
        log.info('Generated %s new events for %s' % (positive_labs.count(), self.name))
        return positive_labs.count() # We can only return one count, and positive is most important


class LabResultFixedThresholdHeuristic(Heuristic):
    '''
    A heuristic for detecting fixed-threshold-based positive lab result events
    '''
    test = models.ForeignKey(AbstractLabTest, blank=False)
    threshold = models.FloatField(blank=False, 
        help_text='Events are generated for lab results greater than or equal to this value')
    date_field = models.CharField(max_length=32, blank=False, choices=DATE_FIELD_CHOICES, default='order')
    
    class Meta:
        verbose_name = 'Fixed Threshold Lab Result Heuristic'
        unique_together = ['test', 'threshold']
    
    def __str__(self):
        return self.verbose_name
    
    def __get_name(self):
        return '%s--threshold--%s' % (self.test.name, self.threshold)
    name = property(__get_name)
    
    def __get_verbose_name(self):
        return '%s %s Threshold Heuristic' % (self.test.verbose_name, self.threshold)
    verbose_name = property(__get_verbose_name)
    
    def __get_event_names(self):
        return [self.name,]
    
    def generate_events(self):
        log.info('Generating events for "%s"' % self.verbose_name)
        unbound_labs = self.test.lab_results.exclude(new_events__heuristic=self)
        log_query('Unbound lab results for %s' % self.name, unbound_labs)
        positive_labs = unbound_labs.filter(result_float__isnull=False, result_float__gte=self.threshold)
        log_query(self.name, positive_labs)
        for lab in positive_labs:
            if self.date_field == 'order':
                lab_date = lab.date
            elif self.date_field == 'result':
                lab_date = lab.result_date
            new_event = Event(
                name = self.name,
                heuristic = self,
                patient = lab.patient,
                date = lab_date,
                content_object = lab,
                )
            new_event.save()
            log.debug('Saved new event: %s' % new_event)
        log.info('Generated %s new events for %s' % (positive_labs.count(), self.name))
        return positive_labs.count() # We can only return one count, and positive is most important


class Event(models.Model):
    '''
    An interesting medical event
    '''
    name = models.SlugField(max_length=128, null=False, blank=False, db_index=True)
    heuristic = models.ForeignKey(Heuristic, blank=False)
    date = models.DateField('Date event occured', blank=False, db_index=True)
    patient = models.ForeignKey(Patient, blank=False, db_index=True, 
        related_name='new_event_set') # FIXME: Remove related_name after hef refactor complete
    timestamp = models.DateTimeField('Time event was created in db', blank=False, auto_now_add=True)
    #
    # Standard generic relation support
    #    http://docs.djangoproject.com/en/dev/ref/contrib/contenttypes/
    #
    content_type = models.ForeignKey(ContentType, db_index=True,
        related_name='new_event_set') # FIXME: Remove related_name after hef refactor complete
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return 'Event # %s (%s %s)' % (self.pk, self.name, self.date)
