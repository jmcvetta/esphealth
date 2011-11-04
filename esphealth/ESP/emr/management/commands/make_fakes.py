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
from ESP.emr.models import Provider
from ESP.emr.models import Patient
from ESP.emr.models import LabResult, LabOrder
from ESP.emr.models import Encounter
from ESP.emr.models import Prescription
from ESP.emr.models import Immunization
from ESP.emr.models import SocialHistory, Problem, Allergy
from ESP.vaers.fake import ImmunizationHistory, check_for_reactions

#change patient generations here
POPULATION_SIZE = 2#10**1
ENCOUNTERS_PER_PATIENT = 10
MIN_ENCOUNTERS_PER_PATIENT = 1
MAXICD9 = 3

MEDS_PER_PATIENT = 5
MIN_MEDS_PER_PATIENT = 1

LAB_TESTS_PER_PATIENT = 5
MIN_LAB_TESTS_PER_PATIENT = 1

CHLAMYDIA_LX_PCT = 20
ICD9_CODE_PCT = 100
IMMUNIZATION_PCT = 20
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
        'provider_id_num',
        'last_name',
        'first_name',
        'middle_name',
        'title',
        'dept_id_num',
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

        row['provider_id_num'] = provider.provider_id_num
        row['last_name'] = provider.last_name
        row['first_name'] = provider.first_name
        row['middle_name'] = provider.middle_name
        row['title'] = provider.title
        row['dept_id_num'] = provider.dept_id_num
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
        'patient_id_num',
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
        'provider_id_num',
        'marital_stat',
        'religion',
        'aliases',
        'mother_mrn',
        'date_of_death'
        ]
    
    def write_row(self, patient):
        row = {}

        row['patient_id_num'] = patient.patient_id_num
        row['mrn'] = patient.mrn
        row['last_name'] = patient.last_name
        row['first_name'] = patient.first_name
        row['middle_name'] = patient.middle_name
        row['provider_id_num'] = patient.pcp.provider_id_num
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
        'patient_id_num',       # 1
        'medical_record_num',   # 2
        'order_id_num',         # 3
        'order_date',           # 4
        'result_date',          # 5
        'provider_id_num',      # 6
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
        'specimen_id_num',      # 18
        'impression',           # 19
        'specimen_source',      # 20
        'collection_date',      # 21
        'procedure_name'        #22
        ]


    def write_row(self, lx):
        self.writer.writerow({
                'patient_id_num':lx.patient.patient_id_num,
                'medical_record_num': lx.mrn,
                'order_id_num': lx.order_num,
                'order_date': str_from_date(lx.date),
                'result_date': str_from_date(lx.result_date),
                'provider_id_num':lx.provider.provider_id_num,
                                 #'FAKE_PROVIDER_%s' % random.randint(1, 100),
                'order_type':' ',
                'cpt': lx.native_code.strip(),
                #lx.native_code.split('--')[1].strip(),
                'component': lx.native_code.strip(),
                #lx.native_code.split('--')[-1].strip(),
                'component_name': lx.native_name,
                'result_string': lx.result_string,
                'normal_flag' : lx.abnormal_flag,
                'ref_low': lx.ref_low_float, #2.1 low_string?
                'ref_high': lx.ref_high_float,#2.1 high string?
                'unit': lx.ref_unit,
                'status' : lx.status,
                'note' : lx.comment,
                'specimen_id_num' : lx.specimen_num,
                'impression' : lx.impression,
                'specimen_source' : lx.specimen_source,
                'collection_date' : str_from_date(lx.collection_date),
                'procedure_name' : lx.procedure_name
                })
        

