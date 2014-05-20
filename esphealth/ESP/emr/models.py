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
from ESP.conf.models import HL7Map
from ESP.conf.common import EPOCH
from ESP.conf.models import LabTestMap
from ESP.static.models import FakeLabs, FakeVitals, FakeMeds, FakeDx_Codes
from ESP.static.models import Ndc
from ESP.static.models import FakeAllergen
from ESP.static.models import Dx_code
from ESP.static.models import Allergen
from ESP.static.models import Vaccine
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
    raw_rec_count = models.IntegerField('Count of records in incoming file', null=True, default=0)
    valid_rec_count = models.IntegerField('Count of valid records loaded to primary table', blank=False, default=0)
    insert_count = models.IntegerField('Count of records inserted to primary table on last load', null=True, default=0)
    update_count = models.IntegerField('Count of records updated in primary table on last load', null=True, default=0)
    post_load_count = models.IntegerField('Count of records in primary table with this provenance_id upon load completion', null=True, default=0)
    error_count = models.IntegerField('Count of record processing errors during load', blank=False, default=0)
    comment = models.TextField(blank=True, null=True)
    data_date = models.DateField(blank=True, null=True)
    
    class Meta:
        unique_together = ['timestamp', 'source', 'hostname']

    @staticmethod
    def get_latest_data_date(source_search_str):
        """
        Return the latest data date for the Provenance objects whose
        source contains the source_search_str
        """
        qs = Provenance.objects.filter(source__icontains=source_search_str).order_by('-data_date')
        if qs:
            return qs[0].data_date
        else: 
            return datetime.date.today()
    
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
        
    def get_hl7(self, mod, var, val, typ):
        '''
        Returns hl7 type associated with variable val a, or throws an exception
        '''
        if val:
            mapObj = HL7Map.objects.get(model=mod, variable=var, value=val)
            if typ=='value':
                ret = mapObj.hl7.value
            elif typ=='description':
                ret = mapObj.hl7.description
            elif typ=='codesys':
                ret = mapObj.hl7.codesys
            elif typ=='version':
                ret = mapObj.hl7.version
        else:
            #if the value being passed is empty, return empty
            ret = ''
        return ret


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
    dept_country = models.CharField('Primary Dept country', max_length=100, blank=True, null=True)
    dept_county_code = models.CharField('Primary Dept county code', max_length=10, blank=True, null=True)
    tel_country_code = models.CharField('Primary Dept country tel code', max_length=10, blank=True, null=True)
    tel_ext = models.CharField('Primary Dept phone extension', max_length=10, blank=True, null=True)
    call_info = models.CharField('Primary Dept address comment', max_length=200, blank=True, null=True)
    clin_address1 = models.CharField('Clinician Address Line 1', max_length=100, blank=True, null=True)
    clin_address2 = models.CharField('Clinician Address Line 2', max_length=100, blank=True, null=True)
    clin_city = models.CharField('Clinician City', max_length=50, blank=True, null=True)
    clin_state = models.CharField('Clinician State', max_length=50, blank=True, null=True)
    clin_zip = models.CharField('Clinician Zip Code', max_length=10, blank=True, null=True)
    clin_country = models.CharField('Clinician Country', max_length=100, blank=True, null=True)
    clin_county_code = models.CharField('Clinician county code', max_length=10, blank=True, null=True)
    clin_tel_country_code = models.CharField('Clinician country tel code', max_length=10, blank=True, null=True)
    clin_areacode = models.CharField('Clinician Phone area code', max_length=5, blank=True, null=True)
    clin_tel = models.CharField('Clinician Phone number', max_length=10, blank=True, null=True)
    clin_tel_ext = models.CharField('Clinician Extension', max_length=10, blank=True, null=True)
    clin_call_info = models.CharField('Clinician address comment', max_length=200, blank=True, null=True)
    suffix = models.CharField('Name suffix', max_length=20, blank=True, null=True)
    dept_addr_type = models.CharField(max_length=20, blank=True, null=True)
    clin_addr_type = models.CharField(max_length=20, blank=True, null=True)

    
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


class Provider_idInfo(models.Model):
    '''
    For Meaningful Use certification, Providers have a number of IDs and extra associated information
    '''
    provider = models.ForeignKey(Provider)
    provider_natural_key = models.CharField('provider_natural_key', unique=True, max_length=128, null=True)
    #unique foreign key ensures one-to-one order to order_idinfo relationship, used in nodis.labreport.makeorc
    provenance = models.ForeignKey(Provenance, blank=False)
    provider_nistid = models.CharField(max_length=100, blank=True, null=True)
    auth_namespaceid = models.CharField(max_length=100, blank=True, null=True)
    auth_universalid = models.CharField(max_length=100, blank=True, null=True)
    auth_universalidtype = models.CharField(max_length=100, blank=True, null=True)
    name_typecode = models.CharField(max_length=100, blank=True, null=True)
    identifier_typecode = models.CharField(max_length=100, blank=True, null=True)
    fac_namespaceid = models.CharField(max_length=100, blank=True, null=True)
    fac_universalid = models.CharField(max_length=100, blank=True, null=True)
    fac_universalidtype = models.CharField(max_length=100, blank=True, null=True)
    facname_type = models.CharField(max_length=100, blank=True, null=True)
    facname_auth_nid = models.CharField(max_length=100, blank=True, null=True)
    facname_auth_uid = models.CharField(max_length=100, blank=True, null=True)
    facname_auth_uidtype = models.CharField(max_length=100, blank=True, null=True)
    facname_auth_idtype = models.CharField(max_length=100, blank=True, null=True)
    facname_auth_id = models.CharField(max_length=100, blank=True, null=True)
    
    
