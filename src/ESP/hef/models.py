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

from ESP.static.models import Loinc
from ESP.emr.models import Patient


HEF_RUN_STATUS = [
    ('r', 'Run in progress'),
    ('a', 'Aborted by user'),
    ('s', 'Successfully completed'),
    ('f', 'Failure'),
    ]

class Run(models.Model):
    '''
    HEF run status.  The 'timestamp' field is automatically set to current 
    time, and 'status' is set to 'r'.  Upon successful completion of the run, 
    status is updated to 's'.  
    '''
    timestamp = models.DateTimeField(blank=False, auto_now_add=True)
    status = models.CharField(max_length=1, blank=False, choices=HEF_RUN_STATUS, default='r')
    
    def __str__(self):
        return '<HEF Run #%s: %s: %s>' % (self.pk, self.status, self.timestamp)


class Event(models.Model):
    '''
    An interesting medical event
    '''
    name = models.SlugField(max_length=128, null=False, blank=False, db_index=True)
    date = models.DateField('Date event occured', blank=False, db_index=True)
    patient = models.ForeignKey(Patient, blank=False, db_index=True)
    timestamp = models.DateTimeField('Time event was created in db', blank=False, auto_now_add=True)
    run = models.ForeignKey(Run, blank=False)
    #
    # Standard generic relation support
    #    http://docs.djangoproject.com/en/dev/ref/contrib/contenttypes/
    #
    content_type = models.ForeignKey(ContentType, db_index=True)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        unique_together = ['name', 'date', 'patient', 'content_type', 'object_id']
    
    def __str__(self):
        return 'Event # %s (%s %s)' % (self.pk, self.name, self.date)
    
    def str_line(self):
        '''
        Returns a single-line string representation of the object
        '''
        values = self.__dict__
        return '%(date)-10s    %(id)-8s    %(name)-30s    %(object_id)-10s' % values
    
    @classmethod
    def str_line_header(cls):
        '''
        Returns a header describing the fields returned by str_line()
        '''
        values = {'date': 'DATE', 'id': 'EVENT #', 'name': 'EVENT', 'object_id': 'OBJECT #'}
        return '%(date)-10s    %(id)-8s    %(name)-30s    %(object_id)-10s' % values


