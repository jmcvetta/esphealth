import datetime
import random

import optparse

from ESP.conf.common import EPOCH
from ESP.conf.models import Icd9
from ESP.esp.models import Demog, Enc, Immunization, Vaccine, Lx
from ESP.vaers.models import DiagnosticsEventRule, AdverseEvent
from ESP.utils import randomizer
from ESP.utils import utils


from rules import TIME_WINDOW_POST_EVENT, VAERS_LAB_RESULTS

FEVER_EVENT_PCT = 40
ICD9_EVENT_PCT = 15
LX_EVENT_PCT = 15
IGNORE_FOR_REOCCURRENCE_PCT = 20
IGNORE_FOR_HISTORY_PCT = 60

   
USAGE_MSG = '''\
%prog [options]
    Either '-p', '-i' or '-a' must be specified.
'''


def main():
    # 
    # TODO: We need a lockfile or some othermeans to prevent multiple 
    # instances running at once.
    #
    parser = optparse.OptionParser(usage=USAGE_MSG)
    parser.add_option('-p', '--patients', action='store_true', 
                      dest='patients', help='Generate new Patient Population')
    parser.add_option('-i', '--immunizations', action='store_true', dest='i',
                      help='Create Immunization History for Patients')

    parser.add_option('-a', '--all', action='store_true', dest='all', 
        help='Generate new patients and immunization history')

    (options, args) = parser.parse_args()

    if options.all:
        fake_world()
    else:
        parser.print_help()
        print 'Right now, only --all is implemented.'
        import sys
        sys.exit()


def clear():
    for klass in [Immunization, Enc, Lx, AdverseEvent]:
        klass.delete_fakes()

def fake_world():
    clear()
    for patient in Demog.fakes():
        history = ImmunizationHistory(patient)
        for i in xrange(ImmunizationHistory.IMMUNIZATIONS_PER_PATIENT):
            imm = history.add_immunization()
            # Should we cause a fever event?
            if random.randrange(100) <= FEVER_EVENT_PCT:
                ev = Vaers(imm)
                ev.cause_fever()
            # Or a icd9 Event?
            elif random.randrange(100) <= ICD9_EVENT_PCT:
                ev = Vaers(imm)
                rule = DiagnosticsEventRule.random()
                code = random.choice(rule.heuristic_defining_codes.all())
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
                loinc = random.choice(VAERS_LAB_RESULTS.keys())
                lx = VAERS_LAB_RESULTS[loinc]
                criterium = random.choice(lx['criteria'])
                ev.cause_positive_lab_result(loinc, criterium)
                # Maybe it's one that should be ignored?
                if random.randrange(100) <= IGNORE_FOR_HISTORY_PCT:
                    ev.cause_negative_lx_for_lkv(loinc, criterium)
                    
                

                
    



