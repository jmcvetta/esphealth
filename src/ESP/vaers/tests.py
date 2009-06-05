import os, sys
import unittest
import datetime
import random
import pdb

# Store messages in the messages folder, on parent level.
MESSAGE_DIR = os.path.realpath(os.path.join(
        os.path.dirname(__file__), '..', 'messages'))

# Models
from ESP.conf.models import Icd9, Loinc, NativeCode
from ESP.emr.models import Patient, Immunization, LabResult, Encounter
from ESP.vaers.models import AdverseEvent


from ESP.vaers.models import DiagnosticsEventRule

# Modules that we are using and/or testing
import fake
import heuristics


from rules import VAERS_DIAGNOSTICS, VAERS_LAB_RESULTS, TIME_WINDOW_POST_EVENT
from fake import ImmunizationHistory, Vaers, clear

FEVER_HEURISTIC = heuristics.fever_heuristic()
DIAGNOSTICS_HEURISTICS = dict([(h.event_name, h) for h in heuristics.diagnostic_heuristics()])
LAB_HEURISTICS = heuristics.lab_heuristics()



class TestLoincCodes(unittest.TestCase):
    def setUp(self):
        self.codes = VAERS_LAB_RESULTS.keys()

    def testLoincTable(self):
        for loinc in self.codes:
            try:
                self.assert_(Loinc.objects.get(loinc_num=loinc))
            except Exception, why:
                self.assert_(False, 'Testing LOINC"%s": %s' % (loinc, why))

    def testNativeCodeTable(self):
        for loinc in self.codes:
            try:
                self.assert_(NativeCode.objects.get(native_code=loinc))
            except Exception, why:
                self.assert_(False, 'Testing NativeCode "%s": %s' % (loinc, why))


class TestFake(unittest.TestCase):
    def setUp(self):
        clear()

    def testAllPatientsHaveProviders(self):
        for patient in Patient.fakes():
            provider = patient.pcp
            self.assert_(provider, 'Does not have a provider')
            self.assert_(provider.is_fake(), 'Provider is not fake')
    
    def testAddVaccination(self):
        random_patient = Patient.fakes().order_by('?')[0]
        history = ImmunizationHistory(random_patient)
        imm = history.add_immunization()
        self.assert_(Immunization.objects.count() == 1)
        self.assert_(imm.patient == random_patient)

    def testImmunizationIsCandidate(self):
        random_patient = Patient.fakes().order_by('?')[0]
        history = ImmunizationHistory(random_patient)
        imm = history.add_immunization()
        ev = Vaers(imm)
        rule = DiagnosticsEventRule.random()
        code = random.choice(rule.heuristic_defining_codes.all())
        ev.cause_icd9(code)
        
        earliest_date = ev.matching_encounter.date - datetime.timedelta(days=TIME_WINDOW_POST_EVENT)
        
        candidates = Immunization.objects.filter(
            patient=random_patient,
            date__gte=earliest_date,
            date__lte=ev.matching_encounter.date
            )

        self.assert_(imm in candidates)
        


class TestClearing(unittest.TestCase):
    def testClear(self):
        clear()
        for klass in [Immunization, Encounter, LabResult, AdverseEvent]:
            self.failIf(klass.fakes().count() != 0)

        

