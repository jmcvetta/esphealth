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

from ESP.hef.choices import HEF_RUN_STATUS
from ESP.static.models import Loinc
from ESP.emr.models import Patient


class Run(models.Model):
    '''
    HEF run status.  Each time a heuristic particular is run and HeuristicEvent objects
    are generated, a new instance is created.  The 'timestamp' field is
    automatically set to current time, and 'status' is set to 'r'.  Upon
    successful completion of the run, status is updated to 's'.  
    '''
    def_name = models.CharField(max_length=255, null=False, blank=False, db_index=True)
    timestamp = models.DateTimeField(blank=False, auto_now_add=True)
    status = models.CharField(max_length=1, blank=False, choices=HEF_RUN_STATUS, default='r')
    
    def __str__(self):
        return '<HEF Run #%s: %s: %s: %s>' % (self.pk, self.def_name, self.status, self.timestamp)


class HeuristicEvent(models.Model):
    '''
    An interesting medical event
    '''
    heuristic_name = models.CharField(max_length=127, null=False, blank=False, db_index=True)
    date = models.DateField('Date event occured', blank=False, db_index=True)
    # FIXME: Remove related_name when hef2 graduates to be new hef version
    patient = models.ForeignKey(Patient, blank=False, db_index=True, related_name='hef2_event_set')
    timestamp = models.DateTimeField('Time event was created in db', blank=False, auto_now_add=True)
    definition = models.CharField(max_length=100, blank=False, db_index=True)
    def_version = models.IntegerField(blank=False)
    #
    # Standard generic relation support
    #    http://docs.djangoproject.com/en/dev/ref/contrib/contenttypes/
    #
    # FIXME: Remove related_name when hef2 graduates to be new hef version
    content_type = models.ForeignKey(ContentType, db_index=True, related_name='hef2_event_set')
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        unique_together = ['definition', 'date', 'patient', 'content_type', 'object_id']
    
    def __str__(self):
        #msg = '%-15s %-12s Patient #%-20s' % (self.heuristic_name, self.date, self.patient.id)
        #msg += '\n'
        #msg += '    %s' % self.content_object
        #return msg
        return 'HeuristicEvent #%s (%s %s)' % (self.pk, self.heuristic_name, self.date)
    
    def str_line(self):
        '''
        Returns a single-line string representation of the object
        '''
        values = self.__dict__
        return '%(date)-10s    %(id)-8s    %(heuristic_name)-30s    %(object_id)-10s' % values
    
    @classmethod
    def str_line_header(cls):
        '''
        Returns a header describing the fields returned by str_line()
        '''
        values = {'date': 'DATE', 'id': 'EVENT #', 'heuristic_name': 'EVENT', 'object_id': 'OBJECT #'}
        return '%(date)-10s    %(id)-8s    %(heuristic_name)-30s    %(object_id)-10s' % values


