'''
                                  ESP Health
                                 Static Tables
                                  Data Models


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory <http://www.channing.harvard.edu>
@copyright: (c) 2009 Channing Laboratory
@license: LGPL 3.0 <http://www.gnu.org/licenses/lgpl-3.0.txt>
'''

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# DEVELOPER NOTE:
#
# These models should not depend upon ANY other modules, except the Django core.
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


from django.db import models

class FakeMeds (models.Model):
    '''
     this is for our new extra med table 
    '''
    def _get_name(self):
    
        #Returns long common name if available, falling back to short name.
        
        if  self.long_name:
            return self.long_name
        else:
            return self.ndc_code
        
    name = property(_get_name)
   
    fakemeds_id = models.AutoField(primary_key=True)
    long_name = models.TextField(blank=True, null=True)
    ndc_code = models.TextField(blank=True, null=True)  
    route = models.TextField(blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)

    class Meta:
        verbose_name = 'FAKEMEDS'

    def __str__(self):
        return '%s -- %s' % (self.fakemeds_id, self.name)
    
 
class DrugSynonym (models.Model):
    '''
     this is for finding the right med name for the disease detection  
    '''
   
    drugynonym_id = models.AutoField(primary_key=True)
    generic_name = models.CharField('Generic name', max_length=100)
    other_name = models.CharField('Other name', max_length=100)
    comment = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Drug Synonym'
    
    @staticmethod
    def generics_plus_synonyms(drugnames):
        alldrugnames = drugnames
        for drug in drugnames:
            alldrugsqs= DrugSynonym.objects.filter(generic_name__icontains = drug)
            for otherdrug in alldrugsqs:
                if not otherdrug.comment == 'Self':
                    alldrugnames.append(otherdrug.other_name)
        return alldrugnames
    
    def __str__(self):
        return '%s -- %s' % (self.drugynonym_id, self.generic_name)
     
class FakeICD9s(models.Model):
    fakeicd9_id = models.AutoField(primary_key=True)
    icd9_codes = models.CharField('icd9_codes', max_length=3350)
    group_name = models.CharField('group_name', max_length=100)
    list_length = models.IntegerField(blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)

    def __str__(self):
        return '%s -- %s' % (self.group_name, self.icd9_codes)
    
    class Meta:
        verbose_name = 'FAKEICD9'


class FakeAllergen(models.Model):
    code = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=300, blank=True, null=True)
    
    def __str__(self):
        return '%s -- %s' % (self.code, self.name)
    
    class Meta:
        verbose_name = 'FAKEALLELRGEN'
    
    
class FakeLabs (models.Model):
    '''
     this is for our new extra lab table 
    '''
    def _get_name(self):
    
        #Returns long common name if available, falling back to short name.
        
        if self.long_name:
            return self.long_name
        elif self.short_name:
            return self.short_name
        else:
            return self.native_code
    name = property(_get_name)
   
    fakelabs_id = models.AutoField(primary_key=True)
    native_code = models.TextField(blank=True, null=True)
    native_name = models.TextField(blank=True, null=True)
    long_name = models.TextField(blank=True, null=True)
    test_sub_category = models.CharField('Test Sub category', max_length=100,blank=True, null=True)
    loinc = models.CharField('LOINC', max_length=100,blank=True, null=True)
    loinc_flag = models.CharField('LOINC flag', max_length=100,blank=True, null=True)
    specimen_source = models.CharField('Specimen Source', max_length=100,blank=True, null=True)
    units_ms = models.CharField('MS Result Units', max_length=100,blank=True, null=True)
    conversion_factor= models.FloatField('Conversion factor', blank=True, null=True)
    units_std = models.CharField('Std Result Units', max_length=100,blank=True, null=True)
    units = models.TextField(blank=True, null=True)
    px = models.CharField('PX', max_length=100,blank=True, null=True)
    px_type = models.CharField('PX code type', max_length=100,blank=True, null=True)
    datatype = models.TextField(blank=True, null=True)
    normal_low = models.FloatField(blank=True, null=True)
    normal_high = models.FloatField(blank=True, null=True)
    critical_low = models.FloatField(blank=True, null=True)
    critical_high = models.FloatField(blank=True, null=True)
    qual_orig = models.TextField('Qualitative values',blank=True, null=True) 
    qual_map =models.TextField('Qualitative map values',blank=True, null=True) 
    cpt_code = models.TextField(blank=True, null=True)  
    weight = models.FloatField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'FAKELABS'

    def __str__(self):
        return '%s -- %s' % (self.fakelabs_id, self.name)
    
    
