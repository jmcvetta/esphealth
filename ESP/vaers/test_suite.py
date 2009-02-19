import os, sys
sys.path.append('../')

import unittest
import datetime

import settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from esp.models import Demog, Immunization, Enc

from tests import mockData
import rules

NOW = datetime.datetime.now()
ONE_YEAR = datetime.timedelta(days=365)
        
class TestImmunization(unittest.TestCase):
    def setUp(self):
        Immunization.objects.all().delete()
        Demog.objects.all().delete()

    def testImmunizationRecord(self):
        size = 100
        mockData.create_patient_population(size)
        self.assertEqual(Demog.objects.count(), size)
        
        for patient in Demog.objects.all():
            mockData.make_fake_immunization(patient)
            
        self.assertEqual(Immunization.objects.count(), size)
        
        


class TestRulesDefinition(unittest.TestCase):
    def setUp(self):
        
        # Setup should consist of:
        #  - deleting whole database (Demog, Immunization and Enc)
        #  - Creating list of 1000 patients with no Immunization
        #  - Creating list of 1000 patients with Immunization Records
        #  - "Giving" fevers to 100 of these patients
        #  - "Giving" Cat 2 adverse events to another 100 of these patients
        #  - "Giving" Cat 3 adverse events to another 100 of these patients
        #  - "Giving" Fevers to 50 patients that were not vaccinated before
        #  - Creating encounters with non-vaers codes for all of the patients

        healthy_population = 1000
        vaccinated_population = 1000
        vaccinated_population_with_fever = 100
        category2_population = 100
        category3_population = 100
        vaccinated_population_without_fever = 100
        
        
   

        self.start_date = NOW - ONE_YEAR
        self.end_date = NOW
        
    def testGetCategoryTwoRules(self):
        pass
        
    def testGetCategoryThreeRules(self):
        pass

    def testOne(self):
        pass


    

        

        




if __name__ == '__main__':
    unittest.main()


    
    
