'''
                                  ESP Health
                           Combined Hepatitis A/B/C
Unit Tests


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@contact: http://www.esphealth.org
@copyright: (c) 2012 Channing Laboratory
@license: LGPL
'''

import os
import datetime
from dateutil.relativedelta import relativedelta

from django.test import TestCase

from ESP.utils import log
from ESP.conf.models import LabTestMap
from ESP.emr.models import Provenance
from ESP.emr.models import Provider
from ESP.emr.models import Patient
from ESP.emr.models import LabResult
from ESP.emr.models import Encounter
from ESP.emr.models import Prescription
from ESP.hef.base import AbstractLabTest
from ESP.hef.models import Event
from ESP.nodis.base import DiseaseDefinition
from ESP.nodis.models import Case

'''
Run me with:
    time ./bin/esp test -v 2 --processes=0 --noinput --where=/home/jason/work/esphealth-trunk/src/disease-hepatitis-combined
'''




class EspTestCase(TestCase):
    
    def setUp(self):
        log.info('Creating TEST provenance')
        self.provenance = Provenance(source='TEST', hostname='TEST')
        self.provenance.save()
        
    def tearDown(self):
        log.info('Deleting TEST provenance')
        self.provenance.delete()
        del self.provenance
    
    
    def create_lab_result(self, provider, patient, date, alt, **kwargs):
        '''
        Create a LabResult and a LabTestMap for the specified abstract lab test.
        @param alt: Abstract lab test name
        @type alt:  String
        '''
        native_code = 'natcode--' + alt 
        native_code = native_code[:255]
        ltm, created = LabTestMap.objects.get_or_create(
            test_name = alt,
            native_code = native_code,
            code_match_type = 'exact',
            record_type = 'result',
            )
        if created:
            log.debug('Created %s' % ltm)
        new_lab = LabResult(
            provenance = self.provenance,
            provider = provider, 
            patient = patient,
            date = date,
            native_code = native_code,
            )
        for key in kwargs:
            if hasattr(new_lab, key):
                value = kwargs[key]
                setattr(new_lab, key, value)
        new_lab.save()
        log.debug('Created fake lab result: %s' % new_lab)
        return new_lab
    
    def create_diagnosis(self, provider, patient, date, codeset, diagnosis_code):
        '''
        Create a encounter record with the provided ICD9 diagnosis'
        @param icd_str: ICD9 string to use in the record
        @type icd_str:  String
        '''
        new_enc = Encounter(
            provenance = self.provenance,
            provider = provider,
            patient = patient,
            date = date,
            )
        new_enc.save()
        new_enc.add_diagnosis(codeset=codeset, diagnosis_code=diagnosis_code)
        return new_enc
    
    def create_provider(self, last, first):
        new_prov = Provider(provenance=self.provenance, last_name=last, first_name=first)
        new_prov.save()
        return new_prov
    
    def create_patient(self, last, first, pcp):
        new_pat = Patient(provenance=self.provenance, last_name=last, first_name=first, pcp=pcp)
        new_pat.save()
        return new_pat
            

