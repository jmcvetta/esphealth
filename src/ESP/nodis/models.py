'''
                                  ESP Health
                         Notifiable Diseases Framework
                                  Data Models
'''


import datetime

from django.db import models

from ESP.emr.models import Encounter
from ESP.emr.models import Immunization
from ESP.emr.models import LabResult
from ESP.emr.models import Patient
from ESP.emr.models import Prescription
from ESP.emr.models import Provider
from ESP.hef.models import HeuristicEvent


STATUS_CHOICES = [
    ('AR', 'Awaiting Review'),
    ('UR', 'Under Review'),
    ('RM', 'Review by MD'),
    ('FP', 'False Positive - Do NOT Process'),
    ('Q',  'Confirmed Case, Transmit to Health Department'), 
    ('S',  'Transmitted to Health Department')
    ]


class Case(models.Model):
    '''
    A case of (reportable) disease
    '''
    patient = models.ForeignKey(Patient, blank=False)
    condition = models.CharField(max_length=100, blank=False, db_index=True)
    provider = models.ForeignKey(Provider, blank=False)
    date = models.DateField(blank=False, db_index=True)
    definition = models.CharField(max_length=100, blank=False)
    def_version = models.IntegerField(blank=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    # Timestamps:
    created_timestamp = models.DateTimeField(auto_now_add=True, blank=False)
    updated_timestamp = models.DateTimeField(auto_now=True, blank=False)
    sent_timestamp = models.DateTimeField(blank=True, null=True)
    #
    # Events that define this case
    #
    events = models.ManyToManyField(HeuristicEvent, blank=False) # The events that caused this case to be generated
    #
    # Reportable Events
    #
    encounters = models.ManyToManyField(Encounter, blank=True, null=True)
    lab_results = models.ManyToManyField(LabResult, blank=True, null=True)
    medications = models.ManyToManyField(Prescription, blank=True, null=True)
    immunizations = models.ManyToManyField(Immunization, blank=True, null=True)
    #
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        permissions = [ ('view_phi', 'Can view protected health information'), ]
    
    def __str__(self):
        return '%s # %s' % (self.condition, self.pk)
    
    def str_line(self):
        '''
        Returns a single-line string representation of the Case instance
        '''
        values = self.__dict__
        return '%(date)-10s    %(id)-8s    %(condition)-30s' % values
    
    @classmethod
    def str_line_header(cls):
        '''
        Returns a header describing the fields returned by str_line()
        '''
        values = {'date': 'DATE', 'id': 'CASE #', 'condition': 'CONDITION'}
        return '%(date)-10s    %(id)-8s    %(condition)-30s' % values
    


class CaseStatusHistory(models.Model):
    '''
    The current review status of a given Case
    '''
    case = models.ForeignKey(Case, blank=False)
    timestamp = models.DateTimeField(auto_now=True, blank=False, db_index=True)
    old_status = models.CharField(max_length=10, choices=STATUS_CHOICES, blank=False)
    new_status = models.CharField(max_length=10, choices=STATUS_CHOICES, blank=False)
    changed_by = models.CharField(max_length=30, blank=False)
    comment = models.TextField(blank=True, null=True)
    
    def  __unicode__(self):
        return u'%s %s' % (self.case, self.timestamp)
    
    class Meta:
        verbose_name = 'Case Status History'
        verbose_name_plural = 'Case Status History'

