'''
                                  ESP Health
                         Notifiable Diseases Framework
                                  Data Models
'''


import datetime

from django.db import models
from django.db.models import Q

from ESP.emr.models import Encounter
from ESP.emr.models import Immunization
from ESP.emr.models import LabResult
from ESP.emr.models import Patient
from ESP.emr.models import Prescription
from ESP.emr.models import Provider
from ESP.hef.models import Event


STATUS_CHOICES = [
    ('AR', 'Awaiting Review'),
    ('UR', 'Under Review'),
    ('RM', 'Review by MD'),
    ('FP', 'False Positive - Do NOT Process'),
    # Only fields before this point will be included in on-screen case status menu
    ('Q',  'Confirmed Case, Transmit to Health Department'), 
    ('S',  'Transmitted to Health Department')
    ]

DISPOSITIONS = [
    ('exact', 'Exact'),
    ('similar', 'Similar'),
    ('missing', 'Missing'),
    ('new', 'New'),
    ]

class Pattern(models.Model):
    '''
    Hash of the ComplexEventPattern used to generate a particular case
    '''
    hash = models.CharField(max_length=512, blank=False, null=False, unique=True, db_index=True)
    name = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    created_timestamp = models.DateTimeField(auto_now_add=True, blank=False)
    

class Case(models.Model):
    '''
    A case of (reportable) disease
    '''
    patient = models.ForeignKey(Patient, blank=False)
    condition = models.CharField(max_length=100, blank=False, db_index=True)
    provider = models.ForeignKey(Provider, blank=False)
    date = models.DateField(blank=False, db_index=True)
    pattern = models.ForeignKey(Pattern, blank=False, db_index=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='AR') # Is it sensible to have default here?
    notes = models.TextField(blank=True, null=True)
    # Timestamps:
    created_timestamp = models.DateTimeField(auto_now_add=True, blank=False)
    updated_timestamp = models.DateTimeField(auto_now=True, blank=False)
    sent_timestamp = models.DateTimeField(blank=True, null=True)
    #
    # Events that define this case
    #
    events = models.ManyToManyField(Event, blank=False) # The events that caused this case to be generated
    past_events = models.ManyToManyField(Event, blank=False, related_name='past_events') # The events that caused this case to be generated
    #
    # Events by class
    #
    def __get_lab_results(self):
        e = self.events.all() | self.past_events.all()
        return LabResult.objects.filter(events__in=e).order_by('date')
    lab_results = property(__get_lab_results)
    
    def __get_encounters(self):
        e = self.events.all() | self.past_events.all()
        return Encounter.objects.filter(events__in=e).order_by('date')
    encounters = property(__get_encounters)
    
    def __get_prescriptions(self):
        e = self.events.all() | self.past_events.all()
        return Prescription.objects.filter(events__in=e).order_by('date')
    prescriptions = property(__get_prescriptions)
    
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


class InterestingLab(models.Model):
    '''
    Cache of lab tests which contain suspicious strings in their names.  This 
    must be cached for display in web UI report, because query can be time 
    consuming.  Populated by find_unmapped_labs.py.
    '''
    native_code = models.CharField(max_length=100, blank=False)
    native_name = models.CharField(max_length=255, blank=False)
    count = models.IntegerField(blank=False)



#===============================================================================
#
# Case Validator Models
#
#-------------------------------------------------------------------------------

class ReferenceCaseList(models.Model):
    '''
    A group of reference cases loaded from the same source.
    '''
    source = models.CharField(max_length=255, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return 'List # %s' % self.pk
    
    class Meta:
        verbose_name = 'Reference Case List'


class ReferenceCase(models.Model):
    '''
    A reference case -- provided from an external source (such as manual Health 
    Department reporting systems), this is presumed to be a known valid case.
    '''
    list = models.ForeignKey(ReferenceCaseList, blank=False)
    #
    # Data provided by Health Dept etc
    #
    patient = models.ForeignKey(Patient, blank=True, null=True) 
    condition = models.CharField(max_length=100, blank=False, db_index=True)
    date = models.DateField(blank=False, db_index=True)
    #
    ignore = models.BooleanField(default=False, db_index=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return '%s - %s - %s' % (self.condition, self.date, self.patient.mrn)
    
    class Meta:
        verbose_name = 'Reference Case'
    
    
class ValidatorRun(models.Model):
    '''
    One run of the validator tool.
    '''
    timestamp = models.DateTimeField(blank=False, auto_now_add=True)
    list = models.ForeignKey(ReferenceCaseList, blank=False)
    complete = models.BooleanField(blank=False, default=False) # Run is complete?
    related_margin = models.IntegerField(blank=False)
    #
    # Statistics
    #
    exact = models.IntegerField(blank=True, null=True)
    similar = models.IntegerField(blank=True, null=True)
    missing = models.IntegerField(blank=True, null=True)
    new = models.IntegerField(blank=True, null=True)
    #
    # Notes
    #
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return 'Run # %s' % self.pk
    
    class Meta:
        verbose_name = 'Validator Run'


class ValidatorResult(models.Model):
    run = models.ForeignKey(ValidatorRun, blank=False)
    ref_case = models.ForeignKey(ReferenceCase, blank=True, null=True)
    nodis_case = models.ForeignKey(Case, blank=True, null=True)
    disposition = models.CharField(max_length=30, blank=False, choices=DISPOSITIONS)
    #
    # ManyToManyFields populated only for missing cases
    #
    events = models.ManyToManyField(Event, blank=True, null=True)
    cases = models.ManyToManyField(Case, blank=True, null=True)
    lab_results = models.ManyToManyField(LabResult, blank=True, null=True)
    encounters = models.ManyToManyField(Encounter, blank=True, null=True)
    prescriptions = models.ManyToManyField(Prescription, blank=True, null=True)

    def nodis_case(self):
        if self.nodis_case_id:
            return Case.objects.get(pk=self.nodis_case_id)
        else:
            return None
    
    def condition(self):
        return self.ref_case.condition
    
    def date(self):
        return self.ref_case.date
        
    def patient(self):
        return self.ref_case.patient
    
    class Meta:
        verbose_name = 'Validator Result'
