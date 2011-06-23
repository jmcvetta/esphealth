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
import re
import pprint
import shutil
import string
from optparse import make_option
from decimal import Decimal

from django.db import transaction
from django.db import IntegrityError
from django.utils.encoding import smart_str
from django.utils.encoding import smart_unicode
from django.utils.encoding import DjangoUnicodeDecodeError

from ESP.settings import DATA_DIR
from ESP.settings import DATE_FORMAT
from ESP.settings import DEBUG
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
UNKNOWN_PROVIDER = Provider.objects.get(provider_id_num='UNKNOWN')
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
    
    decimal_catcher = re.compile(r'(\d+\.?\d*)') 
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
    _patient_cache = {} # {patient_id_num: Patient instance}
    _provider_cache = {} # {provider_id_num: Provider instance}
    
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
    
    def get_patient(self, patient_id_num):
        if not patient_id_num:
            raise LoadException('Called get_patient() with empty patient_id_num')
        if not patient_id_num in self._patient_cache:
            try:
                p = Patient.objects.get(patient_id_num=patient_id_num)
            except Patient.DoesNotExist:
                p = Patient(
                    patient_id_num=patient_id_num,
                    provenance = self.provenance,
                    )
                p.save()
            self._patient_cache[patient_id_num] = p
        return self._patient_cache[patient_id_num]
    
    def get_provider(self, provider_id_num):
        if not provider_id_num:
            return UNKNOWN_PROVIDER
        if not provider_id_num in self._provider_cache:
            try:
                p = Provider.objects.get(provider_id_num=provider_id_num)
            except Provider.DoesNotExist:
                p = Provider(provider_id_num=provider_id_num)
                p.provenance = self.provenance
                p.save()
            self._provider_cache[provider_id_num] = p
        return self._provider_cache[provider_id_num]
    
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
        #
        # Sanitize string values before sending to db.  We cannot sanitize all
        # fields, because some are model instances.  Those are converted by
        # smart_str() into a sanitized version of their string representation,
        # which is useless for saving to the database.
        #
        for field in field_values:
            value = field_values[field]
            if type(value) in [str, unicode]:
                sanitized_value = smart_unicode(value, errors='replace')
                field_values[field] = sanitized_value
        sid = transaction.savepoint()
        #
        # First try to create a new instance.  Integrity error indicates a
        # constraint has been violated - i.e. there is an existing object that
        # should be updated.  We roll back to the savepoint to restore
        # integrity in the transaction, then fetch the existing object for
        # update.
        #
        try:
            obj = model(**field_values)
            obj.save()
            transaction.savepoint_commit(sid)
            created = True
        except IntegrityError:
            transaction.savepoint_rollback(sid)
            keys = {}
            for field_name in key_fields:
                keys[field_name] = field_values[field_name]
                del field_values[field_name]
            # We use get_or_create() rather than get(), to increase the likelihood
            # of successful load in unforseen circumstances
            obj, created = model.objects.get_or_create(defaults=field_values, **keys)
            for field_name in field_values:
                setattr(obj, field_name, field_values[field_name])
            obj.save()
        return obj, created
        
    def decimal_or_none(self, str):
        if not str:
            return None
        m = self.decimal_catcher.match(str)
        if m and m.groups():
            result = Decimal(m.groups()[0])
        else:
            result = None
        if result == Decimal('infinity'): # Rare edge case, but it does happen
            result = None
        return result
    
    def date_or_none(self, str):
        if not str:
            return None
        try:
            return date_from_str(str)
        except ValueError:
            return None
        
    def string_or_none(self, s):
        '''
        Returns a Django-safe version of string s.  If s evaluates to false, 
        e.g. empty string, return None object.
        '''
        if s:
            return smart_str(s)
        else:
            return None
    
    def capitalize(self, s):
        '''
        Returns a capitalized, Django-safe version of string s.  
        Returns None if s evaluates to None, including blank string.
        '''
        if s:
            return string.capwords( smart_str(s) )
        else:
            return None
    
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
            # The last line is a footer, so we skip it
            if cur_row >= self.line_count:
                break
            # check this, too -- in case there are extra blank lines at end of file
            if row[self.fields[0]].upper() == 'CONTROL TOTALS':
                break
            # Coerce to unicode
            for key in row:
                if row[key]:
                    try:
                        row[key] = smart_unicode(row[key].strip())
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
        #
        # Sanity checks
        #
        if not ''.join([i[1] for i in row.items()]): # Concatenate all fields
            log.debug('Empty row encountered -- skipping')
            return
        pin = row['provider_id_num']
        if not pin:
            raise LoadException('Record has blank provider_id_num, which is required')
        #
        # Utility methods
        #
        cap = self.capitalize
        son = self.string_or_none
        daton = self.date_or_none
        decon = self.decimal_or_none
        #
        # Populate field values
        #
        values = {
            'provider_id_num': pin,
            'provenance': self.provenance,
            'last_name': son(row['last_name']),
            'first_name': son(row['first_name']),
            'middle_name': son(row['middle_name']),
            'title': son(row['title']),
            'dept_id_num': son(row['dept_id_num']),
            'dept': son(row['dept']),
            'dept_address_1': son(row['dept_address_1']),
            'dept_address_2': son(row['dept_address_2']),
            'dept_city': son(row['dept_city']),
            'dept_state': son(row['dept_state']),
            'dept_zip': son(row['dept_zip']),
            'area_code': son(row['area_code']),
            'telephone': son(row['telephone']),
            }
        #
        # Create Provider object
        #
        p, created = self.insert_or_update(Provider, values, ['provider_id_num'])
        self._provider_cache[pin] = p
        log.debug('Saved provider object: %s' % p)
        return p



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

    def populate_from_row(self, field_map, row):
        '''
        Populate objects based on fields in a row
        '''
        for field in field_map:
            value = row[field_map[field]]
            if value:
                field = smart_str(value)
            else:
                field = None
        
    def load_row(self, row):
        #
        # Utility methods
        #
        cap = self.capitalize
        son = self.string_or_none
        daton = self.date_or_none
        decon = self.decimal_or_none
        #
        # Natural key
        #
        id_num = son(row['patient_id_num'])
        if not id_num:
            raise LoadException('Record has blank patient_id_num, which is required')
        #
        # Field values
        #
        values = {
            'patient_id_num': id_num,
            'pcp': self.get_provider(row['provider_id_num']),
            'provenance': self.provenance,
            'date_of_birth': daton(row['date_of_birth']),
            'date_of_death': daton(row['date_of_death']),
            'mrn': son(row['mrn']),
            'last_name': son(row['last_name']),
            'first_name': son(row['first_name']),
            'middle_name': son(row['middle_name']),
            'address1': son(row['address1']),
            'address2': son(row['address2']),
            'city': son(row['city']),
            'state': son(row['state']),
            'zip': son(row['zip']),
            'country': son(row['country']),
            'areacode': son(row['areacode']),
            'tel': son(row['tel']),
            'tel_ext': son(row['tel_ext']),
            'gender': son(row['gender']),
            'race': son(row['race']),
            'home_language': son(row['home_language']),
            'ssn': son(row['ssn']),
            'marital_stat': son(row['marital_stat']),
            'religion': son(row['religion']),
            'aliases': son(row['aliases']),
            'mother_mrn': son(row['mother_mrn']),
            }
        p, created = self.insert_or_update(Patient, values, ['patient_id_num'])
        p.zip5 = p._calculate_zip5()
        p.save()
        self._patient_cache[id_num] = p
        log.debug('Saved patient object: %s' % p)
        return p
        

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
        l.result_float = self.decimal_or_none(l.result_string)
        l.ref_low_string = row['ref_low']
        l.ref_high_string = row['ref_high']
        l.ref_low_float = self.decimal_or_none(row['ref_low'])
        l.ref_high_float = self.decimal_or_none(row['ref_high'])
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
        'cpt',#
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
        # Util methods
        cap = self.capitalize
        son = self.string_or_none
        daton = self.date_or_none
        decon = self.decimal_or_none
        values = {
            'native_encounter_num': row['encounter_id_num'].strip(),
            'provenance': self.provenance,
            'patient': self.get_patient(row['patient_id_num']),
            'provider': self.get_provider(row['provider_id_num']),
            'date': daton(row['encounter_date']),
            'native_site_num': son( row['dept_id_num'] ),
            'event_type': cap(row['event_type']),
            'closed_date': daton(row['closed_date']),
            'site_name': cap(row['dept_name']),
            'temperature': decon(row['temp']),
            'bp_systolic': decon(row['bp_systolic']),
            'bp_diastolic': decon(row['bp_diastolic']),
            'o2_stat': decon(row['o2_stat']),
            'peak_flow': decon(row['peak_flow']),
            'edc': daton(row['edc']),
            'weight': weight_str_to_kg(row['weight']),
            'height': height_str_to_cm(row['height']),
            }
        if values['edc']:  
            values['pregnancy_status'] = True
        e, created = self.insert_or_update(Encounter, values, ['native_encounter_num'])
        e.bmi = e.calculate_bmi( row['bmi'] ) # No need to save until we finish ICD9s
        #
        # ICD9 Codes
        #
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
        p.quantity_float = self.decimal_or_none(row['quantity'])
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
            if (not options['reload'] ) and Provenance.objects.filter(source=filename, status__in=('loaded', 'errors')):
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