class Vaers(object):

    def __init__(self, immunization):
        self.immunization = immunization
        self.patient = immunization.ImmPatient
        self.immunization_date = utils.date_from_str(immunization.ImmDate)

        self.matching_encounter = None
        self.matching_lab_result = None
        self.last_lab_result = None # Last Lx done before the immunization



    def _encounter(self):
        days_after =  datetime.timedelta(days=random.randrange(
                0, TIME_WINDOW_POST_EVENT))

        when = self.immunization_date+days_after
        return Enc.make_mock(self.patient, when=when)

    def _lab_result(self, loinc):
        days_after =  datetime.timedelta(days=random.randrange(
                0, TIME_WINDOW_POST_EVENT))

        when = self.immunization_date+days_after
        return  Lx.make_mock(loinc, self.patient, when=when)
       





    def make_post_immunization_encounter(self):
        encounter = self._encounter()
        encounter.EncTemperature = randomizer.body_temperature() 
        encounter.save()
        self.matching_encounter = encounter



    def cause_fever(self):
        encounter = self._encounter()
        encounter.EncTemperature = randomizer.fever_temperature() 
        encounter.save()
        self.matching_encounter = encounter

    def cause_icd9(self, code):
        encounter = self._encounter()
        encounter.save()
        encounter.EncTemperature = randomizer.body_temperature() 
        encounter.reported_icd9_list.add(code)
        encounter.save()
        
        self.matching_encounter = encounter

        


    def cause_icd9_ignored_for_history(self, code):
        maximum_days_ago =  (self.immunization_date - 
                             self.patient.date_of_birth).days

        when = self.immunization_date - datetime.timedelta(
            days=random.randrange(0, maximum_days_ago))

        past_encounter = Enc.make_mock(self.patient, when=when)
        past_encounter.EncTemperature = randomizer.body_temperature()
        past_encounter.save()
        past_encounter.reported_icd9_list.add(code)
        past_encounter.save()


        
    def cause_icd9_ignored_for_reoccurrence(self, code, max_period):
        maximum_days_ago = min(
            (self.immunization_date - self.patient.date_of_birth).days,
            max_period * 30
            )

        when = self.immunization_date - datetime.timedelta(
            days=random.randrange(0, maximum_days_ago))

        past_encounter = Enc.make_mock(self.patient, when=when)
        past_encounter.EncTemperature = randomizer.body_temperature()
        past_encounter.save()
        past_encounter.reported_icd9_list.add(code)
        past_encounter.save()

    def cause_positive_lab_result(self, loinc, criterium):
        lx = self._lab_result(loinc)
        # criterium['trigger'] is always a string that represents an
        # inequation in the "X(>|<)Value" format.
        
        trigger = criterium['trigger']
        gt_pos = trigger.find('>')
        lt_pos = trigger.find('<')
        
        value = -1
        
        if (gt_pos != -1) and (len(trigger.split('>')) == 2):
            baseline = trigger.split('>')[-1]
            value = float(baseline) + 1
            
        if (lt_pos != -1) and (len(trigger.split('<')) == 2):
            baseline = trigger.split('<')[-1]
            value = float(baseline) - 1

        # If value has not been updated, this means our criterium is ill-formed.
        if value == -1: 
            raise ValueError, 'Couldn\'t figure out the trigger value'

        lx.native_code = loinc
        lx.result_float = float(value)
        lx.save()

        self.matching_lab_result = lx

    def cause_negative_lx_for_lkv(self, loinc, criterium):
        ''' 
        exclude_if is a entry that may exist on criteria rules. It is
        a tuple that contains a comparator and a thresold string. The
        thresold string is a string that is supposed to represent a math
        inequation that compares the value of the last known value to
        the value of the current latest post-immunization lab result.

        Example strings are "LKV+0.5" or "LKV*0.8". We use those
        strings to calculate a value for LKV that, given the value of
        the current lx, make the current lx be a negative case.

        Once the proper value for lkv is found, we create a mock Lx with that value.
        
        '''

        # We are supposed to have add the positive case first.
        assert self.matching_lab_result
        
        # This is needed because we need the value for the current lab.
        current_value = self.matching_lab_result.result_float

        # The regular expression that breaks the string into its components.
        import re
        regex = re.compile('(LKV)([\+|\-|\*|\/])(.*)')  #LKV+0.5, LKV-0.5, LKV*1.3...
        comparator, baseline = criterium['exclude_if']

        try:
            lkv_equation = regex.match(baseline)
            op, coefficient = lkv_equation.group(2), float(lkv_equation.group(3))
        except:
            import pdb
            pdb.set_trace()
            raise ValueError, 'Could not create a negative %s lx based on rules from %s' % (loinc, criterium)

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
        

        # Now that we have the value, we create the Lx corresponding
        # to the "Last" one. It has to be before the immunization.
        earliest = max(self.patient.date_of_birth, EPOCH)
        max_days = (self.immunization.date - earliest).days
        days_ago = random.randrange(1, max_days) if max_days > 1 else 1
        when = self.immunization.date - datetime.timedelta(days=days_ago)

        last_lx = Lx.make_mock(loinc, self.patient, when=when)

        # And now we add the values for lkv
        last_lx.result_float = lkv
        last_lx.result_string = str(lkv)
        last_lx.loinc = loinc
        last_lx.save()


class ImmunizationHistory(object):

    IMMUNIZATIONS_PER_PATIENT = 10
    

    def __init__(self, patient):
        self.patient = patient
        self.clear()
        
    def clear(self):
        Immunization.objects.filter(ImmPatient=self.patient).delete()

    def add_immunization(self):
        ''' Gives a completely random vaccine to a patient in a
        completely random date between his date_of_birth and
        today()'''
        
        # Find a vaccine
        vaccine = Vaccine.random()

        # Find a random date

        today = datetime.date.today()

        interval = today - (max(self.patient.date_of_birth, EPOCH))
        days_ago = random.randrange(0, interval.days)
        
        when = today - datetime.timedelta(days=days_ago)
        assert (self.patient.date_of_birth <= when <= today)
        assert (EPOCH <= when <= today)

        # If everything is ok, give patient the vaccine
        return Immunization.make_mock(vaccine, self.patient, when)
        


if __name__ == '__main__':
    main()
