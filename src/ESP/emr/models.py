'''
                              ESP Health Project
                     Electronic Medical Records Warehouse
                                  Data Models

@authors: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''


from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from ESP.emr import choices
from ESP.conf.models import SourceSystem
from ESP.conf.models import NativeCode
from ESP.conf.models import Loinc
from ESP.conf.models import Ndc
from ESP.conf.models import Cpt
from ESP.conf.models import Icd9
from ESP.conf.models import NativeCode
from ESP.utils.utils import log


#class Provenance(models.Model):
#    '''
#    Answers the question "Where did this data come from?"
#    '''
#    provenance_id = models.AutoField(primary_key=True)
#    file_name = models.CharField(max_length=500, blank=True, null=True)
#    file_date = models.DateField('Timestamp on file', blank=True, null=True)
#    hostname = models.CharField('Host from which data was loaded', max_length=255, blank=True)
#    batch_timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)
#    
#    class Meta:
#        unique_together = ['file_name', 'file_date', 'hostname']


class Hl7Message(models.Model):
    '''
    An HL7 file from which EMR data was loaded into the database.  Records when 
    we tried to import the file, and the status of our attempt.
    '''
    filename = models.CharField(max_length=255, blank=False, unique=True, db_index=True)
    timestamp = models.DateTimeField(blank=False)
    status = models.CharField(max_length=1, choices=choices.HL7_MESSAGE_LOAD_STATUS, 
        blank=False, db_index=True)
    message = models.TextField('Status Message', blank=True, null=True)


#===============================================================================
#
#--- ~~~ Medical Records ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class BaseMedicalRecord(models.Model):
    '''
    Abstract base class for a medical record
    '''
    #system = models.ForeignKey(SourceSystem, db_index=True, blank=False)
    #provenance = models.ForeignKey(Provenance, blank=True)
    created_timestamp = models.DateTimeField(auto_now_add=True, blank=False)
    updated_timestamp = models.DateTimeField(auto_now=True, blank=False)
    updated_by = models.CharField(max_length=100, blank=False)
    class Meta:
        abstract = True
    

class Provider(BaseMedicalRecord):
    '''
    A medical care provider
    '''
    provider_id_num = models.CharField('Physician code', unique=True, max_length=20, 
        blank=True, null=True, db_index=True)
    last_name = models.CharField('Last Name',max_length=70,blank=True,null=True)
    first_name = models.CharField('First Name',max_length=50,blank=True,null=True)
    middle_initial = models.CharField('Middle_Initial',max_length=20,blank=True,null=True)
    title = models.CharField('Title',max_length=20,blank=True,null=True)
    dept_id_num = models.CharField('Primary Department Id',max_length=20,blank=True,null=True)
    dept = models.CharField('Primary Department',max_length=200,blank=True,null=True)
    dept_address_1 = models.CharField('Primary Department Address 1',max_length=100,blank=True,null=True)
    dept_address_2 = models.CharField('Primary Department Address 2',max_length=20,blank=True,null=True)
    dept_city = models.CharField('Primary Department City',max_length=20,blank=True,null=True)
    dept_state = models.CharField('Primary Department State',max_length=20,blank=True,null=True)
    dept_zip = models.CharField('Primary Department Zip',max_length=20,blank=True,null=True)
    area_code = models.CharField('Primary Department Phone Areacode',max_length=20,blank=True,null=True)
    telephone = models.CharField('Primary Department Phone Number',max_length=50,blank=True,null=True)
    
    def _get_name(self):
        return u'%s, %s %s %s' % (self.last_name, self.title, self.first_name, self.middle_initial)
    name = property(_get_name)
    
    def __unicode__(self):
        return self.name


