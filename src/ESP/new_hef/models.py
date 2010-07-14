'''
                              ESP Health Project
                          Heuristic Events Framework
                                  Data Models

@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''

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

#HEF_RUN_STATUS = [
#    ('r', 'Run in progress'),
#    ('a', 'Aborted by user'),
#    ('s', 'Successfully completed'),
#    ('f', 'Failure'),
#    ]

#class Run(models.Model):
#    '''
#    HEF run status.  The 'timestamp' field is automatically set to current 
#    time, and 'status' is set to 'r'.  Upon successful completion of the run, 
#    status is updated to 's'.  
#    '''
#    timestamp = models.DateTimeField(blank=False, auto_now_add=True)
#    status = models.CharField(max_length=1, blank=False, choices=HEF_RUN_STATUS, default='r')
#    
#    def __str__(self):
#        return '<HEF Run #%s: %s: %s>' % (self.pk, self.status, self.timestamp)


#class Timespan(models.Model):
#    '''
#    A condition, such as pregnancy, which occurs over a defined span of time.  
#    '''   
#    name = models.SlugField(max_length=128, null=False, blank=False, db_index=True)
#    patient = models.ForeignKey(Patient, blank=False)
#    start_date = models.DateField(blank=False, db_index=True)
#    end_date = models.DateField(blank=False, db_index=True)
#    timestamp = models.DateTimeField('Time this event was created in db', blank=False, auto_now_add=True)
#    run = models.ForeignKey(Run, blank=False)
#    pattern = models.SlugField(blank=False)
#    # 
#    # The 'encounters' field is a short-term hack for generating gdm pregnancy timespans, and should be 
#    # replaced (soon) with a fully generic solution.
#    #
#    encounters = models.ManyToManyField(Encounter)


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
    
    def __str__(self):
        return self.name
    
    def __get_lab_results(self):
        result = LabResult.objects.none()
        for cm in self.codemap_set.all():
            result = result | cm.lab_results
        log_query('Lab Results for %s' % self.name, result)
        return result
    lab_results = property(__get_lab_results)
    
    def __get_lab_orders(self):
        result = LabOrder.objects.none()
        for cm in self.codemap_set.all():
            result = result | cm.lab_orders
        log_query('Lab Orders for %s' % self.name, result)
        return result
    lab_orders = property(__get_lab_orders)
    

class CodeMap(models.Model):
    '''
    Mapping object to associate an abstract lab test type with a concrete, 
    EMR-specific lab test type
    '''
    test = models.ForeignKey(AbstractLabTest, blank=False, db_index=True)
    code = models.CharField(max_length=100, verbose_name='Test Code',
        help_text='Native test code from source EMR system', blank=False, db_index=True)
    code_match_type = models.CharField(max_length=32, blank=False, choices=MATCH_TYPE_CHOICES, db_index=True, 
        help_text='Match type for test code', default='exact')
    threshold = models.FloatField(help_text='Numeric threshold for positive test', blank=True, null=True)
    #
    # Notes
    #
    notes = models.TextField(blank=True, null=True)
    class Meta:
        verbose_name = 'Code Map'
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
        return self.verbose_name
    

class LabOrderHeuristic(Heuristic):
    '''
    A heuristic for detecting lab order events.

    Note that in some EMR systems (e.g. Atrius) lab orders may be less specific
    than lab results, and thus lab orders may require a different
    AbstractLabTest than required for lab results.
    '''
    test = models.ForeignKey(AbstractLabTest, blank=False)
    
    def __get_name(self):
        return '%s--order' % self.test.name
    name = property(__get_name)
    
    def __get_verbose_name(self):
        return '%s Order Heuristic' % self.test.verbose_name
    verbose_name = property(__get_verbose_name)
    
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
