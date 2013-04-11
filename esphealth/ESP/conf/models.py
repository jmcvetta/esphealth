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
from django.db.models import Q

from ESP.conf.choices import DEST_TYPES
from ESP.conf.choices import EMR_SOFTWARE
from ESP.conf.choices import FORMAT_TYPES
from ESP.conf.choices import WORKFLOW_STATES
from ESP.static.models import Icd9
from ESP.static.models import ImmunizationManufacturer
from ESP.static.models import Loinc
from ESP.static.models import Vaccine

POSITIVE_STRINGS = ['reactiv', 'pos', 'detec', 'confirm']
NEGATIVE_STRINGS = ['non', 'neg', 'not det', 'nr']
INDETERMINATE_STRINGS = ['indeterminate', 'not done', 'tnp']

POS_NEG_IND = [
    ('pos', 'Positive'),
    ('neg', 'Negative'),
    ('ind', 'Indeterminate'),
    ]

DATE_FIELD_CHOICES = [
    ('order', 'Order'),
    ('result', 'Result')
    ]

DOSE_UNIT_CHOICES = [
    ('ml', 'Milliliters'),
    ('mg', 'Milligrams'),
    ('g', 'Grams'),
    ('ug', 'Micrograms'),
    ]

DOSE_UNIT_VARIANTS = {
    'ml': ['milliliter', 'ml'],
    'g': ['gram', 'g', 'gm'],
    'mg': ['milligram', 'mg'],
    'ug': ['microgram', 'mcg', 'ug'],
    }

GT_CHOICES = [
    ('gte', 'Greater Than or Equal To: >='),
    ('gt', 'Greater Than: >'),
    ]

LT_CHOICES = [
    ('lte', 'Less Than or Equal To: <='),
    ('lt', 'Less Than: <'),
    ]

TITER_DILUTION_CHOICES = [
    (1, '1:1'),  
    (2, '1:2'),
    (4, '1:4'),
    (8, '1:8'),
    (16, '1:16'),
    (32, '1:32'),
    (64, '1:64'),
    (128, '1:128'),
    (256, '1:256'),
    (512, '1:512'),
    (1024, '1:1024'),
    (2048, '1:2048'),
    ]

MATCH_TYPE_CHOICES = [
    ('exact', 'Exact Match (case sensitive)'),
    ('iexact', 'Exact Match (NOT case sensitive)'),
    ('startswith', 'Starts With (case sensitive)'),
    ('istartswith', 'Starts With (NOT case sensitive)'),
    ('endswith', 'Ends With (case sensitive)'),
    ('iendswith', 'Ends With (NOT case sensitive)'),
    ('contains', 'Contains (case sensitive)'),
    ('icontains', 'Contains (NOT case sensitive)'),
    ]

ORDER_RESULT_RECORD_TYPES = [
    ('order', 'Lab Test Orders'),
    ('result', 'Lab Test Results'),
    ('both', 'Both Lab Test Orders and Results'),
    ]



