'''
                               Core Data Models 
                                for ESP Health
'''


from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from ESP.core import choices
from ESP.conf.models import SourceSystem
from ESP.conf.models import NativeToLoincMap
from ESP.conf.models import Loinc
from ESP.conf.models import Ndc
from ESP.conf.models import Cpt
from ESP.conf.models import Icd9
from ESP.utils.utils import log


#===============================================================================
#
#--- ~~~ Provenance ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Provenance(models.Model):
    '''
    Answers the question "Where did this data come from?"
    '''
    provenance_id = models.AutoField(primary_key=True)
    file_name = models.CharField(max_length=500, blank=True, null=True)
    file_date = models.DateField('Timestamp on file', blank=True, null=True)
    hostname = models.CharField('Host from which data was loaded', max_length=255, blank=True)
    batch_timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    
    class Meta:
        unique_together = ['file_name', 'file_date', 'hostname']


class BaseMedicalRecord(models.Model):
    '''
    Abstract base class for a medical record
    '''
    system = models.ForeignKey(SourceSystem, db_index=True, blank=False)
    #provenance = models.ForeignKey(Provenance, blank=True)
    created_timestamp = models.DateTimeField(auto_now_add=True, blank=False)
    updated_timestamp = models.DateTimeField(auto_now=True, blank=False)
    updated_by = models.CharField(max_length=100, blank=False)
    class Meta:
        abstract = True
    

#===============================================================================
#
#--- ~~~ Medical Records ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class Provider(BaseMedicalRecord):
    '''
    A medical care provider
    '''
    provider_id_num = models.CharField('Physician code', max_length=20, blank=True, null=True, db_index=True)
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
    
    class Meta:
        unique_together = ['provider_id_num', 'system']
    
    def _get_name(self):
        return u'%s, %s %s %s' % (self.last_name, self.title, self.first_name, self.middle_initial)
    name = property(_get_name)
    
    def __unicode__(self):
        return self.name


class Patient(BaseMedicalRecord):
    '''
    A patient, with demographic information
    '''
    patient_id_num = models.CharField('Patient ID #', max_length=20, blank=True, null=True, db_index=True)
    provider_id_num = models.CharField('Provider ID #', max_length=20, blank=True, null=True, db_index=True)
    mrn = models.CharField('Medical Record ', max_length=20, blank=True, null=True, db_index=True)
    last_name = models.CharField('Last Name', max_length=199, blank=True, null=True)
    first_name = models.CharField('First Name', max_length=199, blank=True, null=True)
    middle_name = models.CharField('Middle Name', max_length=199, blank=True, null=True)
    suffix = models.CharField('Suffix', max_length=199, blank=True, null=True)
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
    provider = models.ForeignKey(Provider, verbose_name="Provider ID", blank=True, null=True)
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
    
    def __unicode__(self):
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
    patient_id_num = models.CharField('Patient Identifier', max_length=50, blank=True, null=True)
    provider_id_num = models.CharField('Provider ID #', max_length=50, blank=True, null=True)
    mrn = models.CharField('Medical Record Number', max_length=50, blank=True, null=True)
    
    class Meta:
        abstract = True


class LabOrder(BasePatientRecord):
    '''
    An order for a lab test
    '''
    # Date is order date
    #
    order_id_num = models.CharField('Order Id #', max_length=20, blank=True, null=True)
    
    class Meta:
        verbose_name = 'Lab Test Order'


class LabResultManager(models.Manager):
    @classmethod
    def filter_loincs(self, loinc_nums, **kwargs):
        '''
        Translate LOINC numbers to native codes and lookup
        @param loinc_nums: List of LOINC numbers for which to retrieve lab results
        @type loinc_nums:  [String, String, ...]
        '''
        log.debug('Querying lab results by LOINC')
        log.debug('LOINCs: %s' % loinc_nums)
        native_codes = NativeToLoincMap.objects.filter(loinc__in=loinc_nums).values_list('native_code', flat=True)
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
    native_name = models.CharField(max_length=255, blank=True, null=True)
    # Order
    order = models.ForeignKey(LabOrder, blank=True, null=True)
    order_id_num = models.CharField('Order Id #', max_length=20, blank=True, null=True)
    order_date = models.DateField(blank=True, null=True)
    status = models.CharField('Result Status', max_length=50, blank=True, null=True)
    result_id_num = models.CharField('Result Id #', max_length=100, blank=True, null=True)
    # Reference
    ref_unit = models.CharField('Measurement Unit', max_length=100, blank=True, null=True)
    ref_low_string = models.CharField('Reference Low (string)', max_length=100, blank=True, null=True)
    ref_high_string = models.CharField('Reference High (string)', max_length=100, blank=True, null=True)
    ref_low_float = models.FloatField('Reference Low (number)', blank=True, null=True, db_index=True)
    ref_high_float = models.FloatField('Reference High (number)', blank=True, null=True, db_index=True)
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


class Medication(BasePatientRecord):
    '''
    A prescribed medication
    '''
    # Date is order date
    #
    order_id_num = models.CharField('Order Id #', max_length=20, blank=True, null=True)
    ndc = models.ForeignKey(Ndc, blank=True, null=True)
    # Is ndc_str necessary?
    ndc_str = models.CharField('National Drug Code', max_length=20, blank=True, null=True)
    name = models.TextField(max_length=3000, blank=False)
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
    icd9_codes = models.ManyToManyField(Icd9,  blank=True,  null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    closed_date = models.DateField(blank=True, null=True)
    site_name = models.CharField(max_length=100, blank=True, null=True)
    native_site_num = models.CharField('Site Id #', max_length=30, blank=True, null=True)
    native_encounter_num = models.CharField('Encounter Id #', max_length=20, blank=True, null=True)
    cpt = models.ForeignKey(Cpt,  blank=True,  null=True)
    event_type = models.CharField(max_length=20, blank=True, null=True)
    pregnancy_status = models.CharField(max_length=20, blank=True, null=True)
    edc = models.DateField('Expected date of confinement', blank=True, null=True) 
    temperature = models.FloatField(blank=True, null=True)
    # WTF: What is an icd9_qualifier?
    #icd9_qualifier = models.CharField(max_length=200, blank=True, null=True)
    weight = models.FloatField('Weight (kg)', max_length=200, blank=True, null=True)
    height = models.FloatField('Height (cm)', max_length=200, blank=True, null=True)
    bp_systolic = models.FloatField('Blood Pressure - Systolic', blank=True, null=True)
    bp_diastolic = models.FloatField('Blood Pressure - Diastolic', blank=True, null=True)
    o2_stat = models.FloatField(max_length=50, blank=True, null=True)
    peak_flow = models.FloatField(max_length=50, blank=True, null=True)
            

class Immunization(BasePatientRecord):
    '''
    An immunization
    '''
    # Date is immunization date
    #
    ext_imm_id_num = models.CharField('Immunization Record Id', max_length=200, blank=True, null=True)
    imm_type = models.CharField('Immunization Type', max_length=20, blank=True, null=True)
    name = models.CharField('Immunization Name', max_length=200, blank=True, null=True)
    dose = models.CharField('Immunization Dose', max_length=100, blank=True, null=True)
    manufacturer = models.CharField('Manufacturer', max_length=100, blank=True, null=True)
    lot = models.TextField('Lot Number', max_length=500, blank=True, null=True)
    visit_date = models.DateField('Date of Visit', blank=True, null=True)





