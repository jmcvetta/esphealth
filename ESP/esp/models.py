"""
Updated april 22 for the magic removal branch.
Ouch.

esp.py
Django models

For the ESP project

lots of code for the MADPH simple hl7 components autogenerated
by ESPModel.py which uses some text tables cut and pasted from the
specification document.

april 7

Updated april 24 to include cpt codes and code translations for the incomingMgr

Updated August 9 to remove now unecessary hl7 message segment stuff.

"""
from django.db import models
from django.contrib.auth.models import User 
import string

FORMAT_TYPES = (
    ('Text','Plain text representation'),
    ('XML','eXtended Markup Language format'),
    ('HL7', 'Health Level 7 markup'),
    ('MADPHSimple', 'MADPH Simple markup (pipe delim simplifiedhl7)'),
)



WORKFLOW_STATES = (('AR','AWAITING REVIEW'),('UR','UNDER REVIEW'),('RM', 'REVIEW By MD'),('FP','FALSE POSITIVE - DO NOT PROCESS'),('Q','IN QUEUE FOR MESSAGING'),    ('S','SENT TO DESTINATION'))

DEST_TYPES = (
    ('TextFile','Text file on the filesystem - path'),
    ('PHIN-MS','PHINMS server URL'),
    ('SOAP', 'SOAP service URL'),
    ('XMLRPC', 'XML-RPC Server URL'),
)


class icd9(models.Model):
    icd9Code = models.CharField('ICD9 Code', maxlength=10,)
    icd9Long = models.CharField('Name', maxlength=50,)

    def __str__(self):
        return '%s %s' % (self.icd9Code,self.icd9Code)
        
    class Admin:
        list_display = ('icd9Code', 'icd9Long')
        search_fields = ('icd9Code')
   
class ndc(models.Model):
    """ndc codes from http://www.fda.gov/cder/ndc/
    LISTING_SEQ_NO	LBLCODE	PRODCODE	STRENGTH	UNIT	RX_OTC	FIRM_SEQ_NO	TRADENAME
    eeesh this is horrible - there may be asterisks indicating an optional zero
    and there is no obvious way to fix this..."""
    ndcLbl = models.CharField('NDC Label Code (leading zeros are meaningless)', maxlength=10,db_index=True)
    ndcProd = models.CharField('NDC Product Code', maxlength=5,db_index=True)
    ndcTrade = models.CharField('NDC Trade Name', maxlength=200,)
    
    def __str__(self):
        return '%s %s %s' % (self.ndcLbl,self.ndcProd,self.ndcTrade)
        
    class Admin:
        list_display = ('ndcLbl', 'ndcProd','ndcTrade')
        search_fields = ('ndcProd','ndcLbl')
   
class cpt(models.Model):
    """cpt codes I found at www.tricare.osd.mil/tai/downloads/cpt_codes.xls
    """
    cptCode = models.CharField('CPT Code', maxlength=10,db_index=True)
    cptLong = models.TextField('Long name', maxlength=500,)
    cptShort = models.CharField('Short name', maxlength=60,)
    cptLastedit = models.DateTimeField('Last edited',editable=False,auto_now=True)

    def __str__(self):
        return '%s %s' % (self.cptCode,self.cptShort)
        
    class Admin:
        list_display = ('cptCode', 'cptLong','cptShort')
        search_fields = ('cptLong')


RECODEFILE_TYPES = (
    ('Encounters','Daily encounter records - ICD9, demographics...'),
    ('Labs','Lab Orders and Lab Results - LOINC, CPT'),
    ('Rx', 'Prescription data - NDC'),
    ('PCP', 'Primary Care Physicians'),
    )