class Provider_phones(models.Model):
    '''
    For Meaningful Use certification, Providers have a number of IDs and extra associated information
    '''
    provider = models.ForeignKey(Provider)
    provider_natural_key = models.CharField('provider_natural_key', max_length=128, null=False)
    provider_phone_id =  models.CharField(max_length=12, null=False)
    provenance = models.ForeignKey(Provenance, blank=False)
    tel_use_code = models.CharField(max_length=100, blank=True, null=True)
    tel_eqp_type = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    tel_countrycode = models.CharField(max_length=100, blank=True, null=True)
    tel_areacode = models.CharField(max_length=100, blank=True, null=True)
    tel = models.CharField(max_length=100, blank=True, null=True)
    tel_extension = models.CharField(max_length=100, blank=True, null=True)
    tel_info = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = 'Provider Phones'
        unique_together = ['provider_natural_key','provider_phone_id']
    
    
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
    country = models.CharField('Country', max_length=60, blank=True, null=True)
    # Large max_length value for area code because Atrius likes to put descriptive text into that field
    areacode = models.CharField('Home Phone Area Code', max_length=50, blank=True, null=True)
    tel = models.CharField('Home Phone Number', max_length=100, blank=True, null=True)
    tel_ext = models.CharField('Home Phone Extension', max_length=50, blank=True, null=True)
    date_of_birth = models.DateTimeField('Date of Birth', blank=True, null=True, db_index=True)
    cdate_of_birth = models.CharField('Date of Birth String', max_length=100, blank=True, null=True)
    date_of_death = models.DateTimeField('Date of death', blank=True, null=True)
    cdate_of_death = models.CharField('Date of Death String', max_length=100, blank=True, null=True)
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
    mother_maiden_name = models.CharField('Mother Maiden Name', max_length=100, blank=True, null=True)
    last_update = models.DateTimeField('Date when patient information was last updated',null=True)
    clast_update = models.CharField('Date of last update string', max_length=100, blank=True, null=True)
    last_update_site = models.CharField('Site where patient information was last updated', max_length=100, blank=True, null=True)
    title = models.CharField('Title', max_length=50, blank=True, null=True)
    remark  = models.TextField('Remark', blank=True, null=True)

    
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
     

    def has_history_of(self, dx_codes, begin_date=None, end_date=None):
        '''
        returns a boolean if the patient has any of the dx code 
        in their history of encounters.
        '''
        begin_date = begin_date or self.date_of_birth or EPOCH
        end_date = end_date or datetime.date.today()
        H1 = self.encounters().filter(
            date__gte=begin_date, date__lt=end_date
            ).filter(dx_codes__in=list(dx_codes)).count() != 0
        H2 = self.problems().filter(
            date__gte=begin_date, date__lt=end_date
            ).filter(dx_code_id__in=list(dx_codes)).count() != 0
        H3 = self.hospprobs().filter(
            date__gte=begin_date, date__lt=end_date
            ).filter(dx_code_id__in=list(dx_codes)).count() != 0
        #the point here is only to determine if there is any prior history and use this to stop
        # further heuristic processing.  So just return the first one that has any data, or the last one.
        if H1: 
            return H1
        elif H2:
            return H2
        else:
            return H3
            

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

    def problems(self):
        return Problem.objects.filter(patient=self)

    def hospprobs(self):
        return Hospital_Problem.objects.filter(patient=self)

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
class BasePatRecord(BaseMedicalRecord):
    '''
    A pat record contains normalized data from a specific patient record 
    '''
    patient = models.ForeignKey(Patient, blank=True, null=True) 
    mrn = models.CharField('Medical Record Number', max_length=50, blank=True, null=True)
    
    def get_basePat_hl7(self, model, var, val, typ):
        '''
        Returns hl7 type associated with variable val a, or throws an exception
        '''
        mapObj = HL7Map.objects.get(model=model, variable=var, value=val)
        if typ=='value':
            ret = mapObj.hl7.value
        elif typ=='description':
            ret = mapObj.hl7.description
        elif typ=='codesys':
            ret = mapObj.hl7.codesys
        elif typ=='version':
            ret = mapObj.hl7.version
        return ret

    
    q_fake = Q(patient_natural_key__startswith='FAKE')
    
    def is_fake(self):
        return self.patient.natural_key.startswith('FAKE')
   
    
    class Meta:
        abstract = True

class Patient_Addr(BasePatRecord):
    '''
    For meaningful use certification, patients may have multiple addresses (home, business, secondary home, etc.)
    '''
    address1 = models.CharField('Address1', max_length=200, blank=True, null=True)
    address2 = models.CharField('Address2', max_length=100, blank=True, null=True)
    city = models.CharField('City', max_length=50, blank=True, null=True)
    state = models.CharField('State', max_length=20, blank=True, null=True)
    zip = models.CharField('Zip', max_length=20, blank=True, null=True, db_index=True)
    zip5 = models.CharField('5-digit zip', max_length=5, null=True, db_index=True)
    country = models.CharField('Country', max_length=60, blank=True, null=True)
    county_code = models.CharField('County Code', max_length=10, blank=True, null=True)
    tel_country_code = models.CharField('Telephone Country Code', max_length=10, blank=True, null=True)
    areacode = models.CharField('Phone Area Code', max_length=50, blank=True, null=True)
    tel = models.CharField('Phone Number', max_length=100, blank=True, null=True)
    tel_ext = models.CharField('Phone Extension', max_length=50, blank=True, null=True)
    call_info = models.CharField('Additional information', max_length=100, blank=True, null=True)
    email = models.CharField('email', max_length=200, blank=True, null=True)
    type = models.CharField('Type', max_length=100, blank=True, null=True)
    use = models.CharField(max_length=10, blank=True, null=True)
    eqptype = models.CharField(max_length=10, blank=True, null=True)
    