class FakeVitals (models.Model):
    '''
     this is for our new extra vitals table 
    '''
    def _get_name(self):
    
        #Returns  short name.
        
        return self.short_name
        
    name = property(_get_name)
   
    fakevitals_id = models.AutoField(primary_key=True)
    short_name = models.TextField(blank=True, null=True)
    long_name = models.TextField(blank=True, null=True)
    normal_low = models.FloatField(blank=True, null=True)
    normal_high = models.FloatField(blank=True, null=True)
    units = models.TextField(blank=True, null=True)
    very_low = models.FloatField(blank=True, null=True)
    very_high = models.FloatField(blank=True, null=True)
    

    class Meta:
        verbose_name = 'FAKEVITALS'

    def __str__(self):
        return '%s -- %s' % (self.fakevitals_id, self.name)
        
class Loinc(models.Model):
    '''
    Logical Observation Identifiers Names and Codes
        Derived from RELMA database available at 
        http://loinc.org/downloads
    '''
    # This has to be come before field definitions, because there is a field 
    # named 'property' that, since they live in the same namespace, clashes with
    # the built-in method 'property()'.  
    def _get_name(self):
        '''
        Returns long common name if available, falling back to short name.
        '''
        if self.long_common_name:
            return self.long_common_name
        elif self.shortname:
            return self.shortname
        else:
            return self.component
    name = property(_get_name)
    
    #
    # The structure of this class mirrors exactly the schema of the LOINCDB.TXT 
    # file distributed by RELMA.
    #
    loinc_num = models.CharField(max_length=20, primary_key=True) # The LOINC code itself
    component = models.TextField(blank=True, null=True)
    property = models.TextField(blank=True, null=True)
    time_aspct = models.TextField(blank=True, null=True)
    system = models.TextField(blank=True, null=True)
    scale_typ = models.TextField(blank=True, null=True)
    method_typ = models.TextField(blank=True, null=True)
    relat_nms = models.TextField(blank=True, null=True)
    loinc_class_field = models.TextField(blank=True, null=True)
    source = models.TextField(blank=True, null=True)
    dt_last_ch = models.TextField(blank=True, null=True)
    chng_type = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    answerlist = models.TextField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    map_to = models.TextField(blank=True, null=True)
    scope = models.TextField(blank=True, null=True)
    norm_range = models.TextField(blank=True, null=True)
    ipcc_units = models.TextField(blank=True, null=True)
    reference = models.TextField(blank=True, null=True)
    exact_cmp_sy = models.TextField(blank=True, null=True)
    molar_mass = models.TextField(blank=True, null=True)
    classtype = models.TextField(blank=True, null=True)
    formula = models.TextField(blank=True, null=True)
    species = models.TextField(blank=True, null=True)
    exmpl_answers = models.TextField(blank=True, null=True)
    acssym = models.TextField(blank=True, null=True)
    base_name = models.TextField(blank=True, null=True)
    final = models.TextField(blank=True, null=True)
    naaccr_id = models.TextField(blank=True, null=True)
    code_table = models.TextField(blank=True, null=True)
    setroot = models.TextField(blank=True, null=True)
    panelelements = models.TextField(blank=True, null=True)
    survey_quest_text = models.TextField(blank=True, null=True)
    survey_quest_src = models.TextField(blank=True, null=True)
    unitsrequired = models.TextField(blank=True, null=True)
    submitted_units = models.TextField(blank=True, null=True)
    relatednames2 = models.TextField(blank=True, null=True)
    shortname = models.TextField(blank=True, null=True)
    order_obs = models.TextField(blank=True, null=True)
    cdisc_common_tests = models.TextField(blank=True, null=True)
    hl7_field_subfield_id = models.TextField(blank=True, null=True)
    external_copyright_notice = models.TextField(blank=True, null=True)
    example_units = models.TextField(blank=True, null=True)
    inpc_percentage = models.TextField(blank=True, null=True)
    long_common_name = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'LOINC'

    def __str__(self):
        return '%s -- %s' % (self.loinc_num, self.name)