class recode(models.Model):
    """recode this value in this field in this file to that value eg cpt -> loinc
    """
    recodeFile = models.CharField('File name', maxlength=40,)
    recodeField = models.CharField('Field name', maxlength=40,)
    recodeIn = models.CharField('Field value', maxlength=50,)
    recodeOut = models.CharField('Replacement', maxlength=50,)
    recodeNotes = models.TextField('Note',blank=True, null=True)
    recodeUseMe = models.BooleanField('Use This Definition',)
    recodeCreated = models.DateField('Record created',auto_now_add=True,)

    def __str__(self):
        return '%s %s %s %s' % (self.recodeFile,self.recodeField,self.recodeIn,self.recodeOut)
        
    class Admin:
        list_display = ('recodeFile', 'recodeField','recodeIn','recodeOut')
        search_fields = ('recodeIn')


class helpdb(models.Model):
    """help database entries
    """
    helpTopic = models.CharField('Help Topic', maxlength=100,)
    helpText = models.TextField('Help Text', blank=True, null=True)

    def __str__(self):
        return self.helpTopic 
        
    class Admin:
        list_display = ('helpTopic', 'helpText')
        search_fields = ('helpTopic')

class config(models.Model):
    """local config data - will take a while to accumulate
    Need to be able to read this from a config text file
    as the database is being created
    Now possible to do with the current release - read data after create 
    """
    appName = models.CharField('Application name and version', maxlength=40, blank=True, null=True,)
    instComments = models.TextField('Comments', blank=True, null=True,)
    institution_name = models.CharField('Institution name', blank=True, null=True, maxlength=40,)
    FacilityID = models.CharField('PHIN/DPH Facility Identifier', blank=True, null=True, maxlength=40,)
    sendingFac = models.CharField('PHIN/DPH Sending Facility Identifier', blank=True, null=True, maxlength=40,)
    institution_CLIA = models.CharField('Institution CLIA code', blank=True, null=True, maxlength=40,)
    instTechName = models.CharField('Technical name', blank=True, null=True, maxlength=250,)
    instTechEmail = models.CharField('Technical contact email', blank=True, null=True, maxlength=250,)
    instTechTel = models.CharField('Technical contact telephone', blank=True, null=True, maxlength=50,)
    instTechcel = models.CharField('Technical contact cellphone', blank=True, null=True, maxlength=50,)
    instIDFName = models.CharField('Infectious diseases contact first name', blank=True, null=True, maxlength=250,)
    instIDLName = models.CharField('Infectious diseases contact last name', blank=True, null=True, maxlength=250,)
    instIDEmail = models.CharField('Infectious diseases contact email', blank=True, null=True, maxlength=250,)
    instIDTelArea = models.CharField('Infectious diseases contact telephone areacode', blank=True, null=True, maxlength=50,)
    instIDTel = models.CharField('Infectious diseases contact telephone', blank=True, null=True, maxlength=50,)
    instIDTelExt = models.CharField('Infectious diseases contact telephone ext', blank=True, null=True, maxlength=50,)
    instIDcel = models.CharField('Infectious diseases contact cellphone', blank=True, null=True, maxlength=50,)
    instAddress1 = models.CharField('Institution address 1', maxlength=100, blank=True, null=True,)
    instAddress2 = models.CharField('Institution address 2', maxlength=100, blank=True, null=True,)
    instCity = models.CharField('City', maxlength=100, blank=True, null=True,)
    instState = models.CharField('State', maxlength=10, blank=True, null=True,)
    instZip = models.CharField('Zipcode', maxlength=20, blank=True, null=True,)
    instCountry = models.CharField('Country', maxlength=30, blank=True, null=True,)
    instTel = models.CharField('Institution Telephone', maxlength=50, blank=True, null=True,)
    instFax = models.CharField('Institution Fax', maxlength=50, blank=True, null=True,)
    
    configCreated = models.DateField('Configuration created',auto_now_add=True,)
    configLastChanged = models.DateField('Configuration last changed',auto_now=True,)

    def __str__(self):
        return self.institution_name 

    class Admin:
       list_display=('institution_name','instComments')
        
 
    
