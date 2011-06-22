'''
                              ESP Health Project
                          Heuristic Events Framework
                                  Data Models

@author: Jason McVetta <jason.mcvetta@heliotropi.cc>
@organization: Channing Laboratory http://www.channing.harvard.edu
@contact: http://esphealth.org
@copyright: (c) 2009-2011 Channing Laboratory
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


class Event(models.Model):
    '''
    A medical event
    '''
    name = models.SlugField('Name for this event type', max_length=128, blank=False, db_index=True)
    source = models.TextField('What created this event?', blank=False, db_index=True)
    date = models.DateField('Date event occured', blank=False, db_index=True)
    patient = models.ForeignKey(Patient, blank=False, db_index=True)
    provider = models.ForeignKey(Provider, blank=False, db_index=True)
    timestamp = models.DateTimeField('Time event was created in db', blank=False, auto_now_add=True)
    
    def __unicode__(self):
        return u'Event # %s (%s %s)' % (self.pk, self.name, self.date)
    
    def tag(self, obj):
        '''
        Tags a medical record with this event. 
        '''
        tag = EventTag(
            event = self,
            event_name = self.name,
            content_object = obj,
            )
        tag.save()
        return tag
    
    def tag_qs(self, qs):
        '''
        Tags every record in qs with this event
        '''
        for obj in qs:
            self.tag(obj)


class EventTag(models.Model):
    '''
    A tag associating an Event instance with a medical record
    '''
    event = models.ForeignKey(Event, blank=False)
    # We store event_name here even tho the same info is stored in the 
    # foreign-keyed Event object, in order to improve query performance.
    event_name = models.CharField(max_length=128, blank=False, db_index=True)
    # Generic foreign key - any kind of EMR record can be tagged
    #    http://docs.djangoproject.com/en/dev/ref/contrib/contenttypes/
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
    name = models.SlugField('Common name of this type of timespan', max_length=128, blank=False, db_index=True)
    source = models.TextField('What created this timespan?', blank=False, db_index=True)
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
        return u'Timespan #%s | %s | %s | %s - %s | %s' % (self.pk, 
            self.name, self.patient, self.start_date, self.end_date, self.pattern)
