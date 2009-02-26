import os, sys
import unittest
import datetime
import random


sys.path.append('../')
import settings

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from esp.models import Demog, Immunization


import mockData
import rules


from VAERSevents import match_icd9_expression, diagnosis_codes
from reports import temporal_clustering

NOW = datetime.datetime.now()
ONE_YEAR = datetime.timedelta(days=365)
PERCENTAGE_TO_AFFECT = 50
POPULATION_SIZE = 5000
POPULATION_TO_IMMUNIZE = 1000
        
     
class TestIcd9DiagnosisIdentification(unittest.TestCase):       
    def setUp(self):
        self.diagnosis_codes = VAERSevents.diagnosis_codes()
        
    def testRegularCodes(self):
        diagnostics = rules.VAERS_DIAGNOSTICS
        bells_palsy_code = '351.0'
        guillian_barre_code = '357.0'
        self.assertEqual(diagnostics[bells_palsy_code]['name'], 'Bell''s palsy')
        self.assertEqual(diagnostics[guillian_barre_code]['category'], 2)



class TestIcd9CodeMatching(unittest.TestCase):
    def testDirectMatching(self):
        self.assert_(match_icd9_expression('350.0', '350.0'))
        self.assert_(match_icd9_expression('999.9', '999.9'))
        self.failIf(match_icd9_expression('350.0', '999.9'))


    def testRegexpMatching(self):
        self.assert_(match_icd9_expression('350.0', '350*'))
        self.assert_(match_icd9_expression('350.8', '350*'))
        self.assertRaises(ValueError, match_icd9_expression, '350', '350*')
        self.assert_(match_icd9_expression('350.9', '350*'))


    def testIntervalMatching(self):
        self.assert_(match_icd9_expression('350.0', '350.0-351.5'))
        self.assert_(match_icd9_expression('350.0', '300.0-350.0'))
        self.assert_(match_icd9_expression('350.0', '345.0-355.0'))
        self.assert_(match_icd9_expression('350.9', '300.9-350.9'))
        
        self.assertFalse(match_icd9_expression('350.0', '350.1-350.8'))
        self.assertFalse(match_icd9_expression('350.0', '300.9-349.9'))
        self.assertFalse(match_icd9_expression('350.1', '300.9-350.0'))
        self.assertFalse(match_icd9_expression('349.8', '349.9-350.0'))
                     

    def testIntervalWithRegExpMatching(self):
        self.assert_(match_icd9_expression('820.9', '680.2-820*'))
        self.assert_(match_icd9_expression('820.0', '680.2-820*'))
        self.assert_(match_icd9_expression('680.2', '680.2-820*'))
        self.assert_(match_icd9_expression('680.5', '680.2-820*'))
        self.assert_(match_icd9_expression('700.9', '680.2-820*'))
        
        self.assert_(match_icd9_expression('680.0', '680*-820*'))
        self.assert_(match_icd9_expression('680.9', '680*-820*'))
        self.assert_(match_icd9_expression('681.0', '680*-820*'))
                

        self.assertFalse(match_icd9_expression('821.0', '680.2-820*'))
        self.assertFalse(match_icd9_expression('680.1', '680.2-820*'))
        self.assertFalse(match_icd9_expression('666.6', '680.2-820*'))
        
        self.assertFalse(match_icd9_expression('679.9', '680*-820*'))
        self.assertFalse(match_icd9_expression('821.0', '680*-820*'))
        
        


  
class TestVAERS(unittest.TestCase):
    def setUp(self):
        self.immunizations = []
        self.vaers_cases = []

        for patient in Demog.manager.sample(size=POPULATION_TO_IMMUNIZE):
            imm = mockData.create_recent_immunization(patient)
            self.immunizations.append(imm)
            if random.randrange(100) < PERCENTAGE_TO_AFFECT:
                encounter = mockData.create_adverse_event_encounter(imm, patient)
                self.vaers_cases.append(encounter)


    def testTemporalClusteringReport(self):
        print '\n\n\n'
        temporal_clustering()
        print '\n\n\n'



    def tearDown(self):
        for imm in self.immunizations:
            imm.delete()
        for case in self.vaers_cases:
            case.delete()






if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestVAERS)
    unittest.TextTestRunner(verbosity=2).run(suite)



    
    