class Rule(models.Model):
    """case definition rule with destination and format 
    """
    ruleName = models.CharField('Rule Name', maxlength=100,db_index=True)
    ruleSQL = models.TextField('', blank=True, null=True)
    ruleComments = models.TextField('Comments', blank=True, null=True)
    ruleVerDate = models.DateTimeField('Last Edited date',auto_now=True)
    rulecreatedDate = models.DateTimeField('Date Created', auto_now_add=True)
    rulelastexecDate = models.DateTimeField('Date last executed', editable=False, blank=True, null=True)
    ruleMsgFormat = models.CharField('Message Format', maxlength=10, choices=FORMAT_TYPES,  blank=True, null=True)
    ruleMsgDest = models.CharField('Destination for formatted messages', maxlength=10, choices=DEST_TYPES,  blank=True, null=True)
    ruleHL7Code = models.CharField('Code for HL7 messages with cases', maxlength=10, blank=True, null=True)
    ruleHL7Name = models.CharField('Condition name for HL7 messages with cases', maxlength=30, blank=True, null=True)
    ruleHL7CodeType = models.CharField('Code for HL7 code type', maxlength=10, blank=True, null=True)


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
    
    def __str__(self):
        return self.ruleName 
        #return '%d %s %s' % \
            #(self.id,self.ruleName,self.ruleSQL)

    class Admin:
        ordering = ('ruleVerDate', 'ruleName')
        list_display = ('ruleName', 'ruleComments','ruleVerDate')
        search_fields = ('ruleName')
        
        


class Dest(models.Model):
    """message destination for rules
    """
    destName = models.CharField('Destination Name', maxlength=100)
    destType = models.CharField('Destination Type',choices = DEST_TYPES ,maxlength=20)
    destValue = models.TextField('Destination Value (eg URL)',null=True)
    destComments = models.TextField('Destination Comments',null=True)
    destVerDate = models.DateTimeField('Last Edited date',auto_now=True)
    destcreatedDate = models.DateTimeField('Date Created', auto_now_add=True)
 

    def __str__(self):
        return '%s %s %s' % \
            (self.destName,self.destType,self.destValue)

    class Admin:
        ordering = ('destVerDate', 'destName')



class Format(models.Model):
    """message formats for rules
    """
    formatName = models.CharField('Format Name', maxlength=100,)
    formatType = models.CharField('Format Type',choices = FORMAT_TYPES,maxlength=20 )
    formatValue = models.TextField('Format Value (eg URL)',null=True)
    formatComments = models.TextField('Format Comments',null=True)
    formatVerDate = models.DateTimeField('Last Edited date',auto_now=True)
    formatcreatedDate = models.DateTimeField('Date Created', auto_now_add=True)
 

    def __str__(self):
        return self.formatName 

    class Admin:
        ordering = ('formatVerDate', 'formatName')

class Provider(models.Model):
    provCode= models.CharField('Physician code',maxlength=20,blank=True,db_index=True)
    provLast_Name = models.CharField('Last Name',maxlength=70,blank=True)
    provFirst_Name = models.CharField('First Name',maxlength=50,blank=True)
    provMiddle_Initial = models.CharField('Middle_Initial',maxlength=20,blank=True)
    provTitle = models.CharField('Title',maxlength=20,blank=True)
    provPrimary_Dept_Id = models.CharField('Primary Department Id',maxlength=20,blank=True)
    provPrimary_Dept = models.CharField('Primary Department',maxlength=200,blank=True)
    provPrimary_Dept_Address_1 = models.CharField('Primary Department Address 1',maxlength=100,blank=True)
    provPrimary_Dept_Address_2 = models.CharField('Primary Department Address 2',maxlength=20,blank=True)
    provPrimary_Dept_City = models.CharField('Primary Department City',maxlength=20,blank=True)
    provPrimary_Dept_State = models.CharField('Primary Department State',maxlength=20,blank=True)
    provPrimary_Dept_Zip = models.CharField('Primary Department Zip',maxlength=20,blank=True)
    provTelAreacode = models.CharField('Primary Department Phone Areacode',maxlength=20,blank=True)
    provTel = models.CharField('Primary Department Phone Number',maxlength=50,blank=True)

    def __str__(self):
        return "%s %s %s %s" % (self.provCode,self.provPrimary_Dept,self.provPrimary_Dept_Address_1,self.provPrimary_Dept_Address_2)

    def getcliname(self):
        return '%s, %s' % (self.provLast_Name,self.provFirst_Name)
    
    class Admin:
        list_display = ('provLast_Name', 'provFirst_Name','provPrimary_Dept')
        search_fields = ('provLast_Name')