class TestRuleEngine(unittest.TestCase):

    def setUp(self):
        clear()

    def testDiagnosticsPositiveDetection(self):
        for v in VAERS_DIAGNOSTICS.values():
            clear()
            # Get rule and corresponding heuristic 
            heuristic = DIAGNOSTICS_HEURISTICS[v['name']]
            rule = DiagnosticsEventRule.by_name(v['name'])[0]

            # Cause an adverse reaction to one random "victim".

            # Find proper patient, immunization and code
            victim = Patient.random()
            imm = ImmunizationHistory(victim).add_immunization()
            code = random.choice(rule.heuristic_defining_codes.all())
            
            # Create the adverse event
            ev = Vaers(imm)
            ev.cause_icd9(code)

            matches = heuristic.matches()
  
            self.assert_(len(matches) == 1, 'Expected to find one match, got %d' % len(matches))
            self.assert_(ev.matching_encounter in matches)
            
            


    def testDiagnosticsNegativeDetection(self):
        # Create an adverse event with a different code.
        # The heuristic should NOT result in a detection.
        for v in VAERS_DIAGNOSTICS.values():
            clear()
            # Get rule and corresponding heuristic 
            heuristic = DIAGNOSTICS_HEURISTICS[v['name']]
            rule = DiagnosticsEventRule.by_name(v['name'])[0]

            # Cause an adverse reaction to one random "victim".

            # Find proper patient, immunization and code
            victim = Patient.random()
            imm = ImmunizationHistory(victim).add_immunization()
            code = Icd9.objects.exclude(code__in=rule.heuristic_defining_codes.all()).order_by('?')[0]
            
            # Add an encounter after Immunization, 
            # but icd9 code is not part of the heuristic.
            ev = Vaers(imm)
            ev.cause_icd9(code)
  
            matches = heuristic.matches()

            self.assert_(len(matches) == 0)
            self.assert_(ev.matching_encounter not in matches)
        

    def testDiagnosticsNegativeByReocurrence(self):
        relevant = [v for v in VAERS_DIAGNOSTICS.values() 
                    if v.get('ignore_period', None)]

        for v in relevant:
            clear()
            # Get rule and corresponding heuristic 
            heuristic = DIAGNOSTICS_HEURISTICS[v['name']]
            rule = DiagnosticsEventRule.by_name(v['name'])[0]
            
            # Cause an adverse reaction to one random "victim".

            # Find proper patient, immunization and code
            victim = Patient.random()
            imm = ImmunizationHistory(victim).add_immunization()
            code = random.choice(rule.heuristic_defining_codes.all())
            
            # Create the adverse event
            ev = Vaers(imm)
            ev.cause_icd9(code)

            matches = heuristic.matches()
  
            # So far, the heuristic should detect as a positive
            self.assert_(len(matches) == 1, 'Expected to find one match, got %d' % len(matches))
            self.assert_(ev.matching_encounter in matches)

            # But when we add a past encounter with the same code, it
            # should not.
            ev.cause_icd9_ignored_for_reoccurrence(code, 
                                                   v['ignore_period'])
            matches = heuristic.matches()

            self.assert_(len(matches) == 0, 'Expected to find no match, got %d' % len(matches))
            self.assert_(ev.matching_encounter not in matches)


        
            
                         



    def testDiagnosticsNegativeByHistory(self):
        relevant = [v for v in VAERS_DIAGNOSTICS.values() 
                    if v.get('ignore_codes', None)]

        for v in relevant:
            clear()
            # Get rule and corresponding heuristic 
            heuristic = DIAGNOSTICS_HEURISTICS[v['name']]
            rule = DiagnosticsEventRule.by_name(v['name'])[0]
            
            # Cause an adverse reaction to one random "victim".

            # Find proper patient, immunization and code
            victim = Patient.random()
            imm = ImmunizationHistory(victim).add_immunization()
            code = random.choice(rule.heuristic_defining_codes.all())
            
            # Create the adverse event
            ev = Vaers(imm)
            ev.cause_icd9(code)


            matches = heuristic.matches()

            # So far, the heuristic should detect as a positive
            self.assert_(len(matches) == 1, 'Expected to find one match, got %d' % len(matches))
            self.assert_(ev.matching_encounter in matches, 'encounter not in matches')

            # But when we add a history condition that makes it
            # ignorable, it no longer is a match.
            discarding_code = random.choice(
                rule.heuristic_discarding_codes.all())
            ev.cause_icd9_ignored_for_history(discarding_code)


            matches = heuristic.matches()
            self.assert_(len(matches) == 0,  'Expected to find no match, got %d' % len(matches))
            self.assert_(ev.matching_encounter not in matches, 'heuristic match found encounter that should not be a match')


    def testFeverDetection(self):
        heuristic = FEVER_HEURISTIC
        
        # Find proper patient, immunization and code
        victim = Patient.random()
        imm = ImmunizationHistory(victim).add_immunization()
                
        # Create the adverse event
        ev = Vaers(imm)
        ev.cause_fever()

        matches = heuristic.matches()
  
        # So far, the heuristic should detect as a positive
        self.assert_(len(matches) == 1, 'Expected to find one match, got %d' % len(matches))
        self.assert_(ev.matching_encounter in matches)

        
        
    def testFeverNegativeDetection(self):
        '''To test whether this heuristic is checking only for fever, we'll give a normal encounter to the victim, but with a normal temperature'''
        
        heuristic = FEVER_HEURISTIC
        
        # Find proper patient, immunization and code
        victim = Patient.random()
        imm = ImmunizationHistory(victim).add_immunization()
                
        # Create the adverse event
        ev = Vaers(imm)
        ev.make_post_immunization_encounter()

        matches = heuristic.matches()


        self.assert_(len(matches) == 0)
        self.assert_(ev.matching_encounter not in matches)


    def testLabResultPositiveDetection(self):
        for heuristic in LAB_HEURISTICS:
            loinc = heuristic.loinc
            # Find patient and apply immunization
            victim = Patient.random()
            imm = ImmunizationHistory(victim).add_immunization()

            # Create the adverse event
            ev = Vaers(imm)

            # Get criteria, create one adverse event for each.
            for criterium in VAERS_LAB_RESULTS[loinc]['criteria']:
                if criterium == heuristic.criterium:
                    ev.cause_positive_lab_result(loinc, criterium)

            matches = heuristic.matches()




            # So far, the heuristic should detect as a positive
            self.assert_(len(matches) == 1, 'Expected to find one match, got %d' % len(matches))
            self.assert_(ev.matching_lab_result in matches, 'Lab Result not in matches')

    def testLabResultNegativeDetection(self):
        for heuristic in LAB_HEURISTICS:
            clear()
            # Find patient and apply immunization
            victim = Patient.random()
            imm = ImmunizationHistory(victim).add_immunization()

            # To check if the negative detection is ok, we will add
            # lab results for every possible criterium EXCEPT the one
            # that we are looking for. There should be no match for
            # that.

            #Create the adverse event
            ev = Vaers(imm)

            # Get criteria, trigger event if not considered interesting.
            for loinc in VAERS_LAB_RESULTS.keys():
                for criterium in VAERS_LAB_RESULTS[loinc]['criteria']:
                    if criterium != heuristic.criterium:
                        ev.cause_positive_lab_result(loinc, criterium)

            matches = heuristic.matches()

            # Assert that our heuristic can not find anything. There
            # should not be anything to find.
            self.assert_(len(matches) == 0, 'Expected to find no match, got %d' % len(matches))
            self.assert_(ev.matching_lab_result not in matches, 'Lab Result in matches, when it should not be there.')

    def testLabResultNegativeForHistory(self):
        ''' 
        Same strategy use in diagnosis test for history. We create a
        lab test that is positive, and later we add another old lab
        result that should make the whole thing a negative case. The
        first time, the heuristic must find one positive match, and
        after the excluding criteria, no match should occur'''

        for heuristic in LAB_HEURISTICS:
            loinc = heuristic.loinc
            # Find patient and apply immunization
            victim = Patient.random()
            imm = ImmunizationHistory(victim).add_immunization()

            # Create the adverse event
            ev = Vaers(imm)

            # Get criteria, create one adverse event for each.
            for criterium in VAERS_LAB_RESULTS[loinc]['criteria']:
                if criterium == heuristic.criterium:
                    ev.cause_positive_lab_result(loinc, criterium)

            matches = heuristic.matches()

            # So far, the heuristic should detect as a positive
            self.assert_(len(matches) == 1, 'Expected to find one match, got %d' % len(matches))
            self.assert_(ev.matching_lab_result in matches, 'Lab Result not in matches')

            # Get criteria, create one adverse event for each.
            for criterium in VAERS_LAB_RESULTS[loinc]['criteria']:
                if criterium == heuristic.criterium:
                    ev.cause_negative_lx_for_lkv(loinc, criterium)

            matches = heuristic.matches()

            if len(matches):
                import pdb
                pdb.set_trace()
                heuristic.matches()

            # Now, no match should show up.
            self.assert_(len(matches) == 0, 'Expected to find no match, got %d' % len(matches))
            self.assert_(ev.matching_lab_result not in matches, 'Lab Result in matches')
        



    

if __name__ == '__main__':
    clear()
    unittest.main()
    


