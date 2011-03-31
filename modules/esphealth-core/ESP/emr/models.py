'''
                              ESP Health Project
                     Electronic Medical Records Warehouse
                                  Data Models

@authors: Jason McVetta <jason.mcvetta@gmail.com>, Raphael Lullis <raphael.lullis@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''


import string
import random
import datetime
import sys
import re
from dateutil.relativedelta import relativedelta

from django.db import models
from django.db.models import Q, F
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from ESP.settings import DATABASE_ENGINE, DATA_DIR
from ESP.emr.choices import DATA_SOURCE
from ESP.emr.choices import LOAD_STATUS
from ESP.emr.choices import LAB_ORDER_TYPES
from ESP.conf.common import EPOCH
#from ESP.conf.models import CodeMap
from ESP.static.models import Loinc
from ESP.static.models import Ndc
from ESP.static.models import Icd9, Allergen
from ESP.static.models import Vaccine
from ESP.static.models import ImmunizationManufacturer
from ESP.conf.models import VaccineManufacturerMap
from ESP.utils import randomizer
from ESP.utils.utils import log, log_query, date_from_str, str_from_date



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Models
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class Provenance(models.Model):
    '''
    Answers the question "Where did this data come from?"
    '''
    provenance_id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True, blank=False)
    # source will contain the filename, if data came from a file
    source = models.CharField(max_length=500, blank=False, db_index=True)
    hostname = models.CharField('Host on which data was loaded', max_length=255, blank=False)
    status = models.CharField(max_length=10, choices=LOAD_STATUS, blank=False, db_index=True)
    valid_rec_count = models.IntegerField('Count of valid records loaded', blank=False, default=0)
    error_count = models.IntegerField('Count of errors during load', blank=False, default=0)
    comment = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ['timestamp', 'source', 'hostname']

    @staticmethod
    def fake():
        data_faker = 'Data Faker App'
        try:
            return Provenance.objects.get(source=data_faker)
        except:
            return Provenance.objects.create(
                source=data_faker, status='loaded', hostname='fake',
                comment='Data Faker App add data that should be used ' \
                    'for testing and development purposes only')
                
        
    def __str__(self):
        return '%s | %s | %s' % (self.source, self.timestamp, self.hostname)


class EtlError(models.Model):
    '''
    An ETL error, usually corresponding with a single bad line in a data file.
    '''
    timestamp = models.DateTimeField(auto_now_add=True, blank=False)
    provenance = models.ForeignKey(Provenance, blank=False)
    line = models.IntegerField('Line Number', blank=False)
    err_msg = models.CharField(max_length=512, blank=False)
    data = models.TextField()
    

class LabTestConcordance(models.Model):
    '''
    Concordance table listing all distinct lab test names and codes, and the 
    count results in the database for each test at time table was generated.
    Should be rebuilt after each load of new EMR data.
    '''
    native_code = models.CharField(max_length=100, blank=False, db_index=True)
    native_name = models.CharField(max_length=255, null=True, db_index=True)
    count = models.IntegerField(blank=False)



#===============================================================================
#
#--- ~~~ Medical Records ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class BaseMedicalRecord(models.Model):
    '''
    Abstract base class for a medical record
    '''
    provenance = models.ForeignKey(Provenance, blank=False)
    created_timestamp = models.DateTimeField(auto_now_add=True, blank=False)
    updated_timestamp = models.DateTimeField(auto_now=True, blank=False, db_index=True)

    class Meta:
        abstract = True


class Provider(BaseMedicalRecord):
    '''
    A medical care provider
    '''
    provider_id_num = models.CharField('Physician identifier in source EMR system', unique=True, max_length=128, 
        blank=False, db_index=True)
    last_name = models.CharField('Last Name',max_length=200, blank=True,null=True)
    first_name = models.CharField('First Name',max_length=200, blank=True,null=True)
    middle_name = models.CharField('Middle_Name',max_length=200, blank=True,null=True)
    title = models.CharField('Title', max_length=20, blank=True, null=True)
    dept_id_num = models.CharField('Primary Department identifier in source EMR system', max_length=128, blank=True, null=True)
    dept = models.CharField('Primary Department',max_length=200,blank=True,null=True)
    dept_address_1 = models.CharField('Primary Department Address 1',max_length=100,blank=True,null=True)
    dept_address_2 = models.CharField('Primary Department Address 2',max_length=20,blank=True,null=True)
    dept_city = models.CharField('Primary Department City',max_length=20,blank=True,null=True)
    dept_state = models.CharField('Primary Department State',max_length=20,blank=True,null=True)
    dept_zip = models.CharField('Primary Department Zip',max_length=20,blank=True,null=True)
    # Large max_length value for area code because Atrius likes to put descriptive text into that field
    area_code = models.CharField('Primary Department Phone Areacode',max_length=50,blank=True,null=True)
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
    def make_fakes(save_on_db=True, save_to_epic=False):
        provenance = Provenance.fake()
        if Provider.fakes().count() > 0: return
        import fake
        if save_to_epic:
            filename = os.path.join(DATA_DIR, 'fake', 'epicpro.%s.esp' % EPOCH.strftime('%m%d%Y'))
            epic_file = open(filename, 'a')
        for p in fake.PROVIDERS:
            p.provenance = provenance
            p.provider_id_num = 'FAKE-%05d' % random.randrange(1, 100000)
            if save_on_db: p.save()
            if save_to_epic: p.write

    @staticmethod
    def get_mock():
        if Provider.fakes().count() == 0:        
            Provider.make_fakes()
        return Provider.fakes().order_by('?')[0]
    
    def is_fake(self):
        return self.provider_id_num.startswith('FAKE')

    def _get_name(self):
        return u'%s, %s %s %s' % (self.last_name, self.title, self.first_name, self.middle_name)
    name = property(_get_name)
    full_name = property(_get_name)
    
    def __unicode__(self):
        return self.name
        
    def __get_tel_numeric(self):
        '''
        Returns telephone number string containing only numeric characters
        '''
        if self.telephone:
            return re.sub('[^0-9]', '', self.telephone)
        else:
            return None
    tel_numeric = property(__get_tel_numeric)


class Patient(BaseMedicalRecord):
    '''
    A patient, with demographic information
    '''
    patient_id_num = models.CharField('Patient identifier in source EMR system', unique=True, max_length=128, 
        blank=False, db_index=True)
    mrn = models.CharField('Medical Record ', max_length=20, blank=True, null=True, db_index=True)
    last_name = models.CharField('Last Name', max_length=200, blank=True, null=True)
    first_name = models.CharField('First Name', max_length=200, blank=True, null=True)
    middle_name = models.CharField('Middle Name', max_length=200, blank=True, null=True)
    suffix = models.CharField('Suffix', max_length=199, blank=True, null=True)
    pcp = models.ForeignKey(Provider, verbose_name='Primary Care Physician', blank=True, null=True)
    address1 = models.CharField('Address1', max_length=200, blank=True, null=True)
    address2 = models.CharField('Address2', max_length=100, blank=True, null=True)
    city = models.CharField('City', max_length=50, blank=True, null=True)
    state = models.CharField('State', max_length=20, blank=True, null=True)
    zip = models.CharField('Zip', max_length=20, blank=True, null=True, db_index=True)
    zip5 = models.CharField('5-digit zip', max_length=5, null=True, db_index=True)
    country = models.CharField('Country', max_length=20, blank=True, null=True)
    # Large max_length value for area code because Atrius likes to put descriptive text into that field
    areacode = models.CharField('Home Phone Area Code', max_length=50, blank=True, null=True)
    tel = models.CharField('Home Phone Number', max_length=100, blank=True, null=True)
    tel_ext = models.CharField('Home Phone Extension', max_length=50, blank=True, null=True)
    date_of_birth = models.DateField('Date of Birth', blank=True, null=True, db_index=True)
    date_of_death = models.DateField('Date of death', blank=True, null=True)
    gender = models.CharField('Gender', max_length=20, blank=True, null=True, db_index=True)
    race = models.CharField('Race', max_length=20, blank=True, null=True, db_index=True)
    home_language = models.CharField('Home Language', max_length=128, blank=True, null=True)
    ssn = models.CharField('SSN', max_length=20, blank=True, null=True)
    marital_stat = models.CharField('Marital Status', max_length=20, blank=True, null=True)
    religion = models.CharField('Religion', max_length=100, blank=True, null=True)
    aliases = models.TextField('Aliases', blank=True, null=True)
    mother_mrn = models.CharField('Mother Medical Record Number', max_length=20, blank=True, null=True)
    #death_indicator = models.CharField('Death_Indicator', max_length=30, blank=True, null=True)
    occupation = models.CharField('Occupation', max_length=200, blank=True, null=True)
    
    q_fake = Q(patient_id_num__startswith='FAKE')

    @staticmethod
    def fakes(**kw):
        return Patient.objects.filter(Patient.q_fake)

    @staticmethod
    def clear():
        Patient.fakes().delete()
            
    @staticmethod
    def make_fakes(how_many, save_on_db=True, **kw):
        for i in xrange(how_many):
            Patient.make_mock(save_on_db=save_on_db)

    @staticmethod
    def delete_fakes():
        Patient.fakes().delete()

    @staticmethod
    def make_mock(**kw):
        save_on_db = kw.get('save_on_db', False)

        # Common, random attributes
        provenance = Provenance.fake()
        phone_number = randomizer.phone_number()
        address = randomizer.address()
        city = randomizer.city()
        identifier = randomizer.string(length=8)
        # A Fake Patient must have a fake provider. If we have one on
        # the DB, we get a random one. Else, we'll have to create them
        # ourselves.
        if Provider.fakes().count() == 0:        
            Provider.make_fakes()
        provider = Provider.fakes().order_by('?')[0]
        p = Patient(
            provenance=provenance,
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
            date_of_birth = randomizer.date_of_birth(as_string=False),
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

    def _calculate_zip5(self):
        # Trivial case. If zip is empty or None, we are making 00000 as unknown zip5.
        if not self.zip: return '00000'

        try:
            # we try to cast to int to make sure that the string is digits-only
            sliced = '%05d' % int(self.zip.strip().split('-')[0])
            # There are lots of zip codes with 8 or 9 digits with no
            # dash as separator. So we check if the string is 8 or 9
            # digits long, which might indicate a valid zip code. If
            # it doesn't, we set it as unknown.
            if len(sliced) in [5, 8, 9]:            
                return sliced[:5]
            else:
                return '00000'
        except:
            return '00000'


    def is_fake(self):
        return self.patient_id_num.startswith('FAKE')
        

    def has_history_of(self, icd9s, begin_date=None, end_date=None):
        '''
        returns a boolean if the patient has any of the icd9s code 
        in their history of encounters.
        '''
        begin_date = begin_date or self.date_of_birth or EPOCH
        end_date = end_date or datetime.date.today()
        return self.encounters().filter(
            date__gte=begin_date, date__lt=end_date
            ).filter(icd9_codes__in=list(icd9s)).count() != 0

    phone_number = property(lambda x: '(%s) %s' % (x.areacode, x.tel))
    
    def _get_name(self):
        if self.middle_name:
            name = u'%s, %s %s' % (self.last_name, self.first_name, self.middle_name)
        else:
            name = u'%s, %s' % (self.last_name, self.first_name)
        return name.title()
    name = property(_get_name)
    full_name = property(_get_name)
    
    def _get_age_str(self, precision='years', with_units=False):
        '''Returns patient's age as a string'''
        if not self.date_of_birth: return None
        today = datetime.date.today() 
        days = today.day - self.date_of_birth.day
        months = today.month - self.date_of_birth.month
        years = today.year - self.date_of_birth.year
        if days < 0:
            months -= 1
        if months < 0:
            years -= 1
            months += 12
        d = {
            'years': years,
            'months': (12*years) + months,
            'days':(today - self.date_of_birth).days
            }
        return ' '.join([str(d[precision]), 
                         str(precision) if with_units else ''])


    
    def _get_address(self):
        address = u'%s %s %s, %s, %s' % (self.address1, self.address2, self.city, self.state, self.zip)
        return address.title()
    address = property(_get_address)

    street_address = property(lambda x: (u'%s %s' % (x.address1, x.address2)).strip())
    
    def get_age(self, when=None):
        '''
        Returns patient's age as a relativedelta
        '''
        if not self.date_of_birth: 
            return None
        if not when:
            when = datetime.date.today()
        return relativedelta(when, self.date_of_birth)
    age = property(get_age)

    def age_group(self, **kw):
        when = kw.get('when', None)
        
        interval = kw.pop('interval', 5)
        ceiling = kw.pop('ceiling', 80)
        above_ceiling = ceiling + interval

        age = self._get_age(when=when)        
        return (interval * int(min(age.days/365.25, above_ceiling)/interval)) if age else None
        
    def __get_tel_numeric(self):
        '''
        Returns telephone number string containing only numeric characters
        '''
        return re.sub('[^0-9]', '', self.tel)
    tel_numeric = property(__get_tel_numeric)
        

    def immunizations(self):
        return Immunization.objects.filter(patient=self)

    def lab_results(self):
        return LabResult.objects.filter(patient=self)

    def encounters(self):
        return Encounter.objects.filter(patient=self)

    def prescriptions(self):
        return Prescription.objects.filter(patient=self)


    def document_summary(self):
        '''
        The patient's self-contained register of all of records, in JSON-format
        '''
        import simplejson

        
        
        name = {
            'first_name':self.first_name,
            'last_name':self.last_name
            }

        address = {
            'street': self.street_address,
            'city': self.city,
            'state':self.state,
            'country':self.country,
            'zip':self.zip
            }
        
        provider = {
            'name': self.pcp.full_name,
            'code': self.pcp.provider_id_num,
            'id': self.pcp.id
            }

        phones = [
            {'areacode': self.areacode,
             'phone':self.tel}]

        profile = {
            'date_of_birth': (self.date_of_birth and self.date_of_birth.isoformat()) or None,
            'date_of_death': (self.date_of_death and self.date_of_death.isoformat()) or None,
            'sex':self.gender,
            'race':self.race,        
            'home_language':self.home_language,
            'marital_status':self.marital_stat,
            'religion':self.religion,
            'ocuppation':self.occupation
            }

        encounters = [e.document_summary() for e in self.encounters()]
        prescriptions = [p.document_summary() for p in self.prescriptions()]
        lab_results = [lx.document_summary() for lx in self.lab_results()]
        immunizations = [imm.document_summary() for imm in self.immunizations()]

        return simplejson.dumps({
                'name':name,
                'provider':provider,
                'profile':profile,
                'encounters':encounters,
                'prescriptions':prescriptions,
                'immunizations':immunizations
                })
            
    def __str__(self):
        return self.name

    def __unicode__(self):
        return u'%s' % self.full_name

    


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
    date = models.DateField(blank=False, db_index=True)
    # Does it make sense to have an MRN field on every patient record table?  
    # Will all patient records have their own individual MRN?
    mrn = models.CharField('Medical Record Number', max_length=50, blank=True, null=True)
    
    class Meta:
        abstract = True