class Demog(models.Model):
    DemogPatient_Identifier = models.CharField('Patient Identifier',maxlength=20,blank=True,db_index=True)
    DemogMedical_Record_Number = models.CharField('Medical Record Number',maxlength=20,db_index=True,blank=True)
    DemogLast_Name = models.CharField('Last_Name',maxlength=199,blank=True)
    DemogFirst_Name = models.CharField('First_Name',maxlength=199,blank=True)
    DemogMiddle_Initial = models.CharField('Middle_Initial',maxlength=199,blank=True)
    DemogSuffix = models.CharField('Suffix',maxlength=199,blank=True)
    DemogAddress1 = models.CharField('Address1',maxlength=200,blank=True)
    DemogAddress2 = models.CharField('Address2',maxlength=100,blank=True)
    DemogCity = models.CharField('City',maxlength=50,blank=True)
    DemogState = models.CharField('State',maxlength=20,blank=True)
    DemogZip = models.CharField('Zip',maxlength=20,blank=True)
    DemogCountry = models.CharField('Country',maxlength=20,blank=True)
    DemogAreaCode = models.CharField('Home Phone Area Code',maxlength=20,blank=True)
    DemogTel = models.CharField('Home Phone Number',maxlength=100,blank=True)
    DemogExt = models.CharField('Home Phone Extension',maxlength=50,blank=True)
    DemogDate_of_Birth = models.CharField('Date of Birth',maxlength=20,blank=True)
    DemogGender = models.CharField('Gender',maxlength=20,blank=True)
    DemogRace = models.CharField('Race',maxlength=20,blank=True)
    DemogHome_Language = models.CharField('Home Language',maxlength=20,blank=True)
    DemogSSN = models.CharField('SSN',maxlength=20,blank=True)
    DemogProvider = models.ForeignKey(Provider,verbose_name="Provider ID",blank=True,null=True)
    DemogMaritalStat = models.CharField('Marital Status',maxlength=20,blank=True)
    DemogReligion = models.CharField('Religion',maxlength=20,blank=True)
    DemogAliases = models.CharField('Aliases',maxlength=250,blank=True)
    DemogMotherMRN = models.CharField('Mother Medical Record Number',maxlength=20,blank=True)
    DemogDeath_Date = models.CharField('Date of death',maxlength=200,blank=True)
    DemogDeath_Indicator = models.CharField('Death_Indicator',maxlength=30,blank=True)
    DemogOccupation = models.CharField('Occupation',maxlength=199,blank=True)


    def __str__(self):
        return "PID%s,%s, %s,%s, %s" % (self.DemogPatient_Identifier,self.DemogMedical_Record_Number,self.DemogLast_Name,self.DemogFirst_Name, self.DemogAddress1)

    class Admin:
        list_display = ('DemogFirst_Name', 'DemogLast_Name', 'DemogMedical_Record_Number','DemogDate_of_Birth')
        search_fields = ('DemogLast_Name')

