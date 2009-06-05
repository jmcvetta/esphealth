'''
                              ESP Health Project
                     Electronic Medical Records Warehouse
                                  Data Models

@authors: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''

import string
import random
import datetime

from django.db import models
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from ESP.emr import choices
from ESP.conf.common import EPOCH
from ESP.conf.models import SourceSystem
from ESP.conf.models import Loinc, Ndc, Cpt, Icd9, NativeCode
from ESP.conf.models import Vaccine
from ESP.utils import randomizer
from ESP.utils.utils import log, date_from_str, str_from_date
from ESP.localsettings import DATABASE_ENGINE



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
    
    
    q_fake = Q(provider_id_num__startswith='FAKE')

    # Some methods to deal with mock/fake data
    @staticmethod
    def fakes():
        return Provider.objects.filter(Provider.q_fake)

    @staticmethod
    def delete_fakes():
        Provider.fakes().delete()

    @staticmethod
    def make_fakes(how_many):
        for i in xrange(0, how_many):
            Provider.make_mock(save_on_db=True)
            
    @staticmethod
    def make_mock(save_on_db=False):
        code = 'FAKE-%05d' % random.randrange(1, 100000)
        
        if Provider.objects.filter(provider_id_num=code).count() == 1:
            return Provider.objects.get(provider_id_num=code)
        else:        
            p = Provider(
                provider_id_num = code,
                last_name = randomizer.first_name(),
                first_name = randomizer.last_name(),
                middle_initial = random.choice(string.uppercase),
                title = 'Fake Dr.',
                dept_id_num = 'Department of Wonderland',
                dept_address_1 = randomizer.address(),
                dept_zip = randomizer.zip_code(),
                telephone = randomizer.phone_number()
                )
            
            if save_on_db: p.save()
            return p

    
    def is_fake(self):
        return self.provider_id_num.startswith('FAKE')

    def _get_name(self):
        return u'%s, %s %s %s' % (self.last_name, self.title, self.first_name, self.middle_initial)
    name = property(_get_name)
    full_name = property(_get_name)
    
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
    dob = models.DateField('Date of Birth', blank=True, null=True)
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


    q_fake = Q(patient_id_num__startswith='FAKE')

    @staticmethod
    def fakes():
        return Patient.objects.filter(Patient.q_fake)


    @staticmethod
    def clear():
        Patient.fakes().delete()
            
    @staticmethod
    def make_fakes(how_many, save_on_db=True):
        for i in xrange(how_many):
            Patient.make_mock(save_on_db=save_on_db)


    @staticmethod
    def delete_fakes():
        Patient.fakes().delete()

    @staticmethod
    def make_mock(save_on_db=False):

        # Common, random attributes
        phone_number = randomizer.phone_number()
        address = randomizer.address()
        city = randomizer.city()
        identifier = randomizer.string(length=8)


        # A Fake Patient must have a fake provider. If we have one on
        # the DB, we get a random one. Else, we'll have to create them
        # ourselves.
        if Provider.fakes().count() > 0:        
            provider = Provider.fakes().order_by('?')[0]
        else:
            provider = Provider.make_mock(save_on_db=save_on_db)
        
        p = Patient(
            pcp = provider,
            patient_id_num = 'FAKE-%s' % identifier,
            mrn = 'FAKE-MRN-%s' % identifier,
            last_name = randomizer.last_name(),
            first_name = randomizer.first_name(),
            suffix = '',
            country = 'Fakeland',
            city = city[0],
            state = city[1],
            zip = randomizer.zip_code(),
            address1 = address,
            address2 = '',
            middle_name = random.choice(string.uppercase),
            dob = randomizer.date_of_birth(as_string=False),
            gender = randomizer.gender(),
            race = randomizer.race(),
            areacode = phone_number.split('-')[0],
            tel = phone_number[4:],
            tel_ext = '',
            ssn = randomizer.ssn(),
            marital_stat = randomizer.marital_status(),
            religion = '',
            aliases = '',
            home_language = '',
            mother_mrn = '',
            death_date = '',
            death_indicator = '',
            occupation = ''
            )
        
        if save_on_db: p.save()
        return p

    @staticmethod
    def random(fake=True):
        '''Returns a random fake user. If fake is False, returns a
        completely random user'''
        objs = Patient.objects
        query = objs.filter(Patient.q_fake) if fake else objs.all()
        return query.order_by('?')[0]
        

    def has_history_of(self, icd9s, begin_date=None, end_date=None):
        '''
        returns a boolean if the patient has any of the icd9s code 
        in their history of encounters.
        '''
        begin_date = begin_date or self.dob or EPOCH
        end_date = end_date or datetime.date.today()

        return Encounter.objects.filter(patient=self).filter(
            date__gte=begin_date, date__lt=end_date
            ).filter(icd9_codes__in=icd9s).count() != 0
    
    def _get_name(self):
        return u'%s, %s %s' % (self.last_name, self.first_name, self.middle_name)

    def _get_age_str(self):
        '''Returns patient's age as a string'''
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
                
        if years > 0:
            return str(years) 
        else:
            return '%d Months' % months
        
    def _get_dob(self):
        '''Here just because dob still needs to be changed from a
        CharField to a DateField. Dump This afterwards.'''
        try:
            self.dob.day
            return self.dob
        except:
            return date_from_str(self.dob)

    
    def _set_dob(self, value):
        try:
            self.dob = value
            assert self.dob.day == value.day
        except:
            self.dob = str_from_date(value)

    date_of_birth = property(_get_dob, _set_dob)


    name = property(_get_name)
    full_name = property(_get_name)
    
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
    def following_vaccination(self, days_after, loinc=None, begin_date=None, end_date=None):

        begin_date = begin_date or EPOCH
        end_date = end_date or datetime.date.today()

        lab_result_meta = LabResult.objects.model._meta
        patient_meta = Patient.objects.model._meta
        imm_meta = Immunization.objects.model._meta
        
        # Get PKs from patients, lab results, immunizations
        # We will need them to construct a correct WHERE clause
        ppk =  '%s.%s' % (patient_meta.db_table, patient_meta.pk.name) 
        lab_result_pk = '%s.%s' % (lab_result_meta.db_table, lab_result_meta.pk.name) 

        lab_result_fk = '%s.%s' % (lab_result_meta.db_table, 
                            lab_result_meta.get_field('patient').attname) 
        imm_fk = '%s.%s' % (imm_meta.db_table, 
                            imm_meta.get_field('patient').attname)

        patient_in_encounter = '%s=%s' % (ppk, lab_result_fk) #Patient.id=Encounter.EncounterPatient_id
        patient_in_immunization = '%s=%s' % (ppk, imm_fk) #Patient.id = Imm.ImmPatient_id


        # Get "Full Name" for ResultDate and ImmunizationDate fields
        lab_result_date_field = '%s.%s' % (lab_result_meta.db_table, 'result_date')
        imm_date_field = '%s.%s' % (imm_meta.db_table, 'date')


         
        # Let's construct the date comparison string. Basically, what
        # we want is to compare between the dates of two different
        # fields, in two different models. There is a good chance that
        # Django's F() Objects can do this, but this code was handling
        # string-to-date transformations before and the whole process
        # was even messier.

        
        # We start by getting the proper date comparison function, depending on the database.
        if DATABASE_ENGINE == 'sqlite3':
            date_cmp_select = 'julianday(%s) - julianday(%s)'
            params = (lab_result_date_field, imm_date_field)
        elif DATABASE_ENGINE == 'mysql':
            date_cmp_select = "DATEDIFF(%s, %s)"
            params = (lab_result_date_field, imm_date_field)
        elif DATABASE_ENGINE in ('postgresql_psycopg2', 'postgresql'):
            date_cmp_select = "date(%s) - date(%s)"
            params = (lab_result_date_field, imm_date_field)
        else:
            raise NotImplementedError, 'Implemented only for PostgreSQL, mySQL and Sqlite'

        # Now, we get the comparison string and put it together with
        # the expected value, so we create the time window constraint
        max_days = '%s <= %s' % (date_cmp_select % params, str(days_after))
        same_day = (date_cmp_select % params) + ' >= 0'

        # This is our minimum WHERE clause
        where_clauses = [patient_in_encounter, patient_in_immunization, 
                         max_days, same_day]

        
        # begin_date and end_date are the dates that are give the date
        # range of the encounters we are looking for. Luckily, all of
        # the DB Engines agree on this one. We can compare a date
        # field with a string in the format 'YYYY-MM-DD'.
        where_clauses.append("%s >= '%s'" % (imm_date_field, begin_date.strftime('%Y-%m-%d')))
        where_clauses.append("%s <= '%s'" % (imm_date_field, end_date.strftime('%Y-%m-%d')))


        # To find an specific lab result.    
        qs = self.filter_loincs([loinc]) if loinc else self

        return qs.extra(
            tables = [patient_meta.db_table, imm_meta.db_table],
            where = where_clauses
            )
    




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
    # Date (from base class) is order date
    #
    # Coding
    native_code = models.CharField(max_length=30, blank=True, null=True, db_index=True)
    native_name = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    order_num = models.CharField(max_length=128, blank=True, null=True)
    result_date = models.DateField(blank=True, null=True, db_index=True)
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


    q_fake = Q(patient__patient_id_num__startswith='FAKE')

    @staticmethod
    def fakes():
        return LabResult.objects.filter(LabResult.q_fake)
    
    @staticmethod
    def delete_fakes():
        LabResult.fakes().delete()

    @staticmethod
    def make_mock(loinc, patient, when=None, save_on_db=True):
        when = when or datetime.date.today()

        order_date = when - datetime.timedelta(
            days=random.randrange(1, 10))

        # Make sure the patient was alive for the order...
        order_date = max(order_date, patient.dob)
        lx = LabResult(patient=patient, date=order_date, result_date=when)
        if save_on_db: lx.save()
        return lx


    def previous(self):
        try:
            return LabResult.objects.filter(patient=self.patient, 
                                            native_code=self.native_code
                                            ).exclude(date__gte=self.date
                                                      ).latest('date')
        except:
            return None


    def last_known_value(self, loinc, since=None):
        last = self.previous()                                     
        return (last and (last.result_float or last.result_string)) or None

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

    def _get_loinc(self):
        try:
            return NativeCode.objects.get(native_code=self.native_code, 
                                          native_name=self.native_name)
        except:
            return None
        
    def _set_loinc(self, value):
        try:
            mapping = NativeCode.objects.get(loinc=value)
            self.native_code = mapping.native_code
            self.native_name = mapping.native_name
        except:
            raise ValueError, "%s is not a valid Loinc" % value

    loinc = property(_get_loinc, _set_loinc)


    def __str__(self):
        return 'Lab Result #%s' % self.pk
    
    def __unicode__(self):
        return u'Lab Result #%s' % self.pk
    
    
    
    
    
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