class LabResultManager(models.Manager):
    def following_vaccination(self, days_after, include_same_day=False, **kw):

        if include_same_day:
            q_earliest_date = Q(date__gte=F('patient__immunization__date'))
        else:
            q_earliest_date = Q(date__gt=F('patient__immunization__date'))

        return self.filter(patient__immunization=F('patient__immunization')).filter(
            date__lte=F('patient__immunization__date') + days_after).filter(q_earliest_date)

    
class LabResult(BasePatientRecord):
    '''
    Result data for a lab test
    '''
    # Date (from base class) is order date
    #
    # Coding
    native_code = models.CharField('Native Test Code', max_length=30, blank=True, null=True, db_index=True)
    native_name = models.CharField('Native Test Name', max_length=255, blank=True, null=True, db_index=True)
    order_id_num = models.CharField(max_length=128, blank=False, db_index=True)
    result_date = models.DateField(blank=True, null=True, db_index=True)
    collection_date = models.DateField(blank=True, null=True, db_index=True)
    status = models.CharField('Result Status', max_length=50, blank=True, null=True)
    result_id_num = models.CharField('Result identifier in source EMR system', max_length=128, blank=True, null=True)
    # 
    # In some EMR data sets, reference pos & high, and neg & low, may come from
    # the same field depending whether the value is a string or a number.
    #
    ref_high_string = models.CharField('Reference Positive Value', max_length=100, blank=True, null=True)
    ref_low_string = models.CharField('Reference Negative Value', max_length=100, blank=True, null=True)
    ref_high_float = models.FloatField('Reference High Value', blank=True, null=True, db_index=True)
    ref_low_float = models.FloatField('Reference Low Value', blank=True, null=True, db_index=True)
    ref_unit = models.CharField('Measurement Unit', max_length=100, blank=True, null=True)
    # Result
    abnormal_flag = models.CharField(max_length=20, blank=True, null=True, db_index=True)
    result_float = models.FloatField('Numeric Test Result', blank=True, null=True, db_index=True)
    result_string = models.TextField('Test Result', max_length=2000, blank=True, null=True, db_index=True)
    # Wide fields
    specimen_num = models.CharField('Speciment ID Number', max_length=100, blank=True, null=True)
    specimen_source = models.CharField('Speciment Source', max_length=255, blank=True, null=True)
    impression = models.TextField('Impression (imaging)', max_length=2000, blank=True, null=True)
    comment = models.TextField('Comments', blank=True, null=True)
    procedure_name = models.CharField('Procedure Name', max_length=255, blank=True, null=True)
    # Manager
    objects = LabResultManager()
    # HEF
    tags = generic.GenericRelation('hef.EventRecordTag')
    
    class Meta:
        verbose_name = 'Lab Test Result'
        ordering = ['date']

    q_fake = Q(patient__patient_id_num__startswith='FAKE')

    @staticmethod
    def fakes():
        return LabResult.objects.filter(LabResult.q_fake)
    
    @staticmethod
    def delete_fakes():
        LabResult.fakes().delete()

    @staticmethod
    def make_mock(patient, when=None, **kw):
        save_on_db = kw.pop('save_on_db', False)
        loinc = kw.get('with_loinc', None) or Loinc.objects.order_by('?')[0]

        when = when or datetime.date.today()
        result_date = when + datetime.timedelta(days=random.randrange(1, 30))
        # Make sure the patient was alive for the order...
        order_date = when if patient.date_of_birth is None else max(when, patient.date_of_birth)
        lx = LabResult(patient=patient, provider=Provider.get_mock(), 
                       provenance=Provenance.fake(), date=order_date, result_date=result_date,
                       native_code=loinc.loinc_num, native_name=loinc.name)

        if save_on_db: lx.save()
        return lx

    def previous(self):
        try:
            return LabResult.objects.filter(patient=self.patient, native_code=self.native_code
                                            ).exclude(date__gte=self.date).latest('date')
        except:
            return None

    def last_known_value(self, with_same_unit=True):
        '''
        Returns the value of the Lx that is immediately prior to
        self.  if 'check_same_unit' is True, only returns the value if
        both labs results have a matching (Case insensitive) ref_unit value
        '''
        previous_labs = LabResult.objects.filter(native_code=self.native_code, patient=self.patient, 
                                                 date__lt=self.date).order_by('-date')
        if with_same_unit:
            previous_labs = previous_labs.filter(ref_unit__iexact=self.ref_unit)
        for lab in previous_labs:
            value = (lab.result_float or lab.result_string) or None
            if value: return value
        return None

    def __str__(self):
        return 'Lab Result # %s' % self.pk
    
    def __unicode__(self):
        return u'Lab Result # %s' % self.pk
    
    def str_line(self):
        '''
        Returns a single-line string representation of the Case instance
        '''
        values = self.__dict__
        values['short_name'] = self.native_name[:15] if self.native_name else 'N/A'
        values['res'] = self.result_string[:20] if self.result_string else ''
        return '%(date)-10s    %(id)-8s    %(short_name)-15s    %(native_code)-11s    %(res)-20s' % values
    
    def __get_ref_range(self):
        '''
        Generate a reference range string
        '''
        if self.ref_low_float:
            low = self.ref_low_float
        else:
            low = self.ref_low_string
        if self.ref_high_float:
            high = self.ref_high_float
        else:
            high = self.ref_high_string
        if (high or low):
            return '%s - %s' % (low, high)
        else:
            return None
    ref_range = property(__get_ref_range)
    
    @classmethod
    def str_line_header(cls):
        '''
        Returns a header describing the fields returned by str_line()
        '''
        values = {
            'date': 'DATE', 
            'id': 'LAB #', 
            'short_name': 'TEST NAME', 
            'native_code': 'CODE',
            'res': 'RESULT',
            }
        return '%(date)-10s    %(id)-8s    %(short_name)-15s    %(native_code)-11s    %(res)-20s' % values

    def __get_codemap(self):
        maps = CodeMap.objects.filter(native_code=self.native_code)
        if maps:
            return maps[0]
        else:
            return None
    codemap = property(__get_codemap)
            
    def __get_output_code(self):
        map = self.codemap
        if map:
            return map.output_code
        else:
            return None
    output_code = property(__get_output_code)
    
    def __get_output_name(self):
        map = self.codemap
        if map:
            return map.output_name
        else:
            return None
    output_name = property(__get_output_name)
    
    def __get__output_or_native_code(self):
        output = self.output_code
        if output:
            return output
        else:
            return self.native_code
    output_or_native_code = property(__get__output_or_native_code)
    
    def __get__output_or_native_name(self):
        output = self.output_name
        if output:
            return output
        else:
            return self.native_name
    output_or_native_name = property(__get__output_or_native_name)

    def document_summary(self):
        return {
            'order': { 
                'code': self.order_num,
                'date': (self.date and self.date.isoformat()) or None
                },
            'code': self.output_code,
            'reference': {
                'low':self.ref_low_float,
                'high':self.ref_high_float,
                'positive':self.ref_high_string,
                'negative':self.ref_low_string,
                'unit':self.ref_unit
                },
            'result':{
                'code':self.result_num,
                'date':(self.result_date and self.result_date.isoformat()) or None,
                'status':self.status,
                'abnormal':self.abnormal_flag,
                'value': self.result_float or self.result_string,
                'specimen': self.specimen_num,
                'impression':self.impression,
                'comment':self.comment
                } 
            }
    
    def __get_snomed_pos(self):
        '''
        Returns SNOMED code for positive result, from this test's CodeMap
        '''
        cm = self.codemap
        if not cm:
            return None
        return cm.snomed_pos
    snomed_pos = property(__get_snomed_pos)
    
    def __get_snomed_neg(self):
        '''
        Returns SNOMED code for negative result, from this test's CodeMap
        '''
        cm = self.codemap
        if not cm:
            return None
        return cm.snomed_neg
    snomed_neg = property(__get_snomed_neg)
        
    def __get_snomed_ind(self):
        '''
        Returns SNOMED code for indeterminate result, from this test's CodeMap
        '''
        cm = self.codemap
        if not cm:
            return None
        return cm.snomed_ind
    snomed_ind = property(__get_snomed_ind)
        

