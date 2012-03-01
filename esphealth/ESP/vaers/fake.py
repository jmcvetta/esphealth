import datetime
import random
import optparse
import pdb

from ESP.conf.common import EPOCH
from ESP.static.models import Icd9, Loinc
from ESP.emr.models import Provider, Patient, Encounter, Immunization, LabResult
from ESP.conf.models import Vaccine
from ESP.vaers.models import DiagnosticsEventRule, AdverseEvent
from ESP.utils.utils import log
from ESP.utils import randomizer
from ESP.utils import utils

import rules
from rules import TIME_WINDOW_POST_EVENT, VAERS_LAB_RESULTS


POPULATION_SIZE = 200

FEVER_EVENT_PCT = 40
ICD9_EVENT_PCT = 15
LX_EVENT_PCT = 15
IGNORE_FOR_REOCCURRENCE_PCT = 20
IGNORE_FOR_HISTORY_PCT = 60

USAGE_MSG = '''\
%prog [options]
    Either '-p', '-i' or '-a' must be specified.
'''

class ImmunizationHistory(object):
    IMMUNIZATIONS_PER_PATIENT = 1

    def __init__(self, patient):
        self.patient = patient
        self.clear()
        
    def clear(self):
        Immunization.objects.filter(patient=self.patient).delete()

    def add_immunization(self, save_on_db=False):
        '''
        Gives a completely random vaccine to a patient in a
        completely random date between his date_of_birth and
        today()
        '''
        
        # Find a vaccine
        vaccine = Vaccine.random()

        # Find a random date in the past
        today = datetime.date.today()

        # Sanity check. If the patient was born "today", we can not put the immunization in the past.
        if self.patient.date_of_birth >= today:
            days_ago = 0
        else:
            interval = today - (max(self.patient.date_of_birth, EPOCH))
            days_ago = random.randrange(0, interval.days)
        
        when = today - datetime.timedelta(days=days_ago)
        assert (self.patient.date_of_birth <= when <= today)
        assert (EPOCH <= when <= today)

        # If everything is ok, give patient the vaccine
        return Immunization.make_mock(vaccine, self.patient, when, save_on_db=save_on_db)

def check_for_reactions(imm):
    # Should we cause a fever event?
    if random.randrange(100) <= FEVER_EVENT_PCT:
        ev = Vaers(imm)
        ev.cause_fever()
    # Or a icd9 Event?
    elif random.randrange(100) <= ICD9_EVENT_PCT:
        ev = Vaers(imm)
        rule = DiagnosticsEventRule.random()
        try:
            code = random.choice(rule.heuristic_defining_codes.all())
        except Exception, why:
            rules.define_active_rules()
            #rules.map_lab_tests()

        ev.cause_icd9(code)
        
        # Maybe it's one that should be ignored?
        if random.randrange(100) <= IGNORE_FOR_REOCCURRENCE_PCT:
            ev.cause_icd9_ignored_for_reoccurrence(code, 12)
        elif random.randrange(100) <= IGNORE_FOR_HISTORY_PCT:
            if len(rule.heuristic_discarding_codes.all()) > 0:
                discarding_code = random.choice(
                    rule.heuristic_discarding_codes.all())
                ev.cause_icd9_ignored_for_history(discarding_code)

    # Or a lab result event?
    elif random.randrange(100) <= LX_EVENT_PCT:
        ev = Vaers(imm)
        syndrome = random.choice(VAERS_LAB_RESULTS.keys())
        lx = VAERS_LAB_RESULTS[syndrome]
        loinc = random.choice(lx['codes'])
        criterion = random.choice(lx['criteria_adult'])
        ev.cause_positive_lab_result(loinc, criterion)
        # Maybe it's one that should be ignored?
        if random.randrange(100) <= IGNORE_FOR_HISTORY_PCT:
            ev.cause_negative_lx_for_lkv(loinc, criterion)


                    