class Patient_Guardian(BasePatRecord):
    '''
    For meaningful use certification, patients may have parent or guardian information for
    a person who is not a patient in the system.
    '''
    organization = models.CharField('Relationship', max_length=200, blank=True, null=True)
    relationship = models.CharField('Relationship', max_length=200, blank=True, null=True)
    title = models.CharField('honorific', max_length=20, blank=True, null=True)
    last_name = models.CharField('Last Name', max_length=200, blank=True, null=True)
    first_name = models.CharField('First Name', max_length=200, blank=True, null=True)
    middle_name = models.CharField('Middle Name', max_length=200, blank=True, null=True)
    suffix = models.CharField('Suffix', max_length=20, blank=True, null=True)
    address1 = models.CharField('Address1', max_length=200, blank=True, null=True)
    address2 = models.CharField('Address2', max_length=100, blank=True, null=True)
    city = models.CharField('City', max_length=100, blank=True, null=True)
    state = models.CharField('State', max_length=10, blank=True, null=True)
    zip = models.CharField('Zip', max_length=10, blank=True, null=True, db_index=True)
    zip5 = models.CharField('5-digit zip', max_length=5, null=True, db_index=True)
    country = models.CharField('Country', max_length=60, blank=True, null=True)
    county_code = models.CharField('County Code', max_length=10, blank=True, null=True)
    type = models.CharField('type', max_length=10, blank=True, null=True)
    use = models.CharField('type', max_length=10, blank=True, null=True)  
    eqptype = models.CharField('equipment type', max_length=10, blank=True, null=True)
    tel_country_code = models.CharField('Telephone Country Code', max_length=10, blank=True, null=True)
    areacode = models.CharField('Phone Area Code', max_length=5, blank=True, null=True)
    tel = models.CharField('Phone Number', max_length=10, blank=True, null=True)
    tel_ext = models.CharField('Phone Extension', max_length=5, blank=True, null=True)
    call_info = models.CharField('Additional information', max_length=100, blank=True, null=True)
    email = models.CharField('email', max_length=200, blank=True, null=True)
    email_info = models.CharField('email text', max_length=100, blank=True, null=True)
    auth_nid = models.CharField('Auth Namespace ID', max_length=50, blank=True, null=True)
    auth_uid = models.CharField('Auth Universal ID', max_length=50, blank=True, null=True)
    auth_uidtype = models.CharField('Auth UID Type', max_length=10, blank=True, null=True)
    idtype_code = models.CharField('ID Type Code', max_length=10, blank=True, null=True)
    org_id = models.CharField('Organization ID', max_length=20, blank=True, null=True)

class Patient_ExtraData(BasePatRecord):
    '''
    For meaningful use certification, patient have a bunch of otherwise meaningless data.
    '''
    auth_nid = models.CharField(max_length=100, blank=True, null=True)
    auth_uid = models.CharField(max_length=100, blank=True, null=True)
    auth_uidtype = models.CharField(max_length=100, blank=True, null=True)
    id_typecode = models.CharField(max_length=100, blank=True, null=True)
    fac_nid = models.CharField(max_length=100, blank=True, null=True)
    fac_uid = models.CharField(max_length=100, blank=True, null=True)
    fac_uidtype = models.CharField(max_length=100, blank=True, null=True)
    death_ind = models.CharField(max_length=10, blank=True, null=True)
    last_source_update = models.CharField(max_length=100, blank=True, null=True)
    lsu_nid = models.CharField(max_length=100, blank=True, null=True)
    lsu_uid = models.CharField(max_length=100, blank=True, null=True)
    lsu_uidtype = models.CharField(max_length=10, blank=True, null=True)
    species = models.CharField(max_length=40, blank=True, null=True)
    
    
    

class BasePatientRecordManager(models.Manager):
    
    # TODO: issue 333 This code belongs in VAERS module, not here.
    def following_vaccination(self, days_after, risk_period_start, **kw):

        if risk_period_start ==0 :
            q_earliest_date = Q(date__gte=F('patient__immunization__date'))
        else:
            q_earliest_date = Q(date__gte=F('patient__immunization__date')+ risk_period_start)
            
        q_filter = q_earliest_date & Q(date__lte=F('patient__immunization__date') + days_after) & Q(patient__immunization__id=F('patient__immunization__id'))
        
        return self.filter(patient__immunization__isvaccine=True, 
                           patient__immunization__imm_status='1').filter(q_filter)


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


class LabInfo(models.Model):
    '''
    Information about the lab performing test analysis
    '''
    CLIA_ID = models.CharField('CLIA ID', max_length=20,primary_key=True, blank=True)
    provenance = models.ForeignKey(Provenance, blank=False)
    perf_auth_nid = models.CharField(max_length=100, blank=True, null=True)
    perf_auth_uid = models.CharField(max_length=100, blank=True, null=True)
    perf_auth_uidtype = models.CharField(max_length=100, blank=True, null=True)
    perf_idtypecode = models.CharField(max_length=100, blank=True, null=True)
    laboratory_name =  models.CharField('Laboratory name', max_length=150, blank=True, null=True)
    lab_name_type_code = models.CharField(max_length=100, blank=True, null=True)
    Lab_Director_lname = models.CharField(max_length=100, blank=True, null=True)
    Lab_Director_fname = models.CharField(max_length=100, blank=True, null=True)
    Lab_Director_mname = models.CharField(max_length=100, blank=True, null=True)
    Lab_Director_suff = models.CharField(max_length=100, blank=True, null=True)
    Lab_Director_pref = models.CharField(max_length=100, blank=True, null=True)
    NPI_ID = models.CharField('NPI ID', max_length=60, blank=True, null=True)
    labdir_auth_nid = models.CharField(max_length=100, blank=True, null=True)
    labdir_auth_uid = models.CharField(max_length=100, blank=True, null=True)
    labdir_auth_uidtype = models.CharField(max_length=100, blank=True, null=True)
    labdir_nametypecode = models.CharField(max_length=100, blank=True, null=True)
    labdir_idtypecode = models.CharField(max_length=100, blank=True, null=True)
    labdir_fac_nid = models.CharField(max_length=100, blank=True, null=True)
    labdir_fac_uid = models.CharField(max_length=100, blank=True, null=True)
    labdir_fac_uidtype = models.CharField(max_length=100, blank=True, null=True)
    labdir_profsuff = models.CharField(max_length=100, blank=True, null=True)
    address1 = models.CharField('Address1', max_length=200, blank=True, null=True)
    address2 = models.CharField('Address2', max_length=100, blank=True, null=True)
    city = models.CharField('City', max_length=50, blank=True, null=True)
    state = models.CharField('State', max_length=20, blank=True, null=True)
    zip = models.CharField('Zip', max_length=20, blank=True, null=True, db_index=True)
    zip5 = models.CharField('5-digit zip', max_length=5, null=True, db_index=True)
    country = models.CharField('Country', max_length=60, blank=True, null=True)
    addr_type = models.CharField(max_length=10, blank=True, null=True)
    county_code = models.CharField('County Code', max_length=10, blank=True, null=True)
    
    def __str__(self):
        return u'%20s' % (self.pk)

class LabOrder(BasePatientRecord):
    '''
    An order for a laboratory test
    '''
    
    class Meta:
        verbose_name = 'Lab Order'
    # natural key is order number    
    cdate = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    procedure_code = models.CharField(max_length=20, blank=True, null=True, db_index=True)
    procedure_modifier = models.CharField(max_length=20, blank=True, null=True)
    procedure_name = models.CharField(max_length=300, blank=True, null=True)
    specimen_id = models.CharField(max_length=30, blank=True, null=True, db_index=True)
    order_type = models.CharField(max_length=64, blank=True, db_index=True)
    specimen_source = models.CharField(max_length=300, blank=True, null=True)
    test_status = models.CharField('Test status', max_length=5, null=True)
    patient_class = models.CharField('Patient class',max_length=5, null=True)
    patient_status = models.CharField('Patient status',max_length=5, null=True)
    group_id = models.CharField('Placer Order Group',max_length=15, null=True)
    reason_code = models.CharField('Reason for Order',max_length=15, null=True)
    reason_code_type = models.CharField('Reason code type',max_length=25, null=True)
    order_info = models.CharField('Clinical information',max_length=100, null=True)
    obs_start_date = models.CharField(max_length=100, null=True)
    obs_end_date = models.CharField(max_length=100, null=True)
    remark  = models.TextField('Remark', blank=True, null=True)

    
    
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
    
    
class Order_idInfo(models.Model):
    '''
    For Meaningful Use certification, Orders have a number of IDs and extra associated information
    '''
    laborder = models.ForeignKey(LabOrder)
    order_natural_key = models.CharField('order_natural_key', unique=True, max_length=128, null=True)
    #unique foreign key ensures one-to-one order to order_idinfo relationship, used in nodis.labreport.makeorc
    provenance = models.ForeignKey(Provenance, blank=False)
    placer_ord_eid = models.CharField('Placer Order Number Entity ID', max_length=100, null=True)
    placer_ord_nid = models.CharField('Placer Order Number Namespace ID', max_length=100, null=True)
    placer_ord_uid = models.CharField('Placer Order Number Universal ID', max_length=100, null=True)
    placer_ord_uid_type = models.CharField('Placer Order Number Universal ID Type', max_length=100, null=True)
    filler_ord_eid = models.CharField('Filler Order Number Entity ID', max_length=100, null=True)
    filler_ord_nid = models.CharField('Filler Order Number Namespace ID', max_length=100, null=True)
    filler_ord_uid = models.CharField('Filler Order Number Universal ID', max_length=100, null=True)
    filler_ord_uid_type = models.CharField('Filler Order Number Universal ID Type', max_length=100, null=True)
    placer_grp_eid = models.CharField('Placer Group Number Entity ID', max_length=100, null=True)
    placer_grp_nid = models.CharField('Placer Group Number Namespace ID', max_length=100, null=True)
    placer_grp_uid = models.CharField('Placer Group Number Universal ID', max_length=100, null=True)
    placer_grp_uid_type = models.CharField('Placer Group Number Universal ID Type', max_length=100, null=True)
    