class LabOrderWriter(EpicWriter):    

    FILE_TEMPLATE_NAME = 'epicord.esp.%s'

    fields = [
        'patient_id_num',
        'mrn',
        'order_id',
        'procedure_master_num',
        'modifier',
        'specimen_id',
        'ordering_date',
        'order_type',
        'ordering_provider',
        'procedure_name',
        'specimen_source'
        ]
    
    def write_row(self, lab_order):
        self.writer.writerow({
            'patient_id_num': lab_order.patient.patient_id_num,
            'mrn':lab_order.mrn,
            'order_id': lab_order.order_id,
            'procedure_master_num': lab_order.procedure_master_num,
            'modifier': lab_order.modifier,
            'specimen_id': lab_order.specimen_id,
            'ordering_date': str_from_date(lab_order.date),
            'order_type': str(lab_order.order_type),
            'ordering_provider': lab_order.patient.pcp.provider_id_num,
            'procedure_name': lab_order.procedure_name,
            'specimen_source': lab_order.specimen_source
            })


class EncounterWriter(EpicWriter):

    FILE_TEMPLATE_NAME = 'epicvis.esp.%s'
    
    feet_regex = re.compile('(?P<feet>\d)\' *(?P<inches>\d{1,2})')
    
    # Please see Caching Note on EpicWriter.
    __icd9_cache = set() # {code: icd9_obj}
    
    fields = [
        'patient_id_num',
        'medical_record_num',
        'encounter_id_num',
        'encounter_date',
        'is_closed',
        'closed_date',
        'provider_id_num',
        'dept_id_num',
        'dept_name',
        'event_type',
        'edc',
        'temp',
        'cpt',
        'weight',
        'height',
        'bp_systolic',
        'bp_diastolic',
        'o2_stat',
        'peak_flow',
        'icd9s',
        'bmi',
        'diagnosis'
        ]


    def write_row(self, encounter,icd9_codes, **kw):

        self.writer.writerow({
                'patient_id_num':encounter.patient.patient_id_num,
                'medical_record_num':encounter.patient.mrn,
                'encounter_id_num':encounter.native_encounter_num,#2.1 encounter.id
                'encounter_date':str_from_date(encounter.date),
                'is_closed': '',
                'closed_date':str_from_date(encounter.closed_date) or '',
                'provider_id_num':encounter.patient.pcp.provider_id_num,
                'dept_id_num':encounter.native_site_num,
                'dept_name':encounter.site_name,
                'event_type':encounter.event_type,
                'edc':str_from_date(encounter.edc) or '',
                'temp':str(encounter.temperature or '') ,
                'cpt': '',
                'weight': str(encounter.weight or ''),
                'height': str(encounter.height or ''),
                'bp_systolic':str(encounter.bp_systolic or ''),
                'bp_diastolic':str(encounter.bp_diastolic or ''),
                'o2_stat':str(encounter.o2_stat or ''),
                'peak_flow':str(encounter.peak_flow or ''),
                'icd9s': '; '.join(icd9_codes),
                'bmi':str(encounter.bmi or ''),
                'diagnosis':encounter.diagnosis or ''
                })
  

class PrescriptionWriter(EpicWriter):

    FILE_TEMPLATE_NAME = 'epicmed.esp.%s'

    fields = [
        'patient_id_num',
        'medical_record_num',
        'order_id_num',
        'provider_id_num',
        'order_date',
        'status',
        'drug_name',
        'ndc',
        'drug_desc',
        'quantity',
        'refills',
        'start_date',
        'end_date',
        'route', #if order not in 7400?
        'dose',
    ]

    def write_row(self, prescription, **kw):
        self.writer.writerow({
                'patient_id_num':prescription.patient.patient_id_num,
                'medical_record_num': prescription.patient.mrn,
                'order_id_num':prescription.order_num,
                'order_date': str_from_date(prescription.date),
                'status': prescription.status,
                'drug_name': prescription.name,
                'ndc': prescription.code,
                'quantity': str(prescription.quantity or ''),
                'refills': prescription.refills,
                'start_date': str_from_date(prescription.start_date) or '',
                'end_date': str_from_date(prescription.end_date) or '',
                'route': prescription.route,
                'dose': prescription.dose,
                
                })