class ResultString(models.Model):
    '''
    A string indicating a positive, negative, or indeterminate lab result
    '''
    value = models.CharField(max_length=128, blank=False)
    indicates = models.CharField(max_length=8, blank=False, choices=POS_NEG_IND)
    match_type = models.CharField(max_length=32, blank=False, choices=MATCH_TYPE_CHOICES, 
        help_text='Match type for string', default='istartswith')
    applies_to_all = models.BooleanField(blank=False, default=False, 
        help_text='Match this string for ALL tests.  If not checked, string must be explicitly specified in Lab Test Map')
    
    class Meta:
        ordering = ['value']
        verbose_name = 'Result String'
    
    def __unicode__(self):
        return u'%s ' % (self.value)
    
    def __get_q_obj(self):
        '''
        Returns a Q object to search for this result string
        '''
        if self.match_type == 'exact':
            return Q(result_string__exact=self.value)
        elif self.match_type == 'iexact':
            return Q(result_string__iexact=self.value)
        elif self.match_type == 'startswith':
            return Q(result_string__startswith=self.value)
        elif self.match_type == 'istartswith':
            return Q(result_string__istartswith=self.value)
        elif self.match_type == 'endswith':
            return Q(result_string__endswith=self.value)
        elif self.match_type == 'iendswith':
            return Q(result_string__iendswith=self.value)
        elif self.match_type == 'contains':
            return Q(result_string__contains=self.value)
        elif self.match_type == 'icontains':
            return Q(result_string__icontains=self.value)
    q_obj = property(__get_q_obj)
    
    @classmethod
    def get_q_by_indication(cls, indicates):
        '''
        Returns a Q object for result strings that apply to all labs and 
        indicate the specified outcome.
        @param indicates: Get result strings that indicate this outcome (must 
            be one of (pos, neg, ind)
        @type indicates: String
        @rtype: Q
        '''
        assert indicates in ['pos', 'neg', 'ind'] # Sanity check
        rs_qs = ResultString.objects.filter(indicates=indicates, applies_to_all=True)
        q_obj = rs_qs[0].q_obj
        for rs in rs_qs[1:]:
            q_obj |= rs.q_obj
        return q_obj


