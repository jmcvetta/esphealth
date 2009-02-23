import os, sys
import random
import datetime

sys.path.append('../')
import settings

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from esp.models import Demog, Immunization, Enc, icd9

import rules
from tests import mockData
from utils.utils import timeit

PERCENTAGE_TO_AFFECT = 5
ONE_WEEK = 7

#@timeit
def clear():
    if settings.DEBUG:
        Immunization.objects.all().delete()
        Demog.objects.all().delete()
        Enc.objects.all().delete()
    else: 
        raise ValueError, 'attempt to clear database when not in Debug mode'

def create_population(size):
    mockData.create_patient_population(size)

def create_recent_immunization(patient):
    mockData.create_immunization(patient, force_recent=True)
    

def create_adverse_event_encounter(patient):
    FEVER_EVENT_PCT = 50
    DIAGNOSTICS_EVENT_PCT = 15

    def fever_event(patient, date):
        # How high the fever? 
        fever_temp = rules.FEVER_TEMP_TO_REPORT + float(random.randrange(1, 30))/10
        mockData.create_encounter(patient, 
                                  date=date, 
                                  temperature=fever_temp)
        

    def diagnostics_event(patient, date):
        # What event happens to our patient? A random one...
        adverse_event_codes = rules.VAERS_DIAGNOSTICS.keys()
        try:
            ev_codes = random.choice(adverse_event_codes)
            icd = random.choice(ev_codes.split(';'))
            # Create encounter with specific code
            mockData.create_encounter(patient, date=date, icds=icd)
        except AttributeError:
            raise AttributeError, 'event_diagnosis_rule has no icd code'

        
    imm = mockData.create_immunization(patient)
    if random.randrange(100) <= FEVER_EVENT_PCT:
        delta = datetime.timedelta(days=random.randrange(ONE_WEEK))
        fever_event(patient, imm.ImmDate-delta)

    if random.randrange(100) <= DIAGNOSTICS_EVENT_PCT:
        delta = datetime.timedelta(days=random.randrange(ONE_WEEK))
        diagnostics_event(patient, imm.ImmDate-delta)
                                   
    


def create_false_alarm_adverse_event(patient):
    pass


if __name__=='__main__':
    pass


