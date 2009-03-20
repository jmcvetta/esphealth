import os, sys
import unittest
import datetime
import random
import pdb



#Standard boilerplate code that we put to put the settings file in the
#python path and make the Django environment have access to it.
PWD = os.path.dirname(__file__)
PARENT_DIR = os.path.realpath(os.path.join(PWD, '..'))

if PARENT_DIR not in sys.path: sys.path.append(PARENT_DIR)

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

MESSAGE_DIR = os.path.realpath(os.path.join(PARENT_DIR, 'messages'))

# Models
from esp.models import Demog, Immunization
from vaers.models import AdverseEvent
from vaers.models import FeverEvent, DiagnosticsEvent, LabResultEvent

# Modules that we are using and/or testing
import rules
import diagnostics
import VAERSevents
import reports
import hl7_report

from VAERSevents import events_caused
from diagnostics import match_icd9_expression

# Some constants
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

class TestLxEventDetection(unittest.TestCase):
    def testExclusionRule(self):
        pass


  
class TestReports(unittest.TestCase):
    def setUp(self):
        self.filename = os.path.join(MESSAGE_DIR, 'temporal_clustering.txt')
    
    def testTemporalClusteringReport(self):
        reports.temporal_clustering(self.filename)

        


class TestVAERS(unittest.TestCase):

    
    def setUp(self):
        self.imms = Immunization.objects.filter(
            ImmDate__gte='20080215',
            ImmDate__lte='20080225')
        self.fever_events = []
        self.diagnostics_events = []
        self.lab_results_events = []

        

    def testFeverEventDetection(self): 
        self.fever_events = events_caused(self.imms, only='fevers')
        self.failIf(len(self.fever_events) == 0)

    def testDiagnosisDetection(self):
        self.diagnostics_events = events_caused(self.imms, only='diagnostics')
        self.failIf(len(self.diagnostics_events) == 0)

    def testLabResultEventDetection(self):
        self.lab_results_events = events_caused(self.imms, only='lab_results')
        self.failIf(len(self.lab_results_events) == 0)
        
    def testVaersRecord(self):
        event_count = len(self.fever_events + self.diagnostics_events + self.lab_results_events)
        
        total_count = AdverseEvent.objects.count()
        
        # There is no event on the DB, so all detected events are
        # supposed to be recorded.
        self.assert_(event_count == total_count)



class TestHL7Reporter(unittest.TestCase):
    def setUp(self):
        self.latest_events = AdverseEvent.objects.order_by('-last_updated')[:50]
    def testHasEventsToReport(self):
        self.assert_(self.latest_events)
        
    def testVaersReport(self):
        for event in self.latest_events:
            report = hl7_report.make_report(event)
            self.assert_(report, 'Report is empty')


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestReports)
    unittest.TextTestRunner(verbosity=2).run(suite)



    
    
