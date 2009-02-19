import os, sys
import random

sys.path.append('../')
import settings

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from esp.models import Demog

import rules
from utils import makeESPdata

PERCENTAGE_TO_AFFECT = 5

def make_fake_adverse_event_encounter(patient):
    # What adverse event happens to our patient? A random one...
    ev = random.choice(rules.ADVERSE_EVENTS_DIAGNOSTICS_RULES)
    
    # Get makeESPData to create the encounter for us
    makeESPdata.make_fake_encounter(patient, icds=ev.get('icd9_code', None))


if __name__=='__main__':
    total_patients = Demog.objects.count()
    people_count_to_affect = int(total_patients / (100/PERCENTAGE_TO_AFFECT))

    for p in Demog.manager.sample(size=people_count_to_affect):
        make_fake_adverse_event_encounter(p) 

    
    

    