class ImmunizationWriter(EpicWriter):

    FILE_TEMPLATE_NAME = 'epicimm.esp.%s'
    
    fields = [
        'patient_id_num', 
        'type', 
        'name',
        'date',
        'dose',
        'manufacturer',
        'lot',
        'imm_id_num',
        ]
    
    def write_row(self, immunization, **kw):
        self.writer.writerow({
                'patient_id_num':immunization.patient.patient_id_num, 
                'type':immunization.imm_type, 
                'name':immunization.name,
                'date':str_from_date(immunization.date) or '',
                'dose':immunization.dose,
                'manufacturer': immunization.manufacturer,
                'lot':immunization.lot,
                'imm_id_num':immunization.imm_id_num
                })
                

class SocialHistoryWriter(EpicWriter):

    FILE_TEMPLATE_NAME = 'epicsoc.esp.%s'

    fields = [
        'patient_id_num',
        'mrn',
        'tobacco_use',
        'alcohol_use'
        ]
    
    def write_row(self, history, **kw):
        self.writer.writerow({
                'patient_id_num':history.patient.patient_id_num,
                'mrn':history.mrn,
                'tobacco_use':history.tobacco_use,
                'alcohol_use':history.alcohol_use
                })      

class AllergyWriter(EpicWriter):

    FILE_TEMPLATE_NAME = 'epicall.esp.%s'

    fields = [
        'patient_id_num',
        'mrn',
        'problem_id',
        'date_noted',
        'allergy_id',
        'allergy_name',
        'allergy_status',
        'allergy_description',
        'allergy_entered_date'
        ]
    
    def write_row(self, allergy, **kw):
        self.writer.writerow({
                'patient_id_num':allergy.patient.patient_id_num,
                'mrn':allergy.mrn,
                'problem_id':str(allergy.problem_id),
                'date_noted': str_from_date(allergy.date_noted),
                'allergy_id': allergy.allergen.code,
                'allergy_name': allergy.name,
                'allergy_status' : allergy.status,
                'allergy_description' : allergy.description,
                'allergy_entered_date': str_from_date(allergy.date)
                })
            
        
class ProblemWriter(EpicWriter):

    FILE_TEMPLATE_NAME = 'epicprb.esp.%s'

    fields = [
        'patient_id_num',
        'mrn',
        'problem_id',
        'date_noted',
        'icd9_code',
        'problem_status',
        'comment'
        ]

    def write_row(self, problem, **kw):
        self.writer.writerow({
                'patient_id_num': problem.patient.patient_id_num,
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
        #immunization_writer = ImmunizationWriter()
        
        print 'Generating fake Patients, Labs, Encounters and Prescriptions'
                
        Provider.make_mocks(provider_writer)
        
        for count in xrange(POPULATION_SIZE):
            if (count % ROW_LOG_COUNT) == 0: 
                prof.check('Processed entries for %d patients' % count)

            p = Patient.make_mock()
            patient_writer.write_row(p)
                
            # if random.random() <= float(IMMUNIZATION_PCT/100.0):
            #     history = ImmunizationHistory(p)
            #     for i in xrange(ImmunizationHistory.IMMUNIZATIONS_PER_PATIENT):
            #         imm = history.add_immunization()
            #         check_for_reactions(imm)
            #         immunization_writer.write_row(imm)

            
            # Write random encounters and lab tests.
            for i in xrange(random.randrange(MIN_ENCOUNTERS_PER_PATIENT,ENCOUNTERS_PER_PATIENT)): 
                                          
                encounter_writer.write_row(Encounter.make_mock(p),Encounter.makeicd9_mock(MAXICD9,ICD9_CODE_PCT))
            
            for i in xrange(random.randrange(MIN_LAB_TESTS_PER_PATIENT,LAB_TESTS_PER_PATIENT)):  
                lx = LabResult.make_mock(p)
                lx_writer.write_row(lx)
                
            # Write random encounters and lab tests.
            for i in xrange(random.randrange(MIN_MEDS_PER_PATIENT,MEDS_PER_PATIENT)):  
                prescription_writer.write_row(Prescription.make_mock(p))
                
        print 'Generated %s fake Patients' % POPULATION_SIZE
        print 'with up to max %s Labs, ' % LAB_TESTS_PER_PATIENT
        print 'up to max %s Encounters ' % ENCOUNTERS_PER_PATIENT 
        print 'and up to %s Prescriptions per Patient' % MEDS_PER_PATIENT
        