class LabTestMap(models.Model):
    '''
    Mapping object to associate an abstract lab test type with a concrete, 
    source-EMR-specific lab test type
    '''
    test_name = models.SlugField('Name of Abstract Lab Test', blank=False, db_index=True)
    native_code = models.CharField(max_length=100, verbose_name='Test Code', db_index=True,
        help_text='Native test code from source EMR system', blank=False)
    code_match_type = models.CharField(max_length=32, blank=False, choices=MATCH_TYPE_CHOICES, 
        help_text='Match type for test code', default='exact')
    record_type = models.CharField(max_length=8, blank=False, choices=ORDER_RESULT_RECORD_TYPES, 
        help_text='Does this map relate to lab orders, results, or both?', default='both')
    threshold = models.FloatField(help_text='Fallback positive threshold for tests without reference high', blank=True, null=True)
    extra_positive_strings = models.ManyToManyField(ResultString, blank=True, null=True, related_name='extra_positive_set',
        limit_choices_to={'indicates': 'pos', 'applies_to_all': False})
    excluded_positive_strings = models.ManyToManyField(ResultString, blank=True, null=True, related_name='excluded_positive_set',
        limit_choices_to={'indicates': 'pos', 'applies_to_all': True})
    extra_negative_strings = models.ManyToManyField(ResultString, blank=True, null=True, related_name='extra_negative_set',
        limit_choices_to={'indicates': 'neg', 'applies_to_all': False})
    excluded_negative_strings = models.ManyToManyField(ResultString, blank=True, null=True, related_name='excluded_negative_set',
        limit_choices_to={'indicates': 'neg', 'applies_to_all': True})
    extra_indeterminate_strings = models.ManyToManyField(ResultString, blank=True, null=True, related_name='extra_indeterminate_set',
        limit_choices_to={'indicates': 'ind', 'applies_to_all': False})
    excluded_indeterminate_strings = models.ManyToManyField(ResultString, blank=True, null=True, related_name='excluded_indeterminate_set',
        limit_choices_to={'indicates': 'ind', 'applies_to_all': True})
    #
    # Reporting
    # 
    reportable = models.BooleanField('Is test reportable?', default=True, db_index=True)
    output_code = models.CharField('Test code for template output', max_length=100, blank=True, null=True)
    output_name = models.CharField('Test name for template output', max_length=255, blank=True, null=True)
    snomed_pos = models.CharField('SNOMED positive code', max_length=255, blank=True, null=True)
    snomed_neg = models.CharField('SNOMED neg code', max_length=255, blank=True, null=True)
    snomed_ind = models.CharField('SNOMED indeterminate code', max_length=255, blank=True, null=True)
    #
    # Notes
    #
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Lab Test Map'
        unique_together = ['test_name', 'native_code', 'code_match_type', 'record_type']
    
    def __str__(self):
        return u'LabTestMap (%s --> %s)' % (self.native_code, self.test_name)
    
    def __get_lab_results_q_obj(self):
        if self.code_match_type == 'exact':
            return Q(native_code__exact=self.native_code)
        elif self.code_match_type == 'iexact':
            return Q(native_code__iexact=self.native_code)
        elif self.code_match_type == 'startswith':
            return Q(native_code__startswith=self.native_code)
        elif self.code_match_type == 'istartswith':
            return Q(native_code__istartswith=self.native_code)
        elif self.code_match_type == 'endswith':
            return Q(native_code__endswith=self.native_code)
        elif self.code_match_type == 'iendswith':
            return Q(native_code__iendswith=self.native_code)
        elif self.code_match_type == 'contains':
            return Q(native_code__contains=self.native_code)
        elif self.code_match_type == 'icontains':
            return Q(native_code__icontains=self.native_code)
    lab_results_q_obj = property(__get_lab_results_q_obj)
    
    def __get_lab_orders_q_obj(self):
        #
        # 'procedure_master_num' is a crappy field name, and needs to be changed
        # jason renamed to procedure_code
        if self.code_match_type == 'exact':
            return Q(procedure_code__exact=self.native_code)
        elif self.code_match_type == 'iexact':
            return Q(procedure_code__iexact=self.native_code)
        elif self.code_match_type == 'startswith':
            return Q(procedure_code__startswith=self.native_code)
        elif self.code_match_type == 'istartswith':
            return Q(procedure_code__istartswith=self.native_code)
        elif self.code_match_type == 'endswith':
            return Q(procedure_code__endswith=self.native_code)
        elif self.code_match_type == 'iendswith':
            return Q(procedure_code__iendswith=self.native_code)
        elif self.code_match_type == 'contains':
            return Q(procedure_code__contains=self.native_code)
        elif self.code_match_type == 'icontains':
            return Q(procedure_code__icontains=self.native_code)
    lab_orders_q_obj = property(__get_lab_orders_q_obj)
    
    @property
    def positive_string_q_obj(self):
        rs_qs = self.extra_positive_strings.all()
        if self.excluded_positive_strings.all():
            rs_qs = rs_qs.exclude(self.excluded_positive_strings.all())
        q_obj = ResultString.get_q_by_indication('pos')
        for rs in rs_qs:
            q_obj |= rs.q_obj
        return q_obj
    
    @property
    def negative_string_q_obj(self):
        rs_qs = self.extra_negative_strings.all()
        if self.excluded_negative_strings.all():
            rs_qs = rs_qs.exclude(self.excluded_negative_strings.all())
        q_obj = ResultString.get_q_by_indication('neg')
        for rs in rs_qs:
            q_obj |= rs.q_obj
        return q_obj
    
    @property
    def indeterminate_string_q_obj(self):
        rs_qs = self.extra_indeterminate_strings.all()
        if self.excluded_indeterminate_strings.all():
            rs_qs = rs_qs.exclude(self.excluded_indeterminate_strings.all())
        q_obj = ResultString.get_q_by_indication('ind')
        for rs in rs_qs:
            q_obj |= rs.q_obj
        return q_obj


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
    native_code = models.CharField(max_length=128)
    native_name = models.CharField(max_length=200)
    canonical_code = models.ForeignKey(Vaccine, null=True)

    def __unicode__(self):
        return u'%s' % self.native_name


class VaccineManufacturerMap(models.Model):
    '''
    Maps native manufacturer name to canonical manufacturer code for use in reporting 
    '''
    native_name = models.CharField(max_length=200, unique=True)
    canonical_code = models.ForeignKey(ImmunizationManufacturer, null=True)

    def __unicode__(self):
        return u'%s' % self.name
    
class ImmuExclusion(models.Model):
    '''
    Provides a set of names identified as non-immunizations.
    '''
    non_immu_name = models.CharField(max_length=200, unique=True)

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