class Icd9(models.Model):
    code = models.CharField('ICD9 Code', max_length=10, primary_key=True)
    name = models.CharField('Name', max_length=150,)
    longname = models.CharField('Long Name',max_length=1000,)

    def __unicode__(self):
        return u'%s %s' % (self.code, self.name)
    
    #
    # TODO: issue 333 Move this code to VAERS
    #
    @staticmethod
    def expansion(expression):
        '''
        considering expressions to represent:
        - An interval of codes: 047.0-047.1
        - A wildcard to represent a family of codes: 320*, 345.*
        - An interval with a wildcard: 802.3-998*
        
        Bear in mind that wildcards are supposed to represent only the
        fractional part. E.g: 809.9* is not a valid expression to expand and
        may result in errors.
        
        This method returns a list of all of the codes that satisfy the
        expression.
        '''

        expression = expression.strip()

        # Sanity check. Not a true expression. Should only be a code.
        # If it's a string representing a code, return the appropriate code.
        if '*' not in expression and '-' not in expression:
            return Icd9.objects.filter(code=expression)

    

        if '-' in expression:
            # It's an expression to show a range of values
            low, high = [x.strip() for x in expression.split('-')]
            
            # Lower bound will always be truncated to the integer part
            low = low.rstrip('.*') 
        
            #Higher bound, however, must be appended to the highest
            #possible value of the range if X itself is a wildcard
            #expression. E.g: 998* -> 998.99
            if high.isdigit():
                if high.rstrip('.*') != high:
                    high = high.rstrip('.*') + '.99'
            else: # strip if it is alpha 
                high = high.rstrip('.*')

        if '*' in expression and '-' not in expression:
            low = expression.rstrip('.*')
            high = expression.rstrip('.*') + '.99'

        if low.isdigit():
            assert(float(low))
            assert(float(high))
                
            return Icd9.objects.filter(code__gte=low, code__lte=high).order_by('code')
        else:
            return Icd9.objects.filter(code__startswith = low).order_by('code') | Icd9.objects.filter(code__startswith = high).order_by('code') 
        
        
   
class Ndc(models.Model):
    '''
    ndc codes from http://www.fda.gov/cder/ndc/
    LISTING_SEQ_NO    LBLCODE    PRODCODE    STRENGTH    UNIT    RX_OTC    FIRM_SEQ_NO    TRADENAME
    eeesh this is horrible - there may be asterisks indicating an optional zero
    and there is no obvious way to fix this...
    '''
    label_code = models.CharField('NDC Label Code (leading zeros are meaningless)', 
        blank=True, null=True, max_length=10, db_index=True)
    product_code = models.CharField('NDC Product Code', max_length=5, 
        blank=True, null=True, db_index=True)
    trade_name = models.CharField('NDC Trade Name', max_length=200, blank=False)
    
    def __str__(self):
        return self.trade_name
   


class Vaccine(models.Model):
    '''
    A vaccine drug
    '''
    code = models.CharField(max_length=128, unique=True)
    short_name = models.CharField(max_length=60)
    name = models.CharField(max_length=300)
    
    @staticmethod
    def random():
        return Vaccine.objects.exclude(short_name='UNK').order_by('?')[0]

    @staticmethod
    def acceptable_mapping_values():
        return Vaccine.objects.exclude(short_name__in=['unknown', 'RESERVED - do not use', 'no vaccine administered']).order_by('short_name')

    def __unicode__(self):
        return u'%s (%s)'% (self.short_name, self.name)


class ImmunizationManufacturer(models.Model):
    code = models.CharField(max_length=3)
    full_name = models.CharField(max_length=200)
    active = models.BooleanField(default=True)
    use_instead = models.ForeignKey('self', null=True)
    
    vaccines_produced = models.ManyToManyField(Vaccine)

    def __unicode__(self):
        return self.full_name


class Allergen(models.Model):
    code = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=300, blank=True, null=True)
    
    def __unicode__(self):
        return u'%s %s' % (self.code, self.name)
