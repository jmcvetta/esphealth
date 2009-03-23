#-*- coding:utf-8 -*-
"""

"""

import string
import datetime

import pdb

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User 
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


import choices
from ESP.utils import utils as util
from ESP.utils.utils import log



class Loinc(models.Model):
    '''
    Logical Observation Identifiers Names and Codes
        Derived from RELMA database available at 
        http://loinc.org/downloads
    '''
    
    # This has to be come before field definitions, because there is a field 
    # named property that lives in the same namespace.
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


class icd9(models.Model):
    icd9Code = models.CharField('ICD9 Code', max_length=10,)
    icd9Long = models.CharField('Name', max_length=50,)

    def __unicode__(self):
        return u'%s %s' % (self.icd9Code,self.icd9Code)
        
   
class ndc(models.Model):
    """ndc codes from http://www.fda.gov/cder/ndc/
    LISTING_SEQ_NO    LBLCODE    PRODCODE    STRENGTH    UNIT    RX_OTC    FIRM_SEQ_NO    TRADENAME
    eeesh this is horrible - there may be asterisks indicating an optional zero
    and there is no obvious way to fix this..."""
    ndcLbl = models.CharField('NDC Label Code (leading zeros are meaningless)', max_length=10,db_index=True)
    ndcProd = models.CharField('NDC Product Code', max_length=5,db_index=True)
    ndcTrade = models.CharField('NDC Trade Name', max_length=200,)
    
    def __unicode__(self):
        return u'%s %s %s' % (self.ndcLbl,self.ndcProd,self.ndcTrade)
        
   
class cpt(models.Model):
    """cpt codes I found at www.tricare.osd.mil/tai/downloads/cpt_codes.xls
    """
    cptCode = models.CharField('CPT Code', max_length=10,db_index=True)
    cptLong = models.TextField('Long name', max_length=500,)
    cptShort = models.CharField('Short name', max_length=60,)
    cptLastedit = models.DateTimeField('Last edited',editable=False,auto_now=True)

    def __unicode__(self):
        return u'%s %s' % (self.cptCode,self.cptShort)
        



RECODEFILE_TYPES = (
    (u'Encounters',u'Daily encounter records - ICD9, demographics...'),
    (u'Labs',u'Lab Orders and Lab Results - LOINC, CPT'),
    (u'Rx', u'Prescription data - NDC'),
    (u'PCP', u'Primary Care Physicians'),
    )



class recode(models.Model):
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
        


class helpdb(models.Model):
    """help database entries
    """
    helpTopic = models.CharField('Help Topic', max_length=100,)
    helpText = models.TextField('Help Text', blank=True, null=True)

    def __unicode__(self):
        return u'%s' % self.helpTopic 
        


