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
from ESP.emr.models import LabResult, LabTestConcordance
from ESP.emr.management.commands.make_fakes import *  



class Command(BaseCommand):
    
    help = 'Extracts ESP data to Epic ETL files.'
    
    @transaction.commit_on_success
    def handle(self, *fixture_labels, **options):
        log.info('Extracting ESP data')
        print 'Extracting ESP data'
        
        #file_path = os.path.join(DATA_DIR, 'fake', self.__class__.filename(d))
        
        count = 0
        provider_writer = ProviderWriter()
         
        for p in Provider.objects.order_by('natural_key').exclude(natural_key__icontains="UNKNOWN"): 
            count =count +1 
            provider_writer.write_row(p)
        log.info('Extracted %s Provider from ESP to Epic ETL files' % count)   
        print 'Extracted %s Provider from ESP to Epic ETL files' % count
                 
        count = 0
        patient_writer = PatientWriter()
        #patient_writer.file_path = file_path
        for p in Patient.objects.order_by('natural_key').exclude(natural_key__icontains="UNKNOWN"): 
            count =count +1 
            patient_writer.write_row(p)
        log.info('Extracted %s Patients from ESP to Epic ETL files' % count)   
        print 'Extracted %s Patients from ESP to Epic ETL files' % count
        
        count = 0  
        lx_writer = LabResultWriter()
        for lx in LabResult.objects.order_by('natural_key'):
            count =count +1 
            lx_writer.write_row(lx)
        log.info('Extracted %s Labs from ESP to Epic ETL files' % count)  
        print 'Extracted %s Labs from ESP to Epic ETL files' % count
        
        count = 0    
        encounter_writer = EncounterWriter()
        for enc in Encounter.objects.order_by('natural_key'):
            count =count +1 #TODO icd9
            encounter_writer.write_row(enc, enc.dx_codes_str.split(','))
        log.info('Extracted %s Encounters from ESP to Epic ETL files' % count)  
        print 'Extracted %s Encounters from ESP to Epic ETL files' % count
        
        count = 0
        prescription_writer = PrescriptionWriter()
        for meds in Prescription.objects.order_by('natural_key'):
            count =count +1 
            prescription_writer.write_row(meds)
        log.info('Extracted %s Prescriptions from ESP to Epic ETL files' % count)  
        print 'Extracted %s Prescriptions from ESP to Epic ETL files' % count
        
        count = 0    
        immunization_writer = ImmunizationWriter()
        for imm in Immunization.objects.order_by('natural_key'):
            count =count +1 
            immunization_writer.write_row(imm)
        log.info('Extracted %s Immunizations from ESP to Epic ETL files' % count)  
        print 'Extracted %s Immunizations from ESP to Epic ETL files' % count
        
        count = 0    
        laborder_writer = LabOrderWriter()
        for lx_order in LabOrder.objects.order_by('natural_key'):
            count =count +1 
            laborder_writer.write_row(lx_order)
        log.info('Extracted %s Lab Orders from ESP to Epic ETL files' % count)  
        print 'Extracted %s Lab Orders from ESP to Epic ETL files' % count
       
        count = 0    
        allergy_writer = AllergyWriter()
        for allergy in Allergy.objects.order_by('natural_key'):
            count =count +1 
            allergy_writer.write_row(allergy)
        log.info('Extracted %s Allergies from ESP to Epic ETL files' % count)  
        print 'Extracted %s Allergies from ESP to Epic ETL files' % count
       
        count = 0    
        problem_writer = ProblemWriter()
        for p in Problem.objects.order_by('natural_key'):
            count =count +1 
            problem_writer.write_row(p)
        log.info('Extracted %s Problem from ESP to Epic ETL files' % count)  
        print 'Extracted %s Problem from ESP to Epic ETL files' % count
        
        count = 0    
        socialhistory_writer = SocialHistoryWriter()
        for p in SocialHistory.objects.order_by('id'):
            count =count +1 
            socialhistory_writer.write_row(p)
        log.info('Extracted %s social history from ESP to Epic ETL files' % count)  
        print 'Extracted %s social history from ESP to Epic ETL files' % count
        
        count = 0    
        pregnancy_writer = PregnancyWriter()
        for p in Pregnancy.objects.order_by('id'):
            count =count +1 
            pregnancy_writer.write_row(p)
        log.info('Extracted %s pregnancy from ESP to Epic ETL files' % count)  
        print 'Extracted %s pregancy from ESP to Epic ETL files' % count
        
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