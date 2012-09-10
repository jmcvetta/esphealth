'''
                              ESP Health Project
                     Electronic Medical Records Warehouse
                                  Data Models

@authors: Jason McVetta <jason.mcvetta@gmail.com>, Raphael Lullis <raphael.lullis@gmail.com>
@organization: Channing Laboratory - http://www.channing.harvard.edu
@contact: http://esphealth.org
@copyright: (c) 2009-2011 Channing Laboratory
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''

import string
import time
import random
import datetime
import sys
import re
import os

from decimal import Decimal
from dateutil.relativedelta import relativedelta

from django.db import models
from django.db.models import Q, F
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from ESP.settings import DATA_DIR
from ESP.emr.choices import DATA_SOURCE
from ESP.emr.choices import LOAD_STATUS
from ESP.emr.choices import LAB_ORDER_TYPES
from ESP.conf.common import EPOCH
from ESP.conf.models import LabTestMap
from ESP.static.models import Loinc, FakeLabs, FakeVitals, FakeMeds, FakeICD9s
from ESP.static.models import Ndc
from ESP.static.models import Icd9, Allergen
from ESP.static.models import Vaccine
from ESP.static.models import ImmunizationManufacturer
from ESP.conf.models import VaccineManufacturerMap, VaccineCodeMap
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
    # this is the unique identifier for this record in the source EMR system 
    natural_key = models.CharField(unique=True, blank=True, null=True, max_length=128, help_text='Unique Record identifier in source EMR system')
    created_timestamp = models.DateTimeField(auto_now_add=True, blank=False)
    updated_timestamp = models.DateTimeField(auto_now=True, blank=False, db_index=True)

    class Meta:
        abstract = True


class Provider(BaseMedicalRecord):
    '''
    A medical care provider
    '''
    last_name = models.CharField('Last Name', max_length=200, blank=True, null=True)
    first_name = models.CharField('First Name', max_length=200, blank=True, null=True)
    middle_name = models.CharField('Middle_Name', max_length=200, blank=True, null=True)
    title = models.CharField('Title', max_length=50, blank=True, null=True)
    dept_natural_key = models.CharField('Primary Department identifier in source EMR system', max_length=100, blank=True, null=True)
    dept = models.CharField('Primary Department', max_length=200, blank=True, null=True)
    dept_address_1 = models.CharField('Primary Department Address 1', max_length=100, blank=True, null=True)
    dept_address_2 = models.CharField('Primary Department Address 2', max_length=100, blank=True, null=True)
    dept_city = models.CharField('Primary Department City', max_length=20, blank=True, null=True)
    dept_state = models.CharField('Primary Department State', max_length=20, blank=True, null=True)
    dept_zip = models.CharField('Primary Department Zip', max_length=20, blank=True, null=True)
    # Large max_length value for area code because Atrius likes to put descriptive text into that field
    area_code = models.CharField('Primary Department Phone Areacode', max_length=50, blank=True, null=True)
    telephone = models.CharField('Primary Department Phone Number', max_length=50, blank=True, null=True)
    center_id =  models.CharField('Center ID', max_length=100, blank=True, null=True, db_index=True)
    
    q_fake = Q(natural_key__startswith='FAKE')

    # Some methods to deal with mock/fake data
    @staticmethod
    def fakes():
        return Provider.objects.filter(Provider.q_fake)

    @staticmethod
    def delete_fakes():
        Provider.fakes().delete()
        
    
    @staticmethod
    # this method pre-loads and writes to an etl epic file the fake providers
    # if there aren't any in the emr.provider table
    def make_mocks(provider_writer):

        provenance = Provenance.fake()
        if Provider.fakes().count() > 0: return
        import fake
        
        for p in fake.PROVIDERS:
            p.provenance = provenance
            p.natural_key = 'FAKE-%05d' % random.randrange(1, 100000)
            p.save()
            provider_writer.write_row(p)

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
            p.natural_key = 'FAKE-%05d' % random.randrange(1, 100000)
            
            if save_on_db: p.save()
            if save_to_epic: p.write

    @staticmethod
    def get_mock():
        if Provider.fakes().count() == 0:        
            Provider.make_fakes()
        return Provider.fakes().order_by('?')[0]
    
    
    def _get_name(self):
        if not self.title:
            return u'%s,  %s %s' % (self.last_name, self.first_name, self.middle_name)
        else:
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
    mrn = models.CharField('Medical Record ', max_length=25, blank=True, null=True, db_index=True)
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
    race = models.CharField('Race', max_length=100, blank=True, null=True, db_index=True)
    ethnicity = models.CharField('Ethnicity', max_length=100, blank=True, null=True, db_index=True)
    home_language = models.CharField('Home Language', max_length=128, blank=True, null=True)
    ssn = models.CharField('SSN', max_length=20, blank=True, null=True)
    marital_stat = models.CharField('Marital Status', max_length=20, blank=True, null=True)
    religion = models.CharField('Religion', max_length=100, blank=True, null=True)
    aliases = models.TextField('Aliases', blank=True, null=True)
    mother_mrn = models.CharField('Mother Medical Record Number', max_length=20, blank=True, null=True)
    #death_indicator = models.CharField('Death_Indicator', max_length=30, blank=True, null=True)
    occupation = models.CharField('Occupation', max_length=200, blank=True, null=True)
    center_id =  models.CharField('Center ID', max_length=100, blank=True, null=True, db_index=True)
    
    q_fake = Q(natural_key__startswith='FAKE')

    @staticmethod
    def fakes(**kw):
        return Patient.objects.filter(Patient.q_fake)

    @staticmethod
    def delete_fakes():
        Patient.fakes().delete()
        
    @staticmethod
    def clear():
        Patient.fakes().delete()
            
    @staticmethod
    def make_fakes(how_many, save_on_db=True, **kw):
        for i in xrange(how_many):
            Patient.make_mock(save_on_db=save_on_db)

   
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
            pcp=provider,
            natural_key='FAKE-%s' % identifier,
            mrn=randomizer.autoIncrement(),
            last_name=randomizer.last_name(),
            first_name=randomizer.first_name(),
            suffix='',
            country='Fakeland',
            city=city[0],
            state=city[1],
            zip=randomizer.zip_code(),
            address1=address,
            address2='',
            middle_name=random.choice(string.uppercase),
            date_of_birth=randomizer.date_of_birth(as_string=False),
            gender=randomizer.gender(),
            race=randomizer.race(),
            ethnicity = randomizer.ethnicity(),
            areacode=phone_number.split('-')[0],
            tel=phone_number[4:],
            tel_ext='',
            ssn=randomizer.ssn(),
            marital_stat=randomizer.marital_status(),
            religion='',
            aliases='',
            home_language='',
            mother_mrn='',
            occupation=''
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
            'months': (12 * years) + months,
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

        age = self.get_age(when=when)        
        return (interval * int(min(age.days / 365.25, above_ceiling) / interval)) if age else None
        
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

    def allergies (self):
        return Allergy.objects.filter(patient=self)

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
            'code': self.pcp.natural_key,
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
        allergies = [allergy.document_summary() for allergy in self.allergies()]
        immunizations = [imm.document_summary() for imm in self.immunizations()]

        return simplejson.dumps({
                'name':name,
                'provider':provider,
                'profile':profile,
                'encounters':encounters,
                'prescriptions':prescriptions,
                'lab_results': lab_results,
                'allergy': allergies,
                'immunizations':immunizations
                })
            
    def __getDOB(self):
        return self.date_of_birth.strftime("%B %d, %Y")
    DOB = property(__getDOB)
        
    def __str__(self):
        return u'%20s %s' % (self.pk, self.name)

    


#===============================================================================
#
#--- ~~~ Patient Records ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class BasePatientRecordManager(models.Manager):
    
    # TODO: issue 333 This code belongs in VAERS module, not here.
    def following_vaccination(self, days_after, risk_period_start, **kw):

        if risk_period_start ==0 :
            q_earliest_date = Q(date__gte=F('patient__immunization__date'))
        else:
            q_earliest_date = Q(date__gt=F('patient__immunization__date')+ risk_period_start)

        return self.filter(patient__immunization=F('patient__immunization'), 
                           patient__immunization__isvaccine=True).filter(
            date__lte=F('patient__immunization__date') + days_after).filter(q_earliest_date)


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
    #
    # HEF
    #
    events = generic.GenericRelation('hef.Event')
    #
    # Manager
    #
    objects = BasePatientRecordManager()
    
    q_fake = Q(patient_natural_key__startswith='FAKE')
    
    def is_fake(self):
        return self.patient.natural_key.startswith('FAKE')
   
    
    class Meta:
        abstract = True


  
class LabResult(BasePatientRecord):
    '''
    Result data for a lab test
    '''
    # Date (from base class) is order date
    #
    order_natural_key = models.CharField('Order identifier in source EMR system', max_length=128, db_index=True, blank=True, null=True)
    native_code = models.CharField('Native Test Code', max_length=255, blank=True, null=True, db_index=True)
    native_name = models.CharField('Native Test Name', max_length=255, blank=True, null=True, db_index=True)
    result_date = models.DateField(blank=True, null=True, db_index=True)
    collection_date = models.DateField(blank=True, null=True, db_index=True)
    status = models.CharField('Result Status', max_length=50, blank=True, null=True)
    # 
    # In some EMR data sets, reference pos & high, and neg & low, may come from
    # the same field depending whether the value is a string or a number.
    #
    ref_high_string = models.CharField('Reference High Value (string)', max_length=100, blank=True, null=True)
    ref_low_string = models.CharField('Reference Low Value (string)', max_length=100, blank=True, null=True)
    ref_high_float = models.FloatField('Reference High Value (decimal)', blank=True, null=True, db_index=True)
    ref_low_float = models.FloatField('Reference Low Value (decimal)', blank=True, null=True, db_index=True)
    ref_unit = models.CharField('Measurement Unit', max_length=100, blank=True, null=True)
    #
    # Result
    #
    abnormal_flag = models.CharField(max_length=20, blank=True, null=True, db_index=True)
    result_float = models.FloatField('Numeric Test Result', blank=True, null=True, db_index=True)
    result_string = models.TextField('Test Result', max_length=2000, blank=True, null=True, db_index=True)
    #
    # Wide fields
    #
    specimen_num = models.CharField('Speciment ID Number', max_length=100, blank=True, null=True)
    specimen_source = models.CharField('Speciment Source', max_length=255, blank=True, null=True)
    impression = models.TextField('Impression (imaging)', max_length=2000, blank=True, null=True)
    comment = models.TextField('Comments', blank=True, null=True)
    procedure_name = models.CharField('Procedure Name', max_length=255, blank=True, null=True)
    
    class Meta:
        verbose_name = 'Lab Test Result'
        ordering = ['date']
     
    @staticmethod
    def fakes():
        return LabResult.objects.filter(LabResult.q_fake)
    
    @staticmethod
    def delete_fakes():
        LabResult.fakes().delete()
    
    
    @staticmethod
    def randomWeight(normal, high, low, chigh, clow, first=.3, second=.7, third=.2, fourth=.4):
        
        r = random.random()
        if r <= third:
            return random.choice(chigh)
        elif r <= fourth:
            return random.choice(clow)
        elif r <= second:
            return random.choice(high )
        elif r <= first:
            return random.choice(low )
        else: 
            return random.choice(normal)
        
    @staticmethod
    def make_mock(patient, when=None, **kw):
        normal = ['IN','UN','NL']
        high = ['AH']
        low = ['AL','AB']
        chigh = ['CH','CR']
        clow = ['CL']
    
        save_on_db = kw.pop('save_on_db', False)
        msLabs = FakeLabs.objects.order_by('?')[0]
        now = int(time.time()*1000) #time in milliseconds
        provider = Provider.get_mock()
       
        lx = LabResult(patient=patient, mrn=patient.mrn, provider=provider, provenance=Provenance.fake(), natural_key=now)
        
        when = when or randomizer.date_range(as_string=False) #datetime.date.today()
        lx.result_date = when + datetime.timedelta(days=random.randrange(1, 5)) # date to b 5 days after
        # Make sure the patient was alive for the order...
       
        order_date = when if patient.date_of_birth is None else max(when, patient.date_of_birth)
        lx.date = order_date
        lx.native_code = str(msLabs.native_code)
        lx.order_natural_key = lx.natural_key # same order and key
        
        #not going to do cpt or order type =1 
        
        lx.native_name = msLabs.native_name
        lx.collection_date = order_date
        lx.status = 'Final'
        #lx.result_num = this is result id not in epic ignore
        #lx.ref_high_string = ignore  not included in etl epic care
        #lx.ref_low_string = ignore
        lx.ref_high_float = msLabs.normal_high
        lx.ref_low_float = msLabs.normal_low
        lx.ref_unit = msLabs.units
        # Result
        
        if msLabs.datatype <> 'Qualitative':
            lx.abnormal_flag = LabResult.randomWeight(normal,high,low, chigh, clow)
            
            # never generate abnormal now or critical low 
            if lx.abnormal_flag in clow:
                if msLabs.critical_low == -1:
                    lx.abnormal_flag = random.choice(low)
                else:
                    lx.result_float = round(random.uniform(0, msLabs.critical_low), 2)
                    
            if  lx.abnormal_flag in low:
                if lx.ref_low_float == -1: # do not generate low value
                    lx.abnormal_flag = random.choice(normal)
                    lx.result_float = round(random.uniform(0, lx.ref_high_float), 2)
                else:
                    if msLabs.critical_low == -1:
                        lx.result_float = round(random.uniform(0, lx.ref_low_float), 2)
                    else:
                        lx.result_float = round(random.uniform(msLabs.critical_low, lx.ref_low_float), 2)
                    
            elif lx.abnormal_flag in high:
                # critical high does not have a -1 flag to consider 
                lx.result_float = round(random.uniform(lx.ref_high_float, msLabs.critical_high) , 2)
                
            elif lx.abnormal_flag in chigh:
                upperLimit = msLabs.critical_high * 3
                if msLabs.datatype == 'Percent':
                    upperLimit = 100
                lx.result_float = round(random.uniform(msLabs.critical_high, upperLimit), 2)
                
            else: # normal range 
                if lx.ref_low_float == -1:
                    lx.result_float = round(random.uniform(0, lx.ref_high_float), 2)
                else:
                    lx.result_float = round(random.uniform(lx.ref_low_float, lx.ref_high_float), 2)
                
            lx.result_string = lx.result_float
        else:
            lx.result_string = random.choice(msLabs.qual_orig.split('|'))
            lx.abnormal_flag = random.choice(normal)
        
        # Wide fields
        #lx.specimen_num = ignore
        lx.specimen_source = msLabs.specimen_source
        #lx.impression = ignore
        lx.comment = 'final report'
        #lx.procedure_name = ignore
      
        if save_on_db: lx.save()
        return lx      
       
    def previous(self):
        try:
            return LabResult.objects.filter(patient=self.patient, native_code=self.native_code
                                            ).exclude(date__gte=self.date).latest('date')
        except:
            return None

    def last_known_value(self, with_same_unit=True, prior_vaccine_date=None):
        '''
        Returns the value of the Lx that is immediately prior to
        self.  if 'check_same_unit' is True, only returns the value if
        both labs results have a matching (Case insensitive) ref_unit value
        returns the value and the date 
        '''
        previous_labs = LabResult.objects.filter(native_code=self.native_code, patient=self.patient,
                                                 date__lt=self.date).order_by('-date')
        if with_same_unit:
            try:
                previous_labs = previous_labs.filter(ref_unit__iexact=self.ref_unit)
            except BaseException, e:
                log.error('Query error: %s __iexact cannot accept %s for patient %s for native_code %s for date %s' 
                          % (e, self.ref_unit, self.patient, self.native_code, str(self.date)))
        if prior_vaccine_date:
            try:
                previous_labs = previous_labs.filter(date__lt=prior_vaccine_date)
            except BaseException, e:
                log.error('Query error: %s __lt cannot accept %s for patient %s for native_code %s for date %s' 
                          % (e, prior_vaccine_date, self.patient, self.native_code, str(self.date)))
        for lab in previous_labs:
            value = (lab.result_float or lab.result_string) or None
            if value: 
                return value, lab.date
        return None, None

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
        maps = LabTestMap.objects.filter(native_code=self.native_code)
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
                'code': self.order_natural_key,
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
    
    class Meta:
        verbose_name = 'Lab Order'
    # natural key is order number    
    procedure_code = models.CharField(max_length=20, blank=True, null=True, db_index=True)
    procedure_modifier = models.CharField(max_length=20, blank=True, null=True)
    procedure_name = models.CharField(max_length=300, blank=True, null=True)
    specimen_id = models.CharField(max_length=30, blank=True, null=True, db_index=True)
    order_type = models.CharField(max_length=64, blank=True, db_index=True)
    specimen_source = models.CharField(max_length=300, blank=True, null=True)
    
    
    @staticmethod
    def delete_fakes():
        LabOrder.fakes().delete()

    @staticmethod
    def fakes():
        return LabOrder.objects.filter(LabOrder.q_fake)

    @staticmethod
    def make_mock(patient, when=None, **kw):
        
        save_on_db = kw.pop('save_on_db', False)
        msLabs = FakeLabs.objects.order_by('?')[0]
        now = int(time.time()*1000) #time in milliseconds
        provider = Provider.get_mock()
       
        lx = LabOrder(patient=patient, mrn=patient.mrn, provider=provider, provenance=Provenance.fake(), natural_key=now)
        
        when = when or randomizer.date_range(as_string=False) #datetime.date.today()
        lx.date =  when if patient.date_of_birth is None else max(when, patient.date_of_birth)
        lx.procedure_code = str(msLabs.native_code)
        lx.procedure_name = msLabs.native_name
        #1 for Lab, 2 for Imaging, or 9 for Procedures. 3 for EKG 
        lx.order_type = '1' #lab
       
        if save_on_db: lx.save()
        return lx 
    
    
class Prescription(BasePatientRecord):
    '''
    A prescribed medication
    '''
    # Date is order date
    #
    
    order_natural_key = models.CharField('Order identifier in source EMR system', max_length=128, db_index=True)
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
    
    @staticmethod
    def fakes(**kw):
        return Prescription.objects.filter(Prescription.q_fake)

    @staticmethod
    def delete_fakes():
        Prescription.fakes().delete()
        
    class Meta:
        ordering = ['date']
    
    def __str__(self):
        if not self.name:
            return "unknown prescription"
        else:
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

    @staticmethod
    def make_mock(patient, **kw):
        MIN_REFILLS = 1
        MAX_REFILLS = 12
        
        
        save_on_db = kw.pop('save_on_db', False)
        when = kw.get('when', randomizer.date_range(as_string=False)) #datetime.datetime.now())
        provider = Provider.get_mock()
        msMeds = FakeMeds.objects.order_by('?')[0]
        #CODE THE WEIGHT
       
        now = int(time.time()*1000) #time in milliseconds
        
        p = Prescription(patient=patient, provider=provider,
                      mrn=patient.mrn, date=when)
        
        Status = ['Completed', 'Ordered']
        
        days_range = random.randrange(0, 90) # Up to 90 days 
        p.end_date = when + datetime.timedelta(days=days_range)
        
        p.status = random.choice(Status)
        p.order_natural_key = now
        p.natural_key = now
        p.start_date = p.date
        p.name = msMeds.name
        p.code = msMeds.ndc_code 
        # leave empty, ignore 
        #p.directions = msMeds.directions
        p.route = msMeds.route  
        p.refills = round(random.randint(MIN_REFILLS, MAX_REFILLS)) 
       
        # dose will be in each row in the name
        dose = msMeds.name.split()
        
        # second item contains dose and 3rd contains unit, or could be a longer name
        
        if dose.__len__() > 1 :
            i = 1
            if dose[i].isdigit():
                p.dose = dose[i] + dose[i + 1] 
            else:
                while dose[i].isalpha():
                    i = i + 1
                p.dose = dose[i] + dose[i + 1] 
        
        #ignore 
        #p.frequency  = round(random.randint(MIN_FREQ, MAX_FREQ)) 
        
        # 1 , 2 or 3 multiplied by days btw start and end
        delta = p.end_date - p.start_date
        p.quantity = int((delta.days + 1) * round(random.randint(1, 3)))
        p.quantity_float = p.quantity
        
        
        if save_on_db: p.save()
        return p
    
    def document_summary(self):
        return {
            'order':{
                'id':self.natural_key,
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
    

ENCOUNTER_TYPES = [('VISIT','VISIT'), ('ER','ER'), ('HOSPITALIZATION','HOSPITALIZATION')]
# smaller number is higher priority
PRIORITY_TYPES  = [('3','3'),('2','2'),('1','1')]

class EncounterTypeMap (models.Model):
    raw_encounter_type = models.CharField(max_length=100,  blank=False, db_index=True)
    mapping = models.CharField(max_length=20, default = 'VISIT', choices=ENCOUNTER_TYPES, blank=False, db_index=True)
    priority = models.IntegerField(  blank=False,choices=PRIORITY_TYPES, default =3 ,db_index=True)
    
    def __unicode__(self):
        return u'%s %s' % (self.raw_encounter_type, self.mapping) 
    

class Encounter(BasePatientRecord):
    '''
    A encounter between provider and patient
    '''
    icd9_codes = models.ManyToManyField(Icd9, blank=True, null=True, db_index=True)
    #
    # Fields taken directly from ETL file.  Some minimal processing, such as 
    # standardizing capitalization, may be advisable in loader code.  
    
    raw_encounter_type =  models.CharField('Raw Type of encounter', max_length=100, blank=True, null=True, db_index=True)
    encounter_type = models.CharField('Type of encounter', choices=ENCOUNTER_TYPES, max_length=100, blank=True, null=True, db_index=True)
    priority =  models.CharField(max_length=10,choices=PRIORITY_TYPES, blank=False, db_index=True)
    status = models.CharField('Record status', max_length=100, blank=True, null=True, db_index=True)
    site_natural_key = models.CharField('Native EMR system site ID', max_length=30, blank=True, null=True, db_index=True)
    site_name = models.CharField('Encounter site name', max_length=100, blank=True, null=True, db_index=True)
    #
    # Extracted & calculated fields
    #
    # date is encounter date
    date_closed = models.DateField(blank=True, null=True, db_index=True)
    pregnant = models.BooleanField('Patient is pregnant?', blank=False, default=False, db_index=True)
    edd = models.DateField('Expected Date of Delivery (pregnant women only)', blank=True, null=True, db_index=True) 
    temperature = models.FloatField('Temperature (F)', blank=True, null=True, db_index=True)
    weight = models.FloatField('Weight (kg)', blank=True, null=True, db_index=True)
    height = models.FloatField('Height (cm)', blank=True, null=True, db_index=True)
    bp_systolic = models.FloatField('Blood Pressure - Systolic (mm Hg)', blank=True, null=True, db_index=True)
    bp_diastolic = models.FloatField('Blood Pressure - Diastolic (mm Hg)', blank=True, null=True, db_index=True)
    o2_stat = models.FloatField(blank=True, null=True, db_index=True)
    peak_flow = models.FloatField(blank=True, null=True, db_index=True)
    bmi = models.FloatField('Body Mass Index', null=True, blank=True, db_index=True)
    #
    # Raw string fields 
    #
    # Please do not index these, lest you over burden your poor database.  Be 
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
   
    
    class Meta:
        ordering = ['date']
    
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
    def randomVitalValue(low, high, vlow, vhigh, decimal):
        r = random.random()
        if r <= .7:
            return round(random.uniform(vlow, high), decimal)
        elif r <= .9:
            return round(random.uniform(low, vhigh), decimal) 
        else: 
            return  round(random.uniform(low, high), decimal)
        
    @staticmethod
    def makeicd9_mock (maxicd9, ICD9_CODE_PCT):
        ''' another way
            #msICD9codes = FakeICD9s.objects.order_by('?')
            #icd9 = Icd9(code= msICD9codes[i].code,name=msICD9codes[i].name )
            #icd9_codes.add(icd9)
            icd9_codes = [str(icd9.code) for icd9 in FakeICD9s.objects.order_by('?')[:how_manycodes]]
        ''' 
        
        if random.random() <= float(ICD9_CODE_PCT / 100.0):
            how_many_codes = random.randint(1, maxicd9)              
            icd9_codes = [str(random.choice(icd9.icd9_codes.split(';'))) for icd9 in FakeICD9s.objects.order_by('?')[:how_many_codes]]
        else:
            icd9_codes = ''
            
        return icd9_codes
                    
    @staticmethod
    def make_mock(patient, **kw):
        save_on_db = kw.pop('save_on_db', False)
        when = kw.get('when', randomizer.date_range(as_string=False)) #datetime.datetime.now())
        provider = Provider.get_mock()
        msVitals = FakeVitals.objects.order_by('short_name')
       
        now = int(time.time()*1000) #time in milliseconds
        
        e = Encounter(patient=patient, provider=provider, provenance=Provenance.fake(),
                      mrn=patient.mrn, status='FAKE', date=when, date_closed=when)
        
        e.natural_key = now
        #the order in msVitals depends on the fakevitals load order rows 
        e.bmi = Encounter.randomVitalValue(msVitals[0].normal_low, msVitals[0].normal_high,
                                           msVitals[0].very_low, msVitals[0].very_high, 2) 
        e.temperature = Encounter.randomVitalValue(msVitals[6].normal_low, msVitals[6].normal_high,
                                           msVitals[6].very_low, msVitals[6].very_high, 0) 
        e.raw_weight = str(Encounter.randomVitalValue(msVitals[7].normal_low, msVitals[7].normal_high,
                                           msVitals[7].very_low, msVitals[7].very_high, 0) ) + ' lb'
        e.raw_height = str(Encounter.randomVitalValue(msVitals[3].normal_low, msVitals[3].normal_high,
                                           msVitals[3].very_low, msVitals[3].very_high, 0))  + " '"
        e.bp_systolic = Encounter.randomVitalValue(msVitals[2].normal_low, msVitals[2].normal_high,
                                           msVitals[2].very_low, msVitals[2].very_high, 0)  
        e.bp_diastolic = Encounter.randomVitalValue(msVitals[1].normal_low, msVitals[1].normal_high,
                                           msVitals[1].very_low, msVitals[1].very_high, 0) 
        e.o2_stat = Encounter.randomVitalValue(msVitals[4].normal_low, msVitals[4].normal_high,
                                           msVitals[4].very_low, msVitals[4].very_high, 2) 
        e.peak_flow = Encounter.randomVitalValue(msVitals[5].normal_low, msVitals[5].normal_high,
                                           msVitals[5].very_low, msVitals[5].very_high, 2) 
                    
        if save_on_db: e.save()
        return e

    @staticmethod
    def volume(date, *args, **kw):
        '''
        Returns the total of encounters occurred on a given date.
        Extra named parameters can be passed on **kw, or Q objects on *args.        
        '''
        return Encounter.objects.filter(date=date).filter(*args).filter(**kw).count()


    #
    # TODO: issue 333 Move this code to VAERS
    #
    def is_reoccurrence(self, icd9s, month_period=12):
        '''
        returns a boolean indicating if this encounters shows any icd9
        code that has been registered for this patient in last
        month_period time.
        '''
        
        earliest = self.date - datetime.timedelta(days=30 * month_period)
        
        return Encounter.objects.filter(
            date__lt=self.date, date__gte=earliest, patient=self.patient, icd9_codes__in=icd9s
            ).count() > 0
                
    def __str__(self):
        return 'Encounter # %s' % self.pk
    
    @property
    def verbose_str(self):
        return 'Encounter # %s | %s | %s | %s | %s' % (self.pk, self.date, self.patient, self.edd, self.icd9_codes_str)
    
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
                patient=self.patient,
                ).order_by('-date')
            encs_last_year = pat_encs.filter(
                date__gte=(self.date - relativedelta(days=365)),
                date__lte=self.date,
                )
            recent_bmi_encs = encs_last_year.filter(bmi__isnull=False)
            if recent_bmi_encs:
                return recent_bmi_encs[0].bmi
            # Find the most recent height for this patient, looking back as far 
            # as their 16th birthday if necessary
            
            if not self.patient.date_of_birth: 
                log.warning('Cannot calculate sixteenth birthday because of NULL DOB for encounter %s ' % self.pk)
                ht_encs = pat_encs.filter( height__isnull=False).exclude(height=0)
            else:    
                sixteenth_bday = self.patient.date_of_birth + relativedelta(years=16)
                ht_encs = pat_encs.filter(date__gte=sixteenth_bday, height__isnull=False).exclude(height=0)
                
            # Find the most recent weight this patient within the past year
            wt_encs = encs_last_year.filter(weight__isnull=False).exclude(weight=0)
            if ht_encs and wt_encs:
                height = ht_encs[0].height
                weight = wt_encs[0].weight
            else: # We don't know a recent height and weight for this patient
                log.warning('Cannot calculate BMI for encounter # %s due to null height or weight' % self.pk)
                return None 
        height_m = height / 100  # Height is stored in centimeters
        weight_kg = weight # Already in kilograms
        bmi = weight_kg / (height_m ** 2)
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
                'bmi'    :self.bmi,
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
    
    def add_diagnosis(self, codeset, diagnosis_code):
        '''
        Add a diagnosis code to this Encounter
        @param codeset: The diagnostic codeset (e.g. ICD9, ICD10)
        @type codeset:  String
        @param diagnosis_code: A diagnosis code
        @type diagnosis_code:  String
        @rtype: None
        '''
        if not 'icd9' == codeset:
            raise NotImplementedError('Only icd9 codeset supported at this time.')
        icd9_obj, created = Icd9.objects.get_or_create(code=diagnosis_code)
        self.icd9_codes.add(icd9_obj)
        self.save()
        log.debug('Added diagnosis %s to %s' % (icd9_obj, self))
        
            
class Diagnosis(BasePatientRecord):
    '''
    A diagnosis, typically indicated by an ICD9/ICD10 code, and bound to a 
    particular physician encounter.
    '''
    code = models.CharField('Diagnosis Code', max_length=255, blank=False, db_index=True)
    codeset = models.CharField('Code Set', max_length=255, blank=False, db_index=True,
        help_text='Code set of which the Diagnosis Code is a member (e.g. ICD9)')
    encounter = models.ForeignKey(Encounter, verbose_name='Encounter at which this diagnosis was made',
        blank=False, db_index=True)


class Immunization(BasePatientRecord):
    '''
    An immunization
    '''
    # Date is immunization date
    #
    imm_type = models.CharField('Immunization Type', max_length=20, blank=True, null=True)
    name = models.CharField('Immunization Name', max_length=200, blank=True, null=True)
    dose = models.CharField('Immunization Dose', max_length=180, blank=True, null=True)
    manufacturer = models.CharField('Manufacturer', max_length=100, blank=True, null=True)
    lot = models.TextField('Lot Number', max_length=500, blank=True, null=True)
    visit_date = models.DateField('Date of Visit', blank=True, null=True)
    isvaccine = models.NullBooleanField('Is this a vaccine', default=True)

    class Meta:
        ordering = ['date']

    #
    # TODO: issue 333 Move this code to VAERS module
    #
    @staticmethod
    def vaers_candidates(patient, event_date, days_prior):
        '''Given an adverse event date, returns a queryset that represents
        the possible immunizations that have caused it'''
        
        earliest_date = event_date - datetime.timedelta(days=days_prior)
                
        return Immunization.objects.filter(
            date__gte=earliest_date, date__lte=event_date,
            isvaccine=True,
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
        now = int(time.time()*1000) #time in milliseconds
        
        i = Immunization(patient=patient, provenance=Provenance.fake(),
                         date=date, visit_date=date,
                         #changed name from FAKE to real name 
                         imm_type=vaccine.code, name=vaccine.short_name,
                         provider=patient.pcp, natural_key=now)
        if save_on_db: i.save()
        return i
            
    def _get_vaccine(self):
        try:
            return Vaccine.objects.get(code=VaccineCodeMap.objects.get(native_code=self.imm_type).canonical_code_id)
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
    
    # date is date entered
    tobacco_use = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    alcohol_use = models.CharField(max_length=100, null=True, blank=True, db_index=True)

    @staticmethod
    def delete_fakes():
        SocialHistory.fakes().delete()

    @staticmethod
    def fakes():
        return SocialHistory.objects.filter(SocialHistory.q_fake)

    @staticmethod
    def make_mock( patient, when=None, save_on_db=False):
        now = int(time.time()*1000) #time in milliseconds
        # some time in the past 3 years 
        when = when or randomizer.date_range(as_string=False) #datetime.date.today()
        date =  when if patient.date_of_birth is None else max(when, patient.date_of_birth)
        
        status = ['','yes','no']
        sh = SocialHistory(patient=patient, mrn= patient.mrn, provenance=Provenance.fake(), date=date, 
                         tobacco_use=random.choice(status), alcohol_use=random.choice(status),
                         provider=patient.pcp, natural_key=now)
        if save_on_db: sh.save()
        return sh
            
    
    def document_summary(self):
        return {
            'date':(self.date and self.date.isoformat()) or None,
            'social history':{
                'tobacco use':self.tobacco_use,
                'alcohol use':self.alcohol_use
                }
            }

    def  __unicode__(self):
        return u"Social History on %s used tobacco %s and used alcohol %s on %s" % (
            self.patient.full_name, self.tobacco_use, self.alcohol_use, self.date)

class Allergy(BasePatientRecord):
    '''
    An allergy report natural key is problem id
    '''
    # date is allergy entered date 
    date_noted = models.DateField(null=True, db_index=True)
    allergen = models.ForeignKey(Allergen)
    name = models.CharField(max_length=300, null=True, db_index=True)
    status = models.CharField(max_length=20, null=True, db_index=True)
    description = models.CharField(max_length=600,null=True,blank=True)
    
    @staticmethod
    def fakes():
        return Allergy.objects.filter(Allergy.q_fake)

    @staticmethod
    def delete_fakes():
        Allergy.fakes().delete()

    @staticmethod
    def make_mock( patient, when = None, save_on_db=False):
        now = int(time.time()*1000) #time in milliseconds
        when = when or randomizer.date_range(as_string=False) #datetime.date.today()
        date =  when if patient.date_of_birth is None else max(when, patient.date_of_birth)
        # not adding status or description
        #get the first allergen randomly
        allergen = Allergen.objects.order_by('?')[0]
        allergy = Allergy(patient=patient, provenance=Provenance.fake(),
                         date=date, date_noted=date, 
                         allergen=allergen, name=allergen.name,
                         provider=patient.pcp, natural_key=now)
        
        if save_on_db: allergy.save()
        return allergy
            

    def document_summary(self):
        return {
            'date':(self.date and self.date.isoformat()) or None,
            'allergy':{
                'name':self.name,
                'status':self.status,
                'description':self.description
                },
            'allergen':(self.allergen.code) or None,
            }

    def  __unicode__(self):
        return u"Allergy on %s had %s on %s" % (
            self.patient.full_name, self.name, self.date)

class Problem(BasePatientRecord):
    '''
    Problem list -- cumulative over time, no current 
    '''
    # date is date noted, id is natural key
    icd9 = models.ForeignKey(Icd9)
    status = models.CharField(max_length=20, null=True, db_index=True)
    comment = models.TextField(null=True, blank=True)
    raw_icd9_code = models.CharField('Raw icd9 code',max_length=20, null=True, db_index=True)
    
    @staticmethod
    def delete_fakes():
        Problem.fakes().delete()

    @staticmethod
    def fakes():
        return Problem.objects.filter(Problem.q_fake)

    @staticmethod
    def make_mock(  patient, when=None, save_on_db=False):
        now = int(time.time()*1000) #time in milliseconds
        when = when or randomizer.date_range(as_string=False) #datetime.date.today()
        date =  when if patient.date_of_birth is None else max(when, patient.date_of_birth)
        
        icd9 = Icd9.objects.order_by('?')[0]
        raw_icd9_code = icd9.code
        
        status = ['active',  'deleted','']         
        problem = Problem(patient=patient, mrn = patient.mrn, provenance=Provenance.fake(),
                         date=date, status=random.choice(status), icd9=icd9,
                         raw_icd9_code=raw_icd9_code, provider=patient.pcp,
                         natural_key=now)
        if save_on_db: problem.save()
        return problem
            
    
    def document_summary(self):
        return {
            'date':(self.date and self.date.isoformat()) or None,
            'problem':{
                'icd9':self.icd9.name,
                'comment':self.comment
                },
            'status':self.status
            }

    def  __unicode__(self):
        return u"Problem on %s had %s on %s" % (
            self.patient.full_name, self.icd9, self.date)
        
class Pregnancy(BasePatientRecord):
    '''
    A Pregnancy 
    '''
    # Date is not used, saved as today
    #
    outcome = models.TextField('Outcome', max_length=500, blank=True, null=True)
    edd = models.DateField('Estimated date of delivery', blank=True, null=True, db_index=True)
    actual_date = models.DateField('Actual date of delivery', blank=True, null=True, db_index=True)
    gravida = models.IntegerField( blank=True, null=True )
    parity = models.IntegerField(blank=True, null=True )
    term = models.IntegerField( blank=True, null=True)
    preterm = models.IntegerField(blank=True, null=True)
    ga_delivery =  models.CharField('Gestational Age at delivery', max_length=20, blank=True, null=True)
    raw_birth_weight = models.CharField('Raw birth weight', max_length=200, blank=True, null=True)
    birth_weight  = models.FloatField('Birth Weight (Kg)', blank=True, null=True)
    birth_weight2  = models.FloatField('Birth Weight 2 (Kg)', blank=True, null=True)
    birth_weight3  = models.FloatField('Birth Weight 3 (Kg)', blank=True, null=True)
    births = models.IntegerField(blank=True, null=True )
    delivery = models.TextField('Delivery', max_length=500, blank=True, null=True)
    pre_eclampsia = models.CharField('Pre_eclampsia', max_length=300, blank=True, null=True)
    
    class Meta:
        ordering = ['edd']
   
    @staticmethod
    def fakes():
        return Pregnancy.objects.filter(Pregnancy.q_fake)

    @staticmethod
    def delete_fakes():
        Pregnancy.fakes().delete()
        
    
    @staticmethod
    def make_mock( patient, gravida, parity, term, preterm, when=None, save_on_db=False,):
        now = int(time.time()*1000) #time in milliseconds
        provider = Provider.get_mock()
            
        # from now up to 3 years ago 
        preg_date = when or randomizer.date_range(as_string=False) 
        # patient is already at fertile age when coming here 
        # if dob is not null pick a date between 12 years and their current age
        preg_date = preg_date if patient.date_of_birth is None else patient.date_of_birth + datetime.timedelta(days=random.randrange(12, patient.age.years)*365)
        
        edd = preg_date + datetime.timedelta(days=random.randrange(210, 289)) # 30-40 weeks 
        # if currently pregnant, when is passed in
        if when: 
            actual_date = None
            gad = None
            birth_weight = None
            status = None
            outcome = None
            
        else: 
            actual_date = preg_date + datetime.timedelta(days=random.randrange(7, 289)) # 42 weeks. 7 days could be a miss carriage.
            gad = str(40 - relativedelta(edd, actual_date).days/7 ) + 'w ' 
            if  (relativedelta(edd, actual_date).days % 7 ) > 0:
                gad +=  str( relativedelta(edd, actual_date).days % 7 ) + 'd'
            #dont need to add births because it is calculated on load based on gad
            birth_weight = str(round(random.uniform(0.9, 5),1)) +' lbs'
            status = ['Term', 'Preterm', 'Still birth','']         
            outcome = random.choice(status)  
            
                  
        p = Pregnancy(patient=patient, mrn = patient.mrn, provenance=Provenance.fake(),
                             edd=edd, actual_date=actual_date, gravida=gravida, parity=parity,
                             preterm=preterm, raw_birth_weight=birth_weight,term=term,
                             ga_delivery = gad ,outcome=outcome, date = preg_date,
                             provider=provider,  natural_key=now)
            
        if save_on_db: p.save()
            
        return p
            
    
    def document_summary(self):
        return {
            'Actual date of delivery':(self.actual_date and self.actual_date.isoformat()) or None,
            'pregnancy':{
                'estimated date of delivery':self.edd,
                'gravida':self.gravida,
                'term':self.term
                },
            'gestational age at delivery':self.ga_delivery
            }

    def  __unicode__(self):
        return u"Pregnancy for %s expected %s and delivered %s" % (
            self.patient.full_name, self.edd, self.actual_date)