class Case(models.Model):
    """casePID can't be a foreign key or we get complaints that the pointed to model doesn't
    yet exist
    """
    caseDemog = models.ForeignKey(Demog,verbose_name="Patient ID",db_index=True)
    caseProvider = models.ForeignKey(Provider,verbose_name="Provider ID",blank=True, null=True)
    caseWorkflow = models.CharField('Workflow State', maxlength=20,choices=WORKFLOW_STATES, blank=True,db_index=True )
    caseComments = models.TextField('Comments', blank=True, null=True)
    caseLastUpDate = models.DateTimeField('Last Updated date',auto_now=True)
    casecreatedDate = models.DateTimeField('Date Created', auto_now_add=True)
    caseRule = models.ForeignKey(Rule,verbose_name="Case Definition ID")
    caseQueryID = models.CharField('External Query which generated this case',maxlength=20, blank=True, null=True)
    caseMsgFormat = models.CharField('Case Message Format', maxlength=20, choices=FORMAT_TYPES, blank=True, null=True)
    caseMsgDest = models.CharField('Destination for formatted messages', maxlength=120, choices=DEST_TYPES, blank=True, null=True)
    caseEncID = models.TextField('A list of ESP_ENC IDs',maxlength=500,  blank=True, null=True)
    caseLxID = models.TextField('A list of ESP_Lx IDs',maxlength=500,  blank=True, null=True)
    caseRxID = models.TextField('A list of ESP_Rx IDs',maxlength=500,  blank=True, null=True)
    caseICD9 = models.TextField('A list of related ICD9',maxlength=500,  blank=True, null=True)

    

    def __str__(self):
        p = self.showPatient()# self.pID
        s = 'Patient=%s RuleID=%s MsgFormat=%s Comments=%s' % (p,self.caseRule.id, self.caseMsgFormat,self.caseComments)
        
        return s
    
    class Admin:
        list_filter = ('caseWorkflow','caseQueryID','caseMsgFormat','caseProvider')
        ordering = ('caseLastUpDate', 'casecreatedDate')
        list_display = ('caseProvider','caseWorkflow','caseComments','caseLastUpDate','caseQueryID','caseMsgFormat')
 
    def showPatient(self): # doesn't work
        p = self.getPatient()
        #  s = '%s, %s: %s MRN=%s' % (p.PIDLast_Name, p.PIDFirst_Name, p.PIDFacility1, p.PIDMedical_Record_Number1 )

        s = '%s %s: %s' % (p.DemogLast_Name, p.DemogFirst_Name, p.DemogMedical_Record_Number )

        return s

    def getPatient(self): # doesn't work
        p = Demog.objects.get(id__exact = self.caseDemog.id)        
        return p    

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
            s = '%s %s<br>%s, %s, %s' % (p.DemogAddress1, p.DemogAddress2, p.DemogCity,p.DemogState,p.DemogZip)
        return s

    def getPrevcases(self):
        othercases = Case.objects.filter(caseDemog__id__exact=self.caseDemog.id, caseRule__id__exact=self.caseRule.id, id__lt=self.id)
        returnstr=[]
        for c in othercases:
            returnstr.append(c.id)
        return returnstr

###################################
class CaseWorkflow(models.Model):
    workflowCaseID = models.ForeignKey(Case)
    workflowDate = models.DateTimeField('Activated',auto_now=True)
    workflowState = models.CharField('Workflow State',choices=WORKFLOW_STATES,core=True,maxlength=20 )
    workflowChangedBy = models.CharField('Changed By', maxlength=30)
    workflowComment = models.TextField('Comments',blank=True)
 
    def __str__(self):
        return '%s %s %s' % (self.workflowCaseID, self.workflowDate, self.workflowState)

    class Admin:
        list_filter = ('workflowState','workflowChangedBy',)
        list_display = ('workflowDate','workflowState','workflowChangedBy','workflowComment',)
        search_fields = ('workflowComment',)
        ordering = ('workflowDate',)

# generated by makeCarlamodels.py