class Hepatitis_C_Test(EspTestCase):
    '''
    Unit tests for Hepatitis C algorithm
    '''
    
    def test_definition_a(self):
        '''
        a) (1 or 2) and 3 positive and 4 positive (if done) and 5 positive (if
        done) and 6 positive (if done) and (7 negative or 11 negative) and [8
        negative or 9 non-reactive or (8 not done and 10 non-reactive)] within
        a 28 day period;  AND  no prior positive 3 or  5 or 6 ever;  AND no
        ICD9 (070.54 or 070.70) ever prior to this encounter
        '''
        log.info('Testing Hep C Definition A (complex algo)')
        #
        # (1 or 2)
        # 
        # (jaundice or ALT>400)
        mccoy = self.create_provider(last='McCoy', first='Leonard')
        kirk = self.create_patient(last='Kirk', first='James', pcp=mccoy)
        trigger_date = datetime.date(year=2010, month=2, day=15)
        self.create_diagnosis(
            provider = mccoy, 
            patient = kirk, 
            date = trigger_date - relativedelta(days=5), 
            codeset = 'icd9', 
            diagnosis_code = '782.4'
            )
        #
        # and 3 positive
        # 
        # 3. Hepatitis C ELISA
        #
        self.create_lab_result(
            provider = mccoy, 
            patient = kirk, 
            date = trigger_date,
            alt = 'hepatitis_c_elisa',
            result_string = 'POSITIVE',
            )
        #
        # and 4 positive (if done) and 5 positive (if done) and 6 positive (if done)
        #
        # None are mandatory, so not implimenting at this time.
        # TODO: Add some of these
        #
        #-----
        #
        # and (7 negative or 11 negative)
        #
        # 7. IgM antibody to Hepatitis A
        # 11. Hepatitis A total antibodies
        #
        self.create_lab_result(
            provider = mccoy, 
            patient = kirk, 
            date = trigger_date + relativedelta(days=3),
            alt = 'hepatitis_a_total_antibodies',
            result_string = 'NEGATIVE',
            )
        #
        # and [8 negative or 9 non-reactive or (8 not done and 10 non-reactive)]
        #
        # 8. IgM antibody to Hepatitis B Core Antigen
        # 9. General antibody to Hepatitis B Core Antigen
        # 10. Hepatitis B Surface Antigen
        #
        self.create_lab_result(
            provider = mccoy, 
            patient = kirk, 
            date = trigger_date + relativedelta(days=5),
            alt = 'hepatitis_b_surface_antigen',
            result_string = 'NEGATIVE',
            )
        hep_c_disdef = DiseaseDefinition.get_by_short_name('hepatitis_c')
        DiseaseDefinition.generate_all(disease_list=[hep_c_disdef], dependencies=True)
        case_qs = Case.objects.filter(patient=kirk, condition='hepatitis_c:acute')
        self.assertEqual(case_qs.count(), 1, 'One and only one case should be generated')
        kirk_case = case_qs[0]
        self.assertEqual(kirk_case.provider, mccoy)
        self.assertEqual(kirk_case.date, trigger_date)
        self.assertEqual(kirk_case.events.count(), 4)

    def test_definition_b(self):
        '''
        b) (1 or 2) and 6 positive and 4 positive (if done) and 5 positive (if
        done) and (7 negative or 11 negative) and [8 negative or 9 non-reactive
        or (8 not done and 10 non-reactive)] within a 28 day period; AND no
        prior positive 3 or  5 or 6 ever;  AND no ICD9 (070.54 or 070.70) ever
        prior to this encounter
        '''
        log.info('Testing Hep C Definition B (complex algo)')
        #
        # (1 or 2)
        # 
        # (jaundice or ALT>400)
        mccoy = self.create_provider(last='McCoy', first='Leonard')
        kirk = self.create_patient(last='Kirk', first='James', pcp=mccoy)
        trigger_date = datetime.date(year=2010, month=2, day=15)
        self.create_diagnosis(
            provider = mccoy, 
            patient = kirk, 
            date = trigger_date - relativedelta(days=5), 
            codeset = 'icd9', 
            diagnosis_code = '782.4'
            )
        #
        # and 6 positive
        # 
        # 6. Hepatitis C RNA
        #
        self.create_lab_result(
            provider = mccoy, 
            patient = kirk, 
            date = trigger_date,
            alt = 'hepatitis_c_rna',
            result_string = 'POSITIVE',
            )
        #
        # and 4 positive (if done) and 5 positive (if done)
        #
        # 4. Hepatitis C Signal Cutoff Ratio
        # 5. Hepatitis C RIBA
        #
        self.create_lab_result(
            provider = mccoy, 
            patient = kirk, 
            date = trigger_date + relativedelta(days=15),
            alt = 'hepatitis_c_signal_cutoff',
            result_string = 'POSITIVE',
            )
        #-----
        #
        # and (7 negative or 11 negative)
        #
        # 7. IgM antibody to Hepatitis A
        # 11. Hepatitis A total antibodies
        #
        self.create_lab_result(
            provider = mccoy, 
            patient = kirk, 
            date = trigger_date + relativedelta(days=3),
            alt = 'hepatitis_a_total_antibodies',
            result_string = 'NEGATIVE',
            )
        #
        # and [8 negative or 9 non-reactive or (8 not done and 10 non-reactive)]
        #
        # 8. IgM antibody to Hepatitis B Core Antigen
        # 9. General antibody to Hepatitis B Core Antigen
        # 10. Hepatitis B Surface Antigen
        #
        self.create_lab_result(
            provider = mccoy, 
            patient = kirk, 
            date = trigger_date + relativedelta(days=5),
            alt = 'hepatitis_b_surface_antigen',
            result_string = 'NEGATIVE',
            )
        hep_c_disdef = DiseaseDefinition.get_by_short_name('hepatitis_c')
        DiseaseDefinition.generate_all(disease_list=[hep_c_disdef], dependencies=True)
        case_qs = Case.objects.filter(patient=kirk, condition='hepatitis_c:acute')
        self.assertEqual(case_qs.count(), 1, 'One and only one case should be generated')
        kirk_case = case_qs[0]
        self.assertEqual(kirk_case.provider, mccoy)
        self.assertEqual(kirk_case.date, trigger_date)
        self.assertEqual(kirk_case.events.count(), 5)

    def test_definition_c(self):
        '''
        c) 6 positive and record of (3 negative within the prior 12 months)
        
        3. Hepatitis C ELISA
        6. Hepatitis C RNA
        
        TODO: This test, and the disease algo, currently expect JM's interpretation
        of the Hep C definition.  Make sure Mike Klompas confirms this is correct.
        '''
        log.info('Testing Hep C Definition C (simple algo)')
        mccoy = self.create_provider(last='Nimoy', first='Leonard')
        kirk = self.create_patient(last='Kirk', first='James', pcp=mccoy)
        neg_test_date = datetime.date(day=2, month=6, year=2009)
        pos_test_date = datetime.date(day=15, month=1, year=2010)
        self.create_lab_result(
            provider = mccoy, 
            patient = kirk, 
            date = neg_test_date, 
            alt = 'hepatitis_c_rna',
            result_string = 'NEGATIVE',
            )
        self.create_lab_result(
            provider = mccoy, 
            patient = kirk, 
            date = pos_test_date, 
            alt = 'hepatitis_c_rna',
            result_string = 'POSITIVE',
            )
        hep_c_disdef = DiseaseDefinition.get_by_short_name('hepatitis_c')
        DiseaseDefinition.generate_all(disease_list=[hep_c_disdef], dependencies=True)
        case_qs = Case.objects.filter(patient=kirk, condition='hepatitis_c:acute')
        self.assertEqual(case_qs.count(), 1, 'One and only one case should be generated')
        kirk_case = case_qs[0]
        self.assertEqual(kirk_case.provider, mccoy)
        self.assertEqual(kirk_case.date, pos_test_date)
        self.assertEqual(kirk_case.events.count(), 2)

    def test_definition_d(self):
        '''
        c) 3 positive and record of (3 negative within the prior 12 months)
        
        3. Hepatitis C ELISA
        '''
        log.info('Testing Hep C Definition D (simple algo)')
        mccoy = self.create_provider(last='Nimoy', first='Leonard')
        kirk = self.create_patient(last='Kirk', first='James', pcp=mccoy)
        neg_test_date = datetime.date(day=2, month=6, year=2009)
        pos_test_date = datetime.date(day=15, month=1, year=2010)
        self.create_lab_result(
            provider = mccoy, 
            patient = kirk, 
            date = neg_test_date, 
            alt = 'hepatitis_c_elisa',
            result_string = 'NEGATIVE',
            )
        self.create_lab_result(
            provider = mccoy, 
            patient = kirk, 
            date = pos_test_date, 
            alt = 'hepatitis_c_elisa',
            result_string = 'POSITIVE',
            )
        hep_c_disdef = DiseaseDefinition.get_by_short_name('hepatitis_c')
        DiseaseDefinition.generate_all(disease_list=[hep_c_disdef], dependencies=True)
        case_qs = Case.objects.filter(patient=kirk, condition='hepatitis_c:acute')
        self.assertEqual(case_qs.count(), 1, 'One and only one case should be generated')
        kirk_case = case_qs[0]
        self.assertEqual(kirk_case.provider, mccoy)
        self.assertEqual(kirk_case.date, pos_test_date)
        self.assertEqual(kirk_case.events.count(), 2)
    
        
        
        