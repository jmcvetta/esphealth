'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                Core Data Model
                                      for
                                  ESP Health
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

import string
import datetime

from django.db import models
from django.contrib.auth.models import User 

from ESP.core import choices



class Provenance(models.Model):
    '''
    The provenance of an item of data (i.e. where it came from)
    '''
    source = models.CharField(max_length=255, blank=False) # E.g. a filename, 'web interface', 'db dump', etc
    date = models.DateTimeField(db_index=True, auto_now=True) # Date data was updated in ESP system
    # WTF: Should user really be blank=True?
    user = models.CharField(max_length=100, blank=True) # User who did this update
    class Meta:
        ordering = ['date', ]


class BaseProvenance(models.Model):
    '''
    Abstract base class providing provenance and create/update logging fields.
    '''
    provenance = models.ManyToManyField(Provenance)
    class Meta:
        abstract = True
    def latest_provenance(self):
        '''
        Return the most recent Provenance object for this model
        '''
        # FIXME: Does this work??
        return self.provenance_set.order_by('date')[0]


class BaseCreateUpdate(models.Model):
    '''
    Abstract base class providing Create/Update logging fields.
    '''
    # Maybe this is made redundant by BaseProvenance
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=50) # String repr of User
    class Meta:
        abstract = True


class Loinc(models.Model):
    '''
    Logical Observation Identifiers Names and Codes
        http://loinc.org
    '''
    code = models.CharField(primary_key=True, max_length=20)
    short_name = models.CharField(max_length=50, blank=False, db_index=True)
    long_name = models.CharField(max_length=500, blank=True, null=True)


class Icd9(models.Model):
    '''
    International Classification of Diseases and Related Health Problems codes v9
    '''
    code = models.CharField('ICD9 Code', max_length=10,)
    name = models.CharField('Name', max_length=50,)
        
   
class Ndc(models.Model):
    '''
    National Drug Code
        http://www.fda.gov/cder/ndc/
    '''
    # LISTING_SEQ_NO    LBLCODE    PRODCODE    STRENGTH    UNIT    RX_OTC    FIRM_SEQ_NO    TRADENAME
    # eeesh this is horrible - there may be asterisks indicating an optional 
    # zero and there is no obvious way to fix this...
    label_code = models.CharField('NDC Label Code (leading zeros are meaningless)', max_length=10,db_index=True)
    product_code = models.CharField('NDC Product Code', max_length=5,db_index=True)
    trade_name = models.CharField('NDC Trade Name', max_length=200,)
        
   
class Cpt(models.Model):
    '''
    Current Procedural Terminology code
        www.tricare.osd.mil/tai/downloads/cpt_codes.xls
    '''
    code = models.CharField('CPT Code', max_length=10,db_index=True)
    short_name = models.CharField('Short name', max_length=60,)
    long_name = models.TextField('Long name', max_length=500,)
    last_edit = models.DateTimeField('Last edited',editable=False,auto_now=True)

 
class Provider(BaseProvenance):
    '''
    A medical care provider
    '''
    code = models.CharField('Physician code',max_length=20,blank=True,db_index=True)
    last_name = models.CharField('Last Name',max_length=70,blank=True,null=True)
    first_name = models.CharField('First Name',max_length=50,blank=True,null=True)
    middle_initial = models.CharField('Middle_Initial',max_length=20,blank=True,null=True)
    title = models.CharField('Title',max_length=20,blank=True,null=True)
    primary_dept_id = models.CharField('Primary Department Id',max_length=20,blank=True,null=True)
    primary_dept = models.CharField('Primary Department',max_length=200,blank=True,null=True)
    primary_dept_address_1 = models.CharField('Primary Department Address 1',max_length=100,blank=True,null=True)
    primary_dept_address_2 = models.CharField('Primary Department Address 2',max_length=20,blank=True,null=True)
    primary_dept_city = models.CharField('Primary Department City',max_length=20,blank=True,null=True)
    primary_dept_state = models.CharField('Primary Department State',max_length=20,blank=True,null=True)
    primary_dept_zip = models.CharField('Primary Department Zip',max_length=20,blank=True,null=True)
    tel_area_code = models.CharField('Primary Department Phone Areacode',max_length=20,blank=True,null=True)
    telephone = models.CharField('Primary Department Phone Number',max_length=50,blank=True,null=True)


class Patient(BaseProvenance):
    '''
    A patient
    '''
    patient_identifier = models.CharField('Patient Identifier',max_length=20,blank=True,db_index=True)
    medical_record_number = models.CharField('Medical Record Number',max_length=20,db_index=True,blank=True)
    last_name = models.CharField('Last_Name',max_length=199,blank=True,null=True)
    first_name = models.CharField('First_Name',max_length=199,blank=True,null=True)
    middle_initial = models.CharField('Middle_Initial',max_length=199,blank=True,null=True)
    suffix = models.CharField('Suffix',max_length=199,blank=True,null=True)
    address1 = models.CharField('Address1',max_length=200,blank=True,null=True)
    address2 = models.CharField('Address2',max_length=100,blank=True,null=True)
    city = models.CharField('City',max_length=50,blank=True,null=True)
    state = models.CharField('State',max_length=20,blank=True,null=True)
    zip = models.CharField('Zip',max_length=20,blank=True,null=True)
    country = models.CharField('Country',max_length=20,blank=True,null=True)
    areacode = models.CharField('Home Phone Area Code',max_length=20,blank=True,null=True)
    tel = models.CharField('Home Phone Number',max_length=100,blank=True,null=True)
    ext = models.CharField('Home Phone Extension',max_length=50,blank=True,null=True)
    date_of_birth = models.CharField('Date of Birth',max_length=20,blank=True,null=True)
    gender = models.CharField('Gender',max_length=20,blank=True,null=True)
    race = models.CharField('Race',max_length=20,blank=True,null=True)
    home_language = models.CharField('Home Language',max_length=20,blank=True,null=True)
    ssn = models.CharField('SSN',max_length=20,blank=True,null=True)
    provider = models.ForeignKey(Provider,verbose_name="Provider ID",blank=True,null=True)
    marital_stat = models.CharField('Marital Status',max_length=20,blank=True,null=True)
    religion = models.CharField('Religion',max_length=20,blank=True,null=True)
    aliases = models.CharField('Aliases',max_length=250,blank=True,null=True)
    mother_mrn = models.CharField('Mother Medical Record Number',max_length=20,blank=True,null=True)
    death_date = models.CharField('Date of death',max_length=200,blank=True,null=True)
    death_indicator = models.CharField('Death_Indicator',max_length=30,blank=True,null=True)
    occupation = models.CharField('Occupation',max_length=199,blank=True,null=True)
            
    def  __unicode__(self):
        pass

    def getAge(self):
        # TODO: This should return a TimeDelta object or None if no DoB
        dob = self.DemogDate_of_Birth
        if not dob:
            return u'No DOB'
        
        try:
            yy = int(dob[:4])
            mm = int(dob[4:6])
            dd = int(dob[6:])
        except:
            age = 'Error'
            return age

        cury = int(datetime.datetime.now().strftime("%Y"))
        curm = int(datetime.datetime.now().strftime("%m"))
        curd = int(datetime.datetime.now().strftime("%d"))
        age = cury-yy
        if (curm==mm and curd<dd) or (curm<mm):
            age = age-1
        if age==0 and cury==yy:
            age = u'%s' % (curm-mm) + ' Months'
        elif age==0:
            age = u'%s' % (12-mm+curm) + ' Months'
        return age


class LabResultStatus(models.Model):
    '''
    The status of a lab result.
        This will contain some information that is redundant with LabResult, 
        e.g. result_string.
    '''
    loinc = models.ForeignKey(Loinc, blank=False)
    result_string = models.CharField(max_length=2000, blank=False)
    status = models.CharField(max_length=1, choices=choices.LAB_RESULT_STATUS, blank=False)


class LabResultManager(models.Manager):
    def result_strings(self, loinc):
        '''
        Returns a list of all result codes that have been seen so far for a 
        given LOINC.
        @type loinc: Str
        @return: [Str, Str, ...]
        '''
        return [x[0] for x in self.get_query_set().values_list('LxTest_results').distinct()]


