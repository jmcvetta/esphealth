'''
                                  ESP Health
                            EMR ETL Infrastructure
                         EpicCare Extract File Loader


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory - http://www.channing.harvard.edu
@contact: http://esphealth.org
@copyright: (c) 2009-2010 Channing Laboratory
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''


EPIC_ENCODING = 'iso-8859-15'
#EPIC_ENCODING = 'windows-1252'
#ROW_LOG_COUNT = 10000  # Log progress every N rows.  'None' to disable. '-1' to log progress every row
ROW_LOG_COUNT = -1  # Log progress every N rows.  'None' to disable. '-1' to log progress every row


import csv
import sys
import os
import socket
import datetime
import time
import re
import pprint
import shutil
import string
from optparse import make_option
from decimal import Decimal

from django.db import transaction
from django.db import IntegrityError
from django.utils.encoding import DjangoUnicodeDecodeError


from ESP.settings import DATA_DIR
from ESP.settings import DATE_FORMAT
from ESP.settings import DEBUG
from ESP.settings import ETL_MEDNAMEREVERSE
from ESP.utils import log
from ESP.utils import str_from_date
from ESP.utils import date_from_str
from ESP.utils import height_str_to_cm
from ESP.utils import weight_str_to_kg
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
from ESP.emr.management.commands.common import LoaderCommand


    
# 
# Set global values that will be used by all functions
#
global UPDATED_BY, TIMESTAMP, UNKNOWN_PROVIDER
UPDATED_BY = 'load_epic'
TIMESTAMP = datetime.datetime.now()
UNKNOWN_PROVIDER = Provider.objects.get(natural_key='UNKNOWN')
ETL_FILE_REGEX = re.compile(r'^epic\D\D\D\.esp\.(\d\d)(\d\d)(\d\d\d\d)$')

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


def date_from_filepath(filepath):
    '''
    Extracts datestamp from ETL file path
    '''
    filename = os.path.basename(filepath)
    assert  ETL_FILE_REGEX.match(filename)
    match = ETL_FILE_REGEX.match(filename)
    month = int(match.groups()[0])
    day = int(match.groups()[1])
    year = int(match.groups()[2])
    return datetime.date(day=day, month=month, year=year)



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
    __patient_cache = {} # {patient_id: Patient instance}
    __provider_cache = {} # {provider_id: Provider instance}
    
    def __init__(self, filepath):
        assert os.path.isfile(filepath)
        path, filename = os.path.split(filepath)
        self.filename = filename
        self.filepath = filepath
        prov, created = Provenance.objects.get_or_create(source=filename)
        prov.wtimestamp = TIMESTAMP
        prov.hostname = socket.gethostname()
        prov.status = 'attempted'
        prov.save()
        if created:
            log.debug('Creating new provenance record #%s for %s' % (prov.pk, filename))
        else:
            log.debug('Updating existing provenance record #%s for %s' % (prov.pk, filename))
        self.provenance = prov
        file_handle = open(filepath)
        self.line_count = len(file_handle.readlines())
        file_handle.seek(0) # Reset file position after counting lines
        self.reader = csv.DictReader(file_handle, fieldnames=self.fields, dialect='epic')
        self.created_on = datetime.datetime.now()
    
    def get_patient(self, natural_key):
        if not natural_key:
            raise LoadException('Called get_patient() with empty patient_id')
        if not natural_key in self.__patient_cache:
            try:
                p = Patient.objects.get(natural_key=natural_key)
            except Patient.DoesNotExist:
                p = Patient(
                    natural_key=natural_key,
                    provenance = self.provenance,
                    )
                p.save()
            self.__patient_cache[natural_key] = p
        return self.__patient_cache[natural_key]
    
    def get_provider(self, natural_key):
        if not natural_key:
            return UNKNOWN_PROVIDER
        if not natural_key in self.__provider_cache:
            try:
                p = Provider.objects.get(natural_key=natural_key)
            except Provider.DoesNotExist:
                p = Provider(natural_key=natural_key)
                p.provenance = self.provenance
                p.save()
            self.__provider_cache[natural_key] = p
        return self.__provider_cache[natural_key]
    
    def insert_or_update(self, model, field_values, key_fields):
        '''
        Attempts to create a new instance of model using field_values.  If 
        create fails due to constraint (e.g. unique key), fetches existing 
        object using fields named in key_fields.
        
        @param model: Model to insert/update 
        @type model:  Django ORM Model
        @param field_values: Field names/values to create/update
        @type field_values:  Dict {field_name: value}
        @type key_fields: The field(s) to use as lookup key for updates
        @type key_fields: List [field_name, field_name, ...]
        @return: (obj, created)  Where obj is an instance of model, and created is boolean
        '''
        sid = transaction.savepoint()
        try:
            obj = model(**field_values)
            obj.save()
            transaction.savepoint_commit(sid) # not terribly useful, since we already saved it above.
            created = True
        except IntegrityError:
            transaction.savepoint_rollback(sid)
            
            keys = {}
            for field_name in key_fields:
                keys[field_name] = field_values[field_name]
                del field_values[field_name]
            log.debug('Could not insert new %s with keys %s' % (model, keys))
            # We use get_or_create() rather than get(), to increase the likelihood
            # of successful load in unforeseen circumstances
            obj, created = model.objects.get_or_create(defaults=field_values, **keys)
            for field_name in field_values:
                setattr(obj, field_name, field_values[field_name])
            obj.save()
        return obj, created
        
    def float_or_none(self, str):
        if not str:
            return None
        m = self.float_catcher.match(str)
        if m and m.groups():
            result = float(m.groups()[0])
        else:
            result = None
        if result == float('infinity'): # Rare edge case, but it does happen
            result = None
        return result
    
    def date_or_none(self, str):
        if not str:
            return None
        try:
            return date_from_str(str)
        except ValueError:
            return None
        
    def decimal_or_none(self, str):
        return Decimal(str) if str else None
        
    __string_sanitizer = re.compile(r'[\x80-\xFF]')
    
    def sanatize_str(self,s):
        '''
        Sanitizes strings be replacing non-ASCII characters with a "?"
        @param s: String to be sanitized
        @type  s: String
        @rtype:   String
        '''
        return self.__string_sanitizer.sub("?", s)
        
    def string_or_none(self, s):
        '''
        Returns a Django-safe version of string s.  If s evaluates to false, 
        e.g. empty string, return None object.
        '''
        if s:
           return self.sanatize_str(s)
        else:
            return None
    
    def capitalize(self, s):
        '''
        Returns a capitalized, Django-safe version of string s.  
        Returns None if s evaluates to None, including blank string.
        '''
        if s:
            return string.capwords( self.sanatize_str(s) )
        else:
            return None
        
    def up(self, s):
        '''
        Returns a all upper case string, . 
        Returns None if s evaluates to None, including blank string.
        '''
        if s:
            return string.upper( self.sanatize_str(s) )
        else:
            return None
    
    
    def generateNaturalkey (self,natural_key):
        if not natural_key:
            log.info('Record has blank natural_key, which is required, creating new one')
            return int(time.time()*1000)
        else:
            return natural_key
        
    @transaction.commit_on_success
    def load(self):
        # 
        # We can put error control here as it becomes necessary
        #
        log.info('Loading file "%s" with %s' % (self.filepath, self.__class__))
        cur_row = 0 # Row counter
        valid = 0 # Number of valid records loaded
        errors = 0 # Number of non-fatal errors encountered
        start_time = datetime.datetime.now()
        for row in self.reader:
            if not row:
                continue # Skip None objects
            cur_row += 1 # Increment the counter
            # changed to > because last line is not a footer,dont skip
            if cur_row > self.line_count:
                break
            # check this, too -- in case there are extra blank lines at end of file
            if row[self.fields[0]].upper() == 'CONTROL TOTALS':
                break
            # Coerce to unicode
            for key in row:
                if row[key]:
                    try:
                        row[key] = self.sanatize_str( row[key].strip() )
                    except DjangoUnicodeDecodeError, e:
                        #
                        # Log character set errors to db
                        #
                        err = EtlError()
                        err.provenance = self.provenance
                        err.line = cur_row
                        err.err_msg = str(e)[:512]
                        err.data = pprint.pformat(row)
                        err.save()
            sid = transaction.savepoint()
            # Load the data, with error handling
            if DEBUG:
                ex_to_catch = []
            else:
                ex_to_catch = [BaseException]
            try:
                self.load_row(row)
                transaction.savepoint_commit(sid)
                valid += 1
            except KeyboardInterrupt, e:
                # Allow keyboard interrupt to rise to next catch in main()
                transaction.savepoint_rollback(sid)
                raise e
            except ex_to_catch, e:
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

            if (ROW_LOG_COUNT == -1) or (ROW_LOG_COUNT and not (cur_row % ROW_LOG_COUNT) ):
                now = datetime.datetime.now()
                elapsed_time = now - start_time
                elapsed_seconds = elapsed_time.seconds or 1 # Avoid divide by zero on first few records if startup is quick
                rows_per_sec = float(cur_row) / elapsed_seconds
                log.info('Loaded %s of %s rows:  %s %s (%.2f rows/sec)' % (cur_row, self.line_count, now, self.filename, rows_per_sec))
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
    
    def load_row(self, row):
        if not ''.join([i[1] for i in row.items()]): # Concatenate all fields
            log.debug('Empty row encountered -- skipping')
            return
        natural_key = self.generateNaturalkey(row['natural_key'])
        # load provider in cache if not there, but natural key will never be null here
        p = self.get_provider(natural_key)
        values = {
        'natural_key': natural_key,
        'provenance' : self.provenance,
        #'updated_by' : UPDATED_BY,
        'last_name' : unicode(row['last_name']),
        'first_name' : unicode(row['first_name']),
        'middle_name' : unicode(row['middle_name']),
        'title' : self.string_or_none(row['title']),
        'dept_natural_key' : row['dept_natural_key'],
        'dept' : self.string_or_none(row['dept']),
        'dept_address_1' : row['dept_address_1'], 
        'dept_address_2' : row['dept_address_2'],
        'dept_city' : row['dept_city'],
        'dept_state' : row['dept_state'],
        'dept_zip' : row['dept_zip'],
        'area_code' : row['area_code'],
        'telephone' : row['telephone'],
        }
        p, created = self.insert_or_update(Provider, values, ['natural_key'])
        
        log.debug('Saved provider object: %s' % p)


class PatientLoader(BaseLoader):
    
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
        ]
    
    def load_row(self, row):
        natural_key = self.generateNaturalkey(row['natural_key'])
        p = self.get_patient(natural_key)
        
        values = {
        'natural_key': natural_key,
        'provenance' : self.provenance,
        #'updated_by' : UPDATED_BY,
        'mrn' : row['mrn'],
        'last_name' : self.string_or_none(row['last_name']),
        'first_name' : self.string_or_none(row['first_name']),
        'middle_name' : self.string_or_none(row['middle_name']),
        'pcp' : self.get_provider(row['pcp_id']),
        'address1' : self.string_or_none(row['address1']),
        'address2' : self.string_or_none(row['address2']),
        'city' : row['city'],
        'state' : row['state'],
        'zip' : row['zip'],
        'zip5' : p._calculate_zip5(),
        'country' : row['country'],
        'areacode' : row['areacode'],
        'tel' : row['tel'],
        'tel_ext' : row['tel_ext'],
        'date_of_birth' : self.date_or_none(row['date_of_birth']),
        'date_of_death' : self.date_or_none(row['date_of_death']),
        'gender' : row['gender'],
        'race' : self.string_or_none(row['race']),
        'home_language' : self.string_or_none(row['home_language']),
        'ssn' : self.string_or_none(row['ssn']),
        'marital_stat' : self.string_or_none(row['marital_stat']),
        'religion' : self.string_or_none(row['religion']),
        'aliases' : self.string_or_none(row['aliases']),
        'mother_mrn' : row['mother_mrn'],
        }
        p, created = self.insert_or_update(Patient, values, ['natural_key'])
        
        log.debug('Saved patient object: %s' % p)


class LabResultLoader(BaseLoader):
    
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
        'procedure_name' ,      #22
        'natural_key'           #23 added in 3
        ]

    
    def load_row(self, row):
        native_code = self.string_or_none(row['cpt'])
        component = self.string_or_none(row['component'])
        if component:
            # We only use first 20 characters of component, since some lab 
            # results (always types unimportant to ESP) have quite long 
            # component values, yet we need the native_code field to be a 
            # reasonable width for indexing.  
            if len(component) > 20:
                log.warning('Component field is greater than 20 characters, and will be truncated:')
                log.warning('    "%s"' % component)
            native_code = component[0:20] 
        if not row['natural_key']:
            natural_key = self.generateNaturalkey(row['natural_key']).__str__()
            if native_code:
                natural_key = natural_key + native_code
        else:
            natural_key = row['natural_key']
        
        values = {
        'provenance' : self.provenance,
        'patient' : self.get_patient(row['patient_id']),
        'provider' : self.get_provider(row['provider_id']),
        'mrn' : row['mrn'],
        'order_natural_key' : row['order_natural_key']  ,
        'date' : self.date_or_none(row['order_date']),
        'result_date' : self.date_or_none(row['result_date']),
        'native_code' : native_code,
        'native_name' : self.string_or_none(row['component_name']),
        'result_string' : row['result_string'],
        'result_float' : self.float_or_none(row['result_string']),
        'ref_low_string' : row['ref_low'],
        'ref_high_string' : row['ref_high'],
        'ref_low_float' : self.float_or_none(row['ref_low']),
        'ref_high_float' : self.float_or_none(row['ref_high']),
        'ref_unit' : self.string_or_none(row['unit']),
        'abnormal_flag' : row['normal_flag'],
        'status' : self.string_or_none(row['status']),
        'comment' : self.string_or_none(row['note']),
        'specimen_num' : self.string_or_none(row['specimen_num']),
        'impression' : self.string_or_none(row['impression']),
        'specimen_source' : self.string_or_none(row['specimen_source']),
        'collection_date' : self.date_or_none(row['collection_date']),
        'procedure_name' : self.string_or_none(row['procedure_name']),
        'natural_key' : natural_key,
         }
        lx, created = self.insert_or_update(LabResult, values, ['natural_key'])
        
        log.debug('Saved Lab Result object: %s' % lx)
        

class LabOrderLoader(BaseLoader):    
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
    
    def load_row(self, row):
        natural_key = self.generateNaturalkey(row['natural_key'])
        values = {
            'provenance' : self.provenance,
            'patient' : self.get_patient(row['patient_id']),
            'provider' : self.get_provider(row['provider_id']),
            'mrn' : row['mrn'],
            'natural_key' : natural_key,
            'procedure_code' : self.string_or_none(row['procedure_code']),
            'procedure_modifier' : self.string_or_none(row['procedure_modifier']),
            'specimen_id' : self.string_or_none(row['specimen_id']),
            'date' : self.date_or_none(row['ordering_date']),
            'order_type' : self.string_or_none(row['order_type']),
            'procedure_name' : self.string_or_none(row['procedure_name']),
            'specimen_source' : self.string_or_none(row['specimen_source'])
            
            }
        lxo, created = self.insert_or_update(LabOrder, values, ['natural_key'])
        
        log.debug('Saved LabOrder object: %s' % lxo)


class EncounterLoader(BaseLoader):
    
    feet_regex = re.compile('(?P<feet>\d)\' *(?P<inches>\d{1,2})')
    
    # Please see Caching Note on BaseLoader.
    __icd9_cache = {} # {code: icd9_obj}
    
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
        'cpt',#
        'weight',
        'height',
        'bp_systolic',
        'bp_diastolic',
        'o2_stat',
        'peak_flow',
        'icd9s',
        'raw_diagnosis',
        'bmi' # added in 3
        ]
    
    def load_row(self, row):
        # Util methods
        cap = self.capitalize
        up = self.up
        son = self.string_or_none
        dton = self.date_or_none
        flon = self.float_or_none
        natural_key = self.generateNaturalkey(row['natural_key'])
        values = {
            'natural_key': natural_key,
            'provenance': self.provenance,
            'patient': self.get_patient(row['patient_id']),
            'mrn' : row['mrn'],
            'provider': self.get_provider(row['provider_id']),
            'date': dton(row['encounter_date']),
            'raw_date': son(row['encounter_date']),
            'site_natural_key': son( row['site_natural_key'] ),
            'encounter_type': up(row['event_type']),
            'date_closed': dton(row['date_closed']),
            'raw_date_closed': son(row['date_closed']),
            'site_name': cap(row['site_name']),
            'raw_temperature': son(row['temp']),
            'temperature': flon(row['temp']),
            'raw_bp_systolic': son(row['bp_systolic']),
            'bp_systolic': flon(row['bp_systolic']),
            'raw_bp_diastolic': son(row['bp_diastolic']),
            'bp_diastolic': flon(row['bp_diastolic']),
            'raw_o2_stat': son(row['o2_stat']),
            'o2_stat': flon(row['o2_stat']),
            'raw_peak_flow': son(row['peak_flow']),
            'peak_flow': flon(row['peak_flow']),
            'raw_edd': son(row['edd']),
            'edd': dton(row['edd']),
            'raw_weight': son(row['weight']),
            'weight': weight_str_to_kg(row['weight']),
            'raw_height': son(row['height']),
            'height': height_str_to_cm(row['height']),
            'raw_bmi': son(row['bmi']),
            'raw_diagnosis': son(row['raw_diagnosis']),
            }
        if values['edd']:  
            values['pregnant'] = True
            
        e, created = self.insert_or_update(Encounter, values, ['natural_key'])
        e.bmi = e._calculate_bmi() # No need to save until we finish ICD9s
        #
        # ICD9 Codes
        #
        # TODO issue 329 this will change once we use the new diagnosis object
        if not created: # If updating the record, purge old ICD9 list
            e.icd9_codes = []
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
                i = Icd9.objects.get(code__exact=code)
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
        'patient_id',
        'mrn',
        'natural_key',
        'provider_id',
        'order_date',
        'status',
        'directions',#field 7
        'ndc',
        'drug_desc',# name, field 9
        'quantity',
        'refills',
        'start_date',
        'end_date',
        'route',# added in 3
        'dose', # added in 3
        
    ]

    def load_row(self, row, ):
        
        # setting to load 2.x data
        if ETL_MEDNAMEREVERSE:
            name = self.string_or_none(row['directions'])
            directions = self.string_or_none(row['drug_desc'])
        else:
            name = self.string_or_none(row['drug_desc'])
            directions = self.string_or_none(row['directions'])
            
        natural_key = self.generateNaturalkey(row['natural_key'])
        values = {
        'provenance' : self.provenance,
       #'updated_by' : UPDATED_BY,
        'patient' : self.get_patient(row['patient_id']),
        'mrn' : row['mrn'],
        'provider' : self.get_provider(row['provider_id']),
        'natural_key' : natural_key,
        'date' : self.date_or_none(row['order_date']),
        'status' : self.string_or_none(row['status']),
        'name' : name,
        'directions' : directions,
        'code' : row['ndc'],
        'quantity' : row['quantity'],
        'quantity_float' : self.float_or_none(row['quantity']),
        'refills' : self.string_or_none(row['refills']),
        'start_date' : self.date_or_none(row['start_date']),
        'end_date' : self.date_or_none(row['end_date']),
        'route' : self.string_or_none(row['route']),
        'dose' : self.string_or_none(row['dose']),
        }
        p, created = self.insert_or_update(Prescription, values, ['natural_key'])
        
        log.debug('Saved prescription object: %s' % p)



class ImmunizationLoader(BaseLoader):
    
    fields = [
        'patient_id', 
        'type', 
        'name',
        'date',
        'dose',
        'manufacturer',
        'lot',
        'natural_key',
        'mrn', #added in 3
        'provider_id',# added in 3
        'visit_date' #added in 3
        ]
    
    def load_row(self, row):
        natural_key = self.generateNaturalkey(row['natural_key'])
        values = {
        'provenance' : self.provenance,
        #'updated_by' : UPDATED_BY,
        'patient' : self.get_patient(row['patient_id']),
        'imm_type' : self.string_or_none(row['type']),
        'name' : self.string_or_none(row['name']),
        'date' : self.date_or_none(row['date']),
        'dose' : self.string_or_none(row['dose']),
        'manufacturer' : self.string_or_none(row['manufacturer']),
        'lot' : self.string_or_none(row['lot']),
        'natural_key' : natural_key,
        'mrn' : row['mrn'],
        'provider' : self.get_provider(row['provider_id']),
        'visit_date' : self.date_or_none(row['visit_date']),
        }
        i, created = self.insert_or_update(Immunization, values, ['natural_key'])
        
        log.debug('Saved immunization object: %s' % i)


class SocialHistoryLoader(BaseLoader):
    fields = [
        'patient_id',
        'mrn',
        'tobacco_use',
        'alcohol_use',
        'date_noted', #added in 3
        'natural_key', #added in 3
        'provider_id', # added in 3 cch added
        ]
    
    def load_row(self, row):
        # version 2 did not load this object, 
        natural_key = self.generateNaturalkey(row['natural_key'])
        values = {
            'natural_key': natural_key,
            'provenance' : self.provenance,
            # this date field will only work with version 3 etl
            'date' : self.date_or_none(row['date_noted']), # matching version 3 ETL
            'patient' : self.get_patient(row['patient_id']),
            'mrn' : row['mrn'],
            'tobacco_use' : row['tobacco_use'],
            'alcohol_use' : row['alcohol_use'],
            'provider' : self.get_provider(row['provider_id']),
            }
       
        s, created = self.insert_or_update(SocialHistory, values, ['natural_key'])
       
        log.debug('Saved provider object: %s' % s)
        

class AllergyLoader(BaseLoader):
    fields = [
        'patient_id',
        'mrn', 
        'problem_id',# maybe natural key
        'date_noted',
        'allergen_id',
        'allergy_name',
        'allergy_status',
        'allergy_description',
        'allergy_entered_date',
        'provider_id', #added in 3
        'natural_key' #added in 3 
        ]
    
    def load_row(self, row):
        
        allergy_name = self.string_or_none(row['allergy_name'])
        #adding new rows to allergen table if they are  not there 
        allergen, created = Allergen.objects.get_or_create(code=row['allergen_id'])
        
        if created:
            allergen.name = allergy_name
            allergen.save()
            log.info('created new allergen from load epic')
            
        natural_key = self.generateNaturalkey(row['natural_key'])
        values = {
            'natural_key': natural_key,
            'provenance' : self.provenance,
            'patient' : self.get_patient(row['patient_id']),
            'problem_id' : int(row['problem_id']),
            'date' : self.date_or_none(row['allergy_entered_date']), 
            'date_noted' : self.date_or_none(row['date_noted']),
            'allergen' : allergen,
            'name' : allergy_name, 
            'status' : self.string_or_none(row['allergy_status']),
            'description' : self.string_or_none(row['allergy_description']),
            'mrn' : row['mrn'],
            'provider' : self.get_provider(row['provider_id']),
        }
        
        a, created = self.insert_or_update(Allergy, values, ['natural_key'])
        
        log.debug('Saved Allergy object: %s' % a)
            
        
class ProblemLoader(BaseLoader):
    fields = [
        'patient_id',
        'mrn',
        'problem_id',# could be same as natural key
        'date_noted',
        'icd9_code',
        'problem_status',
        'comment',
        'natural_key',# added in 3
        'provider_id', #added in 3 added cch
        ]

    def load_row(self, row):
        code = row['icd9_code'].upper()
        icd9_code, created = Icd9.objects.get_or_create(code=code, defaults={
                'name':'Added by load_epic.py'})
        if created: log.warning('Could not find ICD9 code "%s" - creating new ICD9 entry.' % code)
        natural_key = self.generateNaturalkey(row['natural_key'])
        values = {
            'natural_key': natural_key, #TODO Fix me this might be the same of problemid
            'provenance' : self.provenance,
            'problem_id' : row['problem_id'],
            'patient' : self.get_patient(row['patient_id']),
            'mrn' : row['mrn'],
            'date' : self.date_or_none(row['date_noted']),
            'icd9' : icd9_code,
            'status' : self.string_or_none(row['problem_status']),
            'comment' : self.string_or_none(row['comment']),
            'provider' : self.get_provider(row['provider_id'])
            }
        
        p, created = self.insert_or_update(Problem, values, ['natural_key'])
        
        log.debug('Saved Problem object: %s' % p)

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
                if not ETL_FILE_REGEX.match(item):
                    log.debug('Invalid filename: %s' % item)
                    continue
                filepath = os.path.join(options['input_folder'], item)
                if not os.path.isfile(filepath):
                    continue
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
        if options['reload']:
            log.warning('You specified --reload, so files will be reloaded if already in database')
        for filepath in input_filepaths:
            path, filename = os.path.split(filepath)
            if (options['reload'] == False) and Provenance.objects.filter(source=filename, status__in=('loaded', 'errors')):
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
            filepath_list = filetype[ft]
            filepath_list.sort(key=lambda filepath: date_from_filepath(filepath))
            for filepath in filepath_list:
                loader_class = loader[ft]
                l = loader_class(filepath) # BaseLoader child instance
                if DEBUG:
                    ex_to_catch = []
                else:
                    ex_to_catch = [BaseException]
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
                except ex_to_catch, e: # Unhandled exception!
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
