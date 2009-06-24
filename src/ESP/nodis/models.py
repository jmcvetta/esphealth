'''
                                  ESP Health
                         Notifiable Diseases Framework
                                  Data Models
'''


import datetime

from django.db import models

from ESP.emr.models import LabResult
from ESP.emr.models import Encounter
from ESP.emr.models import Prescription
from ESP.emr.models import Immunization
from ESP.emr.models import Provider
from ESP.emr.models import Patient
from ESP.hef.models import HeuristicEvent
from ESP.conf.models import Rule
from ESP.conf.choices import WORKFLOW_STATES


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
    #workflow_state = models.CharField(max_length=20, choices=WORKFLOW_STATES, default='AR', 
        #blank=False, db_index=True )
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


class NodisCaseWorkflow(models.Model):
    workflowCaseID = models.ForeignKey(Case)
    workflowDate = models.DateTimeField('Activated',auto_now=True)
    workflowState = models.CharField('Workflow State',choices=WORKFLOW_STATES,max_length=20 )
    workflowChangedBy = models.CharField('Changed By', max_length=30)
    workflowComment = models.TextField('Comments',blank=True,null=True)
    
    def  __unicode__(self):
        return u'%s %s %s' % (self.workflowCaseID, self.workflowDate, self.workflowState)

