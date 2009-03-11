import os, sys
import unittest
import datetime
import random
import pdb

sys.path.append(os.path.realpath('..'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from esp.models import Demog, Immunization
from vaers.models import AdverseEvent

import mockData
import rules
import diagnostics
import VAERSevents
import reports


from diagnostics import match_icd9_expression
from transmitter import make_vaers_report

import hl7_report

NOW = datetime.datetime.now()
ONE_YEAR = datetime.timedelta(days=365)
ONE_MONTH = datetime.timedelta(days=30)
ONE_WEEK = datetime.timedelta(days=7)


PERCENTAGE_TO_AFFECT = 50
POPULATION_SIZE = 5000
POPULATION_TO_IMMUNIZE = 1000



     
class TestIcd9DiagnosisIdentification(unittest.TestCase):
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
        self.assert_(match_icd9_expression('350.9', '350*'))
        self.failIf(match_icd9_expression('351.00', '350*'))


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
        self.start_date = NOW - ONE_YEAR
        self.end_date = NOW - ONE_YEAR + ONE_WEEK

        self.fever_events = VAERSevents.record_adverse_events(
            start_date=self.start_date,
            end_date=self.end_date,
            detect_only='fever'
            )
        
        self.diagnostics_events = VAERSevents.detect_adverse_events(
            start_date=self.start_date,
            end_date=self.end_date,
            detect_only='diagnosis'
            )
        

        self.events = self.fever_events + self.diagnostics_events

        

    def testFeverEventDetection(self):
        self.failIf(len(self.fever_events) == 0)

    def testDiagnosisDetection(self):
        self.failIf(len(self.diagnostics_events) == 0)
        

    def testVaersRecord(self):
        self.failIf(len(self.events) == 0)
        for ev in self.events:
            ev.save()


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



class TestHL7Reporter(unittest.TestCase):
    def setUp(self):
        self.latest_events = AdverseEvent.objects.order_by('-last_updated')[:50]
        patients = [ev.patient for ev in self.latest_events]
        self.patient = random.choice(patients)


    def testHasEventsToReport(self):
        self.assert_(self.latest_events)
        
    def testHasPatient(self):
        self.assert_(self.patient)
        
    def testVaersReport(self):
        for event in self.latest_events:
            report = hl7_report.make_report(event)
            self.assert_(report, 'Report is empty')



                                     
    
            
        

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestHL7Reporter)
    unittest.TextTestRunner(verbosity=2).run(suite)



    
    
