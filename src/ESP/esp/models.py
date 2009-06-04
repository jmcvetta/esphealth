#-*- coding:utf-8 -*-
'''
                               Core Data Models
                                      for
                                  ESP Health

@author: Ross Lazarus <ross.lazarus@channing.harvard.edu>
@author: Xuanlin Hou <rexua@channing.harvard.edu>
@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''

import string
import time
import datetime
import random
import pdb

from django.db import models, connection, backend
from django.db.models import Q
from django.contrib.auth.models import User 
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import SortedDict 


from ESP.conf.common import EPOCH
from ESP.esp import choices
from ESP.utils import randomizer
from ESP.utils.utils import log
from ESP.utils.utils import str_from_date
from ESP.utils.utils import date_from_str
from ESP.conf.models import Ndc 
from ESP.conf.models import Icd9
from ESP.conf.models import Loinc
from ESP.conf.models import Cpt
from ESP.conf.models import Rule
from ESP.conf.models import NativeCode
from ESP.emr.models import Patient as NewPatient
from ESP.emr.models import Provider as NewProvider
from ESP.localsettings import DATABASE_ENGINE



class EncounterManager(models.Manager):
    def following_vaccination(self, days_after, begin_date=None, end_date=None):

        encounter_meta = Enc.objects.model._meta
        demog_meta = Demog.objects.model._meta
        imm_meta = Immunization.objects.model._meta
        
        # Get PKs from patients, encounters, immunizations
        # We will need them to construct a correct WHERE clause
        ppk =  '%s.%s' % (demog_meta.db_table, demog_meta.pk.name) 
        enc_pk = '%s.%s' % (encounter_meta.db_table, encounter_meta.pk.name) 

        enc_fk = '%s.%s' % (encounter_meta.db_table, 
                            encounter_meta.get_field('EncPatient').attname) 
        imm_fk = '%s.%s' % (imm_meta.db_table, 
                            imm_meta.get_field('ImmPatient').attname)

        patient_in_encounter = '%s=%s' % (ppk, enc_fk) #Patient.id=Enc.EncPatient_id
        patient_in_immunization = '%s=%s' % (ppk, imm_fk) #Patient.id = Imm.ImmPatient_id


        # Get "Full Name" for EncounterDate and ImmunizationDate fields
        enc_date_field = '%s.%s' % (encounter_meta.db_table, 'EncEncounter_Date')
        imm_date_field = '%s.%s' % (imm_meta.db_table, 'ImmDate')


        timestamp = r'%Y%m%d'

        if DATABASE_ENGINE == 'sqlite3':
            def STR_TO_DATE():
                # If you know any better way to get a date from
                # a YYYYMMDD string in sqlite, please let me know. 
                return '''julianday(SUBSTR(%s, 0, 4)||'-'||SUBSTR(%s, 5, 2)||'-'||SUBSTR(%s, 7, 2))'''
            date_cmp_select = '- '.join([STR_TO_DATE(), STR_TO_DATE()])

            # And the absurdity is not alone. Check out this tuple. 
            params = (enc_date_field, enc_date_field, enc_date_field, 
                      imm_date_field, imm_date_field, imm_date_field)


        elif DATABASE_ENGINE == 'mysql':
            # MySQL is a little bit less insane, using STR_TO_DATE funcion
            date_cmp_select = "DATEDIFF(STR_TO_DATE(%s, '%s'), STR_TO_DATE(%s, '%s'))"
            params = (enc_date_field, timestamp, imm_date_field, timestamp)
            
        elif DATABASE_ENGINE in ('postgresql_psycopg2', 'postgresql'):
            date_cmp_select = "date %s - date %s"
            params = (enc_date_field, imm_date_field)

        else:
            raise NotImplementedError, 'Implemented only for PostgreSQL, mySQL and Sqlite'

        
        if DATABASE_ENGINE in ('mysql', 'sqlite3'):
            max_days = ' '.join([date_cmp_select % params, '<=', str(days_after)])
            same_day = (date_cmp_select % params) + ' >= 0'
        elif DATABASE_ENGINE in ('postgresql_psycopg2', 'postgresql'):
            max_days = ' '.join([date_cmp_select % params, "<= interval '%s days'" % str(days_after)])
            same_day = (date_cmp_select % params) + " >= interval '0 days'"
        else:
            raise NotImplementedError, 'Implemented for Postgres, MySQL and sqlite.'


        # This is our minimum WHERE clause
        where_clauses = [patient_in_encounter, patient_in_immunization, 
                         max_days, same_day]


        if begin_date:
            where_clauses.append("%s >= '%s'" % (imm_date_field, begin_date.strftime(timestamp)))
        if end_date:
            where_clauses.append("%s <= '%s'" % (imm_date_field, end_date.strftime(timestamp)))


        return self.extra(
            tables = [demog_meta.db_table, imm_meta.db_table],
            where = where_clauses
            )


           
class Provider(models.Model):
    
    q_fake = Q(provCode__startswith='FAKE')

    # Some methods to deal with mock/fake data
    @staticmethod
    def fakes():
        return Provider.objects.filter(Provider.q_fake)

    @staticmethod
    def delete_fakes():
        Provider.objects.filter(Provider.q_fake).delete()

    @staticmethod
    def make_fakes(how_many):
        for i in xrange(0, how_many):
            Provider.make_mock(save_on_db=True)
            
    @staticmethod
    def make_mock(save_on_db=False):
        p = Provider(
            provCode = 'FAKE-%05d' % random.randrange(1, 100000),
            provLast_Name = randomizer.first_name(),
            provFirst_Name = randomizer.last_name(),
            provMiddle_Initial = random.choice(string.uppercase),
            provTitle = 'Fake Dr.',
            provPrimary_Dept = 'Department of Wonderland',
            provPrimary_Dept_Address_1 = randomizer.address(),
            provPrimary_Dept_Zip = randomizer.zip_code(),
            provTel = randomizer.phone_number()
            )
        
        if save_on_db: p.save()
        return p


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

    def full_name(self):
        return unicode(' '.join([self.provTitle, self.provLast_Name]))


    def is_fake(self):
        return self.provCode.startswith('FAKE')
    


    
        
    



class Demog(models.Model):

    fake_q = Q(DemogPatient_Identifier__startswith='FAKE')

    @staticmethod
    def clear():
        Demog.objects.filter(Demog.fake_q).delete()
            
    @staticmethod
    def make_fakes(how_many, save_on_db=True):
        for i in xrange(how_many):
            Demog.make_mock(save_on_db=save_on_db)

    @staticmethod
    def fakes():
        return Demog.objects.filter(Demog.fake_q)

    @staticmethod
    def delete_fakes():
        Demog.fakes().delete()

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
        
        p = Demog(
            DemogProvider = provider,
            DemogPatient_Identifier = 'FAKE-%s' % identifier,
            DemogMedical_Record_Number = 'FAKE-%s' % identifier,
            DemogLast_Name = randomizer.last_name(),
            DemogFirst_Name = randomizer.first_name(),
            DemogSuffix = '',
            DemogCountry = 'Fakeland',
            DemogCity = city[0],
            DemogState = city[1],
            DemogZip = randomizer.zip_code(),
            DemogAddress1 = address,
            DemogAddress2 = '',
            DemogMiddle_Initial = random.choice(string.uppercase),
            DemogDate_of_Birth = randomizer.date_of_birth(as_string=True),
            DemogGender = randomizer.gender(),
            DemogRace = randomizer.race(),
            DemogAreaCode = phone_number.split('-')[0],
            DemogTel = phone_number[4:],
            DemogExt = '',
            DemogSSN = randomizer.ssn(),
            DemogMaritalStat = randomizer.marital_status(),
            DemogReligion = '',
            DemogAliases = '',
            DemogHome_Language = '',
            DemogMotherMRN = '',
            DemogDeath_Date = '',
            DemogDeath_Indicator = '',
            DemogOccupation = ''
            )
        
        if save_on_db: p.save()
        return p

    @staticmethod
    def random(fake=True):
        '''Returns a random fake user. If fake is False, returns a
        completely random user'''
        objs = Demog.objects
        query = objs.filter(Demog.fake_q) if fake else objs.all()
        return query.order_by('?')[0]
        


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


    def is_fake(self):
        return self.DemogPatient_Identifier.startswith('FAKE')

            

    def  __unicode__(self):
        return u"#%-10s MRN: %-10s %-10s %-10s" % (self.id, self.DemogPatient_Identifier, self.DemogLast_Name, self.DemogFirst_Name)

    def full_name(self):
        return u'%s %s' % (self.DemogFirst_Name, self.DemogLast_Name)
    
    def _get_date_of_birth(self):
        '''
        Returns patient's date of birth as a datetime.datetime instance
        '''
        try:
            return datetime.date(*time.strptime(
                    self.DemogDate_of_Birth, '%Y%m%d')[:3])
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

            if years > 0:
                return str(years) 
            else:
                return '%d Months' % months
        
    age = property(_get_age)

    def has_history_of(self, icd9s, begin_date=None, end_date=None):
        '''
        returns a boolean if the patient has any of the icd9s code 
        in their history of encounters.
        '''
        begin_date = begin_date or self.date_of_birth or EPOCH
        end_date = end_date or datetime.date.today()

        return Enc.objects.filter(EncPatient=self).filter(
            EncEncounter_Date__gte=str_from_date(begin_date),
            EncEncounter_Date__lt=str_from_date(end_date),
            ).filter(
            reported_icd9_list__in=icd9s).count() != 0
        
            

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
    def _get_patient(self):
        return self.RxPatient
    def _get_provider(self):
        return self.RxProvider
    def _get_date(self):
        return date_from_str(self.RxOrderDate)
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
            #n = Ndc.objects.get(ndcLbl__exact=lbl,ndcProd__exact=prd)
            n = Ndc.objects.filter(ndcLbl=lbl,ndcProd=prd)
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
    
    def filter_loincs(self, loinc_nums, **kwargs):
        '''
        Translate LOINC numbers to native codes and lookup
        @param loinc_nums: List of LOINC numbers for which to retrieve lab results
        @type loinc_nums:  [String, String, ...]
        '''
        log.debug('Querying lab results by LOINC')
        log.debug('LOINCs: %s' % loinc_nums)
        native_codes = NativeCode.objects.filter(loinc__in=loinc_nums).values_list('native_code', flat=True)
        log.debug('Native Codes: %s' % native_codes)
        return self.filter(native_code__in=native_codes, **kwargs)

    def following_vaccination(self, days_after, loinc=None, begin_date=None, end_date=None):

        lx_meta = Lx.objects.model._meta
        demog_meta = Demog.objects.model._meta
        imm_meta = Immunization.objects.model._meta
        
        # Get PKs from patients, lab results, immunizations
        # We will need them to construct a correct WHERE clause
        ppk =  '%s.%s' % (demog_meta.db_table, demog_meta.pk.name) 
        lx_pk = '%s.%s' % (lx_meta.db_table, lx_meta.pk.name) 

        lx_fk = '%s.%s' % (lx_meta.db_table, 
                            lx_meta.get_field('LxPatient').attname) 
        imm_fk = '%s.%s' % (imm_meta.db_table, 
                            imm_meta.get_field('ImmPatient').attname)

        patient_in_encounter = '%s=%s' % (ppk, lx_fk) #Patient.id=Enc.EncPatient_id
        patient_in_immunization = '%s=%s' % (ppk, imm_fk) #Patient.id = Imm.ImmPatient_id


        # Get "Full Name" for OrderDate and ImmunizationDate fields
        lx_date_field = '%s.%s' % (lx_meta.db_table, 'LxDate_of_result')
        imm_date_field = '%s.%s' % (imm_meta.db_table, 'ImmDate')


        timestamp = r'%Y%m%d'

        if DATABASE_ENGINE == 'sqlite3':
            def STR_TO_DATE():
                # If you know any better way to get a date from
                # a YYYYMMDD string in sqlite, please let me know. 
                return '''julianday(SUBSTR(%s, 0, 4)||'-'||SUBSTR(%s, 5, 2)||'-'||SUBSTR(%s, 7, 2))'''
            date_cmp_select = '- '.join([STR_TO_DATE(), STR_TO_DATE()])

            # And the absurdity is not alone. Check out this tuple. 
            params = (lx_date_field, lx_date_field, lx_date_field, 
                      imm_date_field, imm_date_field, imm_date_field)


        elif DATABASE_ENGINE == 'mysql':
            # MySQL is a little bit less insane, using STR_TO_DATE funcion
            date_cmp_select = "DATEDIFF(STR_TO_DATE(%s, '%s'), STR_TO_DATE(%s, '%s'))"
            params = (lx_date_field, timestamp, imm_date_field, timestamp)

        elif DATABASE_ENGINE in ('postgresql_psycopg2', 'postgresql'):
            date_cmp_select = "date %s - date %s"
            params = (lx_date_field, imm_date_field)

        else:
            raise NotImplementedError, 'Implemented only for PostgreSQL, mySQL and Sqlite'


        if DATABASE_ENGINE in ('mysql', 'sqlite3'):
            max_days = ' '.join([date_cmp_select % params, '<=', str(days_after)])
            same_day = (date_cmp_select % params) + ' >= 0'
        elif DATABASE_ENGINE in ('postgresql_psycopg2', 'postgresql'):
            max_days = ' '.join([date_cmp_select % params, "<= interval '%s days'" % str(days_after)])
            same_day = (date_cmp_select % params) + " >= interval '0 days'"
        else:
            raise NotImplementedError, 'Implemented for Postgres, MySQL and sqlite.'
            


        # This is our minimum WHERE clause
        where_clauses = [patient_in_encounter, patient_in_immunization, 
                         max_days, same_day]


        if begin_date:
            where_clauses.append("%s >= '%s'" % (imm_date_field, begin_date.strftime(timestamp)))
        if end_date:
            where_clauses.append("%s <= '%s'" % (
                    imm_date_field, end_date.strftime(timestamp)))
            

        # To find an specific lab result.    
        qs = self.filter_loincs([loinc]) if loinc else self

        return qs.extra(
            tables = [demog_meta.db_table, imm_meta.db_table],
            where = where_clauses
            )
    

class Lx(models.Model):
    # rename: patient
    LxPatient = models.ForeignKey(Demog) 
    # rename: provider
    LxOrdering_Provider = models.ForeignKey(Provider, blank=True, null=True) 
    # rename: mrn
    LxMedical_Record_Number = models.CharField('Medical Record Number', max_length=20, blank=True, null=True, db_index=True)
    # rename: order_num
    LxOrder_Id_Num = models.CharField('Order Id #', max_length=20, blank=True, null=True)
    native_code = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    native_name = models.CharField(max_length=500, blank=True, null=True)
    # delete
    LxTest_Code_CPT = models.CharField('Test Code (CPT)', max_length=20, blank=True, null=True, db_index=True)
    # delete
    LxTest_Code_CPT_mod = models.CharField('Test Code (CPT) Modifier', max_length=20, blank=True, null=True)
    # rename: order_date
    LxOrderDate = models.CharField('Order Date', max_length=20, blank=True, null=True)
    # Is this garbage?
    LxOrderType = models.CharField('Order Type', max_length=10, blank=True, null=True)   
    # rename: updated
    lastUpDate = models.DateTimeField('Last Updated date', auto_now=True, db_index=True)
    # rename: created
    createdDate = models.DateTimeField('Date Created', auto_now_add=True)
    # rename: date
    LxDate_of_result = models.CharField('Date of result', max_length=20, blank=True, null=True, db_index=True)  
    # is this garbage?
    LxHVMA_Internal_Accession_number = models.CharField('HVMA Internal Accession number', max_length=50, blank=True, null=True)
    # delete
    LxComponent = models.CharField('Component', max_length=20, blank=True, null=True, db_index=True)
    # delete
    LxComponentName = models.CharField('Component Name', max_length=200, blank=True, null=True,  db_index=True)
    # rename: abnormal_flag
    LxNormalAbnormal_Flag = models.CharField('Normal/Abnormal Flag', max_length=20, blank=True, null=True, db_index=True)
    # delete
    LxReference_Low = models.CharField('Reference Low', max_length=100, blank=True, null=True, db_index=True)
    # delete
    LxReference_High = models.CharField('Reference High', max_length=100, blank=True, null=True, db_index=True)
    ref_low_string = models.CharField('Reference Low (string)', max_length=100, blank=True, null=True, db_index=True)
    ref_high_string = models.CharField('Reference High (string)', max_length=100, blank=True, null=True, db_index=True)
    ref_low_float = models.FloatField('Reference Low (number)', blank=True, null=True, db_index=True)
    ref_high_float = models.FloatField('Reference High (number)', blank=True, null=True, db_index=True)
    # rename: ref_unit
    LxReference_Unit = models.CharField('Reference Unit', max_length=100, blank=True, null=True)
    # rename: status
    LxTest_status = models.CharField('Test status', max_length=50, blank=True, null=True)
    # delete
    LxLoinc = models.CharField('LOINC code', max_length=20, blank=True, null=True, db_index=True)
    result_float = models.FloatField(blank=True, null=True, db_index=True)
    result_string = models.CharField(max_length=1000, blank=True, null=True, db_index=True)
    # delete
    LxTest_results = models.CharField('Test results', max_length=1000, blank=True, null=True, db_index=True)
    # rename: impression
    LxImpression = models.TextField('Impression for Imaging only', max_length=1000, blank=True, null=True)
    # rename: comment
    LxComment = models.TextField('Comments',  blank=True,  null=True, )
    def _get_patient(self):
        return self.LxPatient
    def _get_provider(self):
        return self.LxOrdering_Provider
    def _get_date(self):
        return date_from_str(self.LxOrderDate)
    
    def _get_result_date(self):
        return date_from_str(self.LxDate_of_result)

    def _get_loinc(self):
        try:
            return NativeToLoincMap.objects.get(native_code=self.native_code, 
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

    
    patient = property(_get_patient)
    provider = property(_get_provider)
    date = property(_get_date)
    result_date = property(_get_result_date)
    loinc = property(_get_loinc, _set_loinc)
    
    # Use custom manager
    objects = LxManager()

    
    fake_q = Q(LxPatient__DemogPatient_Identifier__startswith='FAKE')
    
    @staticmethod
    def delete_fakes():
        Lx.fakes().delete()

    @staticmethod
    def fakes():
        return Lx.objects.filter(Lx.fake_q)

    @staticmethod
    def make_mock(loinc, patient, when=None, save_on_db=True):
        
        when = when or datetime.date.today()

        order_date = when - datetime.timedelta(
            days=random.randrange(1, 10))

        # Make sure the patient was alive for the order...
        order_date = max(order_date, patient.date_of_birth)

        lx = Lx(
            LxPatient=patient,
            LxOrderDate = str_from_date(order_date),
            LxDate_of_result=str_from_date(when)
            )
        if save_on_db: lx.save()

        return lx



        
        
        

    
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
            c = Cpt.objects.get(cptCode__exact=self.LxTest_Code_CPT)
            s = '%s=%s' % (self.LxTest_Code_CPT,c.cptLong)
        except:
            if self.LxTest_Code_CPT:
                s = "CPT code=%s: not found" % self.LxTest_Code_CPT
            else:
                s=''
        return unicode(s)

    def previous(self):
        try:
            return Lx.objects.filter(
                LxPatient=self.LxPatient,
                native_code=self.native_code
                ).exclude(
                LxDate_of_result__gte=self.LxDate_of_result
                ).latest('LxDate_of_result')
        except:
            return None


    def last_known_value(self, loinc, since=None):
        
        since = since or datetime.date.today()
        date = min(since, self.result_date)

        code, patient = self.native_code, self.LxPatient
      
        try:
            last = Lx.objects.filter(native_code=code, LxPatient=patient).exclude(
                pk=self.pk, LxDate_of_result__gte=self.LxDate_of_result
                ).latest('LxDate_of_result')
                                     
            return last.result_float or last.result_string
        except:
            return None


    def compared_to_lkv(self, comparator, x):
        '''
        Builds and evals an inequation between the value of
        the lab result and the Last Known Value (LKV).
        Uses comparator and x as arguments.  Comparator can only be 
        '>' or '<', while x can be any kind of string that can be 
        part of a mathematical equation.
        '''


        lkv = float(previous.LxTest_Results)
        current = float(self.LxTest_Results)
        
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
        #return u'#%-10s %-12s LOINC: %-7s Ref High: %-5s Result: %s' % (self.pk, self.date, self.LxLoinc, self.LxReference_High, self.LxTest_results)
        return u'Lx #%s' % self.pk
    

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

    fake_q = Q(EncPatient__DemogPatient_Identifier__startswith='FAKE')

    @staticmethod
    def delete_fakes():
        Enc.objects.filter(Enc.fake_q).delete()

    @staticmethod
    def fakes():
        return Enc.objects.filter(Enc.fake_q)

    @staticmethod
    def make_fakes(how_many, **kw):
        now = datetime.datetime.now()
        start = kw.get('start_date', None)
        interval = kw.get('interval', None)
        
        for patient in Demog.fakes():
            when = start or patient.date_of_birth
            for i in xrange(0, how_many):
                next_encounter_interval = interval or random.randrange(0, 180)
                when += datetime.timedelta(days=next_encounter_interval)
                if when < now: 
                    Enc.make_mock(patient, save_on_db=True, when=when)
            
    @staticmethod
    def make_mock(patient, save_on_db=False, **kw):
        
        when = kw.get('when', datetime.datetime.now())
        e = Enc(
            EncPatient=patient,
            EncEncounter_ID = 'FAKE-%s' % randomizer.string(length=10),
            EncEncounter_Provider=patient.DemogProvider,
            EncMedical_Record_Number = patient.DemogMedical_Record_Number,
            EncEvent_Type = 'FAKE',
            EncEncounter_Status = 'FAKE',
            EncEncounter_Date = when.strftime('%Y%m%d'),
            EncEncounter_ClosedDate = when.strftime('%Y%m%d'),
            EncEDC = '', 
            EncPregnancy_Status = '',
            EncEncounter_SiteName = '',
            EncEncounter_Site = '',
            EncCPT_codes = '',
            EncTemperature = '',
            EncICD9_Codes = '',
            EncICD9_Qualifier = '',
            EncWeight = '',
            EncHeight = '',
            EncBPSys = '',
            EncBPDias = '',
            EncO2stat = '',
            EncPeakFlow = '',
            )
        
        if save_on_db: e.save()
        return e





    objects = EncounterManager()
    EncPatient = models.ForeignKey(Demog) 
    EncMedical_Record_Number = models.CharField('Medical Record Number',max_length=20,blank=True,null=True,db_index=True)
    EncEncounter_ID = models.CharField('Encounter ID',max_length=20,blank=True,null=True)
    EncEncounter_Date = models.CharField('Encounter Date', max_length=20, blank=True, null=True, db_index=True)
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
    reported_icd9_list = models.ManyToManyField(Icd9)



    lastUpDate = models.DateTimeField('Last Updated date',auto_now=True,db_index=True)
    createdDate = models.DateTimeField('Date Created', auto_now_add=True)
    def _get_patient(self):
        return self.EncPatient
    def _get_provider(self):
        return self.EncEncounter_Provider
    def _get_date(self):
        return date_from_str(self.EncEncounter_Date)
    patient = property(_get_patient)
    provider = property(_get_provider)
    date = property(_get_date)
    
    def _get_enc_date(self):
        '''
        Returns a datetime.date object
        '''
        return date_from_str(self.EncEncounter_Date)
    encounter_date = property(_get_enc_date)
    
    def geticd9s(self):
        """translate icd9s in comma separated value
        """
        ##icd9_codes are separeted by ' '
        ilist = self.EncICD9_Codes.split(' ')
        if len(ilist) > 0:
            s=[]
            for i in ilist:
                ilong = Icd9.objects.filter(code__exact=i)
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

    def is_fake(self):
        return self.EncEvent_Type == 'FAKE'

    def is_reoccurrence(self, month_period=12):
        '''
        returns a boolean indicating if this encounters shows any icd9
        code that has been registered for this patient in last
        month_period time.
        '''
        
        earliest = self.date-datetime.timedelta(days=30*month_period)
        
        return Enc.objects.filter(
            EncEncounter_Date__lt=self.EncEncounter_Date).filter(
            EncEncounter_Date__gte=str_from_date(earliest)).filter(
                EncPatient=self.EncPatient).filter(
                reported_icd9_list__in=self.reported_icd9_list.all()).count() > 0
                
                    
                    



###################################
class Icd9Fact(models.Model):
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

    fake_q = Q(ImmName='FAKE')


    @staticmethod
    def vaers_candidates(patient, event, days_prior):
        '''Given an encounter that is considered an adverse event,
        returns a queryset that represents the possible immunizations
        that have caused it'''
        
        earliest_date = event.date - datetime.timedelta(days=days_prior)
        
        return Immunization.objects.filter(
            ImmPatient=patient,
            ImmDate__gte=earliest_date.strftime('%Y%m%d'),
            ImmDate__lte=event.date.strftime('%Y%m%d')
            )

    @staticmethod
    def delete_fakes():
        Immunization.objects.filter(Immunization.fake_q).delete()
    
    @staticmethod
    def fakes():
        return Immunization.objects.filter(Immunization.fake_q)

    @staticmethod
    def make_mock(vaccine, patient, date):
        fmt = '%Y%m%d'
        return Immunization.objects.create(
            ImmPatient=patient, ImmRecId='FAKE-%s' % patient.id,
            ImmType=vaccine.code, ImmDose='3.1415 pi',
            ImmDate=date.strftime(fmt), ImmVisDate = date.strftime(fmt),
            ImmName='FAKE', ImmManuf='FAKE', ImmLot='FAKE'
            )

    def is_fake(self):
        return self.ImmName == 'FAKE'

    def _get_date(self):
        return date_from_str(self.ImmDate)

    def vaccine_type(self):
        try:
            vaccine = Vaccine.objects.get(code=self.ImmType)
            return vaccine.name
        except:
            return 'Unknown Vaccine'

    date = property(_get_date)

    def  __unicode__(self):
        return u"Patient with Immunization Record %s received %s on %s" % (
            self.ImmRecId, self.vaccine_type(), self.date)




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

    @staticmethod
    def random():
        return Vaccine.objects.exclude(short_name='UNK').order_by('?')[0]

    code = models.IntegerField(unique=True)
    short_name = models.CharField(max_length=60)
    name = models.CharField(max_length=300)

    def __unicode__(self):
        return '%s (%s)'% (self.short_name, self.name)


        
    

class ImmunizationManufacturer(models.Model):
    code = models.CharField(max_length=3)
    full_name = models.CharField(max_length=200)
    active = models.BooleanField(default=True)
    use_instead = models.ForeignKey('self', null=True)

    def __unicode__(self):
        return self.full_name
                         
    





                                                            

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
    

class Allergy(models.Model):
    AllPatient = models.ForeignKey(Demog)
    AllMRN = models.CharField('Medical Record Number',max_length=25,blank=True,null=True,db_index=True)
    AllPrbID = models.CharField('Problem Id #',max_length=25,blank=True,null=True)
    AllDateNoted = models.CharField('Date Noted',max_length=20,blank=True,null=True)
    AllCode = models.CharField('Allergy ID (Code)',max_length=200,blank=True,null=True)
    AllName = models.CharField('Allergy Name',max_length=255,blank=True,null=True)
    AllStatus = models.CharField('Allergy status',max_length=50,blank=True,null=True)
    AllDesc = models.TextField('Allergy Description',max_length=1000,blank=True,null=True)
    AllDateEntered = models.CharField('Date Entered',max_length=20,blank=True,null=True)
    lastUpDate = models.DateTimeField('Last Updated date',auto_now=True,db_index=True)
    createdDate = models.DateTimeField('Date Created', auto_now_add=True)

    def  __unicode__(self):
        return u"%s %s %s" % (self.AllPatient.DemogPatient_Identifier,self.AllMRN,self.AllPrbID)


class Problem(models.Model):
    '''
    WTF exactly is a "Problem"?  How is it different than an Encounter?
    '''
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

 
class ConditionIcd9(models.Model):
    CondiRule = models.ForeignKey(Rule)
    CondiICD9 = models.TextField('ICD-9 Codes',blank=True,null=True)
    CondiDefine = models.NullBooleanField('Icd9 used in definition or not', blank=True,null=True)
    CondiSend = models.NullBooleanField('Icd9 needs to be sent or not', blank=True,null=True)

    def  __unicode__(self):
        return u'%s %s' % (self.CondiRule,self.CondiICD9)


class ConditionLOINC(models.Model):
    CondiRule = models.ForeignKey(Rule)
    CondiLOINC = models.TextField('LOINC Codes',blank=True,null=True)
    CondiDefine = models.NullBooleanField('Loinc used in definition or not', blank=True,null=True)
    CondiSend = models.NullBooleanField('Loinc needs to be sent or not', blank=True,null=True)
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
    CondiDefine = models.NullBooleanField('Ndc used in definition or not', blank=True,null=True)
    CondiSend = models.NullBooleanField('Ndc need to be send or not', blank=True,null=True)

    def  __unicode__(self):
        return u'%s %s' % (self.CondiRule,self.CondiNdc)
        
 
class ConditionDrugName(models.Model):
    CondiRule = models.ForeignKey(Rule)
    CondiDrugName = models.TextField('Drug Name',blank=True,null=True)
    CondiDrugRoute = models.TextField('Drug Route',blank=True,null=True)
    CondiDefine = models.NullBooleanField('Used in case definition or not', blank=True,null=True)
    CondiSend = models.NullBooleanField('Must be sent or not', blank=True,null=True)

    def  __unicode__(self):
        return u'%s %s %s' % (self.CondiRule,self.CondiDrugName, self.CondiDrugRoute)


        
class DataFile(models.Model):
    filename = models.CharField('Raw data file name',max_length=50,blank=True,null=True)
    numrecords = models.CharField('Number of Records in a file',max_length=50,blank=True,null=True) 
    datedownloaded = models.DateTimeField('Date loaded',editable=False,auto_now_add=True)

 
    def  __unicode__(self):
        return u'%s %s' % (self.filename,self.datedownloaded)



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


#
# Old, deprecated Case model -- here for script testing
#
#class Case(models.Model):
#    """casePID can't be a foreign key or we get complaints that the pointed to model doesn't
#    yet exist
#    """
#    caseDemog = models.ForeignKey(Demog,verbose_name="Patient ID",db_index=True)
#    caseProvider = models.ForeignKey(Provider,verbose_name="Provider ID",blank=True, null=True)
#    caseWorkflow = models.CharField('Workflow State', max_length=20,choices=choices.WORKFLOW_STATES, blank=True,db_index=True )
#    caseComments = models.TextField('Comments', blank=True, null=True)
#    caseLastUpDate = models.DateTimeField('Last Updated date',auto_now=True)
#    casecreatedDate = models.DateTimeField('Date Created', auto_now_add=True)
#    caseSendDate = models.DateTimeField('Date sent', null=True)
#    caseRule = models.ForeignKey(Rule,verbose_name="Case Definition ID")
#    caseQueryID = models.CharField('External Query which generated this case',max_length=20, blank=True, null=True)
#    caseMsgFormat = models.CharField('Case Message Format', max_length=20, choices=choices.FORMAT_TYPES, blank=True, null=True)
#    caseMsgDest = models.CharField('Destination for formatted messages', max_length=120, choices=choices.DEST_TYPES, blank=True,null=True)
#    caseEncID = models.TextField('A list of ESP_ENC IDs',max_length=500,  blank=True, null=True)
#    caseLxID = models.TextField('A list of ESP_Lx IDs',max_length=500,  blank=True, null=True)
#    caseRxID = models.TextField('A list of ESP_Rx IDs',max_length=500,  blank=True, null=True)
#    caseICD9 = models.TextField('A list of related ICD9',max_length=500,  blank=True, null=True)
#    caseImmID = models.TextField('A list of Immunizations same date',max_length=500, blank=True, null=True)


#
# This depends on old Case class above, and will probably need to be both
# relocated (to nodis?) and refactored
#
#class Hl7OutputFile(models.Model):
#    '''
#    An HL7 file that has been sent to Dept Public Health
#    '''
#    filename = models.CharField('hl7 file name',max_length=100,blank=True,null=True)
#    case = models.ForeignKey(Case,verbose_name="Case ID",db_index=True)
#    demogMRN = models.CharField('Medical Record Number',max_length=50,db_index=True,blank=True,null=True)
#    hl7encID = models.TextField('A list of ESP_ENC IDs in hl7', max_length=500,  blank=True, null=True)
#    hl7lxID = models.TextField('A list of ESP_Lx IDs in hl7', max_length=500,  blank=True, null=True)
#    hl7rxID = models.TextField('A list of ESP_Rx IDs in hl7', max_length=500,  blank=True, null=True)
#    hl7ICD9 = models.TextField('A list of related ICD9 in hl7', max_length=500,  blank=True, null=True)
#    hl7reportlxID=models.TextField('A list of report Lx IDs in hl7', max_length=500,  blank=True, null=True)
#    hl7specdate = models.TextField('A list of order date of report Lx in hl7', max_length=500,  blank=True, null=True)
#    hl7trmtDT = models.TextField('the order date of minium Rx', max_length=500,  blank=True, null=True)
#    hl7comment = models.TextField('note in NTE segment',  max_length=500,  blank=True, null=True)
#    lastUpDate = models.DateTimeField('Last Updated date',auto_now=True,db_index=True)
#    createdDate = models.DateTimeField('Date Created', auto_now_add=True)
#          
#    def  __unicode__(self):
#        return u'%s %s' % (self.filename,self.datedownloaded)