class Rx(models.Model):
    RxPatient = models.ForeignKey(Demog) 
    RxMedical_Record_Number = models.CharField('Medical Record Number',maxlength=20,blank=True,db_index=True)
    RxOrder_Id_Num = models.CharField('Order Id #',maxlength=20,blank=True)
    RxProvider = models.ForeignKey(Provider,blank=True,null=True)      
    RxOrderDate = models.CharField('Order Date',maxlength=20,blank=True)
    RxStatus = models.CharField('Order Status',maxlength=20,blank=True)
    RxDrugName = models.TextField('Name of Drug',maxlength=3000,blank=True)
    RxDrugDesc = models.TextField('Drug description',maxlength=3000,blank=True)
    RxNational_Drug_Code = models.CharField('National Drug Code',maxlength=20,blank=True)
    RxDose = models.CharField('Dose',maxlength=200,blank=True)
    RxFrequency = models.CharField('Frequency',maxlength=200,blank=True)
    RxQuantity = models.CharField('Quantity',maxlength=200,blank=True)
    RxRefills = models.CharField('Refills',maxlength=200,blank=True)
    RxRoute = models.CharField('Routes',maxlength=200,blank=True)
    RxStartDate = models.CharField('Start Date',maxlength=20,blank=True)
    RxEndDate = models.CharField('End Date',maxlength=20,blank=True)
    
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
        return s

    def iscaserelated(self):
        
        c = Case.objects.filter(caseDemog__id__exact=self.RxPatient.id)
   
        if '%s' % self.id in string.split(c[0].caseRxID, ','):
            return 1
        else:
            return 0
        
    def __str__(self):

        return "%s %s %s %s" % (self.RxPatient.DemogPatient_Identifier,self.RxMedical_Record_Number,self.getNDC(),self.RxProvider.provCode)


    def getcliname(self):
        return self.RxProvider.getcliname()      

    class Admin:
        pass

class Lx(models.Model):
    LxPatient = models.ForeignKey(Demog) 
    LxMedical_Record_Number = models.CharField('Medical Record Number',maxlength=20,blank=True,db_index=True)
    LxOrder_Id_Num = models.CharField('Order Id #',maxlength=20,blank=True)
    LxTest_Code_CPT = models.CharField('Test Code (CPT)',maxlength=20,blank=True)
    LxTest_Code_CPT_mod = models.CharField('Test Code (CPT) Modifier',maxlength=20,blank=True)
    LxOrderDate = models.CharField('Order Date',maxlength=20,blank=True)
    LxOrderType = models.CharField('Order Type',maxlength=10,blank=True)   
    LxOrdering_Provider = models.ForeignKey(Provider,blank=True,null=True) 
    LxDate_of_result =models.CharField('Date of result',maxlength=20,blank=True)  
    LxHVMA_Internal_Accession_number = models.CharField('HVMA Internal Accession number',maxlength=20,blank=True)
    LxComponent = models.CharField('Component',maxlength=20,blank=True)
    LxComponentName = models.CharField('Component Name',maxlength=200,blank=True)
    LxTest_results = models.TextField('Test results',maxlength=2000,blank=True)
    LxNormalAbnormal_Flag = models.CharField('Normal/Abnormal Flag',maxlength=20,blank=True)
    LxReference_Low = models.CharField('Reference Low',maxlength=100,blank=True)
    LxReference_High = models.CharField('Reference High',maxlength=100,blank=True)
    LxReference_Unit = models.CharField('Reference Unit',maxlength=100,blank=True)
    LxTest_status = models.CharField('Test status',maxlength=50,blank=True)
    LxComment = models.TextField('Comments', blank=True, null=True,)
    LxImpression = models.TextField('Impression for Imaging only',maxlength=2000,blank=True)
    LxLoinc = models.CharField('LOINC code',maxlength=20,blank=True)
   
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
        return s

 
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
    
    def __str__(self):

        return "%s %s %s %s" % (self.LxPatient.DemogPatient_Identifier,self.getCPT(),self.LxOrder_Id_Num,self.LxOrderDate)


    class Admin:
        pass

