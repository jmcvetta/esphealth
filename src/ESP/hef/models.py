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
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from ESP.conf.models import Loinc
from ESP.esp.models import Demog


class NativeToLoincMap(models.Model):
    '''
    A mapping from a native code (for a lab result, etc) to a Loinc number
    '''
    # This table and utilities making use of it assume only one external 
    # code table per ESP installation.  More work will be required if your 
    # installation must comprehend multiple, potentially overlapping, external 
    # code sources
    native_code = models.CharField(max_length=100, unique=True, blank=False)
    native_name = models.CharField(max_length=255, blank=True, null=True)
    # Loinc can be null to indicate an external code that maps to nothing
    loinc = models.ForeignKey(Loinc, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    class Meta:
        verbose_name = 'Native Code to LOINC Map'


class HeuristicEvent(models.Model):
    '''
    An interesting medical event
    '''
    heuristic_name = models.CharField(max_length=127, null=False, blank=False, db_index=True)
    date = models.DateField(blank=False, db_index=True)
    patient = models.ForeignKey(Demog, blank=False, db_index=True)
    #
    # Standard generic relation support
    #    http://docs.djangoproject.com/en/dev/ref/contrib/contenttypes/
    #
    content_type = models.ForeignKey(ContentType, db_index=True)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        unique_together = ['heuristic_name', 'date', 'patient', 'content_type', 'object_id']
    
    def __str__(self):
        #msg = '%-15s %-12s Patient #%-20s' % (self.heuristic_name, self.date, self.patient.id)
        #msg += '\n'
        #msg += '    %s' % self.content_object
        #return msg
        return 'HeuristicEvent #%s (%s %s)' % (self.pk, self.heuristic_name, self.date)


