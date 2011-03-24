'''
                                  ESP Health
                              Site Configuration
                                  Data Models


@author: Jason McVetta <jason.mcvetta@gmail.com>
@author: Raphael Lullis <raphael.lullis@channing.harvard.edu>
@organization: Channing Laboratory <http://www.channing.harvard.edu>
@copyright: (c) 2009 Channing Laboratory
@license: LGPL 3.0 <http://www.gnu.org/licenses/lgpl-3.0.txt>
'''


from ESP.conf.choices import DEST_TYPES
from ESP.conf.choices import EMR_SOFTWARE
from ESP.conf.choices import FORMAT_TYPES
from ESP.conf.choices import WORKFLOW_STATES
from ESP.static.models import Icd9
from ESP.static.models import ImmunizationManufacturer
from ESP.static.models import Loinc
from ESP.static.models import Vaccine
from django.db import models



class CodeMap(models.Model):
    '''
    Map associating lab test native_code with a HEF event
    '''
    heuristic = models.SlugField(max_length=255, blank=False, db_index=True)
    test_uri = models.TextField('URI for Abstract Lab Test', blank=False, db_index=True)
    native_code = models.CharField(max_length=100, blank=False, db_index=True)
    native_name = models.CharField(max_length=255, blank=True, null=True)
    threshold = models.FloatField(help_text='Numeric threshold for positive test', blank=True, null=True)
    output_code = models.CharField('Test code for template output', max_length=100, blank=True, null=True, db_index=True)
    output_name = models.CharField('Test name for template output', max_length=255, blank=True, null=True)
    #
    # Reporting
    # 
    reportable = models.BooleanField('Is test reportable?', default=True, db_index=True)
    snomed_pos = models.CharField('SNOMED positive code', max_length=255, blank=True, null=True)
    snomed_neg = models.CharField('SNOMED neg code', max_length=255, blank=True, null=True)
    snomed_ind = models.CharField('SNOMED indeterminate code', max_length=255, blank=True, null=True)
    #
    # Notes
    #
    notes = models.TextField(blank=True, null=True)
    class Meta:
        verbose_name = 'Code Map'
        #unique_together = ['test_uri', 'native_code']
    
    def __str__(self):
        msg = '%s (%s) --> %s' % (self.native_name, self.native_code, self.heuristic_uri)
        if self.threshold:
            msg += ' (threshold %s)' % self.threshold
        return msg


class IgnoredCode(models.Model):
    '''
    Codes to be ignored by nodis.model.Condition.find_unmapped_tests()
    '''
    native_code = models.CharField(max_length=100, blank=False, unique=True)
    
    def __str__(self):
        return self.native_code
    
    class Meta:
        verbose_name = 'Ignored Test Code'



class VaccineCodeMap(models.Model):
    '''
    Maps native vaccine code to canonical vaccine code for use in reporting 
    '''
    native_code = models.CharField(max_length=128, unique=True)
    native_name = models.CharField(max_length=200)
    canonical_code = models.ForeignKey(Vaccine, null=True)

    def __unicode__(self):
        return u'%s' % self.name


class VaccineManufacturerMap(models.Model):
    '''
    Maps native manufacturer name to canonical manufacturer code for use in reporting 
    '''
    native_name = models.CharField(max_length=200, unique=True)
    canonical_code = models.ForeignKey(ImmunizationManufacturer, null=True)

    def __unicode__(self):
        return u'%s' % self.name

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#--- Nodis Configuration
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

STATUS_CHOICES = [
    ('AR', 'AR - Awaiting Review'),
    ('UR', 'UR - Under Review'),
    ('RM', 'RM - Review by MD'),
    ('FP', 'FP - False Positive - Do NOT Process'),
    # Only fields before this point will be included in on-screen case status menu
    ('Q',  'Q - Confirmed Case, Transmit to Health Department'), 
    ('S',  'S - Transmitted to Health Department'),
    ('NO', 'NO - Do NOT send cases'),
    ]


class ConditionConfig(models.Model):
    '''
    Reporting configuration for a Nodis condition.
    '''
    name = models.CharField('Condition Name', max_length=255, primary_key=True)
    initial_status = models.CharField(max_length=8, choices=STATUS_CHOICES, blank=False, default='AR')
    lab_days_before = models.IntegerField(blank=False, default=28)
    lab_days_after = models.IntegerField(blank=False, default=28)
    icd9_days_before = models.IntegerField(blank=False, default=28)
    icd9_days_after = models.IntegerField(blank=False, default=28)
    med_days_before = models.IntegerField(blank=False, default=28)
    med_days_after = models.IntegerField(blank=False, default=28)
    
    class Meta:
        verbose_name = 'Condition Configuration'
    
    def __str__(self):
        return self.name


class ReportableLab(models.Model):
    '''
    Additional lab tests to be reported for a given condition, in addition to 
    those tests which are mapped to heuristics included in the condition's 
    definition.
    '''
    condition = models.ForeignKey(ConditionConfig, blank=False)
    native_code = models.CharField(max_length=100, blank=False, db_index=True)
    native_name = models.CharField(max_length=255, blank=True, null=True)
    output_code = models.CharField(max_length=100, blank=False, db_index=True)
    #
    # Reporting
    # 
    snomed_pos = models.CharField('SNOMED positive code', max_length=255, blank=True, null=True)
    snomed_neg = models.CharField('SNOMED neg code', max_length=255, blank=True, null=True)
    snomed_ind = models.CharField('SNOMED indeterminate code', max_length=255, blank=True, null=True)
    #
    # Notes
    #
    notes = models.TextField(blank=True, null=True)
    class Meta:
        unique_together = ['native_code', 'condition']
        verbose_name = 'Reportable Lab Test'
    
    def __str__(self):
        msg = '%s (%s) --> %s' % (self.native_name, self.native_code, self.condition)
        return msg


class ReportableIcd9(models.Model):
    '''
    Additional ICD9 codes to be reported for a given condition, in addition to 
    those tests which are mapped to heuristics included in the condition's 
    definition.
    '''
    condition = models.ForeignKey(ConditionConfig, blank=False)
    icd9 = models.ForeignKey(Icd9, blank=False)
    #
    # Notes
    #
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ['icd9', 'condition']
        verbose_name = 'Reportable ICD9 Code'
    
    def __str__(self):
        return '%s (%s)' % (self.icd9.code, self.condition)


class ReportableMedication(models.Model):
    '''
    Additional medications to be reported for a given condition, in addition to 
    those tests which are mapped to heuristics included in the condition's 
    definition.
    '''
    condition = models.ForeignKey(ConditionConfig, blank=False)
    drug_name = models.CharField(blank=False, max_length=255)
    #
    # Notes
    #
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ['drug_name', 'condition']
        verbose_name = 'Reportable Medication'

    def __str__(self):
        return '%s (%s)' % (self.drug_name, self.condition)