class Lxo(models.Model):
    LxoPatient_Identifier = models.CharField('Patient Identifier',maxlength=20,blank=True,db_index=True)
    LxoMedical_Record_Number = models.CharField('Medical Record Number',maxlength=20,blank=True)
    LxoOrder_Id_Num = models.CharField('Order Id #',maxlength=20,blank=True)
    LxoTest_ordered = models.CharField('Test ordered',maxlength=20,blank=True)
    LxoHVMA_accession_number = models.CharField('HVMA accession number',maxlength=20,blank=True)

    def __str__(self):
        return "%s %s %s %s" % (self.LxoPatient_Identifier,self.LxoMedical_Record_Number,self.LxoOrder_Id_Num,self.LxoTest_ordered)

    class Admin:
        pass

class Enc(models.Model):
    EncPatient = models.ForeignKey(Demog) 
    EncMedical_Record_Number = models.CharField('Medical Record Number',maxlength=20,blank=True,db_index=True)
    EncEncounter_ID = models.CharField('Encounter ID',maxlength=20,blank=True)
    EncEncounter_Date = models.CharField('Encounter Date',maxlength=20,blank=True)
    EncEncounter_Status = models.CharField('Encounter Status',maxlength=20,blank=True)
    EncEncounter_ClosedDate = models.CharField('Encounter Closed Date',maxlength=20,blank=True) 
    EncEncounter_Provider = models.ForeignKey(Provider,blank=True,null=True) 
    EncEncounter_Site = models.CharField('Encounter Site',maxlength=20,blank=True)
    EncEncounter_SiteName = models.CharField('Encounter Site Name',maxlength=100,blank=True)
    EncEvent_Type = models.CharField('Event Type',maxlength=20,blank=True)
    EncPregnancy_Status = models.CharField('Pregnancy Status',maxlength=20,blank=True)
    EncEDC = models.CharField('Expected date of confinement',maxlength=20,blank=True) 
    EncTemperature = models.CharField('Temperature',maxlength=20,blank=True)
    EncCPT_codes = models.CharField('CPT codes',maxlength=200,blank=True)
    EncICD9_Codes = models.TextField('ICD-9 Codes',blank=True)
    EncICD9_Qualifier = models.CharField('ICD-9 Qualifier',maxlength=200,blank=True)

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
             #   if icd9l!= 0 and i in icd9l:
              #      s.append((1,'%s=%s' %(i,ilong)))

                if i:
                    s.append((i,ilong))
                else:
                    s.append(('', ''))
        else:
            s = [('', 'No icd9 codes found')]
        return s
    

    def iscaserelated(self):
        
        c = Case.objects.filter(caseEncID__contains=self.id,caseDemog__id__exact=self.EncPatient.id)

        try:
            l=[string.strip(x) for x in string.split(c[0].caseEncID, ',')]
            indx = l.index('%s' % self.id)
            icd9s = string.split(c[0].caseICD9,',')[indx]
            icd9l = string.split(icd9s)
            return icd9l
        except:
            return 0
        

    def getcliname(self):
        return self.EncEncounter_Provider.getcliname()       

    def __str__(self):

        return "%s %s %s %s" % (self.EncPatient.id,self.geticd9s(), self.EncMedical_Record_Number,self.EncEncounter_Date)


    class Admin:
        list_display = ('EncPatient', 'EncEncounter_Date','EncMedical_Record_Number')
        search_fields = ('EncMedical_Record_Number')





class Immunization(models.Model):
    ImmPatient = models.ForeignKey(Demog) 
    ImmType = models.CharField('Immunization Type',maxlength=20,blank=True)
    ImmName = models.CharField('Immunization Name',maxlength=200,blank=True)
    ImmDate = models.CharField('Immunization Date Given',maxlength=20,blank=True)
    ImmDose = models.CharField('Immunization Dose',maxlength=100,blank=True)
    ImmManuf =models.CharField('Manufacturer',maxlength=100,blank=True)
    ImmLot = models.TextField('Lot Number',maxlength=500,blank=True)
    ImmVisDate = models.CharField('Date of Visit',maxlength=20,blank=True)
    ImmRecId = models.CharField('Immunization Record Id',maxlength=200,blank=True)
    

    def __str__(self):

        return "%s %s %s" % (self.ImmPatient.DemogPatient_Identifier,self.ImmName,self.ImmRecId)


    class Admin:
        pass


