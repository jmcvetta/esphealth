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
    note = models.TextField(blank=True, null=True)
    # Generic foreign key - any kind of EMR record can be tagged
    #    http://docs.djangoproject.com/en/dev/ref/contrib/contenttypes/
    content_type = models.ForeignKey(ContentType, db_index=True)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        unique_together = [('source', 'name', 'content_type', 'object_id')]
    
    def __unicode__(self):
        return u'Event # %s (%s %s)' % (self.pk, self.name, self.date)
    
    @classmethod
    def create(cls, 
	    name,
	    source,
	    date,
	    patient,
	    provider,
        emr_record,
        qs=None,
        ):
        '''
        Creates an event linked to emr_record.  If a QuerySet is given as qs
        and emr_record is None, an event of the specified type is created for
        each record in the QS.
        '''
        assert emr_record or qs
        if qs:
            pk_list = qs.values_list('pk').order_by('pk').distinct()
            note = 'Event created from a queryset including the following PKs:\n    '
            note += '\n    '.join(pk_list)
            records = qs
        else:
            records = [emr_record]
            note = None
        for obj in records:
            content_type = ContentType.objects.get_for_model(obj)
            new_event = Event(
                name = name,
                source =source,
				date = date,
				patient = patient,
				provider = provider,
                note = note,
                content_type = content_type,
                object_id = obj.pk,
                )
            new_event.save()
            log.debug('Created new event: %s' % new_event)
        return len(records)
    

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
    pattern = models.TextField(blank=True, null=True)
    # 
    # The 'encounters' field is a short-term hack for generating gdm pregnancy timespans, and should be 
    # replaced (soon) with a fully generic solution.
    #
    encounters = models.ManyToManyField(Encounter)

    def __unicode__(self):
        return u'Timespan #%s | %s | %s | %s - %s | %s' % (self.pk, 
            self.name, self.patient, self.start_date, self.end_date, self.pattern)