class LabOrder(BasePatientRecord):
    '''
    An order for a laboratory test
    '''
    order_id_num = models.CharField('Order identifier in source EMR system', max_length=128, db_index=True)
    procedure_master_num = models.CharField(max_length=20, blank=True, null=True, db_index=True)
    modifier = models.CharField(max_length=20, blank=True, null=True)
    procedure_name = models.CharField(max_length=300, blank=True, null=True)
    specimen_id = models.CharField(max_length=20, blank=True, null=True, db_index=True)
    order_type = models.CharField(max_length=64, blank=True, db_index=True)
    specimen_source = models.CharField(max_length=300, blank=True, null=True)
    # HEF
    tags = generic.GenericRelation('hef.EventRecordTag')
    
    
    
    
class Prescription(BasePatientRecord):
    '''
    A prescribed medication
    '''
    # Date is order date
    #
    order_id_num = models.CharField('Order identifier in source EMR system', max_length=128, blank=False)
    name = models.TextField(max_length=3000, blank=False, db_index=True)
    code = models.CharField('Drug Code (system varies by site)', max_length=255, blank=True, null=True)
    directions = models.TextField(max_length=3000, blank=True, null=True)
    dose = models.CharField(max_length=200, blank=True, null=True, db_index=True)
    frequency = models.CharField(max_length=200, blank=True, null=True)
    # This really should be quantity_string instead of quantity; but I don't 
    # want to break a bunch of other stuff right now.
    quantity_float = models.FloatField(blank=True, null=True, db_index=True)
    quantity = models.CharField(max_length=200, blank=True, null=True)
    refills = models.CharField(max_length=200, blank=True, null=True)
    route = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField('Order Status', max_length=20, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    # HEF
    tags = generic.GenericRelation('hef.EventRecordTag')
    
    class Meta:
        ordering = ['date']
    
    def __str__(self):
        return self.name

    def str_line(self):
        '''
        Returns a single-line string representation of the Case instance
        '''
        values = self.__dict__
        return '%(date)-10s    %(id)-8s    %(name)-30s' % values
    
    @classmethod
    def str_line_header(cls):
        '''
        Returns a header describing the fields returned by str_line()
        '''
        values = {
            'date': 'DATE', 
            'id': 'RX #', 
            'name': 'DRUG NAME'
            }
        return '%(date)-10s    %(id)-8s    %(name)-30s' % values


    def document_summary(self):
        return {
            'order':{
                'id':self.order_num,
                'date':(self.date and self.date.isoformat()) or None,
                'status':self.status
                },
            'provider':self.provider.pk,
            'name':self.name,
            'code':self.code,
            'frequency':self.frequency,
            'quantity':self.quantity,
            'route':self.route,
            'directions':self.directions,
            'refills':self.refills,
            'valid_dates':{
                'start': (self.start_date and self.start_date.isoformat()) or None,
                'end': (self.end_date and self.end_date.isoformat()) or None
                }
            }
    

class EncounterManager(models.Manager):
    def following_vaccination(self, days_after, include_same_day=False, **kw):

        if include_same_day:
            q_earliest_date = Q(date__gte=F('patient__immunization__date'))
        else:
            q_earliest_date = Q(date__gt=F('patient__immunization__date'))

        return self.filter(patient__immunization=F('patient__immunization')).filter(
            date__lte=F('patient__immunization__date') + days_after).filter(q_earliest_date)

    def syndrome_care_visits(self, sites=None):
        qs = self.filter(event_type__in=['URGENT CARE', 'VISIT'])
        if sites: qs = qs.filter(native_site_num__in=sites)
        return qs


    

class Encounter(BasePatientRecord):
    '''
    A encounter between provider and patient
    '''
    objects = EncounterManager()
    icd9_codes = models.ManyToManyField(Icd9,  blank=True,  null=True, db_index=True)
    tags = generic.GenericRelation('hef.EventRecordTag')
    #
    # Fields taken directly from ETL file.  Some minimal processing, such as 
    # standardizing capitalization, may be advisable in loader code.  
    #
    native_encounter_num = models.TextField('Native EMR system encounter ID', blank=False, db_index=True, unique=True)
    encounter_type = models.TextField('Type of encounter', blank=True, null=True, db_index=True)
    status = models.TextField('Record status', blank=True, null=True, db_index=True)
    native_site_num = models.TextField('Native EMR system site ID', blank=True, null=True, db_index=True)
    site_name = models.TextField('Encounter site name', blank=True, null=True, db_index=True)
    #
    # Extracted & calculated fields
    #
    # date is encounter date
    date_closed = models.DateField(blank=True, null=True, db_index=True)
    pregnant = models.BooleanField('Patient is pregnant?', blank=False, default=False, db_index=True)
    edd = models.DateField('Expected Date of Delivery (pregnant women only)', blank=True, null=True, db_index=True) 
    temperature = models.FloatField('Temperature (Celsius)', blank=True, null=True, db_index=True)
    weight = models.FloatField('Weight (kg)', blank=True, null=True, db_index=True)
    height = models.FloatField('Height (cm)', blank=True, null=True, db_index=True)
    bp_systolic = models.FloatField('Blood Pressure - Systolic (mm Hg)', blank=True, null=True, db_index=True)
    bp_diastolic = models.FloatField('Blood Pressure - Diastolic (mm Hg)', blank=True, null=True, db_index=True)
    o2_stat = models.FloatField(blank=True, null=True, db_index=True)
    peak_flow = models.FloatField(blank=True, null=True, db_index=True)
    bmi = models.FloatField(null=True, blank=True, db_index=True)
    #
    # Raw string fields 
    #
    # Please do not index these, lest you overburden your poor database.  Be 
    # kind to it, it has done you no wrong that you did not bring on yourself.
    #
    raw_date = models.TextField(null=True, blank=True)
    raw_date_closed = models.TextField(null=True, blank=True)
    raw_edd = models.TextField(null=True, blank=True)
    raw_temperature = models.TextField(null=True, blank=True)
    raw_weight = models.TextField(null=True, blank=True)
    raw_height = models.TextField(null=True, blank=True)
    raw_bp_systolic = models.TextField(null=True, blank=True)
    raw_bp_diastolic = models.TextField(null=True, blank=True)
    raw_o2_stat = models.TextField(null=True, blank=True)
    raw_peak_flow = models.TextField(null=True, blank=True)
    raw_bmi = models.TextField(null=True, blank=True)
    # Making diagnosis field available in a meaningful way requires full-text
    # indexing.  Support for this is planned, but not currently implemented.
    raw_diagnosis = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['date']
    
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
            when = start or patient.date_of_birth
            for i in xrange(0, how_many):
                next_encounter_interval = interval or random.randrange(0, 180)
                when += datetime.timedelta(days=next_encounter_interval)
                if when < now: 
                    Encounter.make_mock(patient, save_on_db=True, when=when)
            
    @staticmethod
    def make_mock(patient, **kw):
        save_on_db=kw.pop('save_on_db', False)
        when = kw.get('when', datetime.datetime.now())
        provider = Provider.get_mock()

        e = Encounter(patient=patient, provider=provider, provenance=Provenance.fake(),
                      native_encounter_num='FAKE-%s' % randomizer.string(length=15),
                      mrn=patient.mrn, status='FAKE', date=when, closed_date=when)
        
        if save_on_db: e.save()
        return e


    @staticmethod
    def volume(date, *args, **kw):
        '''
        Returns the total of encounters occurred on a given date.
        Extra named parameters can be passed on **kw, or Q objects on *args.        
        '''
        return Encounter.objects.filter(date=date).filter(*args).filter(**kw).count()

    def is_fake(self):
        return self.status == 'FAKE'

    def is_reoccurrence(self, icd9s, month_period=12):
        '''
        returns a boolean indicating if this encounters shows any icd9
        code that has been registered for this patient in last
        month_period time.
        '''
        
        earliest = self.date - datetime.timedelta(days=30*month_period)
        
        return Encounter.objects.filter(
            date__lt=self.date, date__gte=earliest, patient=self.patient, icd9_codes__in=icd9s
            ).count() > 0
                
    def __str__(self):
        return 'Encounter # %s' % self.pk
    
    def str_line(self):
        '''
        Returns a single-line string representation of the Case instance
        '''
        values = self.__dict__ 
        values['icd9s'] = ', '.join([i.code for i in self.icd9_codes.all().order_by('code')])
        return '%(date)-10s    %(id)-8s    %(temperature)-6s    %(icd9s)-30s' % values
    
    @classmethod
    def str_line_header(cls):
        '''
        Returns a header describing the fields returned by str_line()
        '''
        values = {'date': 'DATE', 'id': 'ENC #', 'temperature': 'TEMP (F)', 'icd9s': 'ICD9 CODES'}
        return '%(date)-10s    %(id)-8s    %(temperature)-6s    %(icd9s)-30s' % values
    
    def _get_icd9_codes_str(self):
        return ', '.join(self.icd9_codes.order_by('code').values_list('code', flat=True))
    icd9_codes_str = property(_get_icd9_codes_str)

    def _calculate_bmi(self):
        '''
        Calculate's patient's BMI as of this encounter
        '''
        # If this encounter has a raw bmi value, convert it to float and return
        if self.raw_bmi:
            try:
                return float(self.raw_bmi)
            except ValueError: # Can't convert raw_bmi to a float
                log.warning('Could not convert raw_bmi "%s" to float - will try to calculate BMI' % self.raw_bmi)
        # If this encounter has usable height & weight, calculate BMI based on that
        if (self.height and self.weight):
            height = self.height
            weight = self.weight
        else:
            # If there was a valid BMI in the past year, go with that
            pat_encs = Encounter.objects.filter(
                patient = self.patient,
                ).order_by('-date')
            encs_last_year = pat_encs.filter(
                date__gte = (self.date - relativedelta(days=365)),
                date__lte = self.date,
                )
            recent_bmi_encs = encs_last_year.filter(bmi__isnull=False)
            if recent_bmi_encs:
                return recent_bmi_encs[0].bmi
            # Find the most recent height for this patient, looking back as far 
            # as their 16th birthday if necessary
            sixteenth_bday = self.patient.date_of_birth + relativedelta(years=16)
            ht_encs = pat_encs.filter(date__gte=sixteenth_bday, height__isnull=False).exclude(height=0)
            # Find the most recent weight this patient within the past year
            wt_encs = encs_last_year.filter(weight__isnull=False).exclude(weight=0)
            if ht_encs and wt_encs:
                height = ht_encs[0].height
                weight = wt_encs[0].weight
            else: # We don't know a recent height and weight for this patient
                log.warning('Cannot calculate BMI for encounter # %s' % self.pk)
                return None 
        height_m = height / 100  # Height is stored in centimeters
        weight_kg = weight # Already in kilograms
        bmi = weight_kg / (height_m ** 2 )
        return bmi

    def document_summary(self):
        return {
            'site':self.site_name,
            'provider':self.provider.pk,
            'status':self.status,
            'date':(self.date and self.date.isoformat()) or None,
            'closed_date':(self.closed_date and self.closed_date.isoformat()) or None,
            'event_type':self.event_type,
            'edc':(self.edc and self.edc.isoformat()) or None,
            'measurements':{
                'pregnancy':self.pregnancy_status,
                'temperature':self.temperature,
                'weight':self.weight,
                'height':self.height,
                'bp_systolic':self.bp_systolic,
                'bp_diastolic':self.bp_diastolic,
                'o2_stat':self.o2_stat,
                'peak_flow':self.peak_flow
                }
            }
            

class Immunization(BasePatientRecord):
    '''
    An immunization
    '''
    # Date is immunization date
    #
    imm_id_num = models.CharField('Immunization identifier in source EMR system', max_length=200, blank=True, null=True)
    imm_type = models.CharField('Immunization Type', max_length=20, blank=True, null=True)
    name = models.CharField('Immunization Name', max_length=200, blank=True, null=True)
    dose = models.CharField('Immunization Dose', max_length=100, blank=True, null=True)
    manufacturer = models.CharField('Manufacturer', max_length=100, blank=True, null=True)
    lot = models.TextField('Lot Number', max_length=500, blank=True, null=True)
    visit_date = models.DateField('Date of Visit', blank=True, null=True)
    # HEF
    tags = generic.GenericRelation('hef.EventRecordTag')
    
    class Meta:
        ordering = ['date']

    q_fake = Q(name='FAKE')

    @staticmethod
    def vaers_candidates(patient, event, days_prior):
        '''Given an adverse event, returns a queryset that represents
        the possible immunizations that have caused it'''
        
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
    def make_mock(vaccine, patient, date, save_on_db=False):
        i = Immunization(patient=patient, provenance=Provenance.fake(),
                         date=date, visit_date=date,
                         imm_type=vaccine.code, name='FAKE'
                         )
        if save_on_db: i.save()
        return i
            
    def is_fake(self):
        return self.name == 'FAKE'

    def _get_vaccine(self):
        try:
            return Vaccine.objects.get(code=self.imm_type)
        except:
            return Vaccine.objects.get(short_name='unknown')
    vaccine = property(_get_vaccine)

    def vaccine_type(self):
        return (self.vaccine and self.vaccine.name) or 'Unknown Vaccine'

    def _get_manufacturer(self):
        try:
            return VaccineManufacturerMap.objects.get(native_name=self.manufacturer).canonical_code
        except:
            return None

    vaccine_manufacturer = property(_get_manufacturer)

    def document_summary(self):
        return {
            'date':(self.date and self.date.isoformat()) or None,
            'vaccine':{
                'name':self.vaccine_type(),
                'code':(self.vaccine and self.vaccine.code) or None,
                'lot':self.lot,
                'manufacturer':self.manufacturer
                },
            'dose':self.dose
            }

    def  __unicode__(self):
        return u"Immunization on %s received %s on %s" % (
            self.patient.full_name, self.vaccine_type(), self.date)


class SocialHistory(BasePatientRecord):
    tobacco_use = models.CharField(max_length=20, null=True, blank=True, db_index=True)
    alcohol_use = models.CharField(max_length=20, null=True, blank=True, db_index=True)


class Allergy(BasePatientRecord):
    '''
    An allergy report
    '''
    problem_id = models.IntegerField(null=True, db_index=True)
    date_noted = models.DateField(null=True, db_index=True)
    allergen = models.ForeignKey(Allergen)
    name = models.CharField(max_length=200, null=True, db_index=True)
    status = models.CharField(max_length=20, null=True, db_index=True)
    description = models.CharField(max_length=200)


class Problem(BasePatientRecord):
    '''
    Problem list -- cumulative over time, no current 
    '''
    problem_id = models.IntegerField(null=True)
    icd9 = models.ForeignKey(Icd9)
    status = models.CharField(max_length=20, null=True, db_index=True)
    comment = models.TextField(null=True, blank=True)

    
    
    

    
    