import datetime
import random

from ESP.conf.common import EPOCH
from ESP.conf.models import Icd9
from ESP.esp.models import Demog, Enc, Immunization, Vaccine, Lx
from ESP.vaers.models import DiagnosticsEventRule, AdverseEvent
from ESP.utils import randomizer


from rules import TIME_WINDOW_POST_EVENT

FEVER_EVENT_PCT = 40
ICD9_EVENT_PCT = 10
IGNORE_FOR_REOCCURRENCE_PCT = 20
IGNORE_FOR_HISTORY_PCT = 60


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
    



class Vaers(object):

    def __init__(self, immunization):
        self.immunization = immunization
        self.patient = immunization.ImmPatient
        self.immunization_date = datetime.datetime.strptime(
            immunization.ImmDate, '%Y%m%d')

        self.matching_encounter = None


    def _encounter(self):
        days_after =  datetime.timedelta(days=random.randrange(
                0, TIME_WINDOW_POST_EVENT))

        when = self.immunization_date+days_after
        return Enc.make_mock(self.patient, when=when)


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
        today = datetime.datetime.today()

        interval = today - (max(self.patient.date_of_birth, EPOCH))
        days_ago = random.randrange(0, interval.days)
        
        when = today - datetime.timedelta(days=days_ago)
        assert (self.patient.date_of_birth <= when <= today)
        assert (EPOCH <= when <= today)

        # If everything is ok, give patient the vaccine
        return Immunization.make_mock(vaccine, self.patient, when)
        


    

                    

if __name__ == '__main__':
    fake_world()
