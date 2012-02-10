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
from ESP.utils.testing import EspTestCase
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
    time ./bin/esp test --nologcapture -d -x -v 2 --noinput --where=/home/jason/work/esphealth-trunk/src/disease-hepatitis-combined
'''


class Hepatitis_B_Test(EspTestCase):
    '''
    Unit tests for Hepatitis B algorithm
    '''
    
    def test_definition_a(self):
        '''
        a) (#1 or #2 or #3) AND #4 within 14 day period
        1. ICD9 = 782.4 (jaundice, not of newborn)
        2. Alanine aminotransferase (ALT) >5x upper limit of normal
        3. Aspartate aminotransferase (AST) >5x upper limit of normal
        4. IgM antibody to Hepatitis B Core Antigen = "REACTIVE" (may be truncated)
        '''
        log.info('Testing Hep B Definition A')
        mccoy = self.create_provider(last='McCoy', first='Leonard')
        kirk = self.create_patient(last='Kirk', first='James', pcp=mccoy)
        trigger_date = datetime.date(year=2010, month=2, day=15)
        #
        # 4. IgM antibody to Hepatitis B Core Antigen
        #
        self.create_lab_result(
            provider = mccoy, 
            patient = kirk, 
            date = trigger_date,
            alt = 'hepatitis_b_core_antigen_igm_antibody',
            result_string = 'POSITIVE',
            )
        #
        # 1. ICD9 = 782.4 (jaundice, not of newborn)
        #
        self.create_diagnosis(
            provider = mccoy, 
            patient = kirk, 
            date = trigger_date - relativedelta(days=5), 
            codeset = 'icd9', 
            diagnosis_code = '782.4'
            )
        hep_b_disdef = DiseaseDefinition.get_by_short_name('hepatitis_b')
        DiseaseDefinition.generate_all(disease_list=[hep_b_disdef], dependencies=True)
        case_qs = Case.objects.filter(patient=kirk, condition='hepatitis_b:acute')
        self.assertEqual(case_qs.count(), 1, 'One and only one case should be generated')
        kirk_case = case_qs[0]
        self.assertEqual(kirk_case.provider, mccoy)
        self.assertEqual(kirk_case.date, trigger_date)
        self.assertEqual(kirk_case.events.count(), 2)
    
    def test_definition_b_c(self):
        '''
        Hepatitis Definitions B & C
        b) (#1 or #2 or #3) AND (#12 or #15) AND #5 "reactive" within 21 day period 
            AND no prior positive result for #5 or #7 ever 
            AND no code for ICD9=070.32 at this encounter or in patient's past
        c) (1 or 2 or 3) AND (#12 or #15) AND #7 positive within 21 day period 
            AND no prior positive result for #5 or #7 ever 
            AND no code for ICD9=070.32 at this encounter or in the patient's past
        1. ICD9 = 782.4 (jaundice, not of newborn)
        2. Alanine aminotransferase (ALT) >5x upper limit of normal
        3. Aspartate aminotransferase (AST) >5x upper limit of normal
        5. Hepatitis B Surface Antigen
        7. Hepatitis B Viral DNA
        12. Total bilirubin > 1.5
        15. Calculated bilirubin = (direct bilirubin + indirect bilirubin) = value > 1.5
        ICD9 070.32 = Chronic Hep B
        '''
        log.info('Testing Hep B Definition A')
        mccoy = self.create_provider(last='McCoy', first='Leonard')
        kirk = self.create_patient(last='Kirk', first='James', pcp=mccoy)
        spock = self.create_patient(last='Spock', first='Commander', pcp=mccoy)
        kirk_trigger_date = datetime.date(year=2010, month=2, day=15)
        spock_trigger_date = datetime.date(year=2009, month=6, day=21)
        #
        # Kirk has Hep B.  He has a positive surface antigen test; elevated AST
        # levels; and elevated total bilirubin.
        #
        self.create_lab_result(
            provider = mccoy, 
            patient = kirk, 
            date = kirk_trigger_date,
            alt = 'hepatitis_b_surface_antigen',
            result_string = 'POSITIVE',
            )
        # Result & ref high values are not intended to be realistic, but only
        # to test the ratio heuristic.
        self.create_lab_result(
            provider = mccoy, 
            patient = kirk, 
            date = kirk_trigger_date - relativedelta(days=10),
            alt = 'ast',
            ref_high_float = '100',
            result_float = '700',
            )
        self.create_lab_result(
            provider = mccoy, 
            patient = kirk, 
            date = kirk_trigger_date + relativedelta(days=7),
            alt = 'bilirubin:total',
            result_float = '1.8',
            )
        #
        # Spock has Hep B.  He has a positive surface antigen test; jaundice; 
        # and elevated calculated bilirubin.
        #
        self.create_lab_result(
            provider = mccoy, 
            patient = spock, 
            date = spock_trigger_date,
            alt = 'hepatitis_b_surface_antigen',
            result_string = 'POSITIVE',
            )
        # jaundice
        self.create_diagnosis(
            provider = mccoy, 
            patient = spock, 
            date = spock_trigger_date - relativedelta(days=5), 
            codeset = 'icd9', 
            diagnosis_code = '782.4'
            )
        self.create_lab_result(
            provider = mccoy, 
            patient = spock, 
            date = spock_trigger_date + relativedelta(days=9),
            alt = 'bilirubin:direct',
            result_float = '1.1',
            )
        self.create_lab_result(
            provider = mccoy, 
            patient = spock, 
            date = spock_trigger_date + relativedelta(days=9),
            alt = 'bilirubin:indirect',
            result_float = '0.9',
            )
        #
        # Generate Cases
        #
        hep_b_disdef = DiseaseDefinition.get_by_short_name('hepatitis_b')
        DiseaseDefinition.generate_all(disease_list=[hep_b_disdef], dependencies=True)
        #
        # Check Kirk
        #
        kirk_case_qs = Case.objects.filter(patient=kirk, condition='hepatitis_b:acute')
        self.assertEqual(kirk_case_qs.count(), 1, 'One and only one case should be generated')
        kirk_case = kirk_case_qs[0]
        self.assertEqual(kirk_case.provider, mccoy)
        self.assertEqual(kirk_case.date, kirk_trigger_date)
        self.assertEqual(kirk_case.events.count(), 3)
        #
        # Check Spock
        #
        spock_case_qs = Case.objects.filter(patient=spock, condition='hepatitis_b:acute')
        self.assertEqual(spock_case_qs.count(), 1, 'One and only one case should be generated')
        spock_case = spock_case_qs[0]
        self.assertEqual(spock_case.provider, mccoy)
        self.assertEqual(spock_case.date, spock_trigger_date)
        self.assertEqual(spock_case.events.count(), 2) # The direct/indirect bili labs do not generate events

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
    
        
        
        
