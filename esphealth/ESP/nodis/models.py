'''
                                  ESP Health
                         Notifiable Diseases Framework
                                  Data Models
                                  
@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@contact: http://esphealth.org
@copyright: (c) 2009-2010 Channing Laboratory
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''

from django.db.models import Max
from ESP.static.models import Dx_code
#from ESP.conf.models import CodeMap
from ESP.conf.models import STATUS_CHOICES
from ESP.conf.models import ReportableLab
from ESP.conf.models import ReportableMedication
from ESP.emr.models import LabResult
#from ESP.hef.base import TimespanHeuristic
from ESP.hef.base import BaseLabResultHeuristic, LabResultPositiveHeuristic
from ESP.hef.base import DiagnosisHeuristic
from ESP.hef.models import Timespan
from ESP.conf.models import ConditionConfig

from django.contrib.contenttypes.models import ContentType

import datetime

from django.db import models
from django.db.models import Q

from ESP.emr.models import Encounter
from ESP.emr.models import LabResult
from ESP.emr.models import Patient
from ESP.emr.models import Prescription
from ESP.emr.models import Provider
from ESP.hef.models import Event
from ESP.conf.models import LabTestMap, ResultString

from ESP.utils.utils import log
from ESP.utils.utils import log_query



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
DISPOSITIONS = [
    ('exact', 'Exact'),
    ('similar', 'Similar'),
    ('missing', 'Missing'),
    ('new', 'New'),
    ]


#-------------------------------------------------------------------------------
#
#--- Exceptions
#
#-------------------------------------------------------------------------------

class NodisException(BaseException):
    '''
    A Nodis-specific error
    '''

class InvalidPattern(NodisException):
    '''
    Could not understand the specified pattern
    '''


class InvalidHeuristic(NodisException):
    '''
    You specified a heuristic that is not registered with the system.
    '''


#-------------------------------------------------------------------------------
#
#--- Pattern Matching Logic
#
#-------------------------------------------------------------------------------




class Case(models.Model):
    '''
    A case of (reportable) disease
    '''
    condition = models.CharField('Common English name for this medical condition', 
        max_length=100, blank=False, db_index=True)
    date = models.DateField(blank=False, db_index=True)
    patient = models.ForeignKey(Patient, blank=False)
    provider = models.ForeignKey(Provider, blank=False)
    criteria = models.CharField('Criteria on which case was diagnosed', 
        max_length=500, blank=True, null=True, db_index=True)
    source = models.CharField('What algorithm created this case?', 
        max_length=255, blank=False)
    status = models.CharField('Case status', max_length=32, 
        blank=False, choices=STATUS_CHOICES, default='AR')
    notes = models.TextField(blank=True, null=True)
    # Timestamps:
    created_timestamp = models.DateTimeField(auto_now_add=True, blank=False)
    updated_timestamp = models.DateTimeField(auto_now=True, blank=False)
    sent_timestamp = models.DateTimeField(blank=True, null=True)
    #
    # Events that define this case
    #
    events = models.ManyToManyField(Event, blank=False)
    timespans = models.ManyToManyField(Timespan, blank=False)

    class Meta:
        permissions = [ ('view_phi', 'Can view protected health information'), ]
        unique_together = ['patient', 'condition', 'date', 'source']
        ordering = ['id']

    def __get_condition_config(self):
        '''
        Return the ConditionConfig object for this case's condition
        '''
        config = ConditionConfig.objects.filter(name=self.condition)
        if not config:
            log.warning('Please setup a Configuration for the condition for %s', self.condition)
            return None
        else: return config[0]
        
    condition_config = property(__get_condition_config)

    def __get_first_provider(self):
        '''
        Provider for chronologically first event
        '''
        return self.events.all().order_by('date')[0].tag_set.all()[0].content_object.provider
    first_provider = property(__get_first_provider)

    #
    # Events by class
    #
    def __get_all_events(self):
        # This method was formerly necessary because there were events before, 
        # after etc.  It is no longer required but retained for compatibility.
        return self.events.all()
    all_events = property(__get_all_events)

    def __get_lab_results(self):
        return LabResult.objects.filter(events__in=self.all_events).order_by('date')
    lab_results = property(__get_lab_results)

    def __get_encounters(self):
        return Encounter.objects.filter(events__in=self.all_events).order_by('date')
    encounters = property(__get_encounters)

    def __get_prescriptions(self):
        return Prescription.objects.filter(events__in=self.all_events).order_by('date')
    prescriptions = property(__get_prescriptions)

    def __get_reportable_labs(self):
        from ESP.nodis.base import DiseaseDefinition
        reportable_codes = set(ReportableLab.objects.filter(condition=self.condition).values_list('native_code', flat=True))
        # get native codes from lab heuristics
        for heuristic in DiseaseDefinition.get_by_short_name(self.condition).event_heuristics:
            if isinstance(heuristic, BaseLabResultHeuristic):
                reportable_codes |=set(LabTestMap.objects.filter(test_name =heuristic.test_name, reportable=True).values_list('native_code', flat=True))
        q_obj = Q(patient=self.patient)
        q_obj &= Q(native_code__in=reportable_codes)
        conf = self.condition_config
        if conf:
            start = self.date - datetime.timedelta(days=conf.lab_days_before)
            end = self.date + datetime.timedelta(days=conf.lab_days_after)
        else:
            start = self.date
            end = self.date 
        q_obj &= Q(date__gte=start)
        q_obj &= Q(date__lte=end)
        labs = LabResult.objects.filter(q_obj).distinct()
        #log_query('Reportable labs for %s' % self, labs)
        # this will affect case reports and 
        if not labs and not self.lab_results and self.condition.upper() == 'TUBERCULOSIS':
            labs = LabResult.objects.none()
            # new feature redmine 482
            # This code is used for case report hl7 and case detail view 
            # specific for MDPH specific which requires one lab for TB 
            # if there are no reportable labs or labs associated with a case
            # we create a dummy one.
            dummy_lab = LabResult.createTBDummyLab(self.patient, [self])
            labs._result_cache.append(dummy_lab)
                           
        return labs
    
    reportable_labs = property(__get_reportable_labs)

    @property
    def reportable_dx_codes(self):
        
        if self.reportable_encounters:
            return Dx_code.objects.filter(encounter__in=self.reportable_encounters)
        return None
   
    def __get_reportable_dx_codes(self):
        
        from ESP.nodis.base import DiseaseDefinition
        
        conf = self.condition_config
        if conf:
            dx_code_objs = Dx_code.objects.filter(reportabledx_code__condition=conf)
        else:
            dx_code_objs = None
        disease_def_event_heuristics = DiseaseDefinition.get_by_short_name(self.condition).event_heuristics
        for heuristic in  disease_def_event_heuristics:
            if isinstance(heuristic, DiagnosisHeuristic):
                
                for dx_code_query in heuristic.dx_code_queries:
                    if not dx_code_objs:
                        dx_code_objs = Dx_code.objects.filter( dx_code_query.dx_code_q_obj)
                    else: dx_code_objs |= Dx_code.objects.filter(dx_code_query.dx_code_q_obj)
        if  dx_code_objs:
            return dx_code_objs.distinct()
        return None
    reportable_dx_codes_list = property(__get_reportable_dx_codes)

    def __get_reportable_encounters(self):
        q_obj = Q(patient=self.patient)
        if self.reportable_dx_codes_list:
            q_obj &= Q(dx_codes__in=self.reportable_dx_codes_list)
        conf = self.condition_config
        if conf:
            start = self.date - datetime.timedelta(days=conf.dx_code_days_before)
            end = self.date + datetime.timedelta(days=conf.dx_code_days_after)
        else:
            start = self.date
            end = self.date 
        q_obj &= Q(date__gte=start)
        q_obj &= Q(date__lte=end)
        encs = Encounter.objects.filter(q_obj)
        #log_query('Encounters for %s' % self, encs)
        return encs
    reportable_encounters = property(__get_reportable_encounters)

    def __get_reportable_prescriptions(self):
        conf = self.condition_config
        
        from ESP.nodis.base import DiseaseDefinition
        med_names = DiseaseDefinition.get_by_short_name(self.condition).medications
        med_names |= set(ReportableMedication.objects.filter(condition=conf).values_list('drug_name', flat=True))
        if not med_names:
            return Prescription.objects.none()
        med_names = list(med_names)
        q_obj = Q(name__icontains=med_names[0])
        for med in med_names:
            q_obj |= Q(name__icontains=med)
        q_obj &= Q(patient=self.patient)
        if conf:
            start = self.date - datetime.timedelta(days=conf.med_days_before)
            end = self.date + datetime.timedelta(days=conf.med_days_after)
        else:
            start = self.date
            end = self.date
        q_obj &= Q(date__gte=start)
        q_obj &= Q(date__lte=end)
        prescriptions = Prescription.objects.filter(q_obj).distinct()
        #log_query('Reportable prescriptions for %s' % self, prescriptions)
        return prescriptions
    reportable_prescriptions = property(__get_reportable_prescriptions)

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

    def __get_collection_date(self):
        '''
        Returns the earliest specimen collection date
        '''
        if self.lab_results:
            return self.lab_results.aggregate(maxdate=Max('collection_date'))['maxdate']
        else:
            return None
    collection_date = property(__get_collection_date)

    def __get_result_date(self):
        '''
        Returns the earliest specimen collection date
        '''
        if self.lab_results:
            return self.lab_results.aggregate(maxdate=Max('result_date'))['maxdate']
        else:
            return None
    result_date = property(__get_result_date)

    

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
        verbose_name_plural = 'Case Status Histories'


class ReportRun(models.Model):
    '''
    A run of the case_report command
    '''
    timestamp = models.DateTimeField(auto_now=True)
    hostname = models.CharField('Host on which data was loaded', max_length=255, blank=False)



class Report(models.Model):
    '''
    A reporting message generated from one or more Case objects
    '''
    timestamp = models.DateTimeField(auto_now=True, blank=False)
    run = models.ForeignKey(ReportRun, blank=False)
    cases = models.ManyToManyField(Case, blank=False)
    filename = models.CharField(max_length=512, blank=False)
    sent = models.BooleanField('Case status was set to sent?', default=False)
    message = models.TextField('Case report message', blank=False)


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
    # Notes
    #
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return 'Run # %s' % self.pk

    class Meta:
        verbose_name = 'Validator Run'

    def __get_results(self):
        q_obj = Q(run=self) & ~Q(ref_case__ignore=True)
        qs = ValidatorResult.objects.filter(q_obj)
        #log_query('Validator results', qs)
        return qs
    results = property(__get_results)

    def __get_missing(self):
        return self.results.filter(disposition='missing')
    missing = property(__get_missing)

    def __get_exact(self):
        return self.results.filter(disposition='exact')
    exact = property(__get_exact)

    def __get_similar(self):
        return self.results.filter(disposition='similar')
    similar = property(__get_similar)

    def __get_new(self):
        return self.results.filter(disposition='new')
    new = property(__get_new)

    def __get_ignored(self):
        return ValidatorResult.objects.filter(run=self, ref_case__ignore=True)
    ignored = property(__get_ignored)

    def percent_ignored(self):
        return 100.0 * float(self.ignored.count()) / self.results.count()

    def percent_exact(self):
        return 100.0 * float(self.exact.count()) / self.results.count()

    def percent_similar(self):
        return 100.0 * float(self.similar.count()) / self.results.count()

    def percent_missing(self):
        return 100.0 * float(self.missing.count()) / self.results.count()

    def percent_new(self):
        return 100.0 * float(self.new.count()) / self.results.count()

    @classmethod
    def latest(cls):
        '''
        Return the most recent complete ValidatorRun
        '''
        return cls.objects.filter(complete=True).order_by('-timestamp')[0]


class ValidatorResult(models.Model):
    run = models.ForeignKey(ValidatorRun, blank=False)
    ref_case = models.ForeignKey(ReferenceCase, blank=True, null=True)
    condition = models.CharField(max_length=100, blank=False, db_index=True)
    date = models.DateField(blank=False, db_index=True)
    disposition = models.CharField(max_length=30, blank=False, choices=DISPOSITIONS)
    #
    # ManyToManyFields populated only for missing cases
    #
    events = models.ManyToManyField(Event, blank=True, null=True)
    cases = models.ManyToManyField(Case, blank=True, null=True)
    lab_results = models.ManyToManyField(LabResult, blank=True, null=True)
    encounters = models.ManyToManyField(Encounter, blank=True, null=True)
    prescriptions = models.ManyToManyField(Prescription, blank=True, null=True)

    def patient(self):
        return self.ref_case.patient

    class Meta:
        verbose_name = 'Validator Result'

    def __str__(self):
        return 'Result # %s' % self.pk

    def date_diff(self):
        '''
        For 'similar' cases, date_diff() returns the difference between the 
        reference case date and the ESP case date.
        '''
        if not self.disposition == 'similar':
            raise RuntimeError('date_diff() makes sense only for "similar" cases')
        return self.ref_case.date - self.cases.all()[0].date
