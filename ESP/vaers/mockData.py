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
    return mockData.create_immunization(patient, force_recent=True)
    

def create_adverse_event_encounter(immunization, patient):
    FEVER_EVENT_PCT = 50
    DIAGNOSTICS_EVENT_PCT = 15

    encounter = Enc()
    encounter.EncPatient = patient
    
    def fever_event():
        # How high the fever? 
        fever_temp = rules.TEMP_TO_REPORT + float(random.randrange(1, 30))/10
        encounter.temperature = fever_temp
        encounter.EncTemperature = str(fever_temp)
        

    def diagnostics_event():
        # What event happens to our patient? A random one...
        adverse_event_codes = rules.VAERS_DIAGNOSTICS.keys()
        try:
            ev_codes = random.choice(adverse_event_codes)
            icd = random.choice(ev_codes.split(';')).strip()
            encounter.EncICD9_Codes = icd
        except AttributeError:
            raise AttributeError, 'event_diagnosis_rule has no icd code'

            
    days_from_immunization = random.randrange(rules.TIME_WINDOW_POST_EVENT)
    delta = datetime.timedelta(days=days_from_immunization)
    encounter_date = immunization.date + delta
    
    encounter.date = encounter_date

    if random.randrange(100) <= FEVER_EVENT_PCT:
        fever_event()

    if random.randrange(100) <= DIAGNOSTICS_EVENT_PCT:
        diagnostics_event()

    encounter.save()
    
    return encounter
        
                                   
    


def create_false_alarm_adverse_event(patient):
    pass


if __name__=='__main__':
    pass