class Patient(BaseMedicalRecord):
    '''
    A patient, with demographic information
    '''
    patient_id_num = models.CharField('Patient ID #', unique=True, max_length=20, 
        blank=True, null=True, db_index=True)
    mrn = models.CharField('Medical Record ', max_length=20, blank=True, null=True, db_index=True)
    last_name = models.CharField('Last Name', max_length=199, blank=True, null=True)
    first_name = models.CharField('First Name', max_length=199, blank=True, null=True)
    middle_name = models.CharField('Middle Name', max_length=199, blank=True, null=True)
    suffix = models.CharField('Suffix', max_length=199, blank=True, null=True)
    pcp = models.ForeignKey(Provider, verbose_name='Primary Care Physician', blank=True, null=True)
    address1 = models.CharField('Address1', max_length=200, blank=True, null=True)
    address2 = models.CharField('Address2', max_length=100, blank=True, null=True)
    city = models.CharField('City', max_length=50, blank=True, null=True)
    state = models.CharField('State', max_length=20, blank=True, null=True)
    zip = models.CharField('Zip', max_length=20, blank=True, null=True)
    country = models.CharField('Country', max_length=20, blank=True, null=True)
    areacode = models.CharField('Home Phone Area Code', max_length=20, blank=True, null=True)
    tel = models.CharField('Home Phone Number', max_length=100, blank=True, null=True)
    tel_ext = models.CharField('Home Phone Extension', max_length=50, blank=True, null=True)
    dob = models.CharField('Date of Birth', max_length=20, blank=True, null=True)
    gender = models.CharField('Gender', max_length=20, blank=True, null=True)
    race = models.CharField('Race', max_length=20, blank=True, null=True)
    home_language = models.CharField('Home Language', max_length=20, blank=True, null=True)
    ssn = models.CharField('SSN', max_length=20, blank=True, null=True)
    marital_stat = models.CharField('Marital Status', max_length=20, blank=True, null=True)
    religion = models.CharField('Religion', max_length=20, blank=True, null=True)
    aliases = models.CharField('Aliases', max_length=250, blank=True, null=True)
    mother_mrn = models.CharField('Mother Medical Record Number', max_length=20, blank=True, null=True)
    death_date = models.CharField('Date of death', max_length=200, blank=True, null=True)
    death_indicator = models.CharField('Death_Indicator', max_length=30, blank=True, null=True)
    occupation = models.CharField('Occupation', max_length=199, blank=True, null=True)
    
    def _get_name(self):
        return u'%s, %s %s' % (self.last_name, self.first_name, self.middle_name)
    name = property(_get_name)
    
    def __str__(self):
        return self.name
    


#===============================================================================
#
#--- ~~~ Patient Records ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasePatientRecord(BaseMedicalRecord):
    '''
    A patient record is a medical record tied to a specific patient and provider
    '''
    patient = models.ForeignKey(Patient, blank=True, null=True) 
    provider = models.ForeignKey(Provider, blank=True, null=True) 
    # Meaning of date (e.g. order date or result date?) should be specified in child classes
    date = models.DateField(blank=True, null=True) 
    # Does it make sense to have an MRN field on every patient record table?  
    # Will all patient records have their own individual MRN?
    mrn = models.CharField('Medical Record Number', max_length=50, blank=True, null=True)
    
    class Meta:
        abstract = True


class LabResultManager(models.Manager):
    @classmethod
    def filter_loincs(self, loinc_nums, **kwargs):
        '''
        Translate LOINC numbers to native codes and lookup
        @param loinc_nums: List of LOINC numbers for which to retrieve lab results
        @type loinc_nums:  [String, String, ...]
        @return: QuerySet
        '''
        log.debug('Querying lab results by LOINC')
        log.debug('LOINCs: %s' % loinc_nums)
        native_codes = NativeCode.objects.filter(loinc__in=loinc_nums).values_list('native_code', flat=True)
        log.debug('Native Codes: %s' % native_codes)
        return LabResult.objects.filter(native_code__in=native_codes, **kwargs)

    
