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

from ESP.utils.utils import str_from_date
from ESP.settings import DATA_DIR
from ESP.settings import DATE_FORMAT
from ESP.utils.utils import log
from ESP.utils.utils import date_from_str, Profiler
from ESP.static.models import Icd9, Allergen, Loinc, FakeICD9s
from ESP.emr.models import Provenance
from ESP.emr.models import EtlError
from ESP.emr.models import Provider,Patient,LabResult, LabOrder
from ESP.emr.models import Encounter,Prescription
from ESP.emr.models import SocialHistory, Problem, Allergy,Immunization
from ESP.vaers.fake import ImmunizationHistory, check_for_reactions
from ESP.emr.management.commands.load_epic import LoadException, UPDATED_BY

#change patient generations here
POPULATION_SIZE = 19

# if min and <item>per_patient are >0 and same it will generate that amount
# if min < than <item>per_patient it will generate a random number of object in that range
MIN_ENCOUNTERS_PER_PATIENT = 1
ENCOUNTERS_PER_PATIENT = 2
#it will generate a % of encounters with random number of icd9s between 0 and maxicd9
MAXICD9 = 2
ICD9_CODE_PCT = 20

MIN_LAB_TESTS_PER_PATIENT = 1
LAB_TESTS_PER_PATIENT = 2

MIN_MEDS_PER_PATIENT = 0
MEDS_PER_PATIENT = 1

IMMUNIZATION_PCT = 1
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
        'date_of_death'
        ]
    
    def write_row(self, patient):
        row = {}

        row['natural_key'] = patient.natural_key
        row['mrn'] = patient.mrn
        row['last_name'] = patient.last_name
        row['first_name'] = patient.first_name
        row['middle_name'] = patient.middle_name
        row['pcp_id'] = patient.pcp.natural_key
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

        self.writer.writerow(row)   


class LabResultWriter(EpicWriter):

    FILE_TEMPLATE_NAME = 'epicres.esp.%s'
    
    fields = [
        'patient_id',           # 1
        'mrn',   # 2
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
        'raw_diagnosis',
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
                'event_type':encounter.events.content_type,
                'edd':str_from_date(encounter.edd) or '',
                'temp':str(encounter.temperature or '') ,
                'cpt': '',
                'weight': str(encounter.weight or ''),
                'height': str(encounter.height or ''),
                'bp_systolic':str(encounter.bp_systolic or ''),
                'bp_diastolic':str(encounter.bp_diastolic or ''),
                'o2_stat':str(encounter.o2_stat or ''),
                'peak_flow':str(encounter.peak_flow or ''),
                'icd9s': ';'.join(icd9_codes),
                'bmi':str(encounter.bmi or ''),
                'raw_diagnosis':encounter.raw_diagnosis or ''
                })
  

class PrescriptionWriter(EpicWriter):

    FILE_TEMPLATE_NAME = 'epicmed.esp.%s'

    fields = [
        'patient_id',
        'mrn',
        'natural_key',
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
                'natural_key':prescription.natural_key,
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
                'visit_date' : immunization.visit_date
                })
                

class SocialHistoryWriter(EpicWriter):

    FILE_TEMPLATE_NAME = 'epicsoc.esp.%s'

    fields = [
        'patient_id',
        'mrn',
        'tobacco_use',
        'alcohol_use',
        'date_noted'
        ]
    
    def write_row(self, history, **kw):
        self.writer.writerow({
                'patient_id':history.patient.natural_key,
                'mrn':history.mrn,
                'tobacco_use':history.tobacco_use,
                'alcohol_use':history.alcohol_use,
                'date_noted' : history.date
                })      

class AllergyWriter(EpicWriter):

    FILE_TEMPLATE_NAME = 'epicall.esp.%s'

    fields = [
        'patient_id',
        'mrn',
        'problem_id',
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
                'problem_id':str(allergy.problem_id),
                'date_noted': str_from_date(allergy.date_noted),
                'allergy_id': allergy.allergen.code,
                'allergy_name': allergy.name,
                'allergy_status' : allergy.status,
                'allergy_description' : allergy.description,
                'allergy_entered_date': str_from_date(allergy.date),
                'provider_id': allergy.provider.natural_key
                })
            
        
class ProblemWriter(EpicWriter):

    FILE_TEMPLATE_NAME = 'epicprb.esp.%s'

    fields = [
        'patient_id',
        'mrn',
        'problem_id',
        'date_noted',
        'icd9_code',
        'problem_status',
        'comment'
        ]

    def write_row(self, problem, **kw):
        self.writer.writerow({
                'patient_id': problem.patient.natural_key,
                'mrn': problem.mrn,
                'problem_id': problem.id,
                'date_noted': str_from_date(problem.date),
                'icd9_code': str(problem.icd9.code),
                'problem_status': problem.status,
                'comment': problem.comment
                })


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
        encounter_writer = EncounterWriter()
        prescription_writer = PrescriptionWriter()
        immunization_writer = ImmunizationWriter()

        print 'Generating fake Patients, Labs, Encounters and Prescriptions, immunizations'
                
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
       
            if MEDS_PER_PATIENT>0:
                if (MIN_MEDS_PER_PATIENT==MEDS_PER_PATIENT):
                    for i in xrange(0,MEDS_PER_PATIENT):  
                        prescription_writer.write_row(Prescription.make_mock(p))
                else:
                    for i in xrange(random.randrange(MIN_MEDS_PER_PATIENT,MEDS_PER_PATIENT)):  
                        prescription_writer.write_row(Prescription.make_mock(p))
                              
            #if random.random() <= float(IMMUNIZATION_PCT/100.0):
            if ImmunizationHistory.IMMUNIZATIONS_PER_PATIENT>0:
                history = ImmunizationHistory(p)
                for i in xrange(ImmunizationHistory.IMMUNIZATIONS_PER_PATIENT):
                    imm = history.add_immunization()
                    #check_for_reactions(imm) 
                    immunization_writer.write_row(imm)
            
        print 'Generated %s fake Patients' % POPULATION_SIZE
        print 'up to max %s Encounters ' % ENCOUNTERS_PER_PATIENT 
        print 'up to max %s Labs, ' % LAB_TESTS_PER_PATIENT
        print 'up to %s Prescriptions per Patient' % MEDS_PER_PATIENT
        print 'up to %s Immunizations per Patient' % ImmunizationHistory.IMMUNIZATIONS_PER_PATIENT 
             
                

                
            

                





            

                

