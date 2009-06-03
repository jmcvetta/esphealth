'''
                        Site Configuration Data Models
                                      for
                                  ESP Health

@author: Ross Lazarus <ross.lazarus@channing.harvard.edu>
@author: Xuanlin Hou <rexua@channing.harvard.edu>
@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''

from django.db import models

from ESP.conf.choices import EMR_SOFTWARE
from ESP.conf.choices import FORMAT_TYPES
from ESP.conf.choices import DEST_TYPES
from ESP.conf.choices import WORKFLOW_STATES


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
    name = models.CharField('Name', max_length=50,)

    def __unicode__(self):
        return u'%s %s' % (self.code, self.name)
    
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
            if high.rstrip('.*') != high:
                high = high.rstrip('.*') + '.99'
                

        if '*' in expression and '-' not in expression:
            low = expression.rstrip('.*')
            high = expression.rstrip('.*') + '.99'


        assert(float(low))
        assert(float(high))
            
        return Icd9.objects.filter(
            code__gte=low, 
            code__lte=high
            ).order_by('code')

    
        
        
   
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
        
   
class Cpt(models.Model):
    """cpt codes I found at www.tricare.osd.mil/tai/downloads/cpt_codes.xls
    """
    cptCode = models.CharField('CPT Code', max_length=10,db_index=True)
    cptLong = models.TextField('Long name', max_length=500,)
    cptShort = models.CharField('Short name', max_length=60,)
    cptLastedit = models.DateTimeField('Last edited',editable=False,auto_now=True)

    def __unicode__(self):
        return u'%s %s' % (self.cptCode,self.cptShort)
        





class Recode(models.Model):
    """recode this value in this field in this file to that value eg cpt -> loinc
    """
    recodeFile = models.CharField('File name', max_length=40,)
    recodeField = models.CharField('Field name', max_length=40,)
    recodeIn = models.CharField('Field value', max_length=50,)
    recodeOut = models.CharField('Replacement', max_length=50,)
    recodeNotes = models.TextField('Note',blank=True, null=True)
    recodeUseMe = models.BooleanField('Use This Definition',)
    recodeCreated = models.DateField('Record created',auto_now_add=True,)

    def __unicode__(self):
        return u'%s %s %s %s' % (self.recodeFile,self.recodeField,self.recodeIn,self.recodeOut)
        


class HelpDb(models.Model):
    """help database entries
    """
    helpTopic = models.CharField('Help Topic', max_length=100,)
    helpText = models.TextField('Help Text', blank=True, null=True)

    def __unicode__(self):
        return u'%s' % self.helpTopic 



class Config(models.Model):
    """local config data - will take a while to accumulate
    Need to be able to read this from a config text file
    as the database is being created
    Now possible to do with the current release - read data after create 
    """
    appName = models.CharField('Application name and version', max_length=40, blank=True, null=True,)
    instComments = models.TextField('Comments', blank=True, null=True,)
    institution_name = models.CharField('Institution name', blank=True, null=True, max_length=40,)
    FacilityID = models.CharField('PHIN/DPH Facility Identifier', blank=True, null=True, max_length=40,)
    sendingFac = models.CharField('PHIN/DPH Sending Facility Identifier', blank=True, null=True, max_length=40,)
    institution_CLIA = models.CharField('Institution CLIA code', blank=True, null=True, max_length=40,)
    instTechName = models.CharField('Technical name', blank=True, null=True, max_length=250,)
    instTechEmail = models.CharField('Technical contact email', blank=True, null=True, max_length=250,)
    instTechTel = models.CharField('Technical contact telephone', blank=True, null=True, max_length=50,)
    instTechcel = models.CharField('Technical contact cellphone', blank=True, null=True, max_length=50,)
    instIDFName = models.CharField('Infectious diseases contact first name', blank=True, null=True, max_length=250,)
    instIDLName = models.CharField('Infectious diseases contact last name', blank=True, null=True, max_length=250,)
    instIDEmail = models.CharField('Infectious diseases contact email', blank=True, null=True, max_length=250,)
    instIDTelArea = models.CharField('Infectious diseases contact telephone areacode', blank=True, null=True, max_length=50,)
    instIDTel = models.CharField('Infectious diseases contact telephone', blank=True, null=True, max_length=50,)
    instIDTelExt = models.CharField('Infectious diseases contact telephone ext', blank=True, null=True, max_length=50,)
    instIDcel = models.CharField('Infectious diseases contact cellphone', blank=True, null=True, max_length=50,)
    instAddress1 = models.CharField('Institution address 1', max_length=100, blank=True, null=True,)
    instAddress2 = models.CharField('Institution address 2', max_length=100, blank=True, null=True,)
    instCity = models.CharField('City', max_length=100, blank=True, null=True,)
    instState = models.CharField('State', max_length=10, blank=True, null=True,)
    instZip = models.CharField('Zipcode', max_length=20, blank=True, null=True,)
    instCountry = models.CharField('Country', max_length=30, blank=True, null=True,)
    instTel = models.CharField('Institution Telephone', max_length=50, blank=True, null=True,)
    instFax = models.CharField('Institution Fax', max_length=50, blank=True, null=True,)
    configCreated = models.DateField('Configuration created',auto_now_add=True,)
    configLastChanged = models.DateField('Configuration last changed',auto_now=True,)

    def  __unicode__(self):
        return u'%s' % self.institution_name 
 
    
class Rule(models.Model):
    """case definition rule with destination and format 
    """
    ruleName = models.CharField('Rule Name', max_length=100,db_index=True)
    ruleSQL = models.TextField('', blank=True, null=True)
    ruleComments = models.TextField('Comments', blank=True, null=True)
    ruleVerDate = models.DateTimeField('Last Edited date',auto_now=True)
    rulecreatedDate = models.DateTimeField('Date Created', auto_now_add=True)
    rulelastexecDate = models.DateTimeField('Date last executed', editable=False, blank=True, null=True)
    ruleMsgFormat = models.CharField('Message Format', max_length=10, choices=FORMAT_TYPES,  blank=True, null=True)
    ruleMsgDest = models.CharField('Destination for formatted messages', max_length=10, choices=DEST_TYPES,  blank=True, null=True)
    ruleHL7Code = models.CharField('Code for HL7 messages with cases', max_length=10, blank=True, null=True)
    ruleHL7Name = models.CharField('Condition name for HL7 messages with cases', max_length=30, blank=True, null=True)
    ruleHL7CodeType = models.CharField('Code for HL7 code type', max_length=10, blank=True, null=True)
    ruleExcludeCode = models.TextField('The exclusion list of (CPT, COMPT) when alerting', blank=True, null=True)
    ruleinProd = models.BooleanField('this rule is in production or not', blank=True)
    ruleInitCaseStatus  =models.CharField('Initial Case status', max_length=20,choices=WORKFLOW_STATES, blank=True)
    

    def gethtml_rulenote(self):
        """
        generate a list to rule note display
        """
        data=[]
        lines = self.ruleComments.split('\\n')
        for oneline in lines:
            if lines.index(oneline)==0:
                note=oneline
                continue
            items = oneline.split('|')
            if lines.index(oneline)==1: header=items
            else:
                data.append(items)
        return (note,header,data)
    
    def  __unicode__(self):
        return u'%s' % self.ruleName 


 
class Dest(models.Model):
    """message destination for rules
    """
    destName = models.CharField('Destination Name', max_length=100)
    destType = models.CharField('Destination Type',choices = DEST_TYPES ,max_length=20)
    destValue = models.TextField('Destination Value (eg URL)',null=True)
    destComments = models.TextField('Destination Comments',null=True)
    destVerDate = models.DateTimeField('Last Edited date',auto_now=True)
    destcreatedDate = models.DateTimeField('Date Created', auto_now_add=True)

    def  __unicode__(self):
        return u'%s %s %s' % \
            (self.destName,self.destType,self.destValue)




class Format(models.Model):
    """message formats for rules
    """
    formatName = models.CharField('Format Name', max_length=100,)
    formatType = models.CharField('Format Type',choices = FORMAT_TYPES, max_length=20 )
    formatValue = models.TextField('Format Value (eg URL)',null=True)
    formatComments = models.TextField('Format Comments',null=True)
    formatVerDate = models.DateTimeField('Last Edited date',auto_now=True)
    formatcreatedDate = models.DateTimeField('Date Created', auto_now_add=True)

    def  __unicode__(self):
        return u'%s' % self.formatName 

class SourceSystem(models.Model):
    '''
    A source EMR system providing data to ESP, e.g. HVMA or North Adams
    '''
    name = models.CharField(max_length=100, blank=False)
    # Various non-critical information about the source system:
    software = models.CharField(max_length=50, choices=EMR_SOFTWARE, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Source EMR System'
    
    def __str__(self):
        return self.name


class NativeCode(models.Model):
    '''
    A mapping from a native code (for a lab result, etc) to a Loinc number
    '''
    # This table and utilities making use of it assume only one external 
    # code table per ESP installation.  More work will be required if your 
    # installation must comprehend multiple, potentially overlapping, external 
    # code sources
    native_code = models.CharField(max_length=100, unique=True, blank=False)
    native_name = models.CharField(max_length=255, blank=True, null=True)
    # Loinc can be null to indicate an external code that maps to nothing
    loinc = models.ForeignKey(Loinc, blank=True, null=True)
    ignore = models.BooleanField('Ignore in NLP report', blank=False, default=False)
    notes = models.TextField(blank=True, null=True)
    class Meta:
        verbose_name = 'Native Code to LOINC Map'