class Specimen(models.Model):
    '''
    Details about the lab specimen
    '''
    order_natural_key = models.CharField('order_natural_key', max_length=128, null=True)
    specimen_num = models.CharField('Specimen ID Number', max_length=100, null=True)
    laborder = models.ForeignKey(LabOrder)
    provenance = models.ForeignKey(Provenance, blank=False)
    fill_nid  = models.CharField(max_length=50,null=True)
    fill_uid = models.CharField(max_length=50,null=True)
    fill_uidtype  = models.CharField(max_length=50,null=True)
    specimen_source = models.CharField('Speciment Source', max_length=255, blank=True, null=True)
    type_modifier =  models.CharField('Specimen Type Modifier', max_length=100, blank=True, null=True)
    additives =  models.CharField('Specimen additives', max_length=100, blank=True, null=True)
    collection_method =  models.CharField('Collection Method', max_length=100, blank=True, null=True)
    Source_site =  models.CharField('Specimen Source site', max_length=100, blank=True, null=True)
    Source_site_modifier =  models.CharField('Specimen Source site modifier', max_length=100, blank=True, null=True)
    Specimen_role =  models.CharField('Specimen Role', max_length=100, blank=True, null=True)
    Collection_amount =  models.CharField('Collection Amount', max_length=100, blank=True, null=True)
    amount_id = models.CharField(max_length=50,null=True)
    range_startdt = models.CharField(max_length=50,null=True)
    range_enddt = models.CharField(max_length=50,null=True) 
    Received_date = models.DateTimeField('Received datetime',null=True)
    creceived_date = models.CharField('Received date String', max_length=100, blank=True, null=True)
    analysis_date = models.DateTimeField('Analysis datetime',null=True)
    canalysis_date = models.CharField('Analysis Date String', max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = 'Lab Specimen'
        unique_together = ['order_natural_key', 'specimen_num']

    def get_hl7(self, mod, var, val, typ):
        '''
        Returns hl7 type associated with variable val a, or throws an exception
        '''
        ret = ''
        if val:
            mapObj = HL7Map.objects.get(model=mod, variable=var, value=val)
            if typ=='value':
                ret = mapObj.hl7.value
            elif typ=='description':
                ret = mapObj.hl7.description
            elif typ=='codesys':
                ret = mapObj.hl7.codesys
            elif typ=='version':
                ret = mapObj.hl7.version
        return ret

    
class LabResult(BasePatientRecord):
    '''
    Result data for a lab test
    '''
    # Date (from base class) is order date
    #
    order_natural_key = models.CharField('Order identifier in source EMR system', max_length=128, db_index=True, blank=True, null=True)
    native_code = models.CharField('Native Test Code', max_length=255, blank=True, null=True, db_index=True)
    native_name = models.CharField('Native Test Name', max_length=255, blank=True, null=True, db_index=True)
    result_date = models.DateTimeField('Result Date', blank=True, null=True, db_index=True)
    cresult_date = models.CharField('Result Date String', max_length=100, blank=True, null=True)
    collection_date = models.DateTimeField(blank=True, null=True, db_index=True)
    ccollection_date = models.CharField('Collection date String', max_length=100, blank=True, null=True)
    status = models.CharField('Result Status', max_length=200, blank=True, null=True)
    order_type = models.CharField('Order type', max_length=20, null=True)
    patient_class = models.CharField('Patient class',max_length=5, null=True)
    patient_status = models.CharField('Patient status',max_length=5, null=True)

    # 
    # In some EMR data sets, reference pos & high, and neg & low, may come from
    # the same field depending whether the value is a string or a number.
    #
    ref_high_string = models.CharField('Reference High Value (string)', max_length=100, blank=True, null=True)
    ref_low_string = models.CharField('Reference Low Value (string)', max_length=100, blank=True, null=True)
    ref_text = models.CharField('Reference text', max_length=100, blank=True, null=True)
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
    specimen_num = models.CharField('Specimen ID Number', max_length=100, null=True)
    specimen_source = models.CharField('Specimen Source', max_length=255, blank=True, null=True)
    impression = models.TextField('Impression (imaging)', max_length=2000, blank=True, null=True)
    comment = models.TextField('Comments', blank=True, null=True)
    procedure_name = models.CharField('Procedure Name', max_length=255, blank=True, null=True)
    #
    # Added for meaningful use
    #
    collection_date_end = models.DateTimeField('Lab Collection End date',null=True)
    ccollection_date_end = models.CharField('Collection end date String', max_length=100, blank=True, null=True)
    status_date = models.DateTimeField('Result interpretation/status change date', null=True)
    cstatus_date = models.CharField('Status date String', max_length=100, blank=True, null=True)
    interpreter = models.CharField('Lab result interpreter', max_length=100, blank=True, null=True)
    interpreter_id = models.CharField('Interpreter ID', max_length=20, blank=True, null=True)
    interp_id_auth = models.CharField('Interpreter ID Type', max_length=50, blank=True, null=True)
    interp_uid = models.CharField('Interpreter uid', max_length=50, blank=True, null=True)
    CLIA_ID = models.ForeignKey(LabInfo, blank=True, null=True)
    lab_method = models.CharField('Observation method', max_length=100, blank=True, null=True)

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
    def randomWeight(normal, high, low, chigh, clow, lowestcutoff=.1, lowcutoff=.3, highcutoff=.7, highestcutoff=.9 ):
        
        r = random.random()
        if r <= lowestcutoff:
            return random.choice(clow)
        elif r <= lowcutoff:
            return random.choice(low )
        elif r <= highcutoff:
            return random.choice(high )
        elif r <= highestcutoff:
            return random.choice(chigh)
        else: 
            return random.choice(normal)
        
    @staticmethod    
    # This code is used for case report hl7 and case detail view 
    # specific for MDPH specific which requires one lab for TB 
    # if there are no reportable labs or labs associated with a case
    # we create a dummy one.
    def createDummyLab( patient, cases):    
        lx =[]                                 
        if cases:
            provider = cases[0].provider
            date = cases[0].date
            provenance = Provenance.objects.get(source='SYSTEM')
            now = int(time.time()*1000) #time in milliseconds
            order_date = date
            
            lx = LabResult(patient=patient, mrn=patient.mrn, provider=provider, provenance=provenance, natural_key=now)
            lx.pk = 0
            lx.result_date = datetime.datetime.today()
            lx.date = order_date
            lx.native_code = 'MDPH-250' #this is the loinc
        
            lx.order_natural_key = lx.natural_key # same order and key
            lx.native_name = 'TB NO TEST'
            lx.collection_date = lx.result_date
       
        return lx 
        
    @staticmethod
    def make_mock(patient, when=None, **kw):
        normal = ['IN','UN','NL']
        high = ['AH']
        low = ['AL','AB']
        chigh = ['CH','CR']
        clow = ['CL']
    
        save_on_db = kw.pop('save_on_db', False)
        msLabs = FakeLabs.objects.order_by('?')[0]
        log.info('generating fake lab result for this lab "%s"' % msLabs.native_name)
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
        lx.status =  random.choice(['E', 'S','R','U'])
        #lx.result_num = this is result id not in epic ignore
        #lx.ref_high_string = ignore  not included in etl epic care
        #lx.ref_low_string = ignore
        lx.ref_high_float = msLabs.normal_high
        lx.ref_low_float = msLabs.normal_low
        lx.ref_unit = msLabs.units
        # Result
        
        if msLabs.datatype <> 'Qualitative':
            lx.abnormal_flag = LabResult.randomWeight(normal,high,low, chigh, clow)
            
            # never generate abnormal low or critical low 
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

    def last_known_value(self, lab_values, comparator, with_same_unit=True, prior_vaccine_date=None):
        '''
        Returns the value of the Lx that is immediately prior to
        self.  if 'check_same_unit' is True, only returns the value if
        both labs results have a matching (Case insensitive) ref_unit value
        returns the value and the date.  If there are multiple values on a date
        uses 'comparator' value to determine if highest or lowest is picked. 
        '''

        try:
            #if we are looking to exclude for values greater than, sort to pick largest, otherwise sort for smallest
            if comparator == '>':
                previous_labs = LabResult.objects.filter(native_code__in=lab_values, patient=self.patient,
                                                 date__lt=self.date).order_by('-result_date','result_float')
            else:
                previous_labs = LabResult.objects.filter(native_code__in=lab_values, patient=self.patient,
                                                 date__lt=self.date).order_by('-result_date','-result_float')
        except:
            msg='broken at last_known_value'
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
        

class Labresult_Details(models.Model):
    '''
    For Meaningful Use certification, numeric lab results have extended values, findings are presented as original text 
    in some cases.
    '''
    labresult = models.ForeignKey(LabResult)
    labresult_natural_key = models.CharField('labresult_natural_key', unique=True, max_length=128, null=False)
    provenance = models.ForeignKey(Provenance, blank=False)
    comparator =  models.CharField(max_length=20, null=True)
    num1 = models.CharField(max_length=20, blank=True, null=True)
    sep_suff = models.CharField(max_length=20, blank=True, null=True)
    num2 = models.CharField(max_length=20, blank=True, null=True)
    ref_range = models.CharField(max_length=20, blank=True, null=True)
    char_finding = models.CharField(max_length=50, blank=True, null=True)
    orig_text = models.CharField(max_length=50, blank=True, null=True)
    sub_id = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name = 'Lab result details'
    
    
class SpecObs(models.Model):
    '''
    Observations and comments regarding the specimen
    '''
    specimen = models.ForeignKey(Specimen)
    provenance = models.ForeignKey(Provenance, blank=False)
    order_natural_key = models.CharField(blank=True, null=True, max_length=128)
    specimen_num = models.CharField(max_length=50)
    type = models.CharField('Observation type', max_length=100, blank=True, null=True)
    result = models.CharField('Observation value', max_length=200, blank=True, null=True)
    unit = models.CharField('Observation unit', max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = 'Lab Specimen Observation'
        unique_together = ['order_natural_key', 'specimen_num']
        

    def get_hl7(self, mod, var, val, typ):
        '''
        Returns hl7 type associated with variable val a, or throws an exception
        '''
        ret = ''
        if val:
            mapObj = HL7Map.objects.get(model=mod, variable=var, value=val)
            if typ=='value':
                ret = mapObj.hl7.value
            elif typ=='description':
                ret = mapObj.hl7.description
            elif typ=='codesys':
                ret = mapObj.hl7.codesys
            elif typ=='version':
                ret = mapObj.hl7.version
        return ret

    
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
    patient_class = models.CharField('Patient Class', max_length=5, null=True)
    patient_status = models.CharField('Patient status', max_length=5, null=True)
    
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
    dx_codes = models.ManyToManyField(Dx_code, blank=True, null=True, db_index=True)
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
    cpt = models.CharField('CPT code', max_length=20, blank=True, null=True, db_index=True)
    weight = models.FloatField('Weight (kg)', blank=True, null=True, db_index=True)
    height = models.FloatField('Height (cm)', blank=True, null=True, db_index=True)
    bp_systolic = models.FloatField('Blood Pressure - Systolic (mm Hg)', blank=True, null=True, db_index=True)
    bp_diastolic = models.FloatField('Blood Pressure - Diastolic (mm Hg)', blank=True, null=True, db_index=True)
    o2_sat = models.FloatField(blank=True, null=True, db_index=True)
    peak_flow = models.FloatField(blank=True, null=True, db_index=True)
    bmi = models.FloatField('Body Mass Index', null=True, blank=True, db_index=True)
    hosp_admit_dt = models.DateField('Hospital Admission Date', blank=True, null=True, db_index=True)
    hosp_dschrg_dt = models.DateField('Hospital Discharg Date', blank=True, null=True, db_index=True)
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
    raw_o2_sat = models.TextField(null=True, blank=True)
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
            return round(random.uniform(vlow, low), decimal)
        elif r <= .9:
            return round(random.uniform(high, vhigh), decimal) 
        else: 
            return  round(random.uniform(low, high), decimal)
        
    @staticmethod
    def makedx_code_mock (maxdx_code, DX_CODE_PCT):
        ''' another way
            #msdx_codes = FakeDx_codes.objects.order_by('?')
            #dx_code = Dx_code(code= msdx_codes[i].code,name=msdx_codes[i].name )
            #dx_codes.add(dx_code)
            dx_codes = [str(dx_code.code) for dx_code in FakeDx_codes.objects.order_by('?')[:how_manycodes]]
        ''' 
        
        if random.random() <= float(DX_CODE_PCT / 100.0):
            how_many_codes = random.randint(1, maxdx_code)              
            dx_codes =  [str(random.choice(dx_code.dx_codes.split(';'))) for dx_code in FakeDx_Codes.objects.order_by('?')[:how_many_codes]]
        else:
            dx_codes = ''
            
        return dx_codes
                    
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
        e.o2_sat = Encounter.randomVitalValue(msVitals[4].normal_low, msVitals[4].normal_high,
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
    def is_reoccurrence(self, dx_codes, month_period=12):
        '''
        returns a boolean indicating if this encounters shows any dx 
        code that has been registered for this patient in last
        month_period time.
        '''
        
        earliest = self.date - datetime.timedelta(days=30 * month_period)
        
        return Encounter.objects.filter(
            date__lt=self.date, date__gte=earliest, patient=self.patient, dx_codes__in=dx_codes
            ).count() > 0
                
    def __str__(self):
        return 'Encounter # %s' % self.pk
    
    @property
    def verbose_str(self):
        return 'Encounter # %s | %s | %s | %s | %s' % (self.pk, self.date, self.patient, self.edd, self.dx_codes_str)
    
    def str_line(self):
        '''
        Returns a single-line string representation of the Case instance
        '''
        values = self.__dict__ 
        values['dx_codes'] = ', '.join([i.combotypecode for i in self.dx_codes.all().order_by('combotypecode')])
        return '%(date)-10s    %(id)-8s    %(temperature)-6s    %(dx_codes)-30s' % values
    
    @classmethod
    def str_line_header(cls):
        '''
        Returns a header describing the fields returned by str_line()
        '''
        values = {'date': 'DATE', 'id': 'ENC #', 'temperature': 'TEMP (F)', 'dx_codes': 'DX CODES'}
        return '%(date)-10s    %(id)-8s    %(temperature)-6s    %(dx_codes)-30s' % values
    
    def _get_dx_codes_str(self):
        return ', '.join(self.dx_codes.order_by('combotypecode').values_list('combotypecode', flat=True))
    dx_codes_str = property(_get_dx_codes_str)

    def _calculate_bmi(self):
        '''
        Calculate's patient's BMI as of this encounter
        '''
        # If this encounter has a raw bmi value, convert it to float and return
        if self.raw_bmi:
            try:
                return float(self.raw_bmi)
            except ValueError: # Can't convert raw_bmi to a float
                log.info('Could not convert raw_bmi "%s" to float - will try to calculate BMI' % self.raw_bmi)
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
                log.info('Cannot calculate sixteenth birthday because of NULL DOB for encounter %s ' % self.pk)
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
                log.info('Cannot calculate BMI for encounter # %s due to null height or weight' % self.pk)
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
                'o2_sat':self.o2_sat,
                'peak_flow':self.peak_flow
                }
            }
    
    def add_diagnosis(self, codeset, combotypecode):
        '''
        Add a diagnosis code to this Encounter
        @param codeset: The diagnostic codeset (e.g. ICD9, ICD10)
        @type codeset:  String
        @param combotypecode: A combined code type and diagnosis code
        @type combotypecode:  String
        @rtype: None
        '''
        if not codeset.lower() in  ['icd9','icd10']:
            raise NotImplementedError('Only icd9 and icd10 codeset supported at this time.  Codeset value was %s' % codeset)
        dx_code_obj, created = Dx_code.objects.get_or_create(combotypecode=combotypecode)
        self.dx_codes.add(dx_code_obj)
        self.save()
        log.debug('Added diagnosis %s to %s' % (dx_code_obj, self))
        
            
class Diagnosis(BasePatientRecord):
    '''
    this is not used and will be deprecated 
    A diagnosis, typically indicated by an ICD9/ICD10 code, and bound to a 
    particular physician encounter.
    '''
    code = models.CharField('Diagnosis Code', max_length=255, blank=False, db_index=True)
    codeset = models.CharField('Code Set', max_length=255, blank=False, db_index=True,
        help_text='Code set of which the Diagnosis Code is a member (e.g. icd9 or icd10)')
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
    imm_status = models.CharField('Immunization Order Status', max_length=20, null=True)
    cpt_code = models.CharField('CPT code', max_length=20, null=True)
    patient_class = models.CharField('Patient class', max_length=20, null=True)
    patient_status = models.CharField('Patient status', max_length=20, null=True)

    class Meta:
        ordering = ['date']

    #
    # TODO: issue 333 Move this code to VAERS module
    #
    @staticmethod
    def vaers_candidates(patient, event_date, days_prior, immtypes):
        '''Given an adverse event date, returns a queryset that represents
        the possible immunizations that have caused it'''
        
        earliest_date = event_date - datetime.timedelta(days=days_prior)
        
        if immtypes[0]=='ALL':
            return Immunization.objects.filter(
                date__gte=earliest_date, date__lte=event_date,
                isvaccine=True,
                imm_status='1',
                patient=patient
                )
        else:
            return Immunization.objects.filter(
                date__gte=earliest_date, date__lte=event_date,
                isvaccine=True,
                imm_status='1',
                imm_type__in=immtypes,
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
            return Vaccine.objects.get(id=VaccineCodeMap.objects.filter(native_code=self.imm_type).distinct('canonical_code_id').canonical_code_id)
            #sites have been known to update their vaccine names, while keeping the IDs the same, causing the need for multiple
            # rows in VaccineCodeMap for each immunization type.  This will break if rows for the same immunization type are mapped to
            # multiple canonical codes in static_vaccine
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
        #get the first fake allergen randomly
        # no need to use fake allergens since we have the real allergens filled out 
        allergen = Allergen.objects.order_by('?')[0]
        allergy = Allergy(patient=patient, provenance=Provenance.fake(),
                             date=date, date_noted=date, 
                              name=allergen.name,allergen = allergen,
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
    dx_code = models.ForeignKey(Dx_code)
    status = models.CharField(max_length=20, null=True, db_index=True)
    comment = models.TextField(null=True, blank=True)
    hospital_pl_yn = models.CharField('Hospital-based problem, Y or null',max_length=1, null=True)
    
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
        
        dx_code = Dx_code.objects.order_by('?')[0]
        
        status = ['active',  'deleted','']         
        problem = Problem(patient=patient, mrn = patient.mrn, provenance=Provenance.fake(),
                         date=date, status=random.choice(status), dx_code=dx_code,
                         provider=patient.pcp,natural_key=now)
        if save_on_db: problem.save()
        return problem
            
    
    def document_summary(self):
        return {
            'date':(self.date and self.date.isoformat()) or None,
            'problem':{
                'dx_type':self.dx_code.type,
                'dx_code':self.dx_code.code,
                'dx_name':self.dx_code.name,
                'comment':self.comment
                },
            'status':self.status
            }

    def  __unicode__(self):
        return u"Problem on %s had %s on %s" % (
            self.patient.full_name, self.dx_code, self.date)
        
class Hospital_Problem(BasePatientRecord):
    '''
    Hospital Problem list -- cumulative over time, no current 
    '''
    # date is date noted, id is natural key
    dx_code = models.ForeignKey(Dx_code)
    status = models.CharField(max_length=20, null=True, db_index=True)
    principal_prob_code = models.IntegerField('Principal hospital problem code',null=True)
    principal_prob = models.CharField('Principal hospital problem',max_length=20,null=True, db_index=True)
    present_on_adm_code = models.IntegerField('Present on admission code', null=True)
    present_on_adm = models.CharField('Present on admission',max_length=20,null=True, db_index=True)
    priority_code = models.IntegerField('Priority code',null=True)
    priority = models.CharField('Priority',max_length=20,null=True, db_index=True)
    overview = models.CharField('Overview',max_length=800,null=True)
    
    def document_summary(self):
        return {
            'date':(self.date and self.date.isoformat()) or None,
            'problem':{
                'dx_type':self.dx_code.type,
                'dx_code':self.dx_code.code,
                'dx_name':self.dx_code.name,
                'overview':self.overview,
                'principal_prob':self.principal_prob,
                'present_on_adm':self.present_on_adm,
                'priority':self.priority
                },
            'status':self.status
            }

    def  __unicode__(self):
        return u"Problem %s had %s on %s" % (
            self.patient.full_name, self.dx_code, self.date)
        
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
            actual_date = preg_date + datetime.timedelta(days=random.randrange(14, 289)) # 42 weeks. 7 days could be a miss carriage.
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
        
class SurveyResponse(BasePatientRecord):
    question = models.CharField('Question Name',max_length=80, null=True, blank=True, db_index=False)
    response_float = models.FloatField('response float', null=True, default=0)
    response_string = models.CharField('response string',max_length=30, null=True, blank=True, db_index=False)
    response_choice = models.CharField('response choice', max_length=3,null=True, blank=True,  db_index=False)
    response_boolean = models.BooleanField('response boolean', blank=True, default=False)

    def __str__(self):
        return '%s | %s ' % (self.id, self.survey.id )

    class Meta:
        verbose_name = 'Survey Response'
        ordering = ['date']  

    def  __unicode__(self):
        return u"Survey Response for %s  on %s" % (
            self.mrn,  self.date)