class config(models.Model):
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
    ruleMsgFormat = models.CharField('Message Format', max_length=10, choices=choices.FORMAT_TYPES,  blank=True, null=True)
    ruleMsgDest = models.CharField('Destination for formatted messages', max_length=10, choices=choices.DEST_TYPES,  blank=True, null=True)
    ruleHL7Code = models.CharField('Code for HL7 messages with cases', max_length=10, blank=True, null=True)
    ruleHL7Name = models.CharField('Condition name for HL7 messages with cases', max_length=30, blank=True, null=True)
    ruleHL7CodeType = models.CharField('Code for HL7 code type', max_length=10, blank=True, null=True)
    ruleExcludeCode = models.TextField('The exclusion list of (CPT, COMPT) when alerting', blank=True, null=True)
    ruleinProd = models.BooleanField('this rule is in production or not', blank=True)
    ruleInitCaseStatus  =models.CharField('Initial Case status', max_length=20,choices=choices.WORKFLOW_STATES, blank=True)
    

    def gethtml_rulenote(self):
        """generate a list to rule note display
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
    destType = models.CharField('Destination Type',choices = choices.DEST_TYPES ,max_length=20)
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
    formatType = models.CharField('Format Type',choices = choices.FORMAT_TYPES, max_length=20 )
    formatValue = models.TextField('Format Value (eg URL)',null=True)
    formatComments = models.TextField('Format Comments',null=True)
    formatVerDate = models.DateTimeField('Last Edited date',auto_now=True)
    formatcreatedDate = models.DateTimeField('Date Created', auto_now_add=True)
 

    def  __unicode__(self):
        return u'%s' % self.formatName 


class Provider(models.Model):
    provCode= models.CharField('Physician code',max_length=20,blank=True,db_index=True)
    provLast_Name = models.CharField('Last Name',max_length=70,blank=True,null=True)
    provFirst_Name = models.CharField('First Name',max_length=50,blank=True,null=True)
    provMiddle_Initial = models.CharField('Middle_Initial',max_length=20,blank=True,null=True)
    provTitle = models.CharField('Title',max_length=20,blank=True,null=True)
    provPrimary_Dept_Id = models.CharField('Primary Department Id',max_length=20,blank=True,null=True)
    provPrimary_Dept = models.CharField('Primary Department',max_length=200,blank=True,null=True)
    provPrimary_Dept_Address_1 = models.CharField('Primary Department Address 1',max_length=100,blank=True,null=True)
    provPrimary_Dept_Address_2 = models.CharField('Primary Department Address 2',max_length=20,blank=True,null=True)
    provPrimary_Dept_City = models.CharField('Primary Department City',max_length=20,blank=True,null=True)
    provPrimary_Dept_State = models.CharField('Primary Department State',max_length=20,blank=True,null=True)
    provPrimary_Dept_Zip = models.CharField('Primary Department Zip',max_length=20,blank=True,null=True)
    provTelAreacode = models.CharField('Primary Department Phone Areacode',max_length=20,blank=True,null=True)
    provTel = models.CharField('Primary Department Phone Number',max_length=50,blank=True,null=True)
    lastUpDate = models.DateTimeField('Last Updated date',auto_now=True,db_index=True)
    createdDate = models.DateTimeField('Date Created', auto_now_add=True)
         

    def  __unicode__(self):
        return u"%s %s %s %s" % (self.provCode,self.provPrimary_Dept,self.provPrimary_Dept_Address_1,self.provPrimary_Dept_Address_2)

    def getcliname(self):
        return u'%s, %s' % (self.provLast_Name,self.provFirst_Name)
    



class Demog(models.Model):
    DemogPatient_Identifier = models.CharField('Patient Identifier',max_length=20,blank=True,db_index=True)
    DemogMedical_Record_Number = models.CharField('Medical Record Number',max_length=20,db_index=True,blank=True)
    DemogLast_Name = models.CharField('Last_Name',max_length=199,blank=True,null=True)
    DemogFirst_Name = models.CharField('First_Name',max_length=199,blank=True,null=True)
    DemogMiddle_Initial = models.CharField('Middle_Initial',max_length=199,blank=True,null=True)
    DemogSuffix = models.CharField('Suffix',max_length=199,blank=True,null=True)
    DemogAddress1 = models.CharField('Address1',max_length=200,blank=True,null=True)
    DemogAddress2 = models.CharField('Address2',max_length=100,blank=True,null=True)
    DemogCity = models.CharField('City',max_length=50,blank=True,null=True)
    DemogState = models.CharField('State',max_length=20,blank=True,null=True)
    DemogZip = models.CharField('Zip',max_length=20,blank=True,null=True)
    DemogCountry = models.CharField('Country',max_length=20,blank=True,null=True)
    DemogAreaCode = models.CharField('Home Phone Area Code',max_length=20,blank=True,null=True)
    DemogTel = models.CharField('Home Phone Number',max_length=100,blank=True,null=True)
    DemogExt = models.CharField('Home Phone Extension',max_length=50,blank=True,null=True)
    DemogDate_of_Birth = models.CharField('Date of Birth',max_length=20,blank=True,null=True)
    DemogGender = models.CharField('Gender',max_length=20,blank=True,null=True)
    DemogRace = models.CharField('Race',max_length=20,blank=True,null=True)
    DemogHome_Language = models.CharField('Home Language',max_length=20,blank=True,null=True)
    DemogSSN = models.CharField('SSN',max_length=20,blank=True,null=True)
    DemogProvider = models.ForeignKey(Provider,verbose_name="Provider ID",blank=True,null=True)
    DemogMaritalStat = models.CharField('Marital Status',max_length=20,blank=True,null=True)
    DemogReligion = models.CharField('Religion',max_length=20,blank=True,null=True)
    DemogAliases = models.CharField('Aliases',max_length=250,blank=True,null=True)
    DemogMotherMRN = models.CharField('Mother Medical Record Number',max_length=20,blank=True,null=True)
    DemogDeath_Date = models.CharField('Date of death',max_length=200,blank=True,null=True)
    DemogDeath_Indicator = models.CharField('Death_Indicator',max_length=30,blank=True,null=True)
    DemogOccupation = models.CharField('Occupation',max_length=199,blank=True,null=True)
    lastUpDate = models.DateTimeField('Last Updated date',auto_now=True,db_index=True)
    createdDate = models.DateTimeField('Date Created', auto_now_add=True)
            

    def  __unicode__(self):
        return u"#%-10s MRN: %-10s %-10s %-10s" % (self.id, self.DemogPatient_Identifier, self.DemogLast_Name, self.DemogFirst_Name)
    
    def _get_date_of_birth(self):
        '''
        Returns patient's date of birth as a datetime.datetime instance
        '''
        try:
            return datetime.datetime.strptime(
                self.DemogDate_of_Birth, '%Y%m%d')
        except ValueError:
            return None
    date_of_birth = property(_get_date_of_birth)
        
    def _get_age(self, formatted=False):
        '''
        Returns patient's age as a datetime.timedelta instance
        '''
        if not formatted:  
            return datetime.datetime.today() - self.date_of_birth
        
        if formatted:
            if not self.date_of_birth: return None
            
            today = datetime.datetime.today() 
            days = today.day - self.date_of_birth.day
            months = today.month - self.date_of_birth.month
            years = today.year - self.date_of_birth.year
            
            if days < 0:
                months -= 1
            
            if months < 0:
                years -= 1
                months += 12

            return str(years) if years > 0 else '%d Months' % months
        
    age = property(_get_age)
        
            

#===============================================================================
#
#--- ~~~ Heuristics ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Heuristic_Event(models.Model):
    '''
    An interesting medical event
    '''
    heuristic_name = models.CharField(max_length=127, null=False, blank=False, db_index=True)
    date = models.DateField(blank=False, db_index=True)
    patient = models.ForeignKey(Demog, blank=False, db_index=True)
    #
    # Standard generic relation support
    #    http://docs.djangoproject.com/en/dev/ref/contrib/contenttypes/
    #
    content_type = models.ForeignKey(ContentType, db_index=True)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        unique_together = ['heuristic_name', 'date', 'patient', 'content_type', 'object_id']
    
    def __str__(self):
        msg = '%-15s %-12s Patient #%-20s' % (self.heuristic_name, self.date, self.patient.id)
        msg += '\n'
        msg += '    %s' % self.content_object
        return msg




class Rx(models.Model):
    RxPatient = models.ForeignKey(Demog) 
    RxMedical_Record_Number = models.CharField('Medical Record Number',max_length=20,blank=True,db_index=True)
    RxOrder_Id_Num = models.CharField('Order Id #',max_length=20,blank=True,null=True)
    RxProvider = models.ForeignKey(Provider,blank=True,null=True)      
    RxOrderDate = models.CharField('Order Date',max_length=20,blank=True,null=True)
    RxStatus = models.CharField('Order Status',max_length=20,blank=True,null=True)
    RxDrugName = models.TextField('Name of Drug',max_length=3000,blank=True,null=True)
    RxDrugDesc = models.TextField('Drug description',max_length=3000,blank=True,null=True)
    RxNational_Drug_Code = models.CharField('National Drug Code',max_length=20,blank=True,null=True)
    RxDose = models.CharField('Dose',max_length=200,blank=True,null=True)
    RxFrequency = models.CharField('Frequency',max_length=200,blank=True,null=True)
    RxQuantity = models.CharField('Quantity',max_length=200,blank=True,null=True)
    RxRefills = models.CharField('Refills',max_length=200,blank=True,null=True)
    RxRoute = models.CharField('Routes',max_length=200,blank=True,null=True)
    RxStartDate = models.CharField('Start Date',max_length=20,blank=True,null=True)
    RxEndDate = models.CharField('End Date',max_length=20,blank=True,null=True)
    lastUpDate = models.DateTimeField('Last Updated date',auto_now=True,db_index=True)
    createdDate = models.DateTimeField('Date Created', auto_now_add=True)
    #
    # Heuristics support
    #
    heuristics = generic.GenericRelation(Heuristic_Event)
    def _get_patient(self):
        return self.RxPatient
    def _get_provider(self):
        return self.RxProvider
    def _get_date(self):
        return util.date_from_str(self.RxOrderDate)
    patient = property(_get_patient)
    provider = property(_get_provider)
    date = property(_get_date)
            
    def getNDC(self):
        """translate CPT code
        """
        lbl = self.RxNational_Drug_Code[:6]
        prd = self.RxNational_Drug_Code[6:]
        # hack ! TODO fixme
        lbl = '0%s' % self.RxNational_Drug_Code[:5] # add a leading zero
        prd = self.RxNational_Drug_Code[5:-2] # ignore last 2 digits
        try:
            #n = ndc.objects.get(ndcLbl__exact=lbl,ndcProd__exact=prd)
            n = ndc.objects.filter(ndcLbl=lbl,ndcProd=prd)
            s = '%s=%s' % (self.RxNational_Drug_Code,n[0].ndcTrade)
        except:
            if self.RxNational_Drug_Code:
                s = 'NDC code=%s: not found (tried lbl=%s prod=%s)' % (self.RxNational_Drug_Code,lbl,prd)
            else:
                s=''
        return unicode(s)

    def iscaserelated(self):
        
        c = Case.objects.filter(caseDemog__id__exact=self.RxPatient.id)
   
        if '%s' % self.id in string.split(c[0].caseRxID, ','):
            return 1
        else:
            return 0
        
    def  __unicode__(self):

        return u"%s %s %s %s" % (self.RxPatient.DemogPatient_Identifier,self.RxMedical_Record_Number,self.getNDC(),self.RxProvider.provCode)


    def getcliname(self):
        return self.RxProvider.getcliname()      


class LabComponent(models.Model):
    componentName = models.CharField('Component Name', max_length=250,db_index=True)
    CPT = models.CharField('CPT Codes',max_length=30, blank=True,null=True,db_index=True)
    CPTCompt = models.CharField('Compoment Codes',max_length=30, blank=True,null=True,db_index=True)
    lastUpDate = models.DateTimeField('Last Updated date',auto_now=True,db_index=True)
    createdDate = models.DateTimeField('Date Created', auto_now_add=True)
        
                  
class LxManager(models.Manager):
    def result_strings(self, loinc):
        '''
        Returns a list of all result codes that have been seen so far for a 
        given LOINC.
        @type loinc: Str
        @return: [Str, Str, ...]
        '''
        return [x[0] for x in self.get_query_set().values_list('LxTest_results').distinct()]
    

class Lx(models.Model):
    LxPatient = models.ForeignKey(Demog) 
    LxMedical_Record_Number = models.CharField('Medical Record Number', max_length=20, blank=True, null=True, db_index=True)
    LxOrder_Id_Num = models.CharField('Order Id #', max_length=20, blank=True, null=True)
    LxTest_Code_CPT = models.CharField('Test Code (CPT)', max_length=20, blank=True, null=True, db_index=True)
    LxTest_Code_CPT_mod = models.CharField('Test Code (CPT) Modifier', max_length=20, blank=True, null=True)
    LxOrderDate = models.CharField('Order Date', max_length=20, blank=True, null=True)
    LxOrderType = models.CharField('Order Type', max_length=10, blank=True, null=True)   
    LxOrdering_Provider = models.ForeignKey(Provider, blank=True, null=True) 
    LxDate_of_result = models.CharField('Date of result', max_length=20, blank=True, null=True, db_index=True)  
    LxHVMA_Internal_Accession_number = models.CharField('HVMA Internal Accession number', max_length=50, blank=True, null=True)
    LxComponent = models.CharField('Component', max_length=20, blank=True, null=True, db_index=True)
    LxComponentName = models.CharField('Component Name', max_length=200, blank=True, null=True,  db_index=True)
    LxTest_results = models.TextField('Test results', max_length=2000, blank=True, null=True, db_index=True)
    LxNormalAbnormal_Flag = models.CharField('Normal/Abnormal Flag', max_length=20, blank=True, null=True, db_index=True)
    LxReference_Low = models.CharField('Reference Low', max_length=100, blank=True, null=True, db_index=True)
    LxReference_High = models.CharField('Reference High', max_length=100, blank=True, null=True, db_index=True)
    LxReference_Unit = models.CharField('Reference Unit', max_length=100, blank=True, null=True)
    LxTest_status = models.CharField('Test status', max_length=50, blank=True, null=True)
    LxComment = models.TextField('Comments',  blank=True,  null=True, )
    LxImpression = models.TextField('Impression for Imaging only', max_length=2000, blank=True, null=True)
    LxLoinc = models.CharField('LOINC code', max_length=20, blank=True, null=True, db_index=True)
    lastUpDate = models.DateTimeField('Last Updated date', auto_now=True, db_index=True)
    createdDate = models.DateTimeField('Date Created', auto_now_add=True)
    #
    # New fields
    #
    ext_code = models.CharField(max_length=100, blank=True, null=True)
    loinc = models.ForeignKey(Loinc, blank=True, null=True)
    
    #
    # Heuristics Support
    #
    heuristics = generic.GenericRelation(Heuristic_Event)
    def _get_patient(self):
        return self.LxPatient
    def _get_provider(self):
        return self.LxOrdering_Provider
    def _get_date(self):
        return util.date_from_str(self.LxOrderDate)
    patient = property(_get_patient)
    provider = property(_get_provider)
    date = property(_get_date)
    
    # Use custom manager
    objects = LxManager()
    
    def _get_ext_test_code(self):
        '''
        Returns string representation of test code in the external source 
        system.
        This is a kludge until we implement more uniform handling of external 
        test codes & names.
        '''
        if self.LxTest_Code_CPT:
            if self.LxComponent:
                return '%s / %s' % (self.LxTest_Code_CPT, self.LxComponent)
            return '%s' % self.LxTest_Code_CPT
        return None
    ext_test_code = property(_get_ext_test_code)
    
    def _get_ext_test_name(self):
        '''
        Name of the test in external source system.
        This is a kludge until we implement more uniform handling of external 
        test codes & names.
        '''
        return self.LxComponentName
    ext_test_name = property(_get_ext_test_name)
    
    def getCPT(self):
        """translate CPT code
        """
        try:
            c = cpt.objects.get(cptCode__exact=self.LxTest_Code_CPT)
            s = '%s=%s' % (self.LxTest_Code_CPT,c.cptLong)
        except:
            if self.LxTest_Code_CPT:
                s = "CPT code=%s: not found" % self.LxTest_Code_CPT
            else:
                s=''
        return unicode(s)

    def previous(self):
        last = Lx.objects.filter(
            LxPatient=self.LxPatient,
            LxTest_Code_CPT=self.LxTest_Code_CPT,
            LxComponent=self.LxComponent
            ).exclude(
            LxDate_of_result__gte=self.LxOrder_Date,
            LxTest_Results=''
            ).order_by('-LxDate_of_result')[:1]
        
        return last or None

    def compared_to_lkv(self, comparator, x):
        '''
        Builds and evals an inequation between the value of
        the lab result and the Last Known Value (LKV).
        Uses comparator and x as arguments.  Comparator can only be 
        '>' or '<', while x can be any kind of string that can be 
        part of a mathematical equation.
        '''
        try:
            previous = self.previous()
            assert(previous)
            assert(comparator in ['>', '<'])
            assert('LKV' in x)
            assert(previous.LxReference_Unit.lower() == self.LxReference_Unit.lower())
            lkv = float(previous.LxTest_Results)
            current = float(self.LxTest_Results)
        except:
            return None
        
        x = x.replace('LKV', str(lkv))
        
        equation = ' '.join([current, comparator, x])
        return eval(equation)

 
    def iscaserelated(self):
        c = Case.objects.filter(caseDemog__id__exact=self.LxPatient.id)
        if '%s' % self.id in string.split(c[0].caseLxID, ','):
            return 1
        else:
            return 0

    def getcliname(self):
        return self.LxOrdering_Provider.getcliname()        

    def getPartNote(self):
        return self.LxComment[:10]
    
    def  __unicode__(self):
        #return u"%-10s %-50s %-12s PID %s" % (self.LxOrder_Id_Num, self.getCPT(), self.LxOrderDate, self.LxPatient.DemogPatient_Identifier, )
        return u'#%-10s %-12s LOINC: %-7s Ref High: %-5s Result: %s' % (self.pk, self.date, self.LxLoinc, self.LxReference_High, self.LxTest_results)
    

class Lxo(models.Model):
    LxoPatient_Identifier = models.CharField('Patient Identifier',max_length=20,blank=True,null=True,db_index=True)
    LxoMedical_Record_Number = models.CharField('Medical Record Number',max_length=20,blank=True,null=True)
    LxoOrder_Id_Num = models.CharField('Order Id #',max_length=20,blank=True,null=True)
    LxoTest_ordered = models.CharField('Test ordered',max_length=20,blank=True,null=True)
    LxoHVMA_accession_number = models.CharField('HVMA accession number',max_length=20,blank=True,null=True)

    def  __unicode__(self):
        return u"%s %s %s %s" % (self.LxoPatient_Identifier,self.LxoMedical_Record_Number,self.LxoOrder_Id_Num,self.LxoTest_ordered)



###################################
class Enc(models.Model):
    EncPatient = models.ForeignKey(Demog) 
    EncMedical_Record_Number = models.CharField('Medical Record Number',max_length=20,blank=True,null=True,db_index=True)
    EncEncounter_ID = models.CharField('Encounter ID',max_length=20,blank=True,null=True)
    EncEncounter_Date = models.CharField('Encounter Date',max_length=20,blank=True,null=True)
    EncEncounter_Status = models.CharField('Encounter Status',max_length=20,blank=True,null=True)
    EncEncounter_ClosedDate = models.CharField('Encounter Closed Date',max_length=20,blank=True,null=True) 
    EncEncounter_Provider = models.ForeignKey(Provider,blank=True,null=True) 
    EncEncounter_Site = models.CharField('Encounter Site',max_length=20,blank=True,null=True)
    EncEncounter_SiteName = models.CharField('Encounter Site Name',max_length=100,blank=True,null=True)
    EncEvent_Type = models.CharField('Event Type',max_length=20,blank=True,null=True)
    EncPregnancy_Status = models.CharField('Pregnancy Status',max_length=20,blank=True,null=True)
    EncEDC = models.CharField('Expected date of confinement',max_length=20,blank=True,null=True) 
    EncTemperature = models.CharField('Temperature',max_length=20,blank=True,null=True)
    EncCPT_codes = models.CharField('CPT codes',max_length=200,blank=True,null=True)
    EncICD9_Codes = models.TextField('ICD-9 Codes',blank=True,null=True)
    EncICD9_Qualifier = models.CharField('ICD-9 Qualifier',max_length=200,blank=True,null=True)
    EncWeight = models.CharField('Weight (kg)',max_length=200,blank=True,null=True)
    EncHeight = models.CharField('Height (cm)',max_length=200,blank=True,null=True)
    EncBPSys = models.CharField('BP Systolic',max_length=100,blank=True,null=True)
    EncBPDias = models.CharField('BP Diastolic',max_length=100,blank=True,null=True)
    EncO2stat = models.CharField('O2 Stat',max_length=50,blank=True,null=True)
    EncPeakFlow = models.CharField('Peak Flow',max_length=50,blank=True,null=True)
    lastUpDate = models.DateTimeField('Last Updated date',auto_now=True,db_index=True)
    createdDate = models.DateTimeField('Date Created', auto_now_add=True)
    
    #
    # Heuristics support
    #
    heuristics = generic.GenericRelation(Heuristic_Event)
    def _get_patient(self):
        return self.EncPatient
    def _get_provider(self):
        return self.EncEncounter_Provider
    def _get_date(self):
        return util.date_from_str(self.EncEncounter_Date)
    patient = property(_get_patient)
    provider = property(_get_provider)
    date = property(_get_date)
    
    def _get_enc_date(self):
        '''
        Returns a datetime.date object
        '''
        return util.date_from_str(self.EncEncounter_Date)
    encounter_date = property(_get_enc_date)
    
    def geticd9s(self):
        """translate icd9s in comma separated value
        """
        ##icd9_codes are separeted by ' '
        ilist = self.EncICD9_Codes.split(' ')
        if len(ilist) > 0:
            s=[]
            for i in ilist:
                ilong = icd9.objects.filter(icd9Code__exact=i)
                if ilong:
                    ilong = '='+ilong[0].icd9Long # not sure why, but > 1 being found!
                else:
                    ilong=''
#                if icd9l!= 0 and i in icd9l:
#                    s.append((1,'%s=%s' %(i,ilong)))
                if i:
                    s.append((i,ilong))
                else:
                    s.append(('', ''))
        else:
            s = [('', 'No icd9 codes found')]
        return unicode(s)
    
    def _get_icd9_list(self):
        '''
        Returns a string containing nicely-spaced, comma-delimited, non-null 
        ICD9 codes.
        '''
        list = []
        for i in self.EncICD9_Codes.split():
            if i:
                list += [i]
        return list
    icd9_list = property(_get_icd9_list)
        

    def iscaserelated(self):
        c = Case.objects.filter(caseEncID__contains=self.id,caseDemog__id__exact=self.EncPatient.id)
        try:
            l=[string.strip(x) for x in string.split(c[0].caseEncID, ',')]
            indx = l.index('%s' % self.id)
            icd9s = string.split(c[0].caseICD9,',')[indx]
            icd9l = string.split(icd9s)
            return unicode(icd9l)
        except:
            return 0
        

    def getcliname(self):
        return self.EncEncounter_Provider.getcliname()       

    def  __unicode__(self):
        #return u"%s %s %s %s" % (self.EncPatient.id,self.geticd9s(), self.EncMedical_Record_Number,self.EncEncounter_Date)
        return u"#%-10s %-12s CPT: %s" % (self.EncPatient.id, self.date, ', '.join(self.icd9_list))



###################################
class icd9Fact(models.Model):
    icd9Enc = models.ForeignKey(Enc)
    icd9Code = models.CharField('ICD9 codes',max_length=200,blank=True,null=True)
    icd9Patient = models.ForeignKey(Demog)
    icd9EncDate = models.CharField('Encounter Date',max_length=20,blank=True,null=True)
    lastUpDate = models.DateTimeField('Last Updated date',auto_now=True,db_index=True)
    createdDate = models.DateTimeField('Date Created', auto_now_add=True)
                                    
    def  __unicode__(self):

        return u"%s %s %s" % (self.icd9Patient.id,self.icd9Enc.id, self.icd9EncDate)

                               


class Immunization(models.Model):
    ImmPatient = models.ForeignKey(Demog) 
    ImmType = models.CharField('Immunization Type',max_length=20,blank=True,null=True)
    ImmName = models.CharField('Immunization Name',max_length=200,blank=True,null=True)
    ImmDate = models.CharField('Immunization Date Given',max_length=20,blank=True,null=True)
    ImmDose = models.CharField('Immunization Dose',max_length=100,blank=True,null=True)
    ImmManuf =models.CharField('Manufacturer',max_length=100,blank=True,null=True)
    ImmLot = models.TextField('Lot Number',max_length=500,blank=True,null=True)
    ImmVisDate = models.CharField('Date of Visit',max_length=20,blank=True,null=True)
    ImmRecId = models.CharField('Immunization Record Id',max_length=200,blank=True,null=True)
    lastUpDate = models.DateTimeField('Last Updated date',auto_now=True,db_index=True)
    createdDate = models.DateTimeField('Date Created', auto_now_add=True)
    

            

    def  __unicode__(self):

        return u"%s %s %s" % (self.ImmPatient.DemogPatient_Identifier,self.ImmName,self.ImmRecId)




#########################
class VAERSadditions(models.Model):
    VAERPatient = models.ForeignKey(Demog)
    patientDiedDate = models.CharField('Patient died Date if any',max_length=20,blank=True,null=True)
    illness = models.CharField('Life Threatening Illness',max_length=100,blank=True,null=True)
    reqvisit =models.CharField('Required Emergency room/visit',max_length=100,blank=True,null=True)
    reqhospdays = models.TextField('Required Hospitalization Days',max_length=100,blank=True,null=True)
    reshosp = models.CharField('Resulted in prolongation of hospitalization',max_length=200,blank=True,null=True)
    resdisa = models.CharField('Resulted in permanent disability',max_length=200,blank=True,null=True)
    recovered = models.CharField('Patient Recovered',max_length=100,blank=True,null=True)
    birthweight = models.CharField('Birth Weight',max_length=100,blank=True,null=True)
    numsiblings = models.CharField('Number of brothers and sisters',max_length=50,blank=True,null=True)
    lastUpDate = models.DateTimeField('Last Updated date',auto_now=True,db_index=True)
    createdDate = models.DateTimeField('Date Created', auto_now_add=True)
    

    def  __unicode__(self):
        
        return u"%s" % (self.VAERPatient.DemogPatient_Identifier)


class Vaccine(models.Model):
    code = models.IntegerField(unique=True)
    short_name = models.CharField(max_length=60)
    name = models.CharField(max_length=300)
    

class ImmunizationManufacturer(models.Model):
    code = models.CharField(max_length=3)
    full_name = models.CharField(max_length=200)
    active = models.BooleanField(default=True)
    use_instead = models.ForeignKey('self', null=True)
    





                                                            

###################################
class SocialHistory(models.Model):
    SocPatient = models.ForeignKey(Demog)
    SocMRN = models.CharField('Medical Record Number',max_length=25,blank=True,null=True,db_index=True)
    SocTobUse = models.CharField('Tobacco use',max_length=200,blank=True,null=True)
    SocAlcoUse = models.CharField('Alcohol use',max_length=200,blank=True,null=True)
    lastUpDate = models.DateTimeField('Last Updated date',auto_now=True,db_index=True)
    createdDate = models.DateTimeField('Date Created', auto_now_add=True)


    def  __unicode__(self):
        
        return u"%s %s" % (self.SocPatient.DemogPatient_Identifier,self.SocMRN)
    


class Allergies(models.Model):
    AllPatient = models.ForeignKey(Demog)
    AllMRN = models.CharField('Medical Record Number',max_length=25,blank=True,null=True,db_index=True)
    AllPrbID = models.CharField('Problem Id #',max_length=25,blank=True,null=True)
    AllDateNoted = models.CharField('Date Noted',max_length=20,blank=True,null=True)
    AllCode = models.CharField('Allergy ID (Code)',max_length=200,blank=True,null=True)
    AllName = models.CharField('Allergy Name',max_length=255,blank=True,null=True)
    AllStatus = models.CharField('Allergy status',max_length=50,blank=True,null=True)
    AllDesc = models.TextField('Allergy Description',max_length=2000,blank=True,null=True)
    AllDateEntered = models.CharField('Date Entered',max_length=20,blank=True,null=True)
    lastUpDate = models.DateTimeField('Last Updated date',auto_now=True,db_index=True)
    createdDate = models.DateTimeField('Date Created', auto_now_add=True)

    def  __unicode__(self):
        
        return u"%s %s %s" % (self.AllPatient.DemogPatient_Identifier,self.AllMRN,self.AllPrbID)


class Problems(models.Model):
    PrbPatient = models.ForeignKey(Demog)
    PrbMRN = models.CharField('Medical Record Number',max_length=25,blank=True,null=True,db_index=True)
    PrbID = models.CharField('Problem Id #',max_length=25,blank=True,null=True)
    PrbDateNoted = models.CharField('Date Noted',max_length=20,blank=True,null=True)
    PrbICD9Code = models.CharField('Problem ICD9 Code)',max_length=200,blank=True,null=True)
    PrbStatus = models.CharField('Problem status',max_length=50,blank=True,null=True)
    PrbNote = models.TextField('Comments', blank=True, null=True,)
    lastUpDate = models.DateTimeField('Last Updated date',auto_now=True,db_index=True)
    createdDate = models.DateTimeField('Date Created', auto_now_add=True)

    def  __unicode__(self):
        
        return u"%s %s %s" % (self.PrbPatient.DemogPatient_Identifier,self.PrbMRN,self.PrbID)

 
#
# We should probably do Icd9_Rule and Icd9_Rule_Collection, to parallel the Loinc_Rule structure
#
class ConditionIcd9(models.Model):
    CondiRule = models.ForeignKey(Rule)
    CondiICD9 = models.TextField('ICD-9 Codes',blank=True,null=True)
    CondiDefine = models.BooleanField('Icd9 used in definition or not', blank=True,null=True)
    CondiSend = models.BooleanField('Icd9 needs to be sent or not', blank=True,null=True)

    def  __unicode__(self):
        return u'%s %s' % (self.CondiRule,self.CondiICD9)


class ConditionLOINC(models.Model):
    CondiRule = models.ForeignKey(Rule)
    CondiLOINC = models.TextField('LOINC Codes',blank=True,null=True)
    CondiDefine = models.BooleanField('Loinc used in definition or not', blank=True,null=True)
    CondiSend = models.BooleanField('Loinc needs to be sent or not', blank=True,null=True)
    CondiSNMDPosi = models.TextField('SNOMED Positive Codes',blank=True,null=True)
    CondiSNMDNega = models.TextField('SNOMED Negative Codes',blank=True,null=True)
    CondiSNMDInde = models.TextField('SNOMED Indeterminate Codes',blank=True,null=True)
    CondiOperator=models.TextField('Condition Operation',blank=True,null=True)
    CondiValue = models.TextField('Condition value',blank=True,null=True)
    
    def  __unicode__(self):
        return u'%s %s= %s %s' % (self.CondiRule,self.CondiLOINC,self.CondiOperator,self.CondiValue)
        


class CPTLOINCMap(models.Model):
    #
    # DEPRECATED
    #
    # Use External_To_Loinc_Map instead
    #
    CPT = models.TextField('CPT Codes',blank=True,null=True)
    CPTCompt = models.TextField('Compoment Codes',blank=True,null=True)
    Loinc = models.TextField('Loinc Codes',blank=True,null=True)

    def  __unicode__(self):
        return u'%s %s' % (self.CPT,self.CPTCompt)

    def getComptName(self):
        res = LabComponent.objects.filter(CPT=self.CPT,CPTCompt=self.CPTCompt)
        if res:
            comptnames = map(lambda x:[len(x.componentName), x.componentName], res)
            comptnames.sort()
            #Klompas, Michael: If you think that's too clunky then include the longest name for each test.
            return unicode(comptnames[-1][1])
        else:
            return u''
        
class ConditionNdc(models.Model):
    CondiRule = models.ForeignKey(Rule)
    CondiNdc = models.TextField('NDC Codes',blank=True,null=True)
    CondiDefine = models.BooleanField('Ndc used in definition or not', blank=True,null=True)
    CondiSend = models.BooleanField('Ndc need to be send or not', blank=True,null=True)

    def  __unicode__(self):
        return u'%s %s' % (self.CondiRule,self.CondiNdc)
        
 
class ConditionDrugName(models.Model):
    CondiRule = models.ForeignKey(Rule)
    CondiDrugName = models.TextField('Drug Name',blank=True,null=True)
    CondiDrugRoute = models.TextField('Drug Route',blank=True,null=True)
    CondiDefine = models.BooleanField('Used in case definition or not', blank=True,null=True)
    CondiSend = models.BooleanField('Must be sent or not', blank=True,null=True)

    def  __unicode__(self):
        return u'%s %s %s' % (self.CondiRule,self.CondiDrugName, self.CondiDrugRoute)


        
class DataFile(models.Model):
    filename = models.CharField('Raw data file name',max_length=50,blank=True,null=True)
    numrecords = models.CharField('Number of Records in a file',max_length=50,blank=True,null=True) 
    datedownloaded = models.DateTimeField('Date loaded',editable=False,auto_now_add=True)

 
    def  __unicode__(self):
        return u'%s %s' % (self.filename,self.datedownloaded)


class External_To_Loinc_Map(models.Model):
    '''
    A mapping from an external code (for a lab result, etc) to a Loinc number
    '''
    # This table and utilities making use of it assume only one external 
    # code table per ESP installation.  More work will be required if your 
    # installation must comprehend multiple, potentially overlapping, external 
    # code sources
    ext_code = models.CharField(max_length=100, unique=True, blank=False)
    ext_name = models.CharField(max_length=255, blank=True, null=True)
    # Loinc can be null to indicate an external code that maps to nothing
    loinc = models.ForeignKey(Loinc, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)



#===============================================================================
#
#--- ~~~ Case Management ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TestCase(models.Model):

    caseDemog = models.ForeignKey(Demog,verbose_name="Patient ID",db_index=True)
    caseProvider = models.ForeignKey(Provider,verbose_name="Provider ID",blank=True, null=True)
    caseWorkflow = models.CharField('Workflow State', max_length=20,choices=choices.WORKFLOW_STATES, blank=True,db_index=True )
    caseComments = models.TextField('Comments', blank=True, null=True)
    caseLastUpDate = models.DateTimeField('Last Updated date',auto_now=True)
    casecreatedDate = models.DateTimeField('Date Created', auto_now_add=True)
    caseSendDate = models.DateTimeField('Date sent', null=True)
    caseRule = models.ForeignKey(Rule,verbose_name="Case Definition ID")
    caseQueryID = models.CharField('External Query which generated this case',max_length=20, blank=True, null=True)
    caseMsgFormat = models.CharField('Case Message Format', max_length=20, choices=choices.FORMAT_TYPES, blank=True, null=True)
    caseMsgDest = models.CharField('Destination for formatted messages', max_length=120, choices=choices.DEST_TYPES, blank=True, null=True)
    caseEncID = models.TextField('A list of ESP_ENC IDs',max_length=500,  blank=True, null=True)
    caseLxID = models.TextField('A list of ESP_Lx IDs',max_length=500,  blank=True, null=True)
    caseRxID = models.TextField('A list of ESP_Rx IDs',max_length=500,  blank=True, null=True)
    caseICD9 = models.TextField('A list of related ICD9',max_length=500,  blank=True, null=True)
    caseImmID = models.TextField('A list of Immunizations same date',max_length=500, blank=True, null=True)
    
    
    def  __unicode__(self):
        p = self.showPatient()# self.pID
        s = u'Patient=%s RuleID=%s MsgFormat=%s Comments=%s' % (p,self.caseRule.id, self.caseMsgFormat,self.caseComments)
        return s
    
        
    def showPatient(self): 
        p = self.getPatient()
        s = u'%s %s %s %s' % (p.DemogLast_Name, p.DemogFirst_Name, p.DemogMiddle_Initial, p.DemogMedical_Record_Number)
        return s
    
    def getPatient(self): 
        p = Demog.objects.get(id__exact = self.caseDemog.id)
        return p

    def getPregnant(self):
        p=self.getPatient()
        encdb = Enc.objects.filter(EncPatient=p, EncPregnancy_Status='Y').order_by('EncEncounter_Date')
        lxs = None
        lxlist = self.caseLxID.split(',')
        if len(lxlist) > 0:
            lxs=Lx.objects.filter(id__in=lxlist)
        if encdb and lxs:
            lx = lxs[0]
            lxorderd = lx.LxOrderDate
            lxresd=lx.LxDate_of_result
            lxresd = datetime.date(int(lxresd[:4]),int(lxresd[4:6]),int(lxresd[6:8]))+datetime.timedelta(30)
            lxresd = lxresd.strftime('%Y%m%d')
            for oneenc in encdb:
                encdate = oneenc.EncEncounter_Date
                edcdate = oneenc.EncEDC.replace('/','')
                if edcdate:
                    edcdate = datetime.date(int(edcdate[:4]),int(edcdate[4:6]), int(edcdate[6:8]))
                    dur1 =edcdate-datetime.date(int(lxorderd[:4]),int(lxorderd[4:6]), int(lxorderd[6:8]))
                    dur2 = edcdate-datetime.date(int(lxresd[:4]),int(lxresd[4:6]), int(lxresd[6:8]))
                    if dur1.days>=0 or dur2.days>=0:
                        return (u'Pregnant', oneenc.EncEDC.replace('/',''))
                
        elif encdb and not lxs:
            return (u'Pregnant', encdb[0].EncEDC.replace('/',''))

        return (u'',None)


    def getcaseLastUpDate(self):
        s = u'%s' % self.caseLastUpDate
        return s[:11]
    
    def getLxOrderdate(self):
        """
        """
        # patched 30 jan to not barf if no LxIDs
        lxlist = self.caseLxID.split(',')
        orderdate=[]
        if len(lxlist) > 0:
            lxs=Lx.objects.filter(id__in=lxlist)
            for l in lxs:
                orderdate.append(unicode(l.LxOrderDate))
        return unicode(''.join(orderdate))


    def getLxProviderSite(self):
        '''
        '''
        # patched 30 jan to not barf if no LxIDs    
        res = []
        lxlist = self.caseLxID.split(',')
        if len(lxlist) > 0:
            lxs=Lx.objects.filter(id__in=lxlist)
            sites=[]
            for l in lxs:
                relprov = Provider.objects.filter(id=l.LxOrdering_Provider.id)[0]
                sitename = relprov.provPrimary_Dept
                if sitename and sitename not in sites:
                    sites.append(sitename)
            res = []
            for loc in sites:
                res.append('%s ' % loc)
        return unicode(''.join(res))
        
    def getWorkflows(self): # return a list of workflow states for history
        wIter = CaseWorkflow.objects.iterator(workflowCaseID__exact = self.id).order_by('-workflowDate')
        return wIter
    
    def getCondition(self):
        cond = Rule.objects.get(id__exact=self.caseRule.id)
        return cond
    
    def getAddress(self):
        p = self.getPatient()
        s=''
        if p.DemogAddress1:
            s = u'%s %s %s %s %s' % (p.DemogAddress1, p.DemogAddress2, p.DemogCity,p.DemogState,p.DemogZip)
        return s
    
    def getPrevcases(self):
        othercases = TestCase.objects.filter(caseDemog__id__exact=self.caseDemog.id, caseRule__id__exact=self.caseRule.id, id__lt=self.id)
        returnstr=[]
        for c in othercases:
            returnstr.append(unicode(c.id))
        return returnstr
                                                                                                                                                                    
                                                                                                                                                                                                                    
class Case(models.Model):
    '''
    A case of (reportable) disease
    '''
    patient = models.ForeignKey(Demog, blank=False)
    condition = models.ForeignKey(Rule, blank=False)
    provider = models.ForeignKey(Provider, blank=False)
    date = models.DateField(blank=False, db_index=True)
    workflow_state = models.CharField(max_length=20, choices=choices.WORKFLOW_STATES, default='AR', 
        blank=False, db_index=True )
    # Timestamps:
    created_timestamp = models.DateTimeField(auto_now_add=True, blank=False)
    updated_timestamp = models.DateTimeField(auto_now=True, blank=False)
    sent_timestamp = models.DateTimeField(blank=True, null=True)
    # Events that define this case
    events = models.ManyToManyField(Heuristic_Event, blank=False) # The events that caused this case to be generated
    #
    # Reportable Events
    #
    encounters = models.ManyToManyField(Enc, blank=True, null=True)
    lab_results = models.ManyToManyField(Lx, blank=True, null=True)
    medications = models.ManyToManyField(Rx, blank=True, null=True)
    immunizations = models.ManyToManyField(Immunization, blank=True, null=True)
    #
    notes = models.TextField(blank=True, null=True)
    
    #
    # Backward Compatibility
    #
    def getCaseDemog(self):
        return self.patient
    def getCaseProvider(self):
        return self.provider
    def getCaseRule(self):
        return self.condition
    def getCaseWorkflow(self):
        return self.workflow_state
    def getCaseLastUpDate(self):
        return self.updated_timestamp
    def getCasecreatedDate(self):
        return self.created_timestamp
    def getCaseSendDate(self):
        return self.sent_timestamp
    def getCaseQueryID(self):
        # AFAIK this field is never used.
        return None
    def getCaseMsgFormat(self):
        # AFAIK this field is never used.
        return None
    def getCaseMsgDest(self):
        # AFAIK this field is never used.
        return None
    def getCaseEncID(self):
        return ','.join([str(item.id) for item in self.encounters.all()])
    def getCaseLxID(self):
        return ','.join([str(item.id) for item in self.lab_results.all()])
    def getCaseRxID(self):
        return ','.join([str(item.id) for item in self.medications.all()])
    def getCaseICD9(self):
        result = []
        [result.extend(item.icd9_list) for item in self.encounters.all()]
        return result
    def getCaseImmID(self):
        return ','.join([str(item.id) for item in self.immunizations.all()])
    def getCaseComments(self):
        return self.notes
    def setCaseDemog(self, value):
        self.patient = value
    def setCaseProvider(self, value):
        self.provider = value
    def setCaseRule(self, value):
        self.condition = value
    def setCaseWorkflow(self, value):
        self.workflow_state = value
    def setCaseLastUpDate(self, value):
        self.updated_timestamp = value
    def setCasecreatedDate(self, value):
        self.created_timestamp = value
    def setCaseSendDate(self, value):
        self.sent_timestamp = value
    def setCaseQueryID(self, value):
        raise NotImplementedError('AFAIK this field is never used.')
    def setCaseMsgFormat(self, value):
        raise NotImplementedError('AFAIK this field is never used.')
    def setCaseMsgDest(self, value):
        raise NotImplementedError('AFAIK this field is never used.')
    def setCaseEncID(self, value):
        raise DeprecationWarning('This property is read-only for backwards compatibility.  Use the ManyToManyFields instead.')
        self.__caseEncID = value
    def setCaseLxID(self, value):
        raise DeprecationWarning('This property is read-only for backwards compatibility.  Use the ManyToManyFields instead.')
    def setCaseRxID(self, value):
        raise DeprecationWarning('This property is read-only for backwards compatibility.  Use the ManyToManyFields instead.')
    def setCaseICD9(self, value):
        raise DeprecationWarning('This property is read-only for backwards compatibility.  Use the ManyToManyFields instead.')
    def setCaseImmID(self, value):
        raise DeprecationWarning('This property is read-only for backwards compatibility.  Use the ManyToManyFields instead.')
    def setCaseComments(self, value):
        self.notes = value
    caseDemog = property(getCaseDemog, setCaseDemog)
    caseProvider = property(getCaseProvider, setCaseProvider)
    caseRule = property(getCaseRule, setCaseRule)
    caseWorkflow = property(getCaseWorkflow, setCaseWorkflow)
    caseLastUpDate = property(getCaseLastUpDate, setCaseLastUpDate)
    casecreatedDate = property(getCasecreatedDate, setCasecreatedDate)
    caseSendDate = property(getCaseSendDate, setCaseSendDate)
    caseQueryID = property(getCaseQueryID, setCaseQueryID)
    caseMsgFormat = property(getCaseMsgFormat, setCaseMsgFormat)
    caseMsgDest = property(getCaseMsgDest, setCaseMsgDest)
    caseEncID = property(getCaseEncID, setCaseEncID)
    caseLxID = property(getCaseLxID, setCaseLxID)
    caseRxID = property(getCaseRxID, setCaseRxID)
    caseICD9 = property(getCaseICD9, setCaseICD9)
    caseImmID = property(getCaseImmID, setCaseImmID)
    caseComments = property(getCaseComments, setCaseComments)
    
    class Meta:
        permissions = [ ('view_phi', 'Can view protected health information'), ]
    
    def latest_lx(self):
        '''
        Returns the latest lab test relevant to this case
        '''
        if not self.caseLxID:
            return None
        lab_result_ids = self.caseLxID.split(',')
        lab_results = Lx.objects.filter(id__in=lab_result_ids).order_by('LxOrderDate').reverse()
        return lab_results[0]
        
    def latest_lx_order_date(self):
        '''
        Return a datetime.date instance representing the date on which the 
        latest lab test relevant to this case was ordered.
        '''
        if not self.latest_lx():
            return None
        s = self.latest_lx().LxOrderDate
        year = int(s[0:4])
        month = int(s[4:6])
        day = int(s[6:8])
        return datetime.date(year, month, day)
    
    def latest_lx_provider_site(self):
        '''
        Return the provider site for the latest lab test relevant to this case 
        '''
        lx = self.latest_lx()
        if not lx:
            return None
        return lx.LxOrdering_Provider.provPrimary_Dept

    def  __unicode__(self):
        p = self.showPatient()# self.pID
        #s = u'Patient=%s RuleID=%s MsgFormat=%s Comments=%s' % (p,self.caseRule.id, self.caseMsgFormat,self.caseComments)
        s = u'#%-10s %-10s %-15s Patient: %-10s' % (self.id, self.date, self.condition, self.patient)
        return s
 
    def showPatient(self): 
        p = self.getPatient()
        #  s = '%s, %s: %s MRN=%s' % (p.PIDLast_Name, p.PIDFirst_Name, p.PIDFacility1, p.PIDMedical_Record_Number1 )
        s = u'%s %s %s %s' % (p.DemogLast_Name, p.DemogFirst_Name, p.DemogMiddle_Initial,p.DemogMedical_Record_Number )
        return s

    def getPatient(self): # doesn't work
        p = Demog.objects.get(id__exact = self.caseDemog.id)        
        return p

    def getPregnant(self):
        p=self.getPatient()
        encdb = Enc.objects.filter(EncPatient=p, EncPregnancy_Status='Y').order_by('EncEncounter_Date')
        lxs = None
        lxi = self.caseLxID
        if len(lxi) > 0:
            lxs=Lx.objects.filter(id__in=lxi.split(','))
        if encdb and lxs:
            lx = lxs[0]
            lxorderd = lx.LxOrderDate
            lxresd=lx.LxDate_of_result
            lxresd = datetime.date(int(lxresd[:4]),int(lxresd[4:6]),int(lxresd[6:8]))+datetime.timedelta(30)
            lxresd = lxresd.strftime('%Y%m%d')
            for oneenc in encdb:
                encdate = oneenc.EncEncounter_Date
                edcdate = oneenc.EncEDC.replace('/','')
                if edcdate:
                    edcdate = datetime.date(int(edcdate[:4]),int(edcdate[4:6]), int(edcdate[6:8]))
                    dur1 =edcdate-datetime.date(int(lxorderd[:4]),int(lxorderd[4:6]), int(lxorderd[6:8]))
                    dur2 = edcdate-datetime.date(int(lxresd[:4]),int(lxresd[4:6]), int(lxresd[6:8]))
                    if dur1.days>=0 or dur2.days>=0:
                        return (u'Pregnant', oneenc.EncEDC.replace('/',''))
#            for oneenc in encdb:
#                encdate = oneencdb.EncEncounter_Date
#                dur1 =datetime.date(int(encdate[:4]),int(encdate[4:6]), int(encdate[6:8]))-datetime.date(int(lxorderd[:4]),int(lxorderd[4:6]), int(lxorderd[6:8]))
#                dur2 = datetime.date(int(lxresd[:4]),int(lxresd[4:6]), int(lxresd[6:8])) - datetime.date(int(encdate[:4]),int(encdate[4:6]), int(encdate[6:8]))
#                if dur1.days>=0 and dur2.days>=0:
#                    return ('Pregnant', oneenc.EncEDC.replace('/',''))
        elif encdb and not lxs:
            return (u'Pregnant', encdb[0].EncEDC.replace('/',''))
        return (u'',None)

    def getcaseLastUpDate(self):
        s = u'%s' % self.caseLastUpDate
        return s[:11]

    def getWorkflows(self): # return a list of workflow states for history
        wIter = CaseWorkflow.objects.iterator(workflowCaseID__exact = self.id).order_by('-workflowDate')
        return wIter
    
    def getCondition(self):
        cond = Rule.objects.get(id__exact=self.caseRule.id)
        return cond

    def getAddress(self):
        p = self.getPatient()
        s=''
        if p.DemogAddress1:
            s = u'%s %s %s, %s, %s' % (p.DemogAddress1, p.DemogAddress2, p.DemogCity,p.DemogState,p.DemogZip)
        return s

    def getPrevcases(self):
        othercases = Case.objects.filter(patient=self.patient, condition=self.condition.id, date__lt=self.date)
        returnstr=[]
        for c in othercases:
            returnstr.append(unicode(c.id))
        return returnstr

    
class CaseWorkflow(models.Model):
    workflowCaseID = models.ForeignKey(Case)
    workflowDate = models.DateTimeField('Activated',auto_now=True)
    workflowState = models.CharField('Workflow State',choices=choices.WORKFLOW_STATES,max_length=20 )
    workflowChangedBy = models.CharField('Changed By', max_length=30)
    workflowComment = models.TextField('Comments',blank=True,null=True)
    
    def  __unicode__(self):
        return u'%s %s %s' % (self.workflowCaseID, self.workflowDate, self.workflowState)
                                
    class Meta:
        verbose_name = 'External Code to LOINC Map'



class HL7File(models.Model):
    filename = models.CharField('hl7 file name',max_length=100,blank=True,null=True)
    case = models.ForeignKey(Case,verbose_name="Case ID",db_index=True)
    demogMRN = models.CharField('Medical Record Number',max_length=50,db_index=True,blank=True,null=True)
    hl7encID = models.TextField('A list of ESP_ENC IDs in hl7', max_length=500,  blank=True, null=True)
    hl7lxID = models.TextField('A list of ESP_Lx IDs in hl7', max_length=500,  blank=True, null=True)
    hl7rxID = models.TextField('A list of ESP_Rx IDs in hl7', max_length=500,  blank=True, null=True)
    hl7ICD9 = models.TextField('A list of related ICD9 in hl7', max_length=500,  blank=True, null=True)
    hl7reportlxID=models.TextField('A list of report Lx IDs in hl7', max_length=500,  blank=True, null=True)
    hl7specdate = models.TextField('A list of order date of report Lx in hl7', max_length=500,  blank=True, null=True)
    hl7trmtDT = models.TextField('the order date of minium Rx', max_length=500,  blank=True, null=True)
    hl7comment = models.TextField('note in NTE segment',  max_length=500,  blank=True, null=True)
    lastUpDate = models.DateTimeField('Last Updated date',auto_now=True,db_index=True)
    createdDate = models.DateTimeField('Date Created', auto_now_add=True)
          
    def  __unicode__(self):
        return u'%s %s' % (self.filename,self.datedownloaded)
