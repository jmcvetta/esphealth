'''
                                  ESP Health
                            EMR ETL Infrastructure
                         EpicCare Extract File Loader


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory - http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''


EPIC_ENCODING = 'iso-8859-15'
#EPIC_ENCODING = 'windows-1252'
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
from psycopg2 import Error as Psycopg2Error

from django.db import transaction
from ESP.emr.management.commands.common import LoaderCommand

from ESP.utils.utils import str_from_date
from ESP.settings import DATA_DIR
from ESP.settings import DATE_FORMAT
from ESP.utils.utils import log
from ESP.utils.utils import date_from_str
from ESP.static.models import Icd9, Allergen
from ESP.emr.models import Provenance
from ESP.emr.models import EtlError
from ESP.emr.models import Provider
from ESP.emr.models import Patient
from ESP.emr.models import LabResult, LabOrder
from ESP.emr.models import Encounter
from ESP.emr.models import Prescription
from ESP.emr.models import Immunization
from ESP.emr.models import SocialHistory, Problem, Allergy


    
# 
# Set global values that will be used by all functions
#
global UPDATED_BY, TIMESTAMP, UNKNOWN_PROVIDER
UPDATED_BY = 'load_epic.py'
TIMESTAMP = datetime.datetime.now()
UNKNOWN_PROVIDER = Provider.objects.get(provider_id_num='UNKNOWN')

def get_icd9(self, code):
    '''
    Given an ICD9 code, as a string, return an Icd9 model instance
    '''
    code = code.upper()
    if not code in self.__icd9_cache:
        try:
            i = Icd9.objects.get(code__iexact=code)
        except Icd9.DoesNotExist:
            log.warning('Could not find ICD9 code "%s" - creating new ICD9 entry.' % code)
            i = Icd9()
            i.code = code
            i.name = 'Added by load_epic.py'
            i.save()
            self.__icd9_cache[code] = i
    return self.__icd9_cache[code]




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


class LoadException(BaseException):
    '''
    Raised when there is a problem loading data into db
    '''


class BaseLoader(object):
    
    float_catcher = re.compile(r'(\d+\.?\d*)') 
    #
    # Caching Note
    #
    # Note: this is a primitive cache -- *all* lookups are cached, for the
    # duration of the script's run.  Thus it can consume considerable memory
    # when loading a large data set.  For a set with ~118k patients, Python
    # consumed 1.1G.  However, caching (plus some fine tuning of PostgreSQL, so
    # YMMV) on that same data set showed a 5x increase in load performance.  
    # 
    # If you cannot accept the cache's memory requirements, you can add
    # a preference toggle -- or file a ticket w/ the project requesting
    # the same.
    #
    __patient_cache = {} # {patient_id_num: Patient instance}
    __provider_cache = {} # {provider_id_num: Provider instance}
    
    def __init__(self, filepath):
        assert os.path.isfile(filepath)
        path, filename = os.path.split(filepath)
        self.filename = filename
        self.filepath = filepath
        prov, created = Provenance.objects.get_or_create(timestamp=TIMESTAMP, 
            source=filename, 
            hostname=socket.gethostname(),
            status='attempted',
            )
        prov.save()
        self.provenance = prov
        file_handle = open(filepath)
        self.line_count = len(file_handle.readlines())
        file_handle.seek(0) # Reset file position after counting lines
        self.reader = csv.DictReader(file_handle, fieldnames=self.fields, dialect='epic')
        self.created_on = datetime.datetime.now()
    
    def get_patient(self, patient_id_num):
        if not patient_id_num:
            raise LoadException('Called get_patient() with empty patient_id_num')
        if not patient_id_num in self.__patient_cache:
            try:
                p = Patient.objects.get(patient_id_num=patient_id_num)
            except Patient.DoesNotExist:
                p = Patient(patient_id_num=patient_id_num)
                p.provenance = self.provenance
                p.updated_by = UPDATED_BY
                p.save()
            self.__patient_cache[patient_id_num] = p
        return self.__patient_cache[patient_id_num]
    
    def get_provider(self, provider_id_num):
        if not provider_id_num:
            return UNKNOWN_PROVIDER
        if not provider_id_num in self.__provider_cache:
            try:
                p = Provider.objects.get(provider_id_num=provider_id_num)
            except Provider.DoesNotExist:
                p = Provider(provider_id_num=provider_id_num)
                p.provenance = self.provenance
                p.updated_by = UPDATED_BY
                p.save()
            self.__provider_cache[provider_id_num] = p
        return self.__provider_cache[provider_id_num]
    
    def float_or_none(self, string):
        if not string:
            return None
        m = self.float_catcher.match(string)
        if m and m.groups():
            result = float(m.groups()[0])
        else:
            result = None
        if result == float('infinity'): # Rare edge case, but it does happen
            result = None
        return result
    
    def date_or_none(self, string):
        if not string:
            return None
        try:
            return date_from_str(string)
        except ValueError:
            return None
        
    def decimal_or_none(self, string):
        return Decimal(string) if string else None
        
    
    @transaction.commit_on_success
    def load(self):
        # 
        # We can put error control here as it becomes necessary
        #
        log.info('Loading file "%s" with %s' % (self.filepath, self.__class__))
        cur_row = 0 # Row counter
        valid = 0 # Number of valid records loaded
        errors = 0 # Number of non-fatal errors encountered
        for row in self.reader:
            if not row:
                continue # Skip None objects
            cur_row += 1 # Increment the counter
            # The last line is a footer, so we skip it
            if cur_row >= self.line_count:
                break
            # check this, too -- in case there are extra blank lines at end of file
            if row[self.fields[0]].upper() == 'CONTROL TOTALS':
                break
            sid = transaction.savepoint()
            try:
                # Coerce to unicode
                for key in row:
                    if row[key]:
                        try:
                            row[key] = row[key].strip().decode(EPIC_ENCODING).encode('utf-8')
                        except AttributeError:
                            pass
                self.load_row(row)
                transaction.savepoint_commit(sid)
                valid += 1
            except KeyboardInterrupt, e:
                # Allow keyboard interrupt to rise to next catch in main()
                raise e
            except BaseException, e:
                transaction.savepoint_rollback(sid)
                log.error('Caught Exception:')
                log.error('  File: %s' % self.filename)
                log.error('  Line: %s' % cur_row)
                log.error('  Exception: \n%s' % e)
                log.error(pprint.pformat(row))
                
                errors += 1
                #
                # Log ETL errors to db
                #
                err = EtlError()
                err.provenance = self.provenance
                err.line = cur_row
                err.err_msg = str(e)
                err.data = pprint.pformat(row)
                err.save()

            if ROW_LOG_COUNT and not (cur_row % ROW_LOG_COUNT):
                now = datetime.datetime.now()
                log.info('Loaded %s of %s rows:  %s %s' % (cur_row, self.line_count, now, self.filename))
        log.debug('Loaded %s records with %s errors.' % (valid, errors))

        self.provenance.status = 'loaded' if not errors else 'errors'
        self.provenance.valid_rec_count = valid
        self.provenance.error_count = errors
        self.provenance.save()
        return (valid, errors)

class NotImplementedLoader(BaseLoader):
    
    def __init__(self, filename):
        pass
    
    def load(self):
        log.warning('Loader not implemented for this data type')
        return (0, 0) # count of records loaded is always zero


class ProviderLoader(BaseLoader):
    
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
    
    def load_row(self, row):
        if not ''.join([i[1] for i in row.items()]): # Concatenate all fields
            log.debug('Empty row encountered -- skipping')
            return
        pin = row['provider_id_num']
        if not pin:
            raise LoadException('Record has blank provider_id_num, which is required')
        p = self.get_provider(pin)
        p.provenance = self.provenance
        p.updated_by = UPDATED_BY
        p.last_name = unicode(row['last_name'])
        p.first_name = unicode(row['first_name'])
        p.middle_name = unicode(row['middle_name'])
        p.title = row['title']
        p.dept_id_num = row['dept_id_num']
        p.dept = row['dept']
        p.dept_address_1 = row['dept_address_1']
        p.dept_address_2 = row['dept_address_2']
        p.dept_city = row['dept_city']
        p.dept_state = row['dept_state']
        p.dept_zip = row['dept_zip']
        p.area_code = row['area_code']
        p.telephone = row['telephone']
        p.save()
        log.debug('Saved provider object: %s' % p)



class PatientLoader(BaseLoader):
    
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
        'date_of_death',
        ]
    
    def load_row(self, row):
        p = self.get_patient(row['patient_id_num'])
        p.provenance = self.provenance
        p.updated_by = UPDATED_BY
        p.mrn = row['mrn']
        p.last_name = row['last_name']
        p.first_name = row['first_name']
        p.middle_name = row['middle_name']
        p.pcp = self.get_provider(row['provider_id_num'])
        p.address1 = row['address1']
        p.address2 = row['address2']
        p.city = row['city']
        p.state = row['state']
        p.zip = row['zip']
        p.zip5 = p._calculate_zip5()
        p.country = row['country']
        p.areacode = row['areacode']
        p.tel = row['tel']
        p.tel_ext = row['tel_ext']
        if row['date_of_birth']:
            p.date_of_birth = self.date_or_none(row['date_of_birth'])
        if row['date_of_death']:
            p.date_of_death = self.date_or_none(row['date_of_death'])
        p.gender = row['gender']
        p.race = row['race']
        p.home_language = row['home_language']
        p.ssn = row['ssn']
        p.marital_stat = row['marital_stat']
        p.religion = row['religion']
        p.aliases = row['aliases']
        p.mother_mrn = row['mother_mrn']
        p.save()
        log.debug('Saved patient object: %s' % p)


class LabResultLoader(BaseLoader):
    
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






    
    def load_row(self, row):
        native_code = row['cpt']
        component = row['component']
        if component:
            # We only use first 20 characters of component, since some lab 
            # results (always types unimportant to ESP) have quite long 
            # component values, yet we need the native_code field to be a 
            # reasonable width for indexing.  
            if len(component) > 20:
                log.warning('Component field is greater than 20 characters, and will be truncated:')
                log.warning('    "%s"' % component)
            native_code = native_code + '--' + component[0:20] 
        l = LabResult()
        l.provenance = self.provenance
        l.patient = self.get_patient(row['patient_id_num'])
        l.provider = self.get_provider(row['provider_id_num'])
        l.mrn = row['medical_record_num']
        l.order_num = row['order_id_num']
        l.date = self.date_or_none(row['order_date'])
        l.result_date = self.date_or_none(row['result_date'])
        l.native_code = native_code
        l.native_name = row['component_name']
        res = row['result_string']
        l.result_string = res
        l.result_float = self.float_or_none(l.result_string)
        l.ref_low_string = row['ref_low']
        l.ref_high_string = row['ref_high']
        l.ref_low_float = self.float_or_none(row['ref_low'])
        l.ref_high_float = self.float_or_none(row['ref_high'])
        l.ref_unit = row['unit']
        l.abnormal_flag = row['normal_flag']
        l.status = row['status']
        l.comment = row['note']
        l.specimen_num = row['specimen_id_num']
        l.impression = row['impression']
        l.specimen_source = row['specimen_source']
        l.collection_date = self.date_or_none(row['collection_date'])
        l.procedure_name = row['procedure_name']
        l.save()
        log.debug('Saved lab result object: %s' % l)
        

class LabOrderLoader(BaseLoader):    
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
    
    def load_row(self, row):
        LabOrder.objects.create(
            provenance = self.provenance,
            patient = self.get_patient(row['patient_id_num']),
            provider = self.get_provider(row['ordering_provider']),
            mrn = row['mrn'],
            order_id = row['order_id'],
            procedure_master_num = row['procedure_master_num'],
            modifier = row['modifier'],
            specimen_id = row['specimen_id'],
            date = self.date_or_none(row['ordering_date']),
            order_type = row['order_type'],
            procedure_name = row['procedure_name'],
            specimen_source = row['specimen_source']
            )


class EncounterLoader(BaseLoader):
    
    feet_regex = re.compile('(?P<feet>\d)\' *(?P<inches>\d{1,2})')
    
    # Please see Caching Note on BaseLoader.
    __icd9_cache = {} # {code: icd9_obj}
    
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




    
    def load_row(self, row):
        e, created = Encounter.objects.get_or_create(
            native_encounter_num=row['encounter_id_num'],
            defaults = {
                'provenance':self.provenance,
                'patient':self.get_patient(row['patient_id_num']),
                'provider':self.get_provider(row['provider_id_num']),
                'date':self.date_or_none(row['encounter_date'])
                })

        message = 'Updating existing Encounter' if created else 'Creating new Encounter object'
        log.debug(message)


        # If the row contains new information about the record, we will update it
        # Else, we will just keep it as it was (or default, if it's a new record).
        
        e.native_site_num = row['dept_id_num'] or e.native_site_num or None
        e.event_type = row['event_type'] or e.event_type or None
        e.closed_date = row['closed_date'] or e.closed_date or None
        e.site_name = row['dept_name'] or e.site_name or None
        e.temperature = self.float_or_none(row['temp']) or e.temperature or None
        e.bp_systolic = self.float_or_none(row['bp_systolic'])  or e.bp_systolic or None
        e.bp_diastolic = self.float_or_none(row['bp_diastolic']) or e.bp_diastolic or None
        e.o2_stat = self.float_or_none(row['o2_stat']) or e.o2_stat or None
        e.peak_flow = self.float_or_none(row['peak_flow']) or e.peak_flow or None
        e.closed_date = self.date_or_none(row['closed_date']) or e.closed_date or None
        e.edc = self.date_or_none(row['edc']) or e.edc or None
        e.bmi = self.decimal_or_none(row['bmi']) or e.bmi or None               
#        e.diagnosis = row['diagnosis'] or e.diagnosis or None


        # Elements that derived from the information on the row.
        if e.edc: e.pregnancy_status = True
        raw_weight = row['weight'] 
        raw_height = row['height'] 

        if raw_weight:
            try:
                weight = self.float_or_none(raw_weight.split()[0])
                if 'lb' in raw_weight: # Convert LBs to Kg
                    e.weight = 0.45359237 * weight
            except ValueError:
                log.warning('Cannot cast weight to a number: %s' % raw_weight)
        if raw_height:
            match = self.feet_regex.match(raw_height)
            if match: # Need to convert from feet to cm
                feet = self.float_or_none(match.groupdict()['feet'])
                inches = self.float_or_none(match.groupdict()['inches'])
                inches = inches + (feet * 12)
                e.height = inches * 2.54
            else: # Assume height is in cm
                try:
                    e.height = self.float_or_none(raw_height.split()[0])
                except ValueError:
                    log.warning('Cannot cast height to a number: %s' % raw_height)
                    
        # We still need to process icd9 codes, but we 
        # must save the encounter before using a ManyToMany relationship
        e.save() 
        
        for code_string in row['icd9s'].split(';'):
            if len(code_string.split()) >= 1: 
                code = code_string.split()[0].strip()
                # We'll only accept a code if it has at least one digit in the string.
                if any(c in string.digits for c in code):
                    e.icd9_codes.add(self.get_icd9(code))
        e.save()
        log.debug('Saved encounter object: %s' % e)
    
    def get_icd9(self, code):
        '''
        Given an ICD9 code, as a string, return an Icd9 model instance
        '''
        code = code.upper()
        if not code in self.__icd9_cache:
            try:
                i = Icd9.objects.get(code__iexact=code)
            except Icd9.DoesNotExist:
                log.warning('Could not find ICD9 code "%s" - creating new ICD9 entry.' % code)
                i = Icd9()
                i.code = code
                i.name = 'Added by load_epic.py'
                i.save()
            self.__icd9_cache[code] = i
        return self.__icd9_cache[code]
            
            


class PrescriptionLoader(BaseLoader):

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
        'route',
    ]

    def load_row(self, row):
        p = Prescription()
        p.provenance = self.provenance
        p.updated_by = UPDATED_BY
        p.patient = self.get_patient(row['patient_id_num'])
        p.provider = self.get_provider(row['provider_id_num'])
        p.order_num = row['order_id_num']
        p.date = self.date_or_none(row['order_date'])
        p.status = row['status']
        p.name = row['drug_name']
        p.code = row['ndc']
        p.quantity = row['quantity']
        p.quantity_float = self.float_or_none(row['quantity'])
        p.refills = row['refills']
        p.start_date = self.date_or_none(row['start_date'])
        p.end_date = self.date_or_none(row['end_date'])
        p.route = row['route']
        p.save()
        log.debug('Saved prescription object: %s' % p)



class ImmunizationLoader(BaseLoader):
    
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
    
    def load_row(self, row):
        i = Immunization()
        i.provenance = self.provenance
        i.updated_by = UPDATED_BY
        i.patient = self.get_patient(row['patient_id_num'])
        i.type = row['type']
        i.name = row['name']
        i.date = self.date_or_none(row['date'])
        i.dose = row['dose']
        i.manufacturer = row['manufacturer']
        i.lot = row['lot']
        i.imm_id_num = row['imm_id_num']
        i.save()
        log.debug('Saved immunization object: %s' % i)



class SocialHistoryLoader(BaseLoader):
    fields = [
        'patient_id_num',
        'mrn',
        'tobacco_use',
        'alcohol_use'
        ]
    
    def load_row(self, row):
        SocialHistory.objects.create(
            provenance = self.provenance,
            date = self.created_on, # date does not make sense for SocialHistory.
            patient=self.get_patient(row['patient_id_num']),
            mrn = row['mrn'],
            tobacco_use = row['tobacco_use'],
            alcohol_use = row['alcohol_use']
            )
        

class AllergyLoader(BaseLoader):
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
    
    def load_row(self, row):
        allergen, created = Allergen.objects.get_or_create(code=row['allergy_id'])
        Allergy.objects.create(
            provenance = self.provenance,
            patient = self.get_patient(row['patient_id_num']),
            mrn = row['mrn'],
            problem_id = int(row['problem_id']),
            date = self.date_or_none(row['allergy_entered_date']),
            date_noted = self.date_or_none(row['date_noted']),
            allergen = allergen,
            name = row['allergy_name'],
            status = row['allergy_status'],
            description = row['allergy_description']
            )
            
        
class ProblemLoader(BaseLoader):
    fields = [
        'patient_id_num',
        'mrn',
        'problem_id',
        'date_noted',
        'icd9_code',
        'problem_status',
        'comment'
        ]

    def load_row(self, row):
        code = row['icd9_code'].upper()
        icd9_code, created = Icd9.objects.get_or_create(code=code, defaults={
                'name':'Added by load_epic.py'})
        if created: log.warning('Could not find ICD9 code "%s" - creating new ICD9 entry.' % code)
        
        
        Problem.objects.create(
            provenance = self.provenance,
            patient = self.get_patient(row['patient_id_num']),
            mrn = row['mrn'],
            date = self.date_or_none(row['date_noted']),
            icd9 = icd9_code,
            status = row['problem_status'],
            comment = row['comment']
            )





class Command(LoaderCommand):
    #
    # Parse command line options
    #
    help = 'Loads data from Epic ETL files'
    #log.debug('options: %s' % options)
    
    def handle(self, *fixture_labels, **options):
        self.folder_check()
        #
        # Sort files by type
        #
        input_filepaths = []
        if options['single_file']:
            if not os.path.isfile(options['single_file']):
                sys.stderr.write('Invalid file path specified: %s' % options['single_file'])
            input_filepaths = [options['single_file']]
        else:
            dir_contents = os.listdir(options['input_folder'])
            dir_contents.sort()
            for item in dir_contents:
                filepath = os.path.join(options['input_folder'], item)
                if not os.path.isfile(filepath):
                    continue
                if item[0] == '.':
                    continue # Skip dot files
                input_filepaths.append(filepath)
        conf = [
            ('epicpro', ProviderLoader),
            ('epicmem', PatientLoader),
            ('epicord', LabOrderLoader),
            ('epicres', LabResultLoader),
            ('epicvis', EncounterLoader),
            ('epicmed', PrescriptionLoader),
            ('epicimm', ImmunizationLoader),
            ('epicall', AllergyLoader),
            ('epicprb', ProblemLoader),
            ('epicsoc', SocialHistoryLoader)                      
            ]

        loader = {}
        filetype = {}
        valid_count = {}
        error_count = {}
        load_order = []
        for item in conf:
            load_order.append(item[0])
            loader[item[0]] = item[1]
            filetype[item[0]] = []
            valid_count[item[0]] = 0
            error_count[item[0]] = 0
        for filepath in input_filepaths:
            path, filename = os.path.split(filepath)
            if Provenance.objects.filter(source=filename, status__in=('loaded', 'errors')):
                log.info('File "%s" has already been loaded; skipping' % filename)
                self.archive(options, filepath, 'success')
                continue
            try:
                filetype[filename.split('.')[0]] += [filepath]
            except KeyError:
                log.warning('Unrecognized file type: "%s"' % filename)
        log.debug('Files to load by type: \n%s' % pprint.pformat(filetype))
        #
        # Load data
        #
        for ft in load_order:
            for filepath in filetype[ft]:
                loader_class = loader[ft]
                l = loader_class(filepath) # BaseLoader child instance
                try:
                    valid, error = l.load()
                    valid_count[ft] += valid
                    error_count[ft] += error
                    if error:
                        log.info('File "%s" loaded with %s errors' % (filepath, error))
                        disposition = 'errors'
                    else:
                        log.info('File "%s" loaded successfully.' % filepath)
                        disposition = 'success'
                except KeyboardInterrupt:
                    log.critical('Keyboard interrupt: exiting.')
                    sys.exit(-255)
                except BaseException, e: # Unhandled exception!
                    log.critical('Unhandled exception loading file "%s":' % filepath)
                    log.critical('\t%s' % e)
                    l.provenance.status = 'failure'
                    l.provenance.comment = str(e)
                    l.provenance.save()
                    disposition = 'failure'
                self.archive(options, filepath, disposition)
        #
        # Print job summary
        #
        print '+' * 80
        print 'Valid records loaded:'
        pprint.pprint(valid_count)
        print '-' * 80
        print 'Errors:'
        pprint.pprint(error_count)
