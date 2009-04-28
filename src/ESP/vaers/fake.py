import datetime
import random

from ESP.conf.models import Icd9
from ESP.esp.models import Demog, Enc, Immunization, Vaccine
from ESP.vaers.models import FeverEvent, DiagnosticsEvent
from ESP.vaers.models import DiagnosticsEventRule
from ESP.utils import randomizer


from rules import TIME_WINDOW_POST_EVENT

FEVER_EVENT_PCT = 30
ICD9_EVENT_PCT = 5


def create_history(patient):

    history = ImmunizationHistory(patient)
    vaccine_date = patient.date_of_birth + datetime.timedelta(days=180)


    for i in xrange(ImmunizationHistory.IMMUNIZATIONS_PER_PATIENT):
        try:
            # Check conditions for vaccine and add to history
            causes_fever = random.randrange(100) > FEVER_EVENT_PCT
            causes_icd9 = random.randrange(100) > ICD9_EVENT_PCT
            history.add_immunization(Vaccine.random(), vaccine_date,
                                     causes_fever=causes_fever,
                                     causes_icd9=causes_icd9)
        
            # Set date for next vaccination
            vaccine_date += datetime.timedelta(days=random.randrange(30, 180))
        except:
            continue
        
        
        

class ImmunizationHistory(object):

    IMMUNIZATIONS_PER_PATIENT = 10
    

    def __init__(self, patient):
        self.patient = patient
        self.clear()
        
    def clear(self):
        Immunization.objects.filter(ImmPatient=patient).delete()

    def add_immunization(self, vaccine, date, **kw):
        causes_fever_event = kw.get('causes_fever', False)
        causes_icd9_event = kw.get('causes_icd9', False)
        
        assert (date >= datetime.datetime.now(), 
                'Can not vaccinate someone in the future')

        imm = Immunization.objects.create(
            ImmPatient=self.patient,
            ImmType = vaccine.code,
            ImmDate = date.strftime('%Y%m%d'),
            ImmName = 'FAKE',
            ImmManuf = 'FAKE',
            ImmDose = '3.1415 pi',
            ImmLot = 'FAKE',
            ImmVisDate = date.strftime('%Y%m%d'),
            ImmRecId = 'FAKE-%s' % self.patient.id
            )
        
        # If this immunization causes no event, our job is done.
        if not causes_fever_event and not causes_icd9_event:
            return

        # Else, we need to produce a Enc that happens after vaccination date
        days_after = datetime.timedelta(
            days=random.randrange(0, TIME_WINDOW_POST_EVENT))
        encounter = Enc.make_mock(self.patient,
                                  when=date+days_after)

        # And we need to set the Enc to reflect the information we
        # need recorded to qualify as an event.
        temp = randomizer.fever_temperature() if causes_fever_event else randomizer.body_temperature()

        encounter.EncTemperature = temp

        encounter.save()

        if causes_icd9_event:
            # Get a random rule that is active. This will be our event
            # to be detected. Get one of the icd9s that define that
            # rule and add to the reported icd9 list.
            rule = DiagnosticsEventRule.objects.filter(
                in_use=True).order_by('?')[0]
            code = random.choice(rule.heuristic_defining_codes.all())
            encounter.reported_icd9_list.add(code)

    

                    

if __name__ == '__main__':
    for patient in Demog.fakes():
        create_history(patient)
    
    