class LabResult(BasePatientRecord):
    '''
    Result data for a lab test
    '''
    # Date (from base class) is result date
    #
    # Coding
    native_code = models.CharField(max_length=30, blank=True, null=True, db_index=True)
    native_name = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    # Order
    #order = models.ForeignKey(LabOrder, blank=True, null=True)
    order_date = models.DateField(blank=True, null=True, db_index=True)
    order_num = models.CharField(max_length=128, blank=True, null=True)
    status = models.CharField('Result Status', max_length=50, blank=True, null=True)
    #result_id_num = models.CharField('Result Id #', max_length=100, blank=True, null=True)
    # Reference
    ref_low = models.FloatField('Reference Low', blank=True, null=True, db_index=True)
    ref_high = models.FloatField('Reference High', blank=True, null=True, db_index=True)
    ref_unit = models.CharField('Measurement Unit', max_length=100, blank=True, null=True)
    ref_range = models.CharField('Reference Range (raw string)', max_length=255, blank=True, null=True)
    # Result
    abnormal_flag = models.CharField(max_length=20, blank=True, null=True, db_index=True)
    result_float = models.FloatField('Test results (numeric)', blank=True, null=True, db_index=True)
    result_string = models.TextField('Test results (textual)', max_length=2000, blank=True, null=True, db_index=True)
    # Wide fields
    impression = models.TextField('Impression (for imaging)', max_length=2000, blank=True, null=True)
    comment = models.TextField('Comments',  blank=True,  null=True, )
    # Manager
    objects = LabResultManager()
    # 
    
    class Meta:
        verbose_name = 'Lab Test Result'
        
    def __str__(self):
        return 'Lab Result #%s' % self.pk
    
    def loinc_num(self):
        '''
        Returns LOINC number (not Loinc object!) for this test if it is mapped
        to one, else returns None.
        '''
        nc = NativeCode.objects.filter(native_code=self.native_code)
        if nc:
            return nc[0].loinc.loinc_num
        else:
            return None


class Prescription(BasePatientRecord):
    '''
    A prescribed medication
    '''
    # Date is order date
    #
    order_num = models.CharField('Order Id #', max_length=20, blank=True, null=True)
    name = models.TextField(max_length=3000, blank=False, db_index=True)
    code = models.CharField('Drug Code (system varies by site)', max_length=255, blank=True, null=True)
    directions = models.TextField(max_length=3000, blank=True, null=True)
    dose = models.CharField(max_length=200, blank=True, null=True)
    frequency = models.CharField(max_length=200, blank=True, null=True)
    quantity = models.CharField(max_length=200, blank=True, null=True)
    refills = models.CharField(max_length=200, blank=True, null=True)
    route = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField('Order Status', max_length=20, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    
class Encounter(BasePatientRecord):
    '''
    A encounter between provider and patient
    '''
    # Date is encounter date
    #
    icd9_codes = models.ManyToManyField(Icd9,  blank=True,  null=True, db_index=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    closed_date = models.DateField(blank=True, null=True)
    site_name = models.CharField(max_length=100, blank=True, null=True)
    native_site_num = models.CharField('Site Id #', max_length=30, blank=True, null=True)
    native_encounter_num = models.CharField('Encounter Id #', max_length=20, blank=True, null=True)
    #cpt = models.ForeignKey(Cpt,  blank=True,  null=True)
    event_type = models.CharField(max_length=20, blank=True, null=True)
    pregnancy_status = models.CharField(max_length=20, blank=True, null=True)
    edc = models.DateField('Expected date of confinement', blank=True, null=True) 
    temperature = models.FloatField('Temperature (C)', blank=True, null=True, db_index=True)
    # WTF: What is an icd9_qualifier?
    #icd9_qualifier = models.CharField(max_length=200, blank=True, null=True)
    weight = models.FloatField('Weight (kg)', max_length=200, blank=True, null=True)
    height = models.FloatField('Height (cm)', max_length=200, blank=True, null=True)
    bp_systolic = models.FloatField('Blood Pressure - Systolic (mm Hg)', blank=True, null=True)
    bp_diastolic = models.FloatField('Blood Pressure - Diastolic (mm Hg)', blank=True, null=True)
    o2_stat = models.FloatField(max_length=50, blank=True, null=True)
    peak_flow = models.FloatField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return 'Encounter #%s' % self.pk
            

class Immunization(BasePatientRecord):
    '''
    An immunization
    '''
    # Date is immunization date
    #
    imm_id_num = models.CharField('Immunization Record Id', max_length=200, blank=True, null=True)
    imm_type = models.CharField('Immunization Type', max_length=20, blank=True, null=True)
    name = models.CharField('Immunization Name', max_length=200, blank=True, null=True)
    dose = models.CharField('Immunization Dose', max_length=100, blank=True, null=True)
    manufacturer = models.CharField('Manufacturer', max_length=100, blank=True, null=True)
    lot = models.TextField('Lot Number', max_length=500, blank=True, null=True)
    visit_date = models.DateField('Date of Visit', blank=True, null=True)

