'''
                                  ESP Health
                            EMR ETL Infrastructure
                         EpicCare Extract File Loader


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory - http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''
from ESP.utils.utils import str_from_date

import csv
import sys
import os
import socket
import datetime
import optparse
import re
import pprint
import shutil

from psycopg2 import IntegrityError
from ESP.settings import DATA_DIR
from ESP.utils.utils import log
from ESP.utils.utils import date_from_str
from ESP.static.models import Icd9
from ESP.emr.models import Provenance
from ESP.emr.models import Provider
from ESP.emr.models import Patient
from ESP.emr.models import LabResult
from ESP.emr.models import Encounter
from ESP.emr.models import Prescription
from ESP.emr.models import Immunization



    
# 
# Set global values that will be used by all functions
#
global UPDATED_BY, INCOMING_DIR, ARCHIVE_DIR, ERROR_DIR, TIMESTAMP, UNKNOWN_PROVIDER
UPDATED_BY = 'load_epic.py'
INCOMING_DIR = os.path.join(DATA_DIR, 'epic', 'incoming')
ARCHIVE_DIR = os.path.join(DATA_DIR, 'epic', 'archive') # Successfully loaded files
ERROR_DIR = os.path.join(DATA_DIR, 'epic', 'error') # Files loaded with (handled) errors
FAILURE_DIR = os.path.join(DATA_DIR, 'epic', 'error') # Files that failed to load (w/ unhandled exception)
TIMESTAMP = datetime.datetime.now()
UNKNOWN_PROVIDER = Provider.objects.get(provider_id_num='UNKNOWN')


class EpicDialect(csv.Dialect):
    """Describe the usual properties of EpicCare extract files."""
    delimiter = '^'
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = '\r\n'
    quoting = csv.QUOTE_MINIMAL
csv.register_dialect("epic", EpicDialect)


class LoadException(BaseException):
    '''
    Raised when there is a problem loading data into db
    '''
    pass


class BaseLoader(object):
    
    float_catcher = re.compile(r'(\d+\.?\d*)')
    
    def __init__(self, filepath):
        assert os.path.isfile(filepath)
        path, filename = os.path.split(filepath)
        self.filename = filename
        self.filepath = filepath
        prov = Provenance.objects.get_or_create(timestamp=TIMESTAMP, 
            source=filename, 
            hostname=socket.gethostname(),
            status='attempted',
            )[0]
        prov.save()
        self.provenance = prov
        file_handle = open(filepath)
        self.line_count = len(file_handle.readlines())
        file_handle.seek(0) # Reset file position after counting lines
        self.reader = csv.DictReader(file_handle, fieldnames=self.fields, dialect='epic')
    
    def get_patient(self, patient_id_num):
        if not patient_id_num:
            raise LoadError('Called get_patient() with empty patient_id_num')
        try:
            p = Patient.objects.get(patient_id_num=patient_id_num)
        except Patient.DoesNotExist:
            p = Patient(patient_id_num=patient_id_num)
            p.provenance = self.provenance
            p.updated_by = UPDATED_BY
            p.save()
        return p
    
    def get_provider(self, provider_id_num):
        if not provider_id_num:
            return UNKNOWN_PROVIDER
        try:
            p = Provider.objects.get(provider_id_num=provider_id_num)
        except Provider.DoesNotExist:
            p = Provider(provider_id_num=provider_id_num)
            p.provenance = self.provenance
            p.updated_by = UPDATED_BY
            p.save()
        return p
    
    def float_or_none(self, string):
        m = self.float_catcher.match(string)
        if m.groups():
            return float(m.groups()[0])
        else:
            return None
    
    def date_or_none(self, string):
        try:
            return date_from_str(string)
        except ValueError:
            return None
    
    def load(self):
        # 
        # We can put error control here as it becomes necessary
        #
        log.info('Loading file "%s" with %s' % (self.filepath, self.__class__))
        cur_row = 0 # Row counter
        valid = 0 # Number of valid records loaded
        errors = 0 # Number of non-fatal errors encountered
        for row in self.reader:
            cur_row += 1 # Increment the counter
            # The last line is a footer, so we skip it
            if cur_row >= self.line_count:
                break
            try:
                self.load_row(row)
                valid += 1
            except LoadException, e:
                log.error('Caught LoadException:')
                log.error('  File: %s' % self.filename)
                log.error('  Line: %s' % cur_row)
                log.error('  Exception: \n%s' % e)
                log.error(pprint.pformat(row))
                errors += 1
            except ValueError, e:
                log.error('Caught ValueError:')
                log.error('  File: %s' % self.filename)
                log.error('  Line: %s' % cur_row)
                log.error('  Exception: \n%s' % e)
                log.error(pprint.pformat(row))
                errors += 1
        log.debug('Loaded %s records with %s errors.' % (valid, errors))
        if not errors:
            self.provenance.status = 'loaded'
        else:
            self.provenance.status = 'errors'
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
        pin = row['provider_id_num']
        if not pin:
            raise LoadException('Record has blank provider_id_num, which is required')
        p = self.get_provider(pin)
        p.provenance = self.provenance
        p.updated_by = UPDATED_BY
        p.last_name = row['last_name']
        p.first_name = row['first_name']
        p.middle_name = row['middle_name']
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


class LabOrderLoader(NotImplementedLoader):    
    pass

class LabResultLoader(BaseLoader):
    
    fields = [
        'patient_id_num',
        'medical_record_num',
        'order_id_num',
        'order_date',
        'result_date',
        'provider_id_num',
        'order_type',
        'cpt',
        'component',
        'component_name',
        'result_string',
        'normal_flag',
        'ref_low',
        'ref_high',
        'unit',
        'status',
        'note',
        'specimen_id_num',
        'impression',
        ]
    
    def load_row(self, row):
        native_code = row['cpt']
        if row['component']:
            native_code = native_code + '--' + row['component']
        l = LabResult()
        l.provenance = self.provenance
        l.patient = self.get_patient(row['patient_id_num'])
        l.provider = self.get_provider(row['provider_id_num'])
        l.mrn = row['medical_record_num']
        l.order_num = row['order_id_num']
        l.date = date_from_str(row['order_date'])
        l.result_date = self.date_or_none(row['result_date'])
        l.native_code = native_code
        l.native_name = row['component_name']
        res = row['result_string']
        l.result_string = res
        try:
            l.res_float = float(res)
        except:
            pass # Not every result string is supposed to convert to a float, so this is okay
        l.ref_neg = row['ref_low']
        l.ref_pos = row['ref_high']
        try:
            l.ref_low = float(row['ref_low'])
        except:
            pass
        try:
            l.ref_high = float(row['ref_high'])
        except:
            pass
        l.ref_unit = row['unit']
        l.abnormal_flag = row['normal_flag']
        l.status = row['status']
        l.comment = row['note']
        l.specimen_num = row['specimen_id_num']
        l.impression = row['impression']
        l.save()
        log.debug('Saved lab result object: %s' % l)


class EncounterLoader(BaseLoader):
    
    feet_regex = re.compile('(?P<feet>\d)\' *(?P<inches>\d{1,2})')
    
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
        'encounter_type',
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
        ]
    
    def load_row(self, row):
        e = Encounter()
        e.provenance = self.provenance
        e.patient = self.get_patient(row['patient_id_num'])
        e.provider = self.get_provider(row['provider_id_num'])
        e.native_encounter_num=row['encounter_id_num']
        e.native_site_num = row['dept_id_num']
        e.date = date_from_str(row['encounter_date'])
        cd = row['closed_date']
        if cd:
            e.closed_date = self.date_or_none(cd)
        e.site_name = row['dept_name']
        edc = row['edc']
        if edc:
            e.edc = self.date_or_none(edc)
            e.pregnancy_status = True
        if row['temp']:
            e.temperature = self.float_or_none(row['temp'])
        raw_weight = row['weight']
        if raw_weight:
            try:
                weight = self.float_or_none(raw_weight.split()[0])
                if 'lb' in raw_weight: # Convert LBs to Kg
                    e.weight = 0.45359237 * weight
            except ValueError:
                log.warning('Cannot cast weight to a number: %s' % raw_weight)
        raw_height = row['height']
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
        if row['bp_systolic']:
            e.bp_systolic = self.float_or_none(row['bp_systolic']) 
        if row['bp_diastolic']:
            e.bp_diastolic = self.float_or_none(row['bp_diastolic'])
        if row['o2_stat']:
            e.o2_stat = self.float_or_none(row['o2_stat'])
        if row['peak_flow']:
            e.peak_flow = self.float_or_none(row['peak_flow'])
        e.save() # Must save before using ManyToMany relationship
        for code in row['icd9s'].split():
            try:
                i = Icd9.objects.get(code__iexact=code)
            except Icd9.DoesNotExist:
                log.warning('Could not find ICD9 code "%s" - creating new ICD9 entry.' % code)
                i = Icd9()
                i.code = code
                i.name = 'Added by load_epic.py'
                i.save()
            e.icd9_codes.add(i)
        e.save()
        log.debug('Saved encounter object: %s' % e)
            
            


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
        p.date = date_from_str(row['order_date'])
        p.status = row['status']
        p.name = row['drug_name']
        p.code = row['ndc']
        p.quantity = row['quantity']
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
        i.date = date_from_str(row['date'])
        i.dose = row['dose']
        i.manufacturer = row['manufacturer']
        i.lot = row['lot']
        i.imm_id_num = row['imm_id_num']
        i.save()
        log.debug('Saved immunization object: %s' % i)


def move_file(filepath, disposition):
    '''
    Dispose of a file after attempting to load it.
    @param filepath: Full path to file
    @type filepath:  String
    @param disposition: What to do with this file?
    @type disposition:  String - ('success', 'errors', 'failure')
    '''
    if disposition == 'success':
        year = str(datetime.datetime.now().year)
        month = datetime.datetime.now().strftime('%b')
        folder = os.path.join(ARCHIVE_DIR, year, month)
        if not os.path.exists(folder): 
            os.makedirs(folder)
            log.debug('Created new folder: %s' % folder)
    elif disposition == 'errors':
        folder = ERROR_DIR
    elif disposition == 'failure':
        folder = FAILURE_DIR
    else:
        raise 'This should never happen -- something is badly horked up'
    shutil.move(filepath, folder)


def main():
    #
    # Parse command line options
    #
    parser = optparse.OptionParser()
    parser.add_option('--file', action='store', dest='single_file', metavar='FILEPATH', 
        help='Load an individual message file')
    parser.add_option('--input', action='store', dest='input_folder', default=INCOMING_DIR,
        metavar='FOLDER', help='Folder from which to read incoming HL7 messages')
    parser.add_option('--dry-run', action='store_true', dest='dry_run', default=False,
        help='Show which files would be loaded, but do not actually load them')
    options, args = parser.parse_args()
    log.debug('options: %s' % options)
    #
    # Ensure all required folders exist
    #
    for folder in [ARCHIVE_DIR, ERROR_DIR, FAILURE_DIR]:
        if not os.path.exists(folder): 
            os.makedirs(folder)
            log.debug('Created new folder: %s' % folder)
    #
    # Sort files by type
    #
    input_filepaths = []
    if options.single_file:
        if not os.path.isfile(options.single_file):
            sys.stderr.write('Invalid file path specified: %s' % options.single_file)
        input_filepaths = [options.single_file]
    else:
        dir_contents = os.listdir(options.input_folder)
        dir_contents.sort()
        for item in dir_contents:
            filepath = os.path.join(options.input_folder, item)
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
            log.warning('File "%s" has already been loaded; skipping' % filename)
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
            l = loader_class(filepath)
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
            except BaseException, e: # Unhandled exception!
                log.critical('Unhandled exception loading file "%s":' % filepath)
                log.critical('\t%s' % e)
                l.provenance.status = 'failure'
                l.provenance.comment = str(e)
                l.provenance.save()
                disposition = 'failure'
            move_file(filepath, disposition)
    #
    # Print job summary
    #
    print '+' * 80
    print 'Valid records loaded:'
    pprint.pprint(valid_count)
    print '-' * 80
    print 'Errors:'
    pprint.pprint(error_count)
    


if __name__ == '__main__':
    main()
