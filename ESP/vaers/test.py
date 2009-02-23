import os, sys
import unittest
import datetime
import random

sys.path.append('../')
import settings

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from esp.models import Demog, Immunization

import VAERSevents
import mockData
import rules

from VAERSevents import match_icd9_expression

NOW = datetime.datetime.now()
ONE_YEAR = datetime.timedelta(days=365)
PERCENTAGE_TO_AFFECT = 50
POPULATION_SIZE = 500
        
class TestImmunization(unittest.TestCase):
    def setUp(self):
        mockData.clear()

    def testImmunizationRecord(self):
        mockData.create_population(POPULATION_SIZE)
        self.assertEqual(Demog.objects.count(), POPULATION_SIZE)
        
        for patient in Demog.objects.all():
            mockData.recent_immunization(patient)
            
        self.assertEqual(Immunization.objects.count(), POPULATION_SIZE)
        
        

class TestIcd9DiagnosisIdentification(unittest.TestCase):       
    def setUp(self):
        self.diagnosis_codes = VAERSevents.diagnosis_codes()
        
    def testRegularCodes(self):
        diagnostics = rules.VAERS_DIAGNOSTICS
        bells_palsy_code = '351.0'
        guillian_barre_code = '357.0'
        self.assertEqual(diagnostics[bells_palsy_code]['diagnosis'], 'Bell''s palsy')
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
        
        


  
class TestVAERSCreation(unittest.TestCase):
    def setUp(self):
        mockData.clear()


    def testCreateVAERSPacient(self):
        mockData.create_population(POPULATION_SIZE)
        patient = Demog.manager.random()
        mockData.adverse_event_encounter(patient)
        
        self.assertEqual(len(VAERSevents.vaers_encounters()), 1)


class TestCreateWholePopulation(unittest.TestCase):

    def testCreatePopulation(self):
        mockData.create_population(POPULATION_SIZE)
        

    def testImmunizePopulation(self):

        for patient in Demog.objects.all():
            mockData.create_recent_immunization(patient)
            if random.randrange(0,100) < PERCENTAGE_TO_AFFECT:
                mockData.create_adverse_event_encounter(patient)
                

        






if __name__ == '__main__':
    mockData.clear()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCreateWholePopulation)
    unittest.TextTestRunner(verbosity=2).run(suite)



    
    
