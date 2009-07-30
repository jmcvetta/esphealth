'''
                                  ESP Health
                            EMR ETL Infrastructure
                         EpicCare Extract File Loader


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory - http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''

import csv
import sys
import os
import socket
import datetime
import pprint

from ESP.settings import DATA_DIR
from ESP.utils.utils import log
from ESP.utils.utils import date_from_str
from ESP.emr.models import Provenance
from ESP.emr.models import Provider
from ESP.emr.models import Patient


UPDATED_BY = 'load_epic.py'

PROVIDER_FIELDS = [
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

PATIENT_FIELDS = [
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

LABORDER_FIELDS = {}
LABRESULT_FIELDS = {}
ENCOUNTER_FIELDS = {}
PRESCRIPTION_FIELDS = {}
IMMUNIZATION_FIELDS = {}

    
# 
# Set global values that will be used by all functions
#
global incoming_dir, archive_dir, error_dir, timestamp, unknown_provider
incoming_dir = os.path.join(DATA_DIR, 'epic', 'incoming')
archive_dir = os.path.join(DATA_DIR, 'epic', 'archive')
error_dir = os.path.join(DATA_DIR, 'epic', 'error')
timestamp = datetime.datetime.now()
unknown_provider = Provider.objects.get(provider_id_num='UNKNOWN')

class epic(csv.Dialect):
    """Describe the usual properties of EpicCare extract files."""
    delimiter = '^'
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = '\r\n'
    quoting = csv.QUOTE_MINIMAL
csv.register_dialect("epic", epic)


def load_provider(reader, provenance):
    count = 0
    for row in reader:
        try:
            p = Provider.objects.get(provider_id_num=row['provider_id_num'])
        except Provider.DoesNotExist:
            p = Provider(provider_id_num=row['provider_id_num'])
        p.provenance = provenance
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
        count += 1
    log.info('Loaded %s provider records')
    provenance.status = 'l'
    provenance.save()
    return count



def load_patient(reader, provenance):
    count = 0
    for row in reader:
        try:
            p = Patient.objects.get(patient_id_num=row['patient_id_num'])
        except Patient.DoesNotExist:
            p = Patient(patient_id_num=row['patient_id_num'])
        if row['provider_id_num']:
            provider = Provider.objects.get_or_create(provider_id_num=row['provider_id_num'])[0]
        else:
            log.debug('Provider field is empty -- using UNKNOWN provider')
            provider = unknown_provider
        p.provenance = provenance
        p.updated_by = UPDATED_BY
        p.mrn = row['mrn']
        p.last_name = row['last_name']
        p.first_name = row['first_name']
        p.middle_name = row['middle_name']
        p.pcp = provider
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
            p.date_of_birth = date_from_str(row['date_of_birth'])
        if row['date_of_death']:
            p.date_of_death = date_from_str(row['date_of_death'])
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
        count += 1
    log.info('Loaded %s patient records')
    provenance.status = 'l'
    provenance.save()
    return count


def load_laborder(reader, provenance):
    log.debug('No functionality defined for load_laborder()')
    return 0
    

def load_labresult(reader, provenance):
    return 0


def load_encounter(reader, provenance):
    return 0


def load_prescription(reader, provenance):
    return 0


def load_immunization(reader, provenance):
    return 0


def main():
    #
    # Retrieve files
    #
    dir_contents = os.listdir(incoming_dir)
    dir_contents.sort()
    conf = {
        'epicpro': (load_provider, PROVIDER_FIELDS),
        'epicmem': (load_patient, PATIENT_FIELDS),
        'epicord': (load_laborder, LABORDER_FIELDS),
        'epicres': (load_labresult, LABRESULT_FIELDS),
        'epicvis': (load_encounter, ENCOUNTER_FIELDS),
        'epicmed': (load_prescription, PRESCRIPTION_FIELDS),
        'epicimm': (load_immunization, IMMUNIZATION_FIELDS),
        }
    load_order = [
        'epicpro',
        'epicmem',
        'epicord',
        'epicres',
        'epicvis',
        'epicmed',
        'epicimm',
        ]
    filetype = {}
    record_count = {}
    for item in load_order:
        filetype[item] = []
        record_count[item] = 0
    for filename in dir_contents:
        filepath = os.path.join(incoming_dir, filename)
        if not os.path.isfile(filepath):
            continue
        if Provenance.objects.filter(source=filename, status='l'):
            log.warning('File "%s" has already been loaded; skipping' % filename)
            continue
        filetype[filename.split('.')[0]] += [filename]
    log.debug('Files to load by type: \n%s' % pprint.pformat(filetype))
    #
    # Load data
    #
    for ft in load_order:
        load_function = conf[ft][0]
        field_names = conf[ft][1]
        for filename in filetype[ft]:
            prov = Provenance.objects.get_or_create(timestamp=timestamp, 
                source=filename, 
                hostname=socket.gethostname(),
                status='a',
                )[0]
            prov.save()
            filepath = os.path.join(incoming_dir, filename)
            log.debug('Loading file "%s"' % filepath)
            reader = csv.DictReader(open(filepath), fieldnames=field_names, dialect='epic')
            record_count[ft] += load_function(reader, prov)
    print record_count


if __name__ == '__main__':
    main()
