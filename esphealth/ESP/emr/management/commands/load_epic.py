'''
                                  ESP Health
                            EMR ETL Infrastructure
                         EpicCare Extract File Loader


@author: Bob Zambarano <bzambarano@commoninf.com>
@organization: Commonwealth Informatics - http://www.commoninf.com
@contact: http://esphealth.org
@copyright: (c) 2013 Commonwealth Informatics
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''


EPIC_ENCODING = 'iso-8859-15'
#EPIC_ENCODING = 'windows-1252'

import csv
import sys
import os
import socket
import datetime
import time
import re
import pprint
import string
import collections
from optparse import make_option
from decimal import Decimal

from django.db import IntegrityError, transaction
from django.utils.encoding import DjangoUnicodeDecodeError
from django.core.mail import EmailMultiAlternatives

from ESP.settings import DEBUG, ETL_MEDNAMEREVERSE, ROW_LOG_COUNT, TRANSACTION_ROW_LIMIT
from ESP.utils import log
from ESP.utils.utils import float_or_none
from ESP.utils.utils import string_or_none
from ESP.utils.utils import sanitize_str
from ESP.utils.utils import truncate_str
from ESP.utils import date_from_str
from ESP.utils import height_str_to_cm
from ESP.utils import weight_str_to_kg
from ESP.utils import ga_str_to_days
from ESP.static.models import Icd9, Allergen
from ESP.emr.models import Provenance
from ESP.emr.models import EtlError
from ESP.emr.models import Provider
from ESP.emr.models import Patient
from ESP.emr.models import LabResult, LabOrder
from ESP.emr.models import Encounter, EncounterTypeMap
from ESP.emr.models import Prescription
from ESP.emr.models import Immunization, Pregnancy
from ESP.emr.models import SocialHistory, Problem, Allergy, Hospital_Problem
from ESP.emr.management.commands.common import LoaderCommand
from ESP.emr.base import SiteDefinition
from ESP.conf.models import VaccineCodeMap
from ESP.settings import SITE_NAME, EMAIL_SUBJECT_PREFIX, SERVER_EMAIL, MANAGERS, LOAD_REPORT_DIR

    
# 
# Set global values that will be used by all functions
#
global UPDATED_BY, TIMESTAMP, UNKNOWN_PROVIDER
UPDATED_BY = 'load_epic'
TIMESTAMP = datetime.datetime.now()
UNKNOWN_PROVIDER = Provider.objects.get(natural_key='UNKNOWN')
ETL_FILE_REGEX = re.compile(r'^epic\D\D\D\.esp\.(\d\d)(\d\d)(\d\d\d\d)$')
ICD9PAT_REGEX = re.compile(r'''
((E|V)? \d+ (\.\d+)?) | ([A-DF-UW-Z] \w*) | ([A-Z]{2} \w*) | (E|V)
''',
re.IGNORECASE | re.VERBOSE)

def date_from_filepath(filepath):
    '''
    Extracts datestamp from ETL file path
    '''
    filename = os.path.basename(filepath)
    match = ETL_FILE_REGEX.match(filename)
    assert match
    month = int(match.groups()[0])
    day = int(match.groups()[1])
    year = int(match.groups()[2])
    return datetime.date(day=day, month=month, year=year)


def datestring_from_filepath(filepath):
    '''
    Extracts datestring, in YYYYMMDD format, from ETL file path
    '''
    filename = os.path.basename(filepath)
    match = ETL_FILE_REGEX.match(filename)
    assert match
    month = match.groups()[0]
    day = match.groups()[1]
    year = match.groups()[2]
    return year + month + day


class EpicDialect(csv.Dialect):
    '''
    Describe the usual properties of EpicCare extract files.
    
    When reading, don't do any processing of embedded quotes.
    Otherwise, an unmatched double quote at the start of a field
    will cause the loader to read until it finds a matching double
    quote, despite any intervening field delimiters and line feeds.
    '''
    delimiter = '^'
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = '\r\n'
    quoting = csv.QUOTE_NONE
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
    
    def __init__(self, filepath, options):
        assert os.path.isfile(filepath)
        path, filename = os.path.split(filepath)
        self.filename = filename
        self.filepath = filepath
        file_handle = open(filepath)
        self.line_count = len(file_handle.readlines())
        prov, created = Provenance.objects.get_or_create(source=filename)
        prov.wtimestamp = TIMESTAMP
        prov.hostname = socket.gethostname()
        prov.data_date = date_from_filepath(filepath)
        prov.status = 'attempted'
        prov.raw_rec_count = self.line_count
        if created:
            log.debug('Creating new provenance record #%s for %s' % (prov.pk, filename))
        else:
            log.debug('Updating existing provenance record #%s for %s' % (prov.pk, filename))
            #set counters to zero
            prov.valid_rec_count = 0 
            prov.insert_count = 0 
            prov.update_count = 0 
            prov.post_load_count = 0
            prov.error_count = 0 
            
        prov.save()
        self.provenance = prov
        file_handle.seek(0) # Reset file position after counting lines
        self.reader = csv.DictReader(file_handle, fieldnames=self.fields, dialect='epic')
        self.created_on = datetime.datetime.now()
        self.inserted = 0
        self.updated = 0
        self.options = options
    
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
        #truncate the key some provider keys were too long
        natural_key = truncate_str(natural_key, 'natural_key', 128)
            
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
            #first try to create (insert) a new record
            obj = model(**field_values)
            obj.save()
            created = True
        except IntegrityError:
            #this integrity error we hope is due to a previously loaded record being updated, so now we try to update
            transaction.savepoint_rollback(sid)
            keys = {}
            for field_name in key_fields:
                keys[field_name] = field_values[field_name]
                del field_values[field_name]
            log.debug('Could not insert new %s with keys %s' % (model, keys))
            # We use get_or_create() rather than get(), to increase the likelihood
            # of successful load in unforeseen circumstances
            try:
                # Last try
                obj, created = model.objects.get_or_create(defaults=field_values, **keys)
                for field_name in field_values:
                    setattr(obj, field_name, field_values[field_name])
                obj.save()
            except:
                #most likely missing a non-null field
                transaction.savepoint_rollback(sid)
                log.warning('Record could not be saved')
                raise Exception('Record could not be saved.  System error was: ', sys.exc_info()[0]) 
        if created:
            self.inserted += 1
        else:
            self.updated +=1
        return obj, created
    
    def date_or_none(self, str):
        if not str:
            return None
        try:
            return date_from_str(str)
        except ValueError:
            return None
        
    def decimal_or_none(self, str):
        return Decimal(str) if str else None
        
    def capitalize(self, s):
        '''
        Returns a capitalized, Django-safe version of string s.  
        Returns None if s evaluates to None, including blank string.
        '''
        if s:
            return string.capwords( sanitize_str(s) )
        else:
            return None
        
    def up(self, s):
        '''
        Returns a all upper case string, . 
        Returns None if s evaluates to None, including blank string.
        '''
        if s:
            return string.upper( sanitize_str(s) )
        else:
            return None
    
    
    def generateNaturalkey (self,natural_key):
        if not natural_key:
            log.info('Record has blank natural_key, which is required, creating new one')
            return int(time.time()*1000)
        else:
            return natural_key
               
    def get_icd9(self, code, name, cache):
    
        '''
        Given an ICD9 code, as a string, return an Icd9 model instance
        '''
        if not code:
            log.info("ICD9 code is empty")
            return None
        code = code.upper()
        match = ICD9PAT_REGEX.match(code)
        if match:
            icd9code = match.group()
            if not icd9code in cache:
                i, created = Icd9.objects.get_or_create(code__exact=icd9code, defaults={
                     'code': icd9code,'name':name + ' (Added by load_epic.py)'})
    
                if created:
                    log.warning('Could not find ICD9 code "%s" - creating new ICD9 entry.' % icd9code)
                cache[icd9code] = i
                
            return cache[icd9code]
        else:
            log.info('Could not extract icd9 code: "%s"' % code)
            return None
    
    @transaction.commit_manually
    def load(self):
        # 
        # We can put error control here as it becomes necessary
        #
        log.info('Loading file "%s" with %s' % (self.filepath, self.__class__))
        cur_row = 0 # Row counter
        valid = 0 # Number of valid records loaded
        errors = 0 # Number of errors encountered
        start_time = datetime.datetime.now()
        for row in self.reader:
            sid = transaction.savepoint()
            cur_row += 1            
            # skip the footer, if present, at the end of the file
            if cur_row == self.line_count and row[self.fields[0]].upper() == 'CONTROL TOTALS':
                break
            if cur_row > self.line_count:
                break
            if self.fields.__len__() < row.__len__():
                errors += 1
                e = 'Skipping row. More items in row than fields'  
                err = EtlError()
                err.provenance = self.provenance
                err.line = cur_row
                err.err_msg = e
                err.data = pprint.pformat(row)
                try:
                    err.save()
                    transaction.commit()
                except:
                    transaction.savepoint_rollback(sid)
                    raise
                log.error('Skipping row %s. More than %s items in row.  Item count: %s ' 
                    % (cur_row, self.fields.__len__() , row.__len__() ))
                if not self.options['load_with_errors']:
                    raise BaseException(e)
                continue
            if not row:
                continue # Skip None objects
            for key in row:
                if row[key]:
                    try:
                        if not key:
                            # Not sure how this error could ever trigger since we've already checked for self.fields.__len__() < row.__len__()
                            errors += 1
                            e = ('There is a value that does not correspond to any field in line: %s for value: %s' % (cur_row,row[key]))  
                            err = EtlError()
                            err.provenance = self.provenance
                            err.line = cur_row
                            err.err_msg = e
                            err.data = pprint.pformat(row)
                            try:
                                err.save()
                                transaction.commit()
                            except:
                                transaction.savepoint_rollback(sid)
                                raise
                            log.error(e)
                            if not self.options['load_with_errors']:
                                raise BaseException(e)
                            continue
                        else:
                            row[key] = sanitize_str( row[key].strip() )
                    except DjangoUnicodeDecodeError, e:
                        #
                        # Log character set errors to db
                        #
                        err = EtlError()
                        err.provenance = self.provenance
                        err.line = cur_row
                        err.err_msg = str(e)[:512]
                        err.data = pprint.pformat(row)
                        try:
                            err.save()
                            transaction.commit()
                        except:
                            transaction.savepoint_rollback(sid)
                            raise
                        if not self.options['load_with_errors']:
                            raise e
                        continue
            # Load the data, with error handling
            try:
                self.load_row(row)
                valid += 1
            except KeyboardInterrupt, e:
                #Allow keyboard interrupt to rise to next catch in main()
                raise e
            except:
                log.error('Caught Exception:')
                log.error('  File: %s' % self.filename)
                log.error('  Line: %s' % cur_row)
                log.error('  Exception: \n%s' % sys.exc_info()[1])
                log.error(pprint.pformat(row))
                errors += 1
                #
                # Log ETL errors to db
                #
                err = EtlError()
                err.provenance = self.provenance
                err.line = cur_row
                err.err_msg = sys.exc_info()[1]
                err.data = pprint.pformat(row)
                err.timestamp = datetime.datetime.now()
                try:
                    err.save()
                    transaction.commit()
                except:
                    transaction.savepoint_rollback(sid)
                    raise
                if not self.options['load_with_errors']:
                    raise
                continue
            if (ROW_LOG_COUNT == -1) or (ROW_LOG_COUNT and not (cur_row % ROW_LOG_COUNT) ):
                now = datetime.datetime.now()
                elapsed_time = now - start_time
                elapsed_seconds = elapsed_time.seconds or 1 # Avoid divide by zero on first few records if startup is quick
                rows_per_sec = float(cur_row) / elapsed_seconds
                log.info('Loaded %s of %s rows:  %s %s (%.2f rows/sec)' % (cur_row, self.line_count, now, self.filename, rows_per_sec))
            if (valid % TRANSACTION_ROW_LIMIT) == 0:
                #commit when the row limit is reached
                transaction.commit()
        #commit at the end
        transaction.commit()
        log.info('Loaded %s records with %s errors.' % (valid, errors))

        self.provenance.status = 'loaded' if not errors else 'errors'
        self.provenance.valid_rec_count = valid
        self.provenance.error_count = errors
        self.provenance.post_load_count = self.prov_count()
        try:
            self.provenance.save()
            transaction.commit()
        except:
            transaction.rollback()
            raise
        return (valid, errors)
    
    def prov_count(self):
        '''
        For a given provenance ID
        provides a count of records in the primary target table with that ID.
        NB: This is expensive for large DB tables.
        '''
        prov_qs = self.model.objects.filter(provenance=self.provenance.provenance_id)
        counts = prov_qs.count()
        return counts
    
    def prov_delete(self):
        '''
        Delete all records associated with a given provenance_id 
        EXCEPT the provenance record
        '''
        prov_qs = self.model.objects.filter(provenance=self.provenance.provenance_id)
        try:
            prov_qs.delete()
            return True
        except:
            return False
        
    def load_summary(self):
        '''
        Writes and optionally Emails a set of summary info for each file
        '''
        db_count = self.provenance.post_load_count
        report = '+' * 80 + '\r'
        report = report + 'Load summary for source file: ' + self.filename + '\r'
        report = report +  'Number of rows in source file: ' + str(self.provenance.raw_rec_count) + '\r'
        report = report +  'Number of rows processed without error: ' + str(self.provenance.valid_rec_count) + '\r'
        report = report +  'Number or rows processed with error: ' + str(self.provenance.error_count) + '\r'
        if self.provenance.error_count > 0:
            report = report +  '  Here is a list of data row errors:' + '\r'
            etlerrs = EtlError.objects.filter(provenance=self.provenance.provenance_id)
            for etlerror in etlerrs:
                report = report + 'On row ' + str(etlerror.line) + ', error message was: ' + etlerror.err_msg + '\r'
        report = report + '+' * 80 + '\r'
        report = report +  'Number of database rows created (inserted): ' + str(self.inserted) + '\r'
        report = report +  'Number of updates performed on existing rows: ' + str(self.updated) + '\r'
        report = report +  'Number of rows in the EMR table having the current Provenance ID ' + str(self.provenance.provenance_id) + ': ' + str(db_count) + '\r'
        # basic checks for conditions that shouldn't occur, with appropriate messages if they do
        if ((self.provenance.error_count + self.provenance.valid_rec_count) != self.provenance.raw_rec_count):
            report = report +  'The count of file rows does not equal the count of rows processed (error rows + valid rows). Review carefully -- this should not be possible.' + '\r'
        if (((self.inserted + self.updated) != self.provenance.valid_rec_count)):
            report = report +  'The number of rows processed without error does not equal the sum of rows created plus updates. Review carefully -- this should not be possible.' + '\r'
        if (db_count != self.provenance.valid_rec_count):
            report = report +  'The number of DB rows with the current provenance ID does not equal the number of rows processed without error.' + '\r'
            report = report +  '  This is possible if there are duplicate natural keys, meaning the same DB row gets updated more than once.' + '\r'
            report = report +  '  If your data was pulled with multiple updates per record in the same file, this can be acceptable.' + '\r'
            report = report +  '  If the natural key is being duplicated incorrectly, this is not acceptable.  Review carefully.'     + '\r'
        if self.options['email_admin_reports']:
            msg = EmailMultiAlternatives(
               EMAIL_SUBJECT_PREFIX + ' Load_Epic Report for ' + SITE_NAME + ', Source file: ' + self.filename,
               report,
               SERVER_EMAIL, 
               [a[1] for a in MANAGERS],
               )
            html_content = '<pre>\n%s\n</pre>' % report
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        fpath=LOAD_REPORT_DIR
        log.info('Writing load report.' )
        efile=open(fpath+"load_epic_report_for_"+self.filename+'.txt','w')
        efile.write(report)
        efile.close()
        

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
        'center_id',
        ]
    
    model = Provider
    
    def load_row(self, row):
        
        non_empty_values=[]
        for v in row.values():
            if v:
                non_empty_values.append(v) # Gather all non-empty values
        concat_values = ''.join(non_empty_values)
        if concat_values.strip() == '':
            log.debug('Empty row encountered -- skipping')
            return 
        
        natural_key = self.generateNaturalkey(row['natural_key'])
        natural_key = truncate_str(natural_key, 'natural_key', 128)

        values = {
        # fetching natural key from p because it may have been truncated to 128 characters   
        'natural_key': natural_key,
        'provenance' : self.provenance,
        #'updated_by' : UPDATED_BY,
        'last_name' : unicode(row['last_name']),
        'first_name' : unicode(row['first_name']),
        'middle_name' : unicode(row['middle_name']),
        'title' : string_or_none(row['title']),
        'dept_natural_key' : row['dept_natural_key'],
        'dept' : string_or_none(row['dept']),
        'dept_address_1' : row['dept_address_1'], 
        'dept_address_2' : row['dept_address_2'],
        'dept_city' : row['dept_city'],
        'dept_state' : row['dept_state'],
        'dept_zip' : row['dept_zip'],
        'area_code' : row['area_code'],
        'telephone' : row['telephone'],
        'center_id' : row['center_id'],
        }

        try:
            p, created = self.insert_or_update(Provider, values, ['natural_key'])
            log.debug('Saved provider object: %s' % p)
            p = self.get_provider(natural_key)
        except:
            raise     

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
        'center_id',
        'ethnicity',
        ]
    
    model = Patient
    
    def load_row(self, row):       
        natural_key = self.generateNaturalkey(row['natural_key'])
        
        values = {
        'natural_key': natural_key,
        'provenance' : self.provenance,
        #'updated_by' : UPDATED_BY,
        'mrn' : row['mrn'],
        'last_name' : string_or_none(row['last_name']),
        'first_name' : string_or_none(row['first_name']),
        'middle_name' : string_or_none(row['middle_name']),
        'pcp' : self.get_provider(row['pcp_id']),
        'address1' : string_or_none(row['address1']),
        'address2' : string_or_none(row['address2']),
        'city' : row['city'],
        'state' : row['state'],
        'zip' : row['zip'],
        'country' : row['country'],
        'areacode' : row['areacode'],
        'tel' : row['tel'],
        'tel_ext' : row['tel_ext'],
        'date_of_birth' : self.date_or_none(row['date_of_birth']),
        'date_of_death' : self.date_or_none(row['date_of_death']),
        'gender' : row['gender'],
        'race' : string_or_none(row['race']),
        'home_language' : string_or_none(row['home_language']),
        'ssn' : string_or_none(row['ssn']),
        'marital_stat' : string_or_none(row['marital_stat']),
        'religion' : string_or_none(row['religion']),
        'aliases' : string_or_none(row['aliases']),
        'mother_mrn' : row['mother_mrn'],
        'center_id' : row['center_id'],
        'ethnicity' :string_or_none(row['ethnicity']),
        }

        try:
            p, created = self.insert_or_update(Patient, values, ['natural_key'])
            p.zip5 = p._calculate_zip5()
            p.save()
            log.debug('Saved patient object: %s' % p)
            p = self.get_patient(natural_key)
        except:
            raise
        

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
        'procedure_name' ,      # 22
        'natural_key',          # 23 added in 3
        'patient_class',        # 24 added in 3
        'patient_status'        # 25 added in 3

        ]

    model = LabResult
    
    def load_row(self, row):
        
        # set date based on the date in the ETL file name
        if self.options['use_filename_date'] and not row['order_date'] :            
            log.info('Empty date not allowed, using date from the ETL file name')
            date = datestring_from_filepath(self.filename)
        else:
            date = row['order_date']
            
        # We use the first 70 characters of component, since some lab 
        # results (always types unimportant to ESP) have quite long 
        # component values, yet we need the native_code field to be a 
        # reasonable width for indexing.  
        component = string_or_none(row['component'])  
        component = truncate_str(component, 'Component field', 70)
            
        cpt = string_or_none(row['cpt'])  
        if component and cpt:
            native_code = cpt + '--' + component
        elif cpt:
            native_code=cpt + '--'
        elif component:
            native_code = '--' + component
        else:
            native_code = None
        if not row['natural_key']:
            natural_key = self.generateNaturalkey(row['order_natural_key'])
            if native_code:
                natural_key = natural_key.__str__() + native_code
        else:
            natural_key = self.generateNaturalkey(row['natural_key'])
            
        # if no order natural key then assign the same as natural key
        if not row['order_natural_key']:
            row['order_natural_key'] = natural_key   
        
        values = {
        'provenance' : self.provenance,
        'patient' : self.get_patient(row['patient_id']),
        'provider' : self.get_provider(row['provider_id']),
        'order_type' : string_or_none(row['order_type']),
        'mrn' : row['mrn'],
        'order_natural_key' : row['order_natural_key']  ,
        'date' : self.date_or_none(date),
        'result_date' : self.date_or_none(row['result_date']),
        'native_code' : native_code,
        'native_name' : string_or_none(row['component_name']),
        'result_string' : row['result_string'],
        'result_float' : float_or_none(row['result_string']),
        'ref_low_string' : row['ref_low'],
        'ref_high_string' : row['ref_high'],
        'ref_low_float' : float_or_none(row['ref_low']),
        'ref_high_float' : float_or_none(row['ref_high']),
        'ref_unit' : string_or_none(row['unit']),
        'abnormal_flag' : row['normal_flag'],
        'status' : string_or_none(row['status']),
        'comment' : string_or_none(row['note']),
        'specimen_num' : string_or_none(row['specimen_num']),
        'impression' : string_or_none(row['impression']),
        'specimen_source' : string_or_none(row['specimen_source']),
        'collection_date' : self.date_or_none(row['collection_date']),
        'procedure_name' : string_or_none(row['procedure_name']),
        'natural_key' : natural_key,
        'patient_class' : string_or_none(row['patient_class']),
        'patient_status' : string_or_none(row['patient_status']),
         }
        try:
            lx, created = self.insert_or_update(LabResult, values, ['natural_key'])
            log.debug('Saved Lab Result object: %s' % lx)
        except:
            raise 
        

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
        'specimen_source',
        'test_status',
        'patient_class',
        'patient_status'
        ]
    
    model = LabOrder
    
    def load_row(self, row):
        
        # set date based on the date in the ETL file name
        if self.options['use_filename_date'] and not row['ordering_date'] :            
            log.info('Empty date not allowed, using date from the ETL file name')
            date = datestring_from_filepath(self.filename)
        else:
            date = row['ordering_date']
       
        natural_key = self.generateNaturalkey(row['natural_key'])
        values = {
            'provenance' : self.provenance,
            'patient' : self.get_patient(row['patient_id']),
            'provider' : self.get_provider(row['provider_id']),
            'mrn' : row['mrn'],
            'natural_key' : natural_key,
            'procedure_code' : string_or_none(row['procedure_code']),
            'procedure_modifier' : string_or_none(row['procedure_modifier']),
            'specimen_id' : string_or_none(row['specimen_id']),
            'date' : self.date_or_none(date),
            'order_type' : string_or_none(row['order_type']),
            'procedure_name' : string_or_none(row['procedure_name']),
            'specimen_source' : string_or_none(row['specimen_source']),
            'test_status' : string_or_none(row['test_status']),
            'patient_class' : string_or_none(row['patient_class']),
            'patient_status' : string_or_none(row['patient_status'])
            
            }
        try:
            lxo, created = self.insert_or_update(LabOrder, values, ['natural_key'])
            log.debug('Saved LabOrder object: %s' % lxo)
        except:
            raise


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
        'o2_sat',
        'peak_flow',
        'icd9s',
        'bmi',  # added in 3
        'hosp_admit_dt',  # added in 3
        'hosp_dschrg_dt' # added in 3
        ]
    
    model = Encounter
    
    #this gets used for default encounter type mapping
    mapper_dict = collections.defaultdict(list)
    mapper_qs = EncounterTypeMap.objects.all()
    for encmap in mapper_qs:
        mapper_dict[encmap.raw_encounter_type].append(encmap)
    
    def load_row(self, row): 
        #TODO change to load the  encounter type to the raw from the file
        # and load encounter type with the mapping table which is loaded manually
        # 
       
        #overriding the icd9 to unknown problem if it is empty 
        if not row['icd9s'] or row['icd9s'] =='':
            row['icd9s'] = '799.9'
        # Util methods    
        cap = self.capitalize
        up = self.up
        son = string_or_none
        dton = self.date_or_none
        flon = float_or_none
        natural_key = self.generateNaturalkey(row['natural_key'])
        
        edd = dton(row['edd'])
        encounter_date = dton(row['encounter_date'])
        # Compensate for bad estimated date of delivery values in the
        # Atrius ESP data feed by setting edd to None if either:
        #   edd is earlier than the encounter_date
        #   edd is more than 280 days in the future
        if edd and encounter_date:
            if edd < encounter_date:
                fmt = 'Ignoring estimated date of delivery (edd): edd (%s) < encounter date (%s)'
                log.info(fmt % (edd, encounter_date))
                edd = None
            elif edd > (encounter_date + datetime.timedelta(280)):
                fmt = 'Ignoring estimated date of delivery (edd): edd (%s) > encounter date (%s) + 280 days'
                log.info(fmt % (edd, encounter_date))
                edd = None
        
        values = {
            'natural_key': natural_key,
            'provenance': self.provenance,
            'patient': self.get_patient(row['patient_id']),
            'mrn' : row['mrn'],
            'provider': self.get_provider(row['provider_id']),
            'date': encounter_date,
            'raw_date': son(row['encounter_date']),
            'site_natural_key': son( row['site_natural_key'] ),
            'raw_encounter_type': up(row['event_type']),
            'date_closed': dton(row['date_closed']),
            'raw_date_closed': son(row['date_closed']),
            'site_name': cap(row['site_name']),
            'raw_temperature': son(row['temp']),
            'temperature': flon(row['temp']),
            'cpt': son(row['cpt']),
            'raw_bp_systolic': son(row['bp_systolic']),
            'bp_systolic': flon(row['bp_systolic']),
            'raw_bp_diastolic': son(row['bp_diastolic']),
            'bp_diastolic': flon(row['bp_diastolic']),
            'raw_o2_sat': son(row['o2_sat']),
            'o2_sat': flon(row['o2_sat']),
            'raw_peak_flow': son(row['peak_flow']),
            'peak_flow': flon(row['peak_flow']),
            'raw_edd': son(row['edd']),
            'edd': edd,
            'raw_weight': son(row['weight']),
            'weight': weight_str_to_kg(row['weight']),
            'raw_height': son(row['height']),
            'height': height_str_to_cm(row['height']),
            'raw_bmi': son(row['bmi']),
            'hosp_admit_dt': dton(row['hosp_admit_dt']),
            'hosp_dschrg_dt': dton(row['hosp_dschrg_dt'])
            }
        if values['edd']:  
            values['pregnant'] = True
        try:
            e, created = self.insert_or_update(Encounter, values, ['natural_key'])
        except:
            #pass it on up
            raise
        e.bmi = e._calculate_bmi() # No need to save until we finish ICD9s
        #fill out encounter_type and priority from mapping table if it has a value
        if  row['event_type'] and not option_site:
            try:
                e.encounter_type = self.mapper_dict.get(up(row['event_type']))[0].mapping
                e.priority = self.mapper_dict.get(up(row['event_type']))[0].priority
            except:
                log.debug('Unable to map encounter type for row %s' % self.line_count)
        elif option_site:
            site = SiteDefinition.get_by_short_name(option_site)
            e.encounter_type, e.priority = site.set_enctype(e)
        #
        # ICD9 Codes
        #
        # TODO issue 329 this will change once we use the new diagnosis object
        if not created: # If updating the record, purge old ICD9 list
            e.icd9_codes = []
        icd9 = row['icd9s']
        
        # code_strings are separated by semi-colon
        # within a code string, the code and optional text are separated by white space 
        for code_string in row['icd9s'].strip().split(';'):
            code_string = code_string.strip()
            firstspace = code_string.find(' ')
            if firstspace >= 0:
                code = code_string[:firstspace].strip()
                diagnosis_text = code_string[firstspace:].strip()
            else:
                code = code_string
                diagnosis_text = ''
            if len(code) >= 1 and any(c in string.digits for c in code):
                e.icd9_codes.add(self.get_icd9(code, diagnosis_text, self.__icd9_cache))  
        try:
            e.save()
            log.debug('Saved encounter object: %s' % e)
        except AttributeError as describe:
            log.warning('Could not save encounter object: %s' % e)
            log.warning('Error is: %s ' % describe)
            raise

class PrescriptionLoader(BaseLoader):

    fields = [
        'patient_id',
        'mrn',
        'order_natural_key',
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
        'patient_class', #added in 3
        'patient_status', # added in 3
        
    ]
    
    model = Prescription

    def load_row(self, row, ):
        
        # setting to load 2.x data
        if ETL_MEDNAMEREVERSE:
            name = string_or_none(row['directions'])
            directions = string_or_none(row['drug_desc'])
        else:
            name = string_or_none(row['drug_desc'])
            directions = string_or_none(row['directions'])
            
        if not name:
            name = 'UNKNOWN (value supplied by ESP)'  
              
        natural_key = self.generateNaturalkey(row['order_natural_key'] + row['order_date'])
        
        # some data sources have dirty (and lengthy) data in the 'refills' field.
        # Truncate the field at 200 characters
        refills = string_or_none(row['refills'])
        refills = truncate_str(refills, 'refills', 200)                                     

        # some data sources have dirty (and lengthy) data in the 'quantity' field.
        # Truncate the field at 200 characters
        quantity = string_or_none(row['quantity'])
        quantity = truncate_str(quantity, 'quantity', 200)                                     

        values = {
        'provenance' : self.provenance,
        #'updated_by' : UPDATED_BY,
        'order_natural_key' : row['order_natural_key'],
        'patient' : self.get_patient(row['patient_id']),
        'mrn' : row['mrn'],
        'provider' : self.get_provider(row['provider_id']),
        'natural_key' : natural_key,
        'date' : self.date_or_none(row['order_date']),
        'status' : string_or_none(row['status']),
        'name' : name,
        'directions' : directions,
        'code' : row['ndc'],
        'quantity' : quantity,
        'quantity_float' : float_or_none(quantity),
        'refills' : refills,
        'start_date' : self.date_or_none(row['start_date']),
        'end_date' : self.date_or_none(row['end_date']),
        'route' : string_or_none(row['route']),
        'dose' : string_or_none(row['dose']),
        'patient_class' : string_or_none(row['patient_class']),
        'patient_status' : string_or_none(row['patient_status']),
        
        }
        try:
            p, created = self.insert_or_update(Prescription, values, ['natural_key'])
            log.debug('Saved prescription object: %s' % p)
        except:
            raise

# this object was added for version 3 of esp
class PregnancyLoader(BaseLoader):
    
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
    
    model = Pregnancy
    
    def load_row(self,row):
        if not row['natural_key']:
            # if we don't have a pregnancy episode ID, use the combination
            # of patient ID and actual delivery date as the natural key
            actual_date = row['actual_date'] if row['actual_date'] else ''
            natural_key = self.generateNaturalkey(row['patient_id'] + actual_date)
        else:
            natural_key = self.generateNaturalkey(row['natural_key'])
            
        birth_weights = row['birth_weight']
        
        # set date based on the date in the ETL file name
        date = datestring_from_filepath(self.filename) 
        values = {
            'provenance' : self.provenance,
            'patient' : self.get_patient(row['patient_id']),
            'provider' : self.get_provider(row['provider_id']),
            'natural_key' : natural_key,
            'mrn' : row['mrn'],
            'outcome' : string_or_none(row['outcome']),
            'actual_date' : self.date_or_none(row['actual_date']),
            'edd' : self.date_or_none(row['edd']),
            'date' : self.date_or_none(date),
            'gravida' : self.decimal_or_none(row['gravida']),
            'parity' : self.decimal_or_none(row['parity']),
            'term' : self.decimal_or_none(row['term']),
            'preterm' : self.decimal_or_none(row['preterm']),
            'raw_birth_weight' : string_or_none(birth_weights),
            'ga_delivery' : ga_str_to_days(row['ga_delivery']),
            'delivery' : string_or_none(row['delivery']),
            'pre_eclampsia' : row['pre_eclampsia'],
            }
        try:
            p, created = self.insert_or_update(Pregnancy, values, ['natural_key'])
            p.births = 0        
            if not created: # If updating the record, purge old birth weights
                p.birth_weight = None
                p.birth_weight2 = None
                p.birth_weight3 = None
                
            for birth in birth_weights.strip().split(';'):
                birth = birth.strip()
                if birth != '':
                    p.births += 1
                    #get the weight     
                    if p.births == 1: 
                        p.birth_weight = weight_str_to_kg(birth)
                    elif  p.births == 2:  
                        p.birth_weight2 = weight_str_to_kg(birth)
                    elif  p.births ==3:  
                        p.birth_weight3 = weight_str_to_kg(birth)                   
            p.save()                
        except:
            #pass it on up
            raise
        
        log.debug('Saved pregnancy object: %s' % p)

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
        'provider_id', # added in 3
        'visit_date', # added in 3
        'imm_status', # added in 3
        'cpt_code', # added in 3
        'patient_class', # added in 3
        'patient_status' # added in 3
        ]
    
    model = Immunization
    
    def load_row(self, row):
        natural_key = self.generateNaturalkey(row['natural_key'])
        values = {
        'provenance' : self.provenance,
        #'updated_by' : UPDATED_BY,
        'patient' : self.get_patient(row['patient_id']),
        'imm_type' : string_or_none(row['type']),
        'name' : string_or_none(row['name']),
        'date' : self.date_or_none(row['date']),
        'dose' : string_or_none(row['dose']),
        'manufacturer' : string_or_none(row['manufacturer']),
        'lot' : string_or_none(row['lot']),
        'natural_key' : natural_key,
        'mrn' : row['mrn'],
        'provider' : self.get_provider(row['provider_id']),
        'visit_date' : self.date_or_none(row['visit_date']),
        'imm_status' : string_or_none(row['imm_status']),
        'cpt_code' : string_or_none(row['cpt_code']),
        'patient_class' : string_or_none(row['patient_class']),
        'patient_status' : string_or_none(row['patient_status']),
        }
        if self.options['use_filename_date'] and not values['date'] :            
            log.info('Empty date not allowed, using date from the ETL file name')
            values['date'] = datetime.datetime.strptime(datestring_from_filepath(self.filename), "%Y%m%d").strftime("%Y-%m-%d") 

        try:
            i, created = self.insert_or_update(Immunization, values, ['natural_key'])
            log.debug('Saved immunization object: %s' % i)
        except:
            raise
        
        try:
            nativevax, new = VaccineCodeMap.objects.get_or_create(
                    native_code=string_or_none(row['type']), native_name=string_or_none(row['name']))
            if new:
                log.debug('Saved new VaccineCodeMap entry: %s' %nativevax)
        except:
            log.debug('Could not save VaccineCodeMap entry: %s' %string_or_none(row['name']))
            raise


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
    
    model = SocialHistory
    
    def load_row(self, row):
        if self.options['use_filename_date'] and not row['date_noted'] :
            log.info('Empty date not allowed, using date from the ETL file name')
            date = datestring_from_filepath(self.filename)
        else:
            date = row['date_noted']
            
        if not row['natural_key']:
            natural_key = self.generateNaturalkey(row['patient_id'] + date)
        else:
            natural_key = self.generateNaturalkey(row['natural_key'])
        
        values = {
            'natural_key': natural_key,
            'provenance' : self.provenance,
            # this date field will only work with version 3 etl
            'date' : self.date_or_none(date), # matching version 3 ETL
            'patient' : self.get_patient(row['patient_id']),
            'mrn' : row['mrn'],
            'tobacco_use' : row['tobacco_use'],
            'alcohol_use' : row['alcohol_use'],
            'provider' : self.get_provider(row['provider_id']),
            }
       
        if DEBUG:
            ex_to_catch = []
        else:
            ex_to_catch = [BaseException]
        try:
            s, created = self.insert_or_update(SocialHistory, values, ['natural_key'])
            log.debug('Saved provider object: %s' % s)
        except ex_to_catch, e:
            raise e

class AllergyLoader(BaseLoader):
    fields = [
        'patient_id',
        'mrn', 
        'natural_key',#  problemid
        'date_noted',
        'allergen_id',
        'allergy_name',
        'allergy_status',
        'allergy_description',
        'allergy_entered_date',# added in 3
        'provider_id', #added in 3
        ]
    
    model = Allergy
        
    def load_row(self, row):        
        allergy_name = string_or_none(row['allergy_name'])
        
        if not row['allergen_id'] and not allergy_name:
            log.info('Empty allergy name and code encountered, setting allergy name to UNSPECIFIED')
            allergy_name = 'UNSPECIFIED'
            
        #adding new rows to allergen table if they are  not there 
        if row['allergen_id'].strip() != '':
            allergen, created = Allergen.objects.get_or_create(code=row['allergen_id'][:100])
        else:
            allergen, created = Allergen.objects.get_or_create(code=allergy_name)
        
        if created:
            allergen.name = allergy_name
            allergen.save()
            log.info('created new allergen from load epic')
            
        description = row['allergy_description']
            
        if  len(description) > 600 :
            log.warning('Allergy description longer than 600 characters, now truncating "%s"' % description )
            description = description[0:600]   
            
        natural_key = self.generateNaturalkey(row['natural_key'])
        values = {
            'natural_key': natural_key,
            'provenance' : self.provenance,
            'patient' : self.get_patient(row['patient_id']),
            'date' : self.date_or_none(row['allergy_entered_date']), 
            'date_noted' : self.date_or_none(row['date_noted']),
            'allergen' : allergen,
            'name' : allergy_name, 
            'status' : string_or_none(row['allergy_status']),
            'description' : string_or_none(description),
            'mrn' : row['mrn'],
            'provider' : self.get_provider(row['provider_id']),
        }
        try:
            a, created = self.insert_or_update(Allergy, values, ['natural_key'])
            log.debug('Saved Allergy object: %s' % a)
        except:
            #pass it on up
            raise
            
        
class ProblemLoader(BaseLoader):
    fields = [
        'patient_id',
        'mrn',
        'natural_key',# problemid 
        'date_noted',
        'icd9_code',
        'problem_status',
        'comment',
        'provider_id', #added in 3 added cch
        'hospital_pl_yn', #added in 3
        ]
    
    model = Problem

    def load_row(self, row):
        code = row['icd9_code']
        if not code or code =='':
            code = '799.9'
        icd9_code = self.get_icd9(code, '', {})
        
        natural_key = self.generateNaturalkey(row['natural_key'])
        values = {
            'natural_key': natural_key, 
            'provenance' : self.provenance,
            'patient' : self.get_patient(row['patient_id']),
            'mrn' : row['mrn'],
            'date' : self.date_or_none(row['date_noted']),
            'icd9' : icd9_code,
            'raw_icd9_code' : code,
            'status' : string_or_none(row['problem_status']),
            'comment' : string_or_none(row['comment']),
            'provider' : self.get_provider(row['provider_id']),
            'hospital_pl_yn' : string_or_none(row['hospital_pl_yn'])
            }
        
        try:
            p, created = self.insert_or_update(Problem, values, ['natural_key'])    
            log.debug('Saved Problem object: %s' % p)
        except:
            raise

class HospProblemLoader(BaseLoader):
    fields = [
        'patient_id',
        'mrn',
        'natural_key',# problemid 
        'date_noted',
        'icd9_code',
        'problem_status',
        'principal_prob_code',
        'present_on_adm_code',
        'priority_code',
        'overview',
        'provider_id', 
        ]
    
    model = Hospital_Problem

    def load_row(self, row):
        code = row['icd9_code']
        if not code or code =='':
            code = '799.9'
        icd9_code = self.get_icd9(code, '', {})
        
        natural_key = self.generateNaturalkey(row['natural_key'])
        values = {
            'natural_key': natural_key, 
            'provenance' : self.provenance,
            'patient' : self.get_patient(row['patient_id']),
            'mrn' : row['mrn'],
            'date' : self.date_or_none(row['date_noted']),
            'icd9' : icd9_code,
            'raw_icd9_code' : code,
            'status' : string_or_none(row['problem_status']),
            'principal_prob_code' : string_or_none(row['principal_prob_code']),
            'present_on_adm_code' : string_or_none(row['present_on_adm_code']),
            'priority_code' : string_or_none(row['priority_code']),
            'overview' : string_or_none(row['overview']),
            'provider' : self.get_provider(row['provider_id'])
            }
        
        try:
            hp, created = self.insert_or_update(Hospital_Problem, values, ['natural_key'])
            if option_site:
                site = SiteDefinition.get_by_short_name(option_site)
                hp.principal_prob, hp.present_on_adm, hp.priority = site.set_hospprobs(hp)
            hp.save()
            log.debug('Saved Problem object: %s' % hp)
        except:
            raise
                

class Command(LoaderCommand):
    #
    # Parse command line options
    #
    option_list = LoaderCommand.option_list + (
        make_option('-l', '--load_with_errors', dest='load_with_errors' , action='store_true', default=False, 
            help='Load skips bad input records, but does not fail'),
        make_option('-u', '--use_filename_date', dest='use_filename_date' , action='store_true', default=False, 
            help='When a date value is a required field, will use the filename date if the row value is missing'),
        make_option('-e', '--email_admin_reports', dest='email_admin_reports' , action='store_true', default=False, 
            help='Sends file-level load reports to administrator email list'),
        )
    help = 'Loads data from Epic ETL files'
    #log.debug('options: %s' % options)
    
    def handle(self, *fixture_labels, **options):
        self.folder_check()
        #
        # Sort files by type
        #
        input_filepaths = []
        global option_site
        option_site=None
        if options['single_file']:
            if not os.path.isfile(options['single_file']):
                sys.stderr.write('Invalid file path specified: %s' % options['single_file'])
            input_filepaths = [options['single_file']]
        else:
            if options['site_name']:
                option_site=options['site_name']
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
            ('epichpr', HospProblemLoader),
            ('epicsoc', SocialHistoryLoader),
            ('epicprg', PregnancyLoader)    
                               
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
                l = loader_class(filepath, options) # BaseLoader child instance
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
                    if not l.prov_delete():
                        log.error('Could not clear out data for stopped load of PROVENANCE ID %s: ' % l.provenance.provenance_id)
                    sys.exit(-255)
                except: # Unhandled exception!
                    log.critical('Exception loading file "%s":' % filepath)
                    log.critical('\t%s' % sys.exc_info()[1])
                    l.provenance.status = 'failure'
                    l.provenance.comment = sys.exc_info()[1]
                    l.provenance.save()
                    if not l.prov_delete():
                        log.error('Could not clear out data for failed load of PROVENANCE ID %s: ' % l.provenance.provenance_id)
                    disposition = 'failure'
                    transaction.commit()
                self.archive(options, filepath, disposition)
                if disposition == 'failure':
                    sys.exit()               
                l.load_summary() 
        #
        # Print job summary
        #
        print '+' * 80
        print 'Valid records loaded:'
        pprint.pprint(valid_count)
        print '-' * 80
        print 'Errors:'
        pprint.pprint(error_count)
