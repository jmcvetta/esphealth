import os, sys
import unittest
import datetime
import random
import pdb

# Store messages in the messages folder, on parent level.
MESSAGE_DIR = os.path.realpath(os.path.join(
        os.path.dirname(__file__), '..', 'messages'))

# Models
from ESP.conf.models import Icd9
from ESP.esp.models import Demog, Immunization, Lx, Enc
from ESP.vaers.models import AdverseEvent
from ESP.vaers.models import FeverEvent, DiagnosticsEvent, LabResultEvent

from ESP.vaers.models import DiagnosticsEventRule

# Modules that we are using and/or testing
import fake
import heuristics
import reports

from rules import VAERS_DIAGNOSTICS
from heuristics import ACTIVE_DIAGNOSTICS_HEURISTICS
from heuristics import make_diagnosis_heuristic
from fake import ImmunizationHistory, Vaers, clear



    

class TestClearing(unittest.TestCase):
    def testClear(self):
        clear()
        for klass in [Immunization, Enc, Lx, AdverseEvent]:
            self.failIf(klass.fakes().count() != 0)

        

class TestRuleEngine(unittest.TestCase):

    def setUp(self):
        clear()

    def testDiagnosticsPositiveDetection(self):
        for v in VAERS_DIAGNOSTICS.values():
            clear()
            # Get rule and corresponding heuristic 
            heuristic = make_diagnosis_heuristic(v['name'])
            rule = DiagnosticsEventRule.by_name(v['name'])[0]

            # Cause an adverse reaction to one random "victim".

            # Find proper patient, immunization and code
            victim = Demog.random()
            imm = ImmunizationHistory(victim).add_immunization()
            code = random.choice(rule.heuristic_defining_codes.all())
            
            # Create the adverse event
            ev = Vaers(imm)
            ev.cause_icd9(code)
  
            self.assert_(len(heuristic.matches()) == 1)
            self.assert_(ev.matching_encounter in heuristic.matches())
            
            


    def testDiagnosticsNegativeDetection(self):
        # Create an adverse event with a different code.
        # The heuristic should NOT result in a detection.
        for v in VAERS_DIAGNOSTICS.values():
            clear()
            # Get rule and corresponding heuristic 
            heuristic = make_diagnosis_heuristic(v['name'])
            rule = DiagnosticsEventRule.by_name(v['name'])[0]

            # Cause an adverse reaction to one random "victim".

            # Find proper patient, immunization and code
            victim = Demog.random()
            imm = ImmunizationHistory(victim).add_immunization()
            code = Icd9.objects.exclude(code__in=rule.heuristic_defining_codes.all()).order_by('?')[0]
            
            # Add an encounter after Immunization, 
            # but icd9 code is not part of the heuristic.
            ev = Vaers(imm)
            ev.cause_icd9(code)
  
            self.assert_(len(heuristic.matches()) == 0)
            self.assert_(ev.matching_encounter not in heuristic.matches())
        

    def testDiagnosticsNegativeByReocurrence(self):
        relevant = [v for v in VAERS_DIAGNOSTICS.values() 
                    if v.get('ignore_period', None)]

        for v in relevant:
            clear()
            # Get rule and corresponding heuristic 
            heuristic = make_diagnosis_heuristic(v['name'])
            rule = DiagnosticsEventRule.by_name(v['name'])[0]
            
            # Cause an adverse reaction to one random "victim".

            # Find proper patient, immunization and code
            victim = Demog.random()
            imm = ImmunizationHistory(victim).add_immunization()
            code = random.choice(rule.heuristic_defining_codes.all())
            
            # Create the adverse event
            ev = Vaers(imm)
            ev.cause_icd9(code)

            matches = heuristic.matches()
  
            # So far, the heuristic should detect as a positive
            self.assert_(len(matches) == 1)
            self.assert_(ev.matching_encounter in matches)

            # But when we add a past encounter with the same code, it
            # should not.
            ev.cause_icd9_ignored_for_reoccurrence(code, 
                                                   v['ignore_period'])
            matches = heuristic.matches()

            self.assert_(len(matches) == 0)
            self.assert_(ev.matching_encounter not in matches)


        
            
                         



    def testDiagnosticsNegativeByHistory(self):
        relevant = [v for v in VAERS_DIAGNOSTICS.values() 
                    if v.get('ignore_codes', None)]

        for v in relevant:
            clear()
            # Get rule and corresponding heuristic 
            heuristic = make_diagnosis_heuristic(v['name'])
            rule = DiagnosticsEventRule.by_name(v['name'])[0]
            
            # Cause an adverse reaction to one random "victim".

            # Find proper patient, immunization and code
            victim = Demog.random()
            imm = ImmunizationHistory(victim).add_immunization()
            code = random.choice(rule.heuristic_defining_codes.all())
            
            # Create the adverse event
            ev = Vaers(imm)
            ev.cause_icd9(code)

            matches = heuristic.matches()
  
            # So far, the heuristic should detect as a positive
            self.assert_(len(matches) == 1)
            self.assert_(ev.matching_encounter in matches)

            # But when we add a history condition that makes it
            # ignorable, it no longer is a match.
            discarding_code = random.choice(
                rule.heuristic_discarding_codes.all())
            ev.cause_icd9_ignored_for_history(discarding_code)


            matches = heuristic.matches()
            self.assert_(len(matches) == 0)
            self.assert_(ev.matching_encounter not in matches)


    def testFeverDetection(self):
        pass

    def testFeverNegativeDetection(self):
        pass



    

if __name__ == '__main__':
    clear()
    unittest.main()
    


