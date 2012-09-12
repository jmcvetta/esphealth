'''
                                  ESP Health
                            EMR ETL Infrastructure
                         EpicCare Extract File Writer


@author: Raphael Lullis <raphael.lullis@channing.harvard.edu>
@organization: Channing Laboratory - http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''


EPIC_ENCODING = 'iso-8859-15'
ROW_LOG_COUNT = 10000  # Log progress every N rows.  'None' to disable.


import csv
import sys
import os
import socket
import datetime
import optparse
from optparse import make_option
import re
import pprint
import shutil
import codecs
import string
from decimal import Decimal
import random
from psycopg2 import Error as Psycopg2Error

from django.db import transaction

from ESP.emr.management.commands.common import LoaderCommand
from dateutil.relativedelta import relativedelta

from ESP.utils.utils import str_from_date
from ESP.settings import DATA_DIR, POPULATION_SIZE, MIN_ENCOUNTERS_PER_PATIENT ,ENCOUNTERS_PER_PATIENT ,MAXICD9 ,ICD9_CODE_PCT 
from ESP.settings import MIN_LAB_TESTS_PER_PATIENT ,LAB_TESTS_PER_PATIENT ,MIN_LAB_ORDERS_PER_PATIENT ,LAB_ORDERS_PER_PATIENT ,MIN_MEDS_PER_PATIENT ,MEDS_PER_PATIENT 
from ESP.settings import IMMUNIZATION_PCT, IMMUNIZATIONS_PER_PATIENT , MAX_PREGNANCIES ,CURRENTLY_PREG_PCT ,MAX_ALLERGIES ,MAX_PROBLEMS ,MAX_SOCIALHISTORY 
from ESP.settings import DATE_FORMAT
from ESP.utils.utils import log
from ESP.utils.utils import date_from_str, Profiler
from ESP.static.models import Icd9, Allergen, Loinc, FakeICD9s
from ESP.emr.models import Provenance
from ESP.emr.models import EtlError
from ESP.emr.models import Provider,Patient,LabResult, LabOrder
from ESP.emr.models import Encounter,Prescription, Pregnancy
from ESP.emr.models import SocialHistory, Problem, Allergy,Immunization
from ESP.vaers.fake import ImmunizationHistory, check_for_reactions
from ESP.emr.management.commands.load_epic import LoadException, UPDATED_BY


# below are not used
CHLAMYDIA_LX_PCT = 20
CHLAMYDIA_INFECTION_PCT = 15
 
class EpicDialect(csv.Dialect):
    """Describe the usual properties of EpicCare extract files."""
    delimiter = '^'
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = '\r\n'
    quoting = csv.QUOTE_MINIMAL
csv.register_dialect("epic", EpicDialect)
# Some Epic comments are _long_, so we have to increase default csv module 
# field limit size, lest it barf out for the whole file when it hits a single 
# too-long comment.
csv.field_size_limit(1000000000) # <-- arbitrary big number


class DataFakerException(BaseException):
    '''
    Raised when there is a problem loading data into db
    '''


class EpicWriter(object):

    @classmethod
    def filename(cls, file_date):
        return cls.FILE_TEMPLATE_NAME % file_date.strftime('%m%d%Y')

    def __init__(self, date=None):
        d = date or datetime.date.today()
        file_path = os.path.join(DATA_DIR, 'fake', self.__class__.filename(d))
        self.writer = csv.DictWriter(open(file_path, 'a'),
                                     self.__class__.fields, dialect='epic')


    def write_row(self, record):
        raise NotImplementedError

class ProviderWriter(EpicWriter):

    FILE_TEMPLATE_NAME = 'epicpro.esp.%s'
    
    fields = [
        'natural_key',
        'last_name',
        'first_name',
        'middle_name',
        'title',
        'dept_natural_key',
        'dept',
        'dept_address_1',
        'dept_address_2',
        'dept_city',
        'dept_state',
        'dept_zip',
        'area_code',
        'telephone',
        'center_id',
        ]
    
    def write_row(self, provider):
        row = {}

        row['natural_key'] = provider.natural_key
        row['last_name'] = provider.last_name
        row['first_name'] = provider.first_name
        row['middle_name'] = provider.middle_name
        row['title'] = provider.title
        row['dept_natural_key'] = provider.dept_natural_key
        row['dept'] = provider.dept
        row['dept_address_1'] = provider.dept_address_1
        row['dept_address_2'] = provider.dept_address_2
        row['dept_city'] = provider.dept_city
        row['dept_state'] = provider.dept_state
        row['dept_zip'] = provider.dept_zip
        row['area_code'] = provider.area_code
        row['telephone'] = provider.telephone
        row['center_id'] = provider.center_id

        self.writer.writerow(row)


class PatientWriter(EpicWriter):

    FILE_TEMPLATE_NAME = 'epicmem.esp.%s'
    
    fields = [
        'natural_key',
        'mrn',
        'last_name',
        'first_name',
        'middle_name',
        'address1',
        'address2',
        'city',
        'state',
        'zip',
        'country',
        'areacode',
        'tel',
        'tel_ext',
        'date_of_birth',
        'gender',
        'race',
        'home_language',
        'ssn',
        'pcp_id',
        'marital_stat',
        'religion',
        'aliases',
        'mother_mrn',
        'date_of_death',
        'center_id',
        'ethnicity',
        ]
    
    def write_row(self, patient):
        row = {}

        row['natural_key'] = patient.natural_key
        row['mrn'] = patient.mrn
        row['last_name'] = patient.last_name
        row['first_name'] = patient.first_name
        row['middle_name'] = patient.middle_name
        if patient.pcp:
            row['pcp_id'] = patient.pcp.natural_key
        else:
            row['pcp_id'] = None
        row['address1'] = patient.address1
        row['address2'] = patient.address2
        row['city'] = patient.city
        row['state'] = patient.state
        row['zip'] = patient.zip
        row['country'] = patient.country
        row['areacode'] = patient.areacode
        row['tel'] = patient.tel
        row['tel_ext'] = patient.tel_ext
        if patient.date_of_birth:
            row['date_of_birth'] = str_from_date(patient.date_of_birth) or ''
        if patient.date_of_death:
            row['date_of_death'] = str_from_date(patient.date_of_death) or ''
        row['gender'] = patient.gender
        row['race'] = patient.race
        row['home_language'] = patient.home_language
        row['ssn'] = patient.ssn
        row['marital_stat'] = patient.marital_stat
        row['religion'] = patient.religion
        row['aliases'] = patient.aliases
        row['mother_mrn'] = patient.mother_mrn
        row['center_id'] = patient.center_id
        row['ethnicity'] = patient.ethnicity 

        self.writer.writerow(row)   


class LabResultWriter(EpicWriter):

    FILE_TEMPLATE_NAME = 'epicres.esp.%s'
    
    fields = [
        'patient_id',           # 1
        'mrn',                  # 2
        'order_natural_key',    # 3
        'order_date',           # 4
        'result_date',          # 5
        'provider_id',          # 6
        'order_type',           # 7
        'cpt',                  # 8
        'component',            # 9
        'component_name',       # 10
        'result_string',        # 11
        'normal_flag',          # 12
        'ref_low',              # 13
        'ref_high',             # 14
        'unit',                 # 15
        'status',               # 16
        'note',                 # 17
        'specimen_num',         # 18
        'impression',           # 19
        'specimen_source',      # 20
        'collection_date',      # 21
        'procedure_name',        #22
        'natural_key'           #23
        ]


    def write_row(self, lx):
        self.writer.writerow({
                'patient_id':lx.patient.natural_key,
                'mrn': lx.mrn,
                'order_natural_key': lx.order_natural_key,
                'order_date': str_from_date(lx.date),
                'result_date': str_from_date(lx.result_date),
                'provider_id': lx.provider.natural_key,
                'order_type':' ',
                'cpt': lx.native_code,
                'component': lx.native_code.strip(),
                'component_name': lx.native_name,
                'result_string': lx.result_string,
                'normal_flag' : lx.abnormal_flag,
                'ref_low': lx.ref_low_float,
                'ref_high': lx.ref_high_float,
                'unit': lx.ref_unit,
                'status' : lx.status,
                'note' : lx.comment,
                'specimen_num' : lx.specimen_num,
                'impression' : lx.impression,
                'specimen_source' : lx.specimen_source,
                'collection_date' : str_from_date(lx.collection_date),
                'procedure_name' : lx.procedure_name,
                'natural_key'   : lx.natural_key
                })
        

class LabOrderWriter(EpicWriter):    

    FILE_TEMPLATE_NAME = 'epicord.esp.%s'

    fields = [
        'patient_id',
        'mrn',
        'natural_key',
        'procedure_code',
        'procedure_modifier',
        'specimen_id',
        'ordering_date',
        'order_type',
        'provider_id',
        'procedure_name',
        'specimen_source'
        ]
    
    def write_row(self, lab_order):
        self.writer.writerow({
            'patient_id': lab_order.patient.natural_key,
            'mrn':lab_order.mrn,
            'natural_key': lab_order.natural_key,
            'procedure_code': lab_order.procedure_code,
            'procedure_modifier': lab_order.procedure_modifier,
            'specimen_id': lab_order.specimen_id,
            'ordering_date': str_from_date(lab_order.date),
            'order_type': str(lab_order.order_type),
            'provider_id': lab_order.provider.natural_key,
            'procedure_name': lab_order.procedure_name,
            'specimen_source': lab_order.specimen_source
            })


class EncounterWriter(EpicWriter):

    FILE_TEMPLATE_NAME = 'epicvis.esp.%s'
    
    feet_regex = re.compile('(?P<feet>\d)\' *(?P<inches>\d{1,2})')
    
    # Please see Caching Note on EpicWriter.
    __icd9_cache = set() # {code: icd9_obj}
    
    fields = [
        'patient_id',
        'mrn',
        'natural_key',
        'encounter_date',
        'is_closed',
        'date_closed',
        'provider_id',
        'site_natural_key',
        'site_name',
        'event_type',
        'edd',
        'temp',
        'cpt',
        'weight',
        'height',
        'bp_systolic',
        'bp_diastolic',
        'o2_stat',
        'peak_flow',
        'icd9s',
        'bmi'
        ]


    def write_row(self, encounter,icd9_codes, **kw):


        self.writer.writerow({
                'patient_id':encounter.patient.natural_key,
                'mrn':encounter.mrn,
                'natural_key': encounter.natural_key,
                'encounter_date':str_from_date(encounter.date),
                'is_closed': 'YES',
                'date_closed':str_from_date(encounter.date_closed) or '',
                'provider_id':encounter.provider.natural_key,
                'site_natural_key':encounter.site_natural_key,
                'site_name':encounter.site_name,
                'event_type':encounter.raw_encounter_type,
                'edd':str_from_date(encounter.edd) or '',
                'temp':str(encounter.temperature or '') ,
                'cpt': '',
                'weight': encounter.raw_weight,
                'height': encounter.raw_height,
                'bp_systolic':str(encounter.bp_systolic or ''),
                'bp_diastolic':str(encounter.bp_diastolic or ''),
                'o2_stat':str(encounter.o2_stat or ''),
                'peak_flow':str(encounter.peak_flow or ''),
                # no need to add the icd9 text
                'icd9s': ';'.join(icd9_codes ),
                'bmi':str(encounter.bmi or '')
                })
  

class PrescriptionWriter(EpicWriter):

    FILE_TEMPLATE_NAME = 'epicmed.esp.%s'

    fields = [
        'patient_id',
        'mrn',
        'order_natural_key',
        'provider_id',
        'order_date',
        'status',
        'directions',
        'ndc',
        'drug_desc',
        'quantity',
        'refills',
        'start_date',
        'end_date',
        'route',
        'dose',
    ]

    def write_row(self, prescription, **kw):
        self.writer.writerow({
                'patient_id':prescription.patient.natural_key,
                'mrn': prescription.patient.mrn,
                'order_natural_key':prescription.order_natural_key,
                'order_date': str_from_date(prescription.date),
                'status': prescription.status,
                'directions' : prescription.directions,
                'drug_desc': prescription.name,
                'ndc': prescription.code,
                'quantity': str(prescription.quantity or ''),
                'refills': prescription.refills,
                'start_date': str_from_date(prescription.start_date) or '',
                'end_date': str_from_date(prescription.end_date) or '',
                'route': prescription.route,
                'dose': prescription.dose,
                'provider_id':prescription.provider.natural_key
                })



class ImmunizationWriter(EpicWriter):

    FILE_TEMPLATE_NAME = 'epicimm.esp.%s'
    
    fields = [
        'patient_id', 
        'type', 
        'name',
        'date',
        'dose',
        'manufacturer',
        'lot',
        'natural_key',
        'mrn',
        'provider_id',
        'visit_date',
        ]
    
    def write_row(self, immunization, **kw):
        self.writer.writerow({
                'patient_id':immunization.patient.natural_key, 
                'type':immunization.imm_type, 
                'name':immunization.name,
                'date':str_from_date(immunization.date) or '',
                'dose':immunization.dose,
                'manufacturer': immunization.manufacturer,
                'lot':immunization.lot,
                'natural_key' :immunization.natural_key,
                'mrn': immunization.patient.mrn,
                'provider_id':immunization.provider.natural_key,
                'visit_date' : str_from_date(immunization.visit_date) or ''
                })
                

class SocialHistoryWriter(EpicWriter):

    FILE_TEMPLATE_NAME = 'epicsoc.esp.%s'

    fields = [
        'patient_id',
        'mrn',
        'tobacco_use',
        'alcohol_use',
        'date_noted',
        'natural_key', #added in 3
        'provider_id', # added in 3 cch added
        ]
    
    def write_row(self, history, **kw):
        self.writer.writerow({
                'patient_id':history.patient.natural_key,
                'mrn':history.mrn,
                'tobacco_use':history.tobacco_use,
                'alcohol_use':history.alcohol_use,
                'date_noted' : str_from_date(history.date),
                'natural_key' :history.natural_key,
                'provider_id':history.provider.natural_key
                
                })      

class AllergyWriter(EpicWriter):

    FILE_TEMPLATE_NAME = 'epicall.esp.%s'

    fields = [
        'patient_id',
        'mrn',
        'natural_key',
        'date_noted',
        'allergy_id',
        'allergy_name',
        'allergy_status',
        'allergy_description',
        'allergy_entered_date',
        'provider_id'
        ]
    
    def write_row(self, allergy, **kw):
        self.writer.writerow({
                'patient_id':allergy.patient.natural_key,
                'mrn':allergy.patient.mrn,
                'natural_key':str(allergy.natural_key),
                'date_noted': str_from_date(allergy.date_noted),
                'allergy_id': allergy.allergen.code,
                'allergy_name': allergy.name,
                'allergy_status' : allergy.status,
                'allergy_description' : allergy.description,
                'allergy_entered_date': str_from_date(allergy.date) or '',
                'provider_id': allergy.provider.natural_key
                })
            
        
class ProblemWriter(EpicWriter):

    FILE_TEMPLATE_NAME = 'epicprb.esp.%s'

    fields = [
        'patient_id',
        'mrn',
        'natural_key',
        'date_noted',
        'icd9_code',
        'problem_status',
        'comment',
        'provider_id', #added in 3 added cch
        ]

    def write_row(self, problem, **kw):
        self.writer.writerow({
                'patient_id': problem.patient.natural_key,
                'mrn': problem.mrn,
                'natural_key': problem.natural_key,
                'date_noted': str_from_date(problem.date),
                'icd9_code': problem.raw_icd9_code,
                'problem_status': problem.status,
                'comment': problem.comment,
                'provider_id': problem.provider.natural_key
               
                })

class PregnancyWriter(EpicWriter):

    FILE_TEMPLATE_NAME = 'epicprg.esp.%s'
    
    fields = [
        'patient_id', 
        'mrn', 
        'provider_id', 
        'natural_key', 
        'outcome', 
        'edd', 
        'actual_date', 
        'gravida', 
        'parity', 
        'term', 
        'preterm', 
        'ga_delivery', 
        'birth_weight', 
        'delivery', 
        'pre_eclampsia'
        ]
    
    def write_row(self, pregnancy):
        row = {}
        row['patient_id'] = pregnancy.patient.natural_key
        row['provider_id']= pregnancy.provider.natural_key
        row['natural_key']= pregnancy.natural_key
        row['mrn']= pregnancy.patient.mrn
        row['outcome']= pregnancy.outcome
        row['edd']= str_from_date(pregnancy.edd)
        row['actual_date']= str_from_date(pregnancy.actual_date)
        row['gravida']= pregnancy.gravida
        row['parity']= pregnancy.parity
        row['term']= pregnancy.term
        row['preterm']= pregnancy.preterm
        row['ga_delivery']= pregnancy.ga_delivery
        row['birth_weight']= pregnancy.raw_birth_weight
        row['delivery']= pregnancy.delivery
        row['pre_eclampsia']= pregnancy.pre_eclampsia

        self.writer.writerow(row)


class Command(LoaderCommand):
    #
    # Parse command line options
    #
    help = 'Creates fake data and serializes it in text format, to be used by our Epic Loader.'


    def handle(self, *fixture_labels, **options):


        prof = Profiler()

        provider_writer = ProviderWriter()
        patient_writer = PatientWriter()
        lx_writer = LabResultWriter()
        lo_writer = LabOrderWriter()
        encounter_writer = EncounterWriter()
        prescription_writer = PrescriptionWriter()
        immunization_writer = ImmunizationWriter()
        pregnancy_writer = PregnancyWriter()
        allergy_writer = AllergyWriter()
        problem_writer = ProblemWriter()
        social_history_writer = SocialHistoryWriter()
        countprg = 0

        print 'Generating fake Patients, Labs, Encounters and Prescriptions, immunizations, prescription'
                
        Provider.make_mocks(provider_writer)
        #TODO issue 331 add the header rows her for each writer
        # do a join of fields object by ^
        # use icd9code 
        
        #from 0 to POPULATION_SIZE 
        for count in xrange(POPULATION_SIZE):
            if (count % ROW_LOG_COUNT) == 0 and count >0 : 
                prof.check('Processed entries for %d patients' % count)

            p = Patient.make_mock()
            patient_writer.write_row(p)
            
            # Write random or up to n objects per patient.
            if ENCOUNTERS_PER_PATIENT>0 :
                if (MIN_ENCOUNTERS_PER_PATIENT== ENCOUNTERS_PER_PATIENT):
                    for i in xrange(0,ENCOUNTERS_PER_PATIENT): 
                        #TODO add patients that have gestational diabetes that are not pregnant 648.8 icd9
                        encounter_writer.write_row(Encounter.make_mock(p),Encounter.makeicd9_mock(MAXICD9,ICD9_CODE_PCT))
                else:
                    for i in xrange(random.randrange(MIN_ENCOUNTERS_PER_PATIENT,ENCOUNTERS_PER_PATIENT)): 
                        encounter_writer.write_row(Encounter.make_mock(p),Encounter.makeicd9_mock(MAXICD9,ICD9_CODE_PCT))             
        
            if LAB_TESTS_PER_PATIENT>0:
                if (MIN_LAB_TESTS_PER_PATIENT==LAB_TESTS_PER_PATIENT):
                    for i in xrange(0,LAB_TESTS_PER_PATIENT):  
                        lx_writer.write_row(LabResult.make_mock(p))
                else:
                    for i in xrange(random.randrange(MIN_LAB_TESTS_PER_PATIENT,LAB_TESTS_PER_PATIENT)):  
                        lx_writer.write_row(LabResult.make_mock(p))                
       
            if LAB_ORDERS_PER_PATIENT>0:
                if (MIN_LAB_ORDERS_PER_PATIENT==LAB_ORDERS_PER_PATIENT):
                    for i in xrange(0,LAB_ORDERS_PER_PATIENT):  
                        lo_writer.write_row(LabOrder.make_mock(p))
                else:
                    for i in xrange(random.randrange(MIN_LAB_ORDERS_PER_PATIENT,LAB_ORDERS_PER_PATIENT)):  
                        lo_writer.write_row(LabOrder.make_mock(p))                
       
       
            if MEDS_PER_PATIENT>0:
                if (MIN_MEDS_PER_PATIENT==MEDS_PER_PATIENT):
                    for i in xrange(0,MEDS_PER_PATIENT):  
                        prescription_writer.write_row(Prescription.make_mock(p))
                else:
                    for i in xrange(random.randrange(MIN_MEDS_PER_PATIENT,MEDS_PER_PATIENT)):  
                        prescription_writer.write_row(Prescription.make_mock(p))
                              
            if random.random() <= float(IMMUNIZATION_PCT/100.0):
                if IMMUNIZATIONS_PER_PATIENT>0:
                    history = ImmunizationHistory(p)
                    for i in xrange(IMMUNIZATIONS_PER_PATIENT):
                        imm = history.add_immunization()
                        #check_for_reactions(imm) 
                        immunization_writer.write_row(imm)
                    
            #if patient is female and has birth bearing age 12-55, generate pregnancy                 
            if p.gender.startswith('F') and p.age.years > 12 and p.age.years < 55 :
                gravida = random.randint(1, MAX_PREGNANCIES)
                totparity =  random.randint(0, gravida) # births that persisted beyond 20 weeks
                totterm = random.randint(0, totparity) 
                totpreterm = random.randint(0,gravida - totterm) 
                for i in xrange(gravida): 
                    #
                    
                    curr_preg = random.random()
                    if curr_preg <= CURRENTLY_PREG_PCT:
                        pregnancy = Pregnancy.make_mock(p,i, totparity, totterm, totpreterm,when=datetime.date.today())
                    else :
                        pregnancy = Pregnancy.make_mock(p,i, totparity, totterm, totpreterm)
                    # reduce one as long as they are not 0
                    if totparity >0: totparity = totparity -1 
                    if totterm >0 :totterm = totterm - 1
                    if totpreterm >0 :totpreterm = totpreterm - 1
                    
                    
                    pregnancy_writer.write_row(pregnancy)
                    # generate encounter with edd field 
                    e= Encounter.make_mock(p,when = pregnancy.date)
                    e.edd = pregnancy.edd
                    
                    encounter_writer.write_row(e,[str(random.choice (['V22.1','V22.0','V22.2','V23.0']))])
                    # some % have gestational diabetes during pregnancy
                    gdm = .8
                    r = random.random()
                    range = relativedelta( pregnancy.actual_date,pregnancy.date).months*30+relativedelta( pregnancy.actual_date,pregnancy.date).days
                    if range<= 30: range = 40
                    # 30 days is after pregnancy start
                    randomdays = random.randrange(30, range )
                        
                    if r <= gdm:
                        e= Encounter.make_mock(p,when = pregnancy.date + datetime.timedelta(days=randomdays))
                        e.edd = pregnancy.edd
                        encounter_writer.write_row(e,['648.83'])
                    # sometimes date  can be + 30 days after pregnancy 
                    outsidepregn = .5
                    r = random.random()
                    if r <= outsidepregn and pregnancy.actual_date:
                        when = pregnancy.actual_date + datetime.timedelta(days=30)
                    else:
                        when = pregnancy.date + datetime.timedelta(days =randomdays )
                    # 3rd encounter give pre eclampsia  or hypertension  sometime during or after pregnancy
                    othercomplications = .5
                    r = random.random()
                    if r <= othercomplications:
                        e= Encounter.make_mock(p,when=when)
                        e.edd = pregnancy.edd
                        encounter_writer.write_row(e,[str(random.choice (['642.43','642.53','642.63','642.73','642.33','642.93']))])
        
                countprg +=1
                
            if MAX_ALLERGIES>0:
                for i in xrange(MAX_ALLERGIES):
                    allergy = Allergy.make_mock(p)
                    allergy_writer.write_row(allergy)
            
            if MAX_PROBLEMS>0:
                for i in xrange(MAX_PROBLEMS):
                    problem = Problem.make_mock(p)
                    problem_writer.write_row(problem)
                    
            if MAX_SOCIALHISTORY>0:
                for i in xrange(MAX_SOCIALHISTORY):
                    sh = SocialHistory.make_mock(p)
                    social_history_writer.write_row(sh)                
                
            
        print 'Generated %s fake Patients' % POPULATION_SIZE
        print 'up to max %s Encounters ' % ENCOUNTERS_PER_PATIENT 
        print 'up to max %s Labs ' % LAB_TESTS_PER_PATIENT
        print 'up to %s Lab orders ' % LAB_ORDERS_PER_PATIENT
        print 'up to %s Prescriptions per Patient' % MEDS_PER_PATIENT
        print 'up to %s Immunizations per Patient' % ImmunizationHistory.IMMUNIZATIONS_PER_PATIENT 
        print 'up to %s Patients with up to %s Pregnancies' % (countprg ,MAX_PREGNANCIES)
        print 'up to %s Allergies ' % MAX_ALLERGIES
        print 'up to %s Problems ' % MAX_PROBLEMS
        print 'up to %s Social History ' % MAX_SOCIALHISTORY         