class LabResult(models.Model):
    '''
    A result of a laboratory test
    '''
    patient = models.ForeignKey(Patient) 
    medical_record_num = models.CharField('Medical Record Id #', max_length=50, blank=True, null=True, db_index=True)
    loinc = models.ForeignKey(Loinc)
    order_num = models.CharField('Order Id #',max_length=20,blank=True,null=True)
    test_code_cpt = models.CharField('Test Code (CPT)',max_length=20,blank=True,null=True,db_index=True)
    test_code_cpt_mod = models.CharField('Test Code (CPT) Modifier',max_length=20,blank=True,null=True)
    order_date = models.CharField('Order Date',max_length=20,blank=True,null=True)
    order_type = models.CharField('Order Type',max_length=10,blank=True,null=True)   
    provider = models.ForeignKey(Provider, blank=True, null=True)  # Provider who ordered test
    result_date = models.CharField('Date of result',max_length=20,blank=True,null=True)  
    # This should not be here -- it must be a generalized field, not HVMA specific
    #LxHVMA_Internal_Accession_number = models.CharField('HVMA Internal Accession number',max_length=50,blank=True,null=True)
    component = models.CharField('Component',max_length=20,blank=True,null=True,db_index=True)
    component_name = models.CharField('Component Name', max_length=200, blank=True, null=True, db_index=True)
    result_string = models.TextField('Test Result String', max_length=2000, blank=True, null=True, db_index=True)
    # What is this about?
    #LxNormalAbnormal_Flag = models.CharField('Normal/Abnormal Flag',max_length=20,blank=True,null=True,db_index=True)
    #
    # Should references be in the result row?
    #LxReference_Low = models.CharField('Reference Low',max_length=100,blank=True,null=True)
    #LxReference_High = models.CharField('Reference High',max_length=100,blank=True,null=True)
    #LxReference_Unit = models.CharField('Reference Unit',max_length=100,blank=True,null=True)
    status = models.ForeignKey(LabResultStatus, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    impression = models.TextField('Impression for Imaging only',max_length=2000,blank=True,null=True)
    lastUpDate = models.DateTimeField('Last Updated date',auto_now=True,db_index=True)
    createdDate = models.DateTimeField('Date Created', auto_now_add=True)
    # Use custom manager
    objects = LabResultManager()
            
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
        return u"%s %s %s %s" % (self.LxPatient.DemogPatient_Identifier,self.getCPT(),self.LxOrder_Id_Num,self.LxOrderDate)
    

class Immunization(BaseProvenance):
    patient = models.ForeignKey(Patient) 
    type         = models.CharField('Immunization Type',max_length=20,blank=True,null=True)
    name         = models.CharField('Immunization Name',max_length=200,blank=True,null=True)
    date         = models.DateField('Immunization Date Given',max_length=20,blank=True,null=True)
    dose         = models.CharField('Immunization Dose',max_length=100,blank=True,null=True)
    manufacturer = models.CharField('Manufacturer',max_length=100,blank=True,null=True)
    lot          = models.TextField('Lot Number',max_length=500,blank=True,null=True)
    visit_date   = models.DateField('Date of Visit',max_length=20,blank=True,null=True)
    record_id    = models.CharField('Immunization Record Id',max_length=200,blank=True,null=True)
    def  __unicode__(self):
        return u"%s %s %s" % (self.patient, self.name, self.record_id)


class Encounter(BaseProvenance):
    patient = models.ForeignKey(Patient) 
    provider = models.ForeignKey(Provider,blank=True,null=True) 
    medical_record_number = models.CharField('Medical Record Number',max_length=20,blank=True,null=True,db_index=True)
    external_id = models.CharField('Encounter External ID',max_length=20,blank=True,null=True)
    date = models.CharField('Encounter Date',max_length=20,blank=True,null=True)
    # WTF: What's the diff between site and site_name?
    site = models.CharField('Encounter Site',max_length=20,blank=True,null=True)
    site_name = models.CharField('Encounter Site Name',max_length=100,blank=True,null=True)
    status = models.CharField('Encounter Status',max_length=20,blank=True,null=True)
    closed_date = models.DateField('Encounter Closed Date',max_length=20,blank=True,null=True) 
    event_type = models.CharField('Event Type',max_length=20,blank=True,null=True)
    pregnancy_status = models.CharField('Pregnancy Status',max_length=20,blank=True,null=True)
    edc = models.CharField('Expected Date of Confinement',max_length=20,blank=True,null=True) 
    temperature = models.CharField('Temperature',max_length=20,blank=True,null=True)
    cpt_codes = models.ForeignKey(Cpt, blank=True, null=True)
    icd9_codes = models.ForeignKey(Icd9, blank=True, null=True)
    # WTF: What is this qualifier?
    icd9_qualifier = models.CharField('ICD-9 Qualifier',max_length=200,blank=True,null=True)
    weight = models.CharField('Weight (kg)',max_length=200,blank=True,null=True)
    height = models.CharField('Height (cm)',max_length=200,blank=True,null=True)
    bpsys = models.FloatField('BP Systolic',max_length=100,blank=True,null=True)
    bpdias = models.FloatField('BP Diastolic',max_length=100,blank=True,null=True)
    o2stat = models.FloatField('O2 Stat',max_length=50,blank=True,null=True)
    peakflow = models.FloatField('Peak Flow',max_length=50,blank=True,null=True)
    def  __unicode__(self):
        return u"%s %s %s %s" % (self.patient.id, self.icd9_codes, self.medical_record_number,self.encounter_date)


class Case(models.Model):
    '''
    A case of reportable disease
    '''
    patient = models.ForeignKey(Patient, db_index=True)
    provider = models.ForeignKey(Provider, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    # Is this made redundant by CaseWorkFlow?
    #workflow_state = models.CharField(max_length=8, choices=choices.WORKFLOW_STATES, 
    #    blank=True, db_index=True )
    # 
    # Not sure what to do with these guys
    #
    #caseRule = models.ForeignKey(Rule,verbose_name="Case Definition ID")
    #caseQueryID = models.CharField('External Query which generated this case',max_length=20, blank=True, null=True)
    #caseMsgFormat = models.CharField('Case Message Format', max_length=20, choices=choices.FORMAT_TYPES, blank=True, null=True)
    #caseMsgDest = models.CharField('Destination for formatted messages', max_length=120, choices=choices.DEST_TYPES, blank=True,null=True)
    #
    # Related Objects:
    encounters = models.ManyToManyField(Encounter, blank=True, null=True)
    lab_results = models.ManyToManyField(LabResult, blank=True, null=True)
    icd9s = models.ManyToManyField(Icd9, blank=True, null=True)
    immunizations = models.ManyToManyField(Immunization, blank=True, null=True)
    send_date = models.DateTimeField('Date sent', null=True)


class CaseWorkflow(models.Model):
    case = models.ForeignKey(Case)
    # Date on which this workflow condition was activated
    date = models.DateTimeField(auto_now=True)
    state = models.CharField('Workflow State', choices=choices.WORKFLOW_STATES, max_length=8 )
    changed_by = models.CharField(max_length=50) # String repr of User
    comment = models.TextField(blank=True,null=True)


class Rx(models.Model):
    '''
    A prescription
    '''
    patient = models.ForeignKey(Patient) 
    medical_record_num = models.CharField('Medical Record #', max_length=20, blank=True, db_index=True)
    order_num = models.CharField('Order Id #', max_length=20, blank=True, null=True)
    provider = models.ForeignKey(Provider, blank=True, null=True)      
    order_date = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField('Order Status',max_length=20,blank=True,null=True)
    drug_name = models.TextField(max_length=3000, blank=True, null=True)
    drug_desc = models.TextField(max_length=3000, blank=True, null=True)
    ndc = models.ForeignKey(Ndc)
    dose = models.CharField(max_length=200, blank=True, null=True)
    frequency = models.CharField(max_length=200, blank=True, null=True)
    quantity = models.CharField(max_length=200, blank=True, null=True)
    refills = models.CharField(max_length=200, blank=True, null=True)
    route = models.CharField(max_length=200, blank=True, null=True)
    rx_start = models.CharField('Start Date',max_length=20,blank=True,null=True)
    rx_end = models.CharField('End Date',max_length=20,blank=True,null=True)
    lastUpDate = models.DateTimeField('Last Updated date',auto_now=True,db_index=True)
    createdDate = models.DateTimeField('Date Created', auto_now_add=True)
            
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
        
                  

class Lxo(models.Model):
    LxoPatient_Identifier = models.CharField('Patient Identifier',max_length=20,blank=True,null=True,db_index=True)
    LxoMedical_Record_Number = models.CharField('Medical Record Number',max_length=20,blank=True,null=True)
    LxoOrder_Id_Num = models.CharField('Order Id #',max_length=20,blank=True,null=True)
    LxoTest_ordered = models.CharField('Test ordered',max_length=20,blank=True,null=True)
    LxoHVMA_accession_number = models.CharField('HVMA accession number',max_length=20,blank=True,null=True)

    def  __unicode__(self):
        return u"%s %s %s %s" % (self.LxoPatient_Identifier,self.LxoMedical_Record_Number,self.LxoOrder_Id_Num,self.LxoTest_ordered)


class Icd9Fact(BaseProvenance):
    encounter = models.ForeignKey(Encounter, blank=False)
    code = models.ForeignKey(Icd9, blank=False)
    patient = models.ForeignKey(Patient, blank=False)
    encounter_date = models.CharField('Encounter Date',max_length=20,blank=True,null=True)
                               


#########################
class VAERSadditions(models.Model):
    patient = models.ForeignKey(Patient, blank=False)
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


                                                            

###################################
class SocialHistory(models.Model):
    patient = models.ForeignKey(Patient, blank=False)
    SocMRN = models.CharField('Medical Record Number',max_length=25,blank=True,null=True,db_index=True)
    SocTobUse = models.CharField('Tobacco use',max_length=200,blank=True,null=True)
    SocAlcoUse = models.CharField('Alcohol use',max_length=200,blank=True,null=True)
    lastUpDate = models.DateTimeField('Last Updated date',auto_now=True,db_index=True)
    createdDate = models.DateTimeField('Date Created', auto_now_add=True)


    def  __unicode__(self):
        
        return u"%s %s" % (self.SocPatient.DemogPatient_Identifier,self.SocMRN)
    


class Allergies(models.Model):
    patient = models.ForeignKey(Patient, blank=False)
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
    patient = models.ForeignKey(Patient, blank=False)
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


class Condition(BaseCreateUpdate):
    '''
    A reportable condition
    '''
    name = models.CharField(max_length=100, blank=False, db_index=True)
    comment = models.TextField(blank=True, null=True)
    ruleVerDate = models.DateTimeField('Last Edited date',auto_now=True)
    rulecreatedDate = models.DateTimeField('Date Created', auto_now_add=True)
    # Not sure how to handle these:
    #rulelastexecDate = models.DateTimeField('Date last executed', editable=False, blank=True, null=True)
    #ruleMsgFormat = models.CharField('Message Format', max_length=10, choices=FORMAT_TYPES,  blank=True, null=True)
    #ruleMsgDest = models.CharField('Destination for formatted messages', max_length=10, choices=DEST_TYPES,  blank=True, null=True)
    #ruleExcludeCode = models.TextField('The exclusion list of (CPT, COMPT) when alerting', blank=True, null=True)
    hl7_code = models.CharField('Code for HL7 messages with cases', max_length=10, blank=True, null=True)
    hl7_code_type = models.CharField('Code for HL7 code type', max_length=10, blank=True, null=True)
    hl7_name = models.CharField('Condition name for HL7 messages with cases', max_length=30, blank=True, null=True)
    production = models.BooleanField(blank=False, default=False) # Scheme for detecting this condition is in production
    init_case_status = models.CharField('Initial Case status', max_length=10, choices=choices.WORKFLOW_STATES, blank=False)
                                              
                                            
class ConditionIcd9(models.Model):
    condition = models.ForeignKey(Condition, blank=False)
    CondiICD9 = models.TextField('ICD-9 Codes',blank=True,null=True)
    CondiDefine = models.BooleanField('Icd9 used in definition or not', blank=True,null=True)
    CondiSend = models.BooleanField('Icd9 needs to be sent or not', blank=True,null=True)
    def  __unicode__(self):
        return u'%s %s' % (self.CondiRule,self.CondiICD9)


class ConditionNdc(models.Model):
    condition = models.ForeignKey(Condition, blank=False)
    CondiNdc = models.TextField('NDC Codes',blank=True,null=True)
    CondiDefine = models.BooleanField('Ndc used in definition or not', blank=True,null=True)
    CondiSend = models.BooleanField('Ndc need to be send or not', blank=True,null=True)

    def  __unicode__(self):
        return u'%s %s' % (self.CondiRule,self.CondiNdc)
        
 
class ConditionDrugName(models.Model):
    condition = models.ForeignKey(Condition, blank=False)
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


###################################
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

