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


from django.db import models

from ESP.conf.choices import EMR_SOFTWARE
from ESP.conf.choices import FORMAT_TYPES
from ESP.conf.choices import DEST_TYPES
from ESP.conf.choices import WORKFLOW_STATES

from ESP.static.models import Loinc
from ESP.static.models import Vaccine
from ESP.static.models import ImmunizationManufacturer



class CodeMap(models.Model):
    '''
    Map associating lab test native_code with a HEF event
    '''
    heuristic = models.SlugField(max_length=255, blank=False, db_index=True)
    native_code = models.CharField(max_length=100, blank=False, db_index=True)
    native_name = models.CharField(max_length=255, blank=True, null=True)
    threshold = models.FloatField(help_text='Positive numeric threshold (if relevant)', blank=True, null=True)
    output_code = models.CharField(max_length=100, blank=True, null=True, db_index=True)
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
        unique_together = ['native_code', 'heuristic']
    
    def __str__(self):
        msg = '%s (%s) --> %s' % (self.native_name, self.native_code, self.heuristic)
        if self.threshold:
            msg += ' (threshold %s)' % self.threshold
        return msg


class IgnoredCode(models.Model):
    '''
    Codes to be ignored by nodis.core.Condition.find_unmapped_tests()
    '''
    native_code = models.CharField(max_length=100, blank=False, unique=True)
    
    def __str__(self):
        return self.native_code



class NativeVaccine(models.Model):
    code = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    canonical_code = models.ForeignKey(Vaccine, null=True)

    def __unicode__(self):
        return u'%s' % self.name


class NativeManufacturer(models.Model):
    name = models.CharField(max_length=200, unique=True)
    canonical_code = models.ForeignKey(ImmunizationManufacturer, null=True)

    def __unicode__(self):
        return u'%s' % self.name

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#--- Nodis Configuration
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

STATUS_CHOICES = [
    ('AR', 'Awaiting Review'),
    ('UR', 'Under Review'),
    ('RM', 'Review by MD'),
    ('FP', 'False Positive - Do NOT Process'),
    # Only fields before this point will be included in on-screen case status menu
    ('Q',  'Confirmed Case, Transmit to Health Department'), 
    ('S',  'Transmitted to Health Department'),
    ('NO', 'Do NOT send cases'),
    ]


class ConditionConfig(models.Model):
    '''
    A condition detected by Nodis.  Currently this model is used only for 
    controlling the initial status of newly created cases.
    '''
    name = models.CharField(max_length=255, primary_key=True)
    initial_status = models.CharField(max_length=8, choices=STATUS_CHOICES, blank=False, default='AR')



class ReportableLab(models.Model):
    '''
    Additional lab tests to be reported for a given condition, in addition to 
    those tests which are mapped to heuristics included in the condition's 
    definition.
    '''
    condition = models.CharField(max_length=255, blank=False, db_index=True)
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
        verbose_name = 'Code Map'
        unique_together = ['native_code', 'condition']
    
    def __str__(self):
        msg = '%s (%s) --> %s' % (self.native_name, self.native_code, self.condition)
        return msg