class ConditionIcd9(models.Model):
    CondiRule = models.ForeignKey(Rule)
    CondiICD9 = models.TextField('ICD-9 Codes',blank=True)
    CondiDefine = models.BooleanField('Icd9 used in definition or not', blank=True)
    CondiSend = models.BooleanField('Icd9 needs to be sent or not', blank=True)

    def __str__(self):
        return '%s %s' % (self.CondiRule,self.CondiICD9)
        
    class Admin:
        list_display = ('CondiRule', 'CondiICD9')
        search_fields = ('CondiICD9')

class ConditionLOINC(models.Model):
    CondiRule = models.ForeignKey(Rule)
    CondiLOINC = models.TextField('LOINC Codes',blank=True)
    CondiDefine = models.BooleanField('Loinc used in definition or not', blank=True)
    CondiSend = models.BooleanField('Loinc needs to be sent or not', blank=True)
    CondiSNMDPosi = models.TextField('SNOMED Positive Codes',blank=True)
    CondiSNMDNega = models.TextField('SNOMED Negative Codes',blank=True)
    CondiSNMDInde = models.TextField('SNOMED Indeterminate Codes',blank=True)
    

    def __str__(self):
        return '%s %s' % (self.CondiRule,self.CondiLOINC)
        
    class Admin:
        list_display = ('CondiRule', 'CondiLOINC')
        search_fields = ('CondiLOINC')

class CPTLOINCMap(models.Model):
    CPT = models.TextField('CPT Codes',blank=True)
    CPTCompt = models.TextField('Compoment Codes',blank=True)
    Loinc = models.TextField('Loinc Codes',blank=True)

    def __str__(self):
        return '%s %s' % (self.CPT,self.CPTCompt)
        
    class Admin:
        list_display = ('CPT', 'CPTCompt')
        search_fields = ('CPT')

class ConditionNdc(models.Model):
    CondiRule = models.ForeignKey(Rule)
    CondiNdc = models.TextField('NDC Codes',blank=True)
    CondiDefine = models.BooleanField('Ndc used in definition or not', blank=True)
    CondiSend = models.BooleanField('Ndc need to be send or not', blank=True)

    def __str__(self):
        return '%s %s' % (self.CondiRule,self.CondiNdc)
        
    class Admin:
        list_display = ('CondiRule', 'CondiNdc')
        search_fields = ('CondiNdc')

    
class ConditionDrugName(models.Model):
    CondiRule = models.ForeignKey(Rule)
    CondiDrugName = models.TextField('Drug Name',blank=True)
    CondiDrugRoute = models.TextField('Drug Route',blank=True)
    CondiDefine = models.BooleanField('Used in case definition or not', blank=True)
    CondiSend = models.BooleanField('Must be sent or not', blank=True)

    def __str__(self):
        return '%s %s %s' % (self.CondiRule,self.CondiDrugName, self.CondiDrugRoute)
        
    class Admin:
        list_display = ('CondiRule', 'CondiDrugName','CondiDrugRoute')
        search_fields = ('CondiDrugName')


        
class DataFile(models.Model):
    filename = models.CharField('Raw data file name',maxlength=50,blank=True)
    datedownloaded = models.DateTimeField('Date loaded',editable=False,auto_now=True)

 
    def __str__(self):
        return '%s %s' % (self.filename,self.datedownloaded)

    class Admin:
        list_display = ('filename', 'datedownloaded')
        search_fields =('filename')
                                
