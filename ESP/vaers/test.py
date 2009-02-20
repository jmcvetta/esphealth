import os, sys
import unittest
import datetime


sys.path.append('../')
import settings

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from esp.models import Demog, Immunization

import VAERSevents
import mockData
import rules

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
            mockData.make_recent_immunization(patient)
            
        self.assertEqual(Immunization.objects.count(), POPULATION_SIZE)
        
        

class TestIcd9DiagnosisIdentification(unittest.TestCase):       
    def setUp(self):
        self.diagnosis_codes = VAERSevents.diagnosis_codes()
        
    def testRegularCodes(self):
        diagnostics = rules.ADVERSE_EVENTS_DIAGNOSTICS
        bells_palsy_code = '351.0'
        guillian_barre_code = '357.0'
        self.assertEqual(diagnostics[bells_palsy_code]['diagnosis'], 'Bell''s palsy')
        self.assertEqual(diagnostics[guillian_barre_code]['category'], 2)



 
        
class TestRulesDefinition(unittest.TestCase):
    def setUp(self):
        
        

        self.start_date = NOW - ONE_YEAR
        self.end_date = NOW
        
    def testGetCategoryTwoRules(self):
        pass
        
    def testGetCategoryThreeRules(self):
        pass

    def testOne(self):
        pass


    
class TestVAERSCreation(unittest.TestCase):
    def setUp(self):
        mockData.clear()


    def testCreateVAERSPacient(self):
        mockData.create_population(POPULATION_SIZE)
        patient = Demog.manager.random()
        mockData.make_fake_adverse_event_encounter(patient)
        
        self.assertEqual(len(VAERSevents.vaers_encounters()), 1)
        




if __name__ == '__main__':
    unittest.main()


    
    
