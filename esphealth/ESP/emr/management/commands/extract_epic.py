'''
                                  ESP Health
                         Notifiable Diseases Framework
                         Populate Unmapped Labs Cache


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory <http://www.channing.harvard.edu>
@copyright: (c) 2009 Channing Laboratory
@license: LGPL 3.0 <http://www.gnu.org/licenses/lgpl-3.0.txt>
'''

from django.db import transaction
from django.db import connection
from django.db.models import Q
from django.db.models import Count
from django.core.management.base import BaseCommand
from optparse import make_option

from ESP.utils.utils import log
from ESP.utils.utils import log_query
from ESP.emr.models import LabResult
from ESP.emr.models import LabTestConcordance
from ESP.emr.management.commands.make_fakes import * #ImmunizationWriter, EncounterWriter, AllergyWriter, 



class Command(BaseCommand):
    
    help = 'Extracts ESP data to Epic ETL files.'
    
    @transaction.commit_on_success
    def handle(self, *fixture_labels, **options):
        log.info('Extracting ESP data')
        print 'Extracting ESP data'
        
        
        #file_path = os.path.join(DATA_DIR, 'fake', self.__class__.filename(d))
                 
        count = 0
        patient_writer = PatientWriter()
        #patient_writer.file_path = file_path
        for p in Patient.objects.order_by('patient_id_num').exclude(patient_id_num__icontains="UNKNOWN"): 
            count =count +1 
            patient_writer.write_row(p)
        log.info('Extracted %s Patients from ESP to Epic ETL files' % count)   
        print 'Extracted %s Patients from ESP to Epic ETL files' % count
        
        count = 0  
        lx_writer = LabResultWriter()
        for lx in LabResult.objects.order_by('native_code'):
            count =count +1 
            lx_writer.write_row(lx)
        log.info('Extracted %s Labs from ESP to Epic ETL files' % count)  
        print 'Extracted %s Labs from ESP to Epic ETL files' % count
        
        count = 0    
        encounter_writer = EncounterWriter()
        for e in Encounter.objects.order_by('native_encounter_num'):
            count =count +1 
            encounter_writer.write_row(e, e.icd9_codes_str.split(','))
        log.info('Extracted %s Encounters from ESP to Epic ETL files' % count)  
        print 'Extracted %s Encounters from ESP to Epic ETL files' % count
        
        count = 0
        prescription_writer = PrescriptionWriter()
        for meds in Prescription.objects.order_by('name'):
            count =count +1 
            prescription_writer.write_row(meds)
        log.info('Extracted %s Prescriptions from ESP to Epic ETL files' % count)  
        print 'Extracted %s Prescriptions from ESP to Epic ETL files' % count
        
'''       
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
        
'''