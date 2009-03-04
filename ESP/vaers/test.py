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

import VAERSevents
from VAERSevents import match_icd9_expression

import reports

from transmitter import make_vaers_report

NOW = datetime.datetime.now()
ONE_YEAR = datetime.timedelta(days=365)
ONE_MONTH = datetime.timedelta(days=30)
ONE_WEEK = datetime.timedelta(days=7)


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
        
        


  
class TestReports(unittest.TestCase):
    def testTemporalClusteringReport(self):
        start = NOW - ONE_YEAR - ONE_WEEK
        end = NOW - ONE_YEAR
        
        reports.temporal_clustering(start_date=start, end_date=end)


class TestVAERS(unittest.TestCase):
    def setUp(self):
        self.start_date = NOW - ONE_MONTH 
        self.end_date = NOW - ONE_MONTH + ONE_WEEK

        self.events = VAERSevents.get_adverse_events(
            start_date=start_date,
            end_date=end_date
            )
        
    def testDiagnosisDetection(self):
        events = VAERSevents.get_adverse_events(
            start_date=start_date,
            end_date=end_date, 
            detect_only='diagnosis'
            )
        
        print '\nchecking vaers based on icd9 codes\n'
        for event in events:
            print event.encounter
            print event.trigger_immunization
            print event.name


class TestHL7Emitter(unittest.TestCase):
    def setUp(self):
        start_date = NOW - ONE_MONTH 
        end_date = NOW - ONE_MONTH + ONE_WEEK

        self.one_event = VAERSevents.any_event(start_date=start_date,
                                          end_date=end_date)

        
    def testVaersReport(self):

        event = self.one_event
        imm = event.trigger_immunization
        patient = event.patient
        report = {
            'summary':reports.vaers_summary(imm),
            'vaccines_on_date':reports.vaccines_on_date(imm),
            'prior_vaccinations':reports.prior_vaccinations(imm),
            'previous_reports':reports.previous_reports(event),
            'prior_vaers':reports.prior_vaers(imm),
            'prior_siblings_vaers':reports.prior_vaers_in_sibling(imm),
            'patient_stats':reports.patient_stats(patient),
            'project_stats':reports.vaccination_project_stats(imm)
            }
        msg = make_vaers_report(report)

        print msg
    
            
        









if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestHL7Emitter)
    unittest.TextTestRunner(verbosity=2).run(suite)



    
    
