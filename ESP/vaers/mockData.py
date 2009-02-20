import os, sys
import random

sys.path.append('../')
import settings

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from esp.models import Demog, Immunization, Enc, icd9

import rules
from tests import mockData

PERCENTAGE_TO_AFFECT = 5

def clear():
    if settings.DEBUG:
        Immunization.objects.all().delete()
        Demog.objects.all().delete()
        Enc.objects.all().delete()
    else: 
        raise ValueError, 'attempt to clear database when not in Debug mode'

def create_population(size):
    mockData.create_patient_population(size)

def make_recent_immunization(patient):
    mockData.fake_immunization(patient, force_recent=True)
    

def make_fake_adverse_event_encounter(patient):
    # What adverse event happens to our patient? A random one...
    adverse_event_codes = rules.ADVERSE_EVENTS_DIAGNOSTICS.keys()
    try:
        ev_codes = random.choice(adverse_event_codes)
        icd = random.choice(ev_codes.split(';'))
        # Create encounter with specific code
        mockData.make_fake_encounter(patient, icds=icd)
    except AttributeError:
        raise AttributeError, 'event_diagnosis_rule has no icd code'


if __name__=='__main__':
    total_patients = Demog.objects.count()
    total_affected = int(total_patients / (100/PERCENTAGE_TO_AFFECT))

    for p in Demog.manager.sample(size=total_affected):
        make_fake_adverse_event_encounter(p) 

    
    

    