class Vaers(object):

    def __init__(self, immunization):
        self.immunization = immunization
        self.patient = immunization.patient
        self.immunization_date = immunization.date

        self.matching_encounter = None
        self.matching_lab_result = None
        self.last_lab_result = None # Last LabResult done before the immunization

    def _encounter(self):
        days_after =  datetime.timedelta(days=random.randrange(
                1, TIME_WINDOW_POST_EVENT))
        when = self.immunization_date+days_after
        return Encounter.make_mock(self.patient, when=when)

    def _lab_result(self):
        days_after =  datetime.timedelta(days=random.randrange(
                1, TIME_WINDOW_POST_EVENT))
        when = self.immunization_date+days_after
        return LabResult.make_mock(self.patient, when=when)

    def make_post_immunization_encounter(self):
        encounter = self._encounter()
        encounter.temperature = randomizer.body_temperature() 
        encounter.save()
        self.matching_encounter = encounter

    def cause_fever(self):
        encounter = self._encounter()
        encounter.temperature = randomizer.fever_temperature() 
        encounter.save()
        self.matching_encounter = encounter

    def cause_icd9(self, code):
        encounter = self._encounter()
        encounter.save()
        encounter.temperature = randomizer.body_temperature() 
        encounter.icd9_codes.add(code)
        encounter.save()
        
        self.matching_encounter = encounter

    def cause_icd9_ignored_for_history(self, code):
        
        
        
        maximum_days_ago =  (self.immunization_date - 
                             self.patient.date_of_birth).days

        try:
            when = self.immunization_date - datetime.timedelta(
                days=random.randrange(1, maximum_days_ago))
        except:
            pdb.set_trace()

        past_encounter = Encounter.make_mock(self.patient, when=when)
        past_encounter.temperature = randomizer.body_temperature()
        past_encounter.save()
        past_encounter.icd9_codes.add(code)
        past_encounter.save()
        
    def cause_icd9_ignored_for_reoccurrence(self, code, max_period):
        maximum_days_ago = min(
            (self.immunization_date - self.patient.date_of_birth).days,
            max_period * 30
            )

        when = self.immunization_date - datetime.timedelta(
            days=random.randrange(1, maximum_days_ago))

        past_encounter = Encounter.make_mock(self.patient, when=when)
        past_encounter.temperature = randomizer.body_temperature()
        past_encounter.save()
        past_encounter.icd9_codes.add(code)
        past_encounter.save()

    def cause_positive_lab_result(self, loinc, criterion):
        lx = self._lab_result()
        # criterion['trigger'] is always a string that represents an
        # inequation in the "X(>|<)Value" format.
        
        trigger = criterion['trigger']
        gt_pos = trigger.find('>')
        lt_pos = trigger.find('<')
        
        value = -1
        
        if (gt_pos != -1) and (len(trigger.split('>')) == 2):
            baseline = trigger.split('>')[-1]
            value = float(baseline) + 1
            
        if (lt_pos != -1) and (len(trigger.split('<')) == 2):
            baseline = trigger.split('<')[-1]
            value = float(baseline) - 1

        # If value has not been updated, this means our criterion is ill-formed.
        if value == -1: 
            raise ValueError, 'Couldn\'t figure out the trigger value'


        lx.native_code = loinc
        lx.result_float = float(value)
        lx.save()
        self.matching_lab_result = lx

    def cause_negative_lx_for_lkv(self, loinc, criterion):
        ''' 
        exclude_if is a entry that may exist on criteria rules. It is
        a tuple that contains a comparator and a thresold string. The
        thresold string is a string that is supposed to represent a math
        inequation that compares the value of the last known value to
        the value of the current latest post-immunization lab result.

        Example strings are "LKV+0.5" or "LKV*0.8". We use those
        strings to calculate a value for LKV that, given the value of
        the current lx, make the current lx be a negative case.

        Once the proper value for lkv is found, we create a mock LabResult
        with that value.
        '''

        # We are supposed to have add the positive case first.
        assert self.matching_lab_result
        
        # This is needed because we need the value for the current lab.
        current_value = self.matching_lab_result.result_float

        # The regular expression that breaks the string into its components.
        import re
        regex = re.compile('(LKV)([\+|\-|\*|\/])(.*)')  #LKV+0.5, LKV-0.5, LKV*1.3...
        comparator, baseline = criterion['exclude_if']

        try:
            lkv_equation = regex.match(baseline)
            op, coefficient = lkv_equation.group(2), float(lkv_equation.group(3))
        except:
            raise ValueError, 'Could not create a negative %s lx based on rules from %s' % (loinc, criterion)

        # Now that we have all the terms of the inequation, we solve it
        # (in a very rudimentary way)

        # One example for uur original inequation could be "X > LKV*1.5'
        # So we do the operation to isolate LKV in one side of the inequation

        if op == '*': current_value /= coefficient # X > LKV*1.5 --> X/1.5 > LKV
        elif op == '/': current_value *= coefficient # You got the idea
        elif op == '-': current_value += coefficient
        elif op == '+': current_value -= coefficient

        # Now that LKV is isolated, we just checked the comparator and
        # give it a value that make the inequation true.
        lkv = (current_value - 0.1) if comparator == '>' else (current_value + 0.1) 
        
        # Now that we have the value, we create the LabResult corresponding
        # to the "Last" one. It has to be before the immunization.
        earliest = max(self.patient.date_of_birth, EPOCH)
        max_days = (self.immunization.date - earliest).days
        days_ago = random.randrange(1, max_days) if max_days > 1 else 1
        when = self.immunization.date - datetime.timedelta(days=days_ago)

        last_lx = LabResult.make_mock(self.patient, when=when)

        # And now we add the values for lkv
        last_lx.result_float = lkv
        last_lx.result_string = str(lkv)
        last_lx.loinc = loinc
        last_lx.save()

        


def main():
    parser = optparse.OptionParser(usage=USAGE_MSG)
    parser.add_option('-c', '--clear', action='store_true', dest='clear',
                      help='Clear all fake Entities from the Database')
    parser.add_option('-p', '--patients', action='store_true', dest='patients',
                      help='Create Population of Patients')
    parser.add_option('-i', '--imm', action='store_true', dest='immunizations',
                      help='Create Immunization History for Patients')
    
    parser.add_option('-n', '--how-many', dest='population_size', default=None,
                      help='Define how many patients will be affected/created.')


    parser.add_option('-a', '--all', action='store_true', dest='all', 
        help='Generate new patients and immunization history')

    (options, args) = parser.parse_args()


    total_patients = int(options.population_size) or POPULATION_SIZE
    
    if options.all:
        options.patients = True
        options.immunizations = True
        options.clear = False

    if not (options.patients or options.immunizations):
        parser.print_help()
        import sys
        sys.exit()


    if options.clear:
        clear()

    patients = []

    if options.patients:
        for i in xrange(total_patients):
            patients.append(Patient.make_mock())


    if options.immunizations:
        for patient in patients:
            log.info('Creating Immunization history for patient %s' % patient)
            history = ImmunizationHistory(patient)
            for i in xrange(ImmunizationHistory.IMMUNIZATIONS_PER_PATIENT):
                imm = history.add_immunization()
                check_for_reactions(imm)
                
                




def clear():
    for klass in [Patient, Immunization, Encounter, LabResult, AdverseEvent]:
        klass.delete_fakes()




if __name__ == '__main__':
    main()