class EncounterManager(models.Manager):
    def following_vaccination(self, days_after, begin_date=None, end_date=None):

        begin_date = begin_date or EPOCH
        end_date = end_date or datetime.date.today()
        
        encounter_meta = Encounter.objects.model._meta
        patient_meta = Patient.objects.model._meta
        imm_meta = Immunization.objects.model._meta
        
        # Get PKs from patients, encounters, immunizations
        # We will need them to construct a correct WHERE clause
        ppk =  '%s.%s' % (patient_meta.db_table, patient_meta.pk.name) 
        enc_pk = '%s.%s' % (encounter_meta.db_table, encounter_meta.pk.name) 

        enc_fk = '%s.%s' % (encounter_meta.db_table, 
                            encounter_meta.get_field('patient').attname) 
        imm_fk = '%s.%s' % (imm_meta.db_table, 
                            imm_meta.get_field('patient').attname)

        #Patient.id=Encounter.patient_id
        patient_in_encounter = '%s=%s' % (ppk, enc_fk) 

        #Patient.id = Immunization.patient_id
        patient_in_immunization = '%s=%s' % (ppk, imm_fk) 

        # Get "Full Name" for date fields
        enc_date_field = '%s.%s' % (encounter_meta.db_table, 'date')
        imm_date_field = '%s.%s' % (imm_meta.db_table, 'date')


     
        # Let's construct the date comparison string. Basically, what
        # we want is to compare between the dates of two different
        # fields, in two different models. There is a good chance that
        # Django's F() Objects can do this, but this code was handling
        # string-to-date transformations before and the whole process
        # was even messier.

        
        # We started by getting the proper date comparison function, depending on the database.
        if DATABASE_ENGINE == 'sqlite3':
            date_cmp_select = 'julianday(%s) - julianday(%s)'
            params = (enc_date_field, imm_date_field)
        elif DATABASE_ENGINE == 'mysql':
            date_cmp_select = "DATEDIFF(%s, %s)"
            params = (enc_date_field, imm_date_field)
        elif DATABASE_ENGINE in ('postgresql_psycopg2', 'postgresql'):
            date_cmp_select = "date(%s) - date(%s)"
            params = (enc_date_field, imm_date_field)
        else:
            raise NotImplementedError, 'Implemented only for PostgreSQL, mySQL and Sqlite'

        
        # Now, we get the comparison string and put it together with
        # the expected value, so we create the time window constraint
        max_days = '%s <= %s' % (date_cmp_select % params, str(days_after))
        same_day = (date_cmp_select % params) + ' >= 0'

        # This is our minimum WHERE clause
        where_clauses = [patient_in_encounter, patient_in_immunization, 
                         max_days, same_day]


        # begin_date and end_date are the dates that are give the date
        # range of the encounters we are looking for. Luckily, all of
        # the DB Engines agree on this one. We can compare a date
        # field with a string in the format 'YYYY-MM-DD'.
        where_clauses.append("%s >= '%s'" % (imm_date_field, begin_date.strftime('%Y-%m-%d')))
        where_clauses.append("%s <= '%s'" % (imm_date_field, end_date.strftime('%Y-%m-%d')))


        return self.extra(
            tables = [patient_meta.db_table, imm_meta.db_table],
            where = where_clauses
            )    


class Encounter(BasePatientRecord):
    '''
    A encounter between provider and patient
    '''
    # Date is encounter date
    #
    objects = EncounterManager()
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

    q_fake = Q(patient__patient_id_num__startswith='FAKE')

    @staticmethod
    def fakes():
        return Encounter.objects.filter(Encounter.q_fake)

    @staticmethod
    def delete_fakes():
        Encounter.fakes().delete()

    @staticmethod
    def make_fakes(how_many, **kw):
        now = datetime.datetime.now()
        start = kw.get('start_date', None)
        interval = kw.get('interval', None)
        
        for patient in Patient.fakes():
            when = start or patient.dob
            for i in xrange(0, how_many):
                next_encounter_interval = interval or random.randrange(0, 180)
                when += datetime.timedelta(days=next_encounter_interval)
                if when < now: 
                    Encounter.make_mock(patient, save_on_db=True, when=when)
            
    @staticmethod
    def make_mock(patient, save_on_db=False, **kw):
        when = kw.get('when', datetime.datetime.now())
        
        try:
            provider = patient.pcp
        except:
            provider = Provider.make_mock(save_on_db=True)

        e = Encounter(patient=patient, provider=provider, mrn=patient.mrn, 
                      status='FAKE', date=when, closed_date=when)
        
        if save_on_db: e.save()
        return e

    def is_fake(self):
        return self.status == 'FAKE'

    def is_reoccurrence(self, month_period=12):
        '''
        returns a boolean indicating if this encounters shows any icd9
        code that has been registered for this patient in last
        month_period time.
        '''
        
        earliest = self.date-datetime.timedelta(days=30*month_period)
        
        return Encounter.objects.filter(
            date__lt=self.date, date__gte=earliest, 
            patient=self.patient, icd9_codes__in=self.icd9_codes.all()
            ).count() > 0
                
    
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

    q_fake = Q(name='FAKE')

    @staticmethod
    def vaers_candidates(patient, event, days_prior):
        '''Given an encounter that is considered an adverse event,
        returns a queryset that represents the possible immunizations
        that have caused it'''
        
        earliest_date = event.date - datetime.timedelta(days=days_prior)
                
        return Immunization.objects.filter(
            date__gte=earliest_date, date__lte=event.date,
            patient=patient
            )
    
    @staticmethod
    def fakes():
        return Immunization.objects.filter(Immunization.q_fake)
    
    @staticmethod
    def delete_fakes():
        Immunization.fakes().delete()


    @staticmethod
    def make_mock(vaccine, patient, date):
        return Immunization.objects.create(
            patient=patient, imm_id_num='FAKE-%s' % patient.id,
            date=date, visit_date=date,
            imm_type=vaccine.code, dose='3.1415 pi', 
            name='FAKE', manufacturer='FAKE', lot='FAKE'
            )

    def is_fake(self):
        return self.name == 'FAKE'

    def vaccine_type(self):
        try:
            vaccine = Vaccine.objects.get(code=self.imm_type)
            return vaccine.name
        except:
            return 'Unknown Vaccine'

    def  __unicode__(self):
        return u"Patient with Immunization Record %s received %s on %s" % (
            self.imm_id_num, self.vaccine_type(), self.date)    