class Hl7InputFile(models.Model):
    '''
    An HL7 file containing EMR data.  Records when we tried to import the
    file, and the status of our attempt.
    '''
    filename = models.CharField(max_length=255, blank=False, unique=True, db_index=True)
    timestamp = models.DateTimeField(blank=False)
    status = models.CharField(max_length=1, choices=choices.HL7_INPUT_FILE_STATUS, blank=False, db_index=True)
    message = models.TextField('Status Message', blank=True, null=True)


class Case(models.Model):
    """casePID can't be a foreign key or we get complaints that the pointed to model doesn't
    yet exist
    """
    #caseDemog = models.ForeignKey(Demog, verbose_name="Patient ID",db_index=True)
    caseDemog = models.ForeignKey(NewPatient, related_name='oldcase_set', verbose_name="Patient ID",db_index=True)
    caseProvider = models.ForeignKey(NewProvider, related_name='oldcase_set', verbose_name="Provider ID",blank=True, null=True)
    caseRule = models.ForeignKey(Rule,verbose_name="Case Definition ID") # Condition
    # Date roughly indicates when condition was first detected
    date = models.DateField(blank=False)
    #caseWorkflow = models.CharField('Workflow State', max_length=20,choices=choices.WORKFLOW_STATES, blank=True,db_index=True )
    caseLastUpDate = models.DateTimeField('Last Updated date',auto_now=True)
    casecreatedDate = models.DateTimeField('Date Created', auto_now_add=True)
    caseSendDate = models.DateTimeField('Date sent', null=True)
    # Garbage?
    caseQueryID = models.CharField('External Query which generated this case',max_length=20, blank=True, null=True)
    caseMsgFormat = models.CharField('Case Message Format', max_length=20, choices=choices.FORMAT_TYPES, blank=True, null=True)
    caseMsgDest = models.CharField('Destination for formatted messages', max_length=120, choices=choices.DEST_TYPES, blank=True,null=True)
    # Reporting
    caseEncID = models.TextField('A list of ESP_ENC IDs',max_length=500,  blank=True, null=True)
    caseLxID = models.TextField('A list of ESP_Lx IDs',max_length=500,  blank=True, null=True)
    caseRxID = models.TextField('A list of ESP_Rx IDs',max_length=500,  blank=True, null=True)
    caseICD9 = models.TextField('A list of related ICD9',max_length=500,  blank=True, null=True)
    caseImmID = models.TextField('A list of Immunizations same date',max_length=500, blank=True, null=True)
    #
    caseComments = models.TextField('Comments', blank=True, null=True)
    def _get_patient(self):
        return self.caseDemog
    def _set_patient(self, value):
        self.caseDemog = value
    def _get_provider(self):
        return self.caseProvider
    def _set_provider(self, value):
        self.caseProvider = value
    def _get_condition(self):
        return self.caseRule
    def _set_condition(self, value):
        self.caseRule = value
    def _get_encounters(self):
        if self.caseEncID:
            return Enc.objects.filter(id__in=self.caseEncID)
        else:
            return Enc.objects.none()
    def _set_encounters(self, value):
        # value is list of Enc objects
        self.caseEncID = ' '.join([str(encounter.id) for encounter in value])
    def _get_labs(self):
        if self.caseLxID:
            return Lx.objects.filter(id__in=self.caseLxID)
        else:
            return Lx.objects.none()
    def _set_labs(self, value):
        self.caseLxID = ' '.join([str(lab.id) for lab in value])
    def _get_meds(self):
        if self.caseRxID:
            return Rx.objects.filter(id__in=self.caseRxID)
        else:
            return Rx.objects.none()
    def _set_meds(self, value):
        self.caseRxID = ' '.join([str(rx.id) for rx in value])
    patient = property(_get_patient, _set_patient)
    provider = property(_get_provider, _set_provider)
    condition = property(_get_condition, _set_condition)
    rep_encounters = property(_get_encounters, _set_encounters)
    rep_labs = property(_get_labs, _set_labs)
    rep_meds = property(_get_meds, _set_meds)
    
    class Meta:
        permissions = [
            ('view_phi', 'Can view protected health information'),
            ]
    
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
        #p = self.showPatient()# self.pID
        #s = u'Patient=%s RuleID=%s MsgFormat=%s Comments=%s' % (p,self.caseRule.id, self.caseMsgFormat,self.caseComments)
        s = '#%s (%s)' % (self.pk, self.caseDemog)
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
        othercases = Case.objects.filter(caseDemog__id__exact=self.caseDemog.id, caseRule__id__exact=self.caseRule.id, id__lt=self.id)
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
