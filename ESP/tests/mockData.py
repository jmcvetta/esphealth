import os, sys
sys.path.append('../')

import datetime, random
import string



# FIXME: some utility functions are not able to see the ESP module
# For now, We need it, so we add the parent folder to the path.
# In the future, this should not be necessary.
import settings
sys.path.append(os.path.join(settings.TOPDIR, '../'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from esp.models import Demog, Immunization, Enc
from utils import utils

# For testing
FIRST_NAMES = ['Bill', 'Mary', 'Jim', 'Donna', 'Patricia', 
               'Susan', 'Robert', 'Barry', 'Bazza', 'Deena', 
               'Kylie', 'Shane', 'John', 'Michael', 'Anne',
               'Spock', 'Kruskal', 'Platt', 'Klompas', 'Lazarus', 
               'Who', 'Nick', 'Livingston', 'Doolittle', 'Casey', 'Finlay'
               ]


LAST_NAMES = ['Bazfar', 'Barfoo', 'Hoobaz', 'Sotbar', 'Farbaz', 
              'Zotbaz', 'Smith', 'Jones', 'Fitz', 'Wong', 'Wright', 
              'Ngyin', 'Miller']


SITES = ['Brookline Ave', 'West Roxbury', 'Matapan', 'Sydney', 'Kansas']

VACCINES = {
    'mmr':'Measles, Mumps, Rubeola', 
    'Tetanus':'Tetanus',
    'Flu':'Influenza',
    'OPV':'polio', 
    'BCG':'Tuberculosis'
    }





def make_fake_demog():
    id = utils.random_string(length=20)
    medical_record_id = utils.random_string(length=20)
    last_name = random.choice(LAST_NAMES)
    first_name = random.choice(FIRST_NAMES)
    middle_initial = random.choice(string.uppercase)
    date_of_birth = datetime.datetime.now() - datetime.timedelta(
        days=random.randrange(0, 36500),
        minutes=random.randrange(0, 1440),
        seconds=random.randrange(0, 60)
        ) # Any age up to 100 years old.
    
    gender = 'M' if random.random() <= 0.49 else 'F'
    
    d = Demog(
        DemogPatient_Identifier=id,
        DemogMedical_Record_Number=medical_record_id,
        DemogFirst_Name = first_name,
        DemogLast_Name = last_name,
        DemogMiddle_Initial = middle_initial,
        DemogDate_of_Birth = date_of_birth,
        DemogGender = gender
        )

    d.save()
    
    return d


def make_fake_immunization(patient=None, force_recent=False):
    vaccine_type = random.choice(VACCINES.keys())
    vaccine_name = VACCINES[vaccine_type]
    now = datetime.datetime.now()
    days_ago = 0 if force_recent else random.randrange(0, 1000)
    date = now - datetime.timedelta(days=days_ago, minutes=random.randrange(0, 2500)) 
    
    # if patient is not defined, we get a random one from the database.
    patient = patient or Demog.manager.random() 

    # Let's check if this patient has a immunization record
    # In case there are multiple records, we take any one.
    # If patient has a immunization record, use it. Else, create random.
    # lullis: I think a patient should have only one imm_record. 
    patient_imm = Immunization.objects.filter(ImmPatient=patient)
    imm_record_id = patient_imm[0].ImmRecId if patient_imm else utils.random_string(length=100)
        
       
    i = Immunization(
        ImmPatient=patient,
        ImmType = vaccine_type,
        ImmName = vaccine_name,
        ImmDate = date,
        ImmRecId = imm_record_id
        )
        
    i.save()
    return i
        
def make_fake_encounter(patient, force_recent=False, **conditions):
    # make a date for the encounter
    now = datetime.datetime.now()
    days_ago = 0 if force_recent else random.randrange(0, 1000)
    date = now - datetime.timedelta(days=days_ago, 
                                    minutes=random.randrange(0, 2000))

    # Conditions that are to be reported in encounter.
    # Magic Numbers: default temperature oscilate between 97 and 98 degrees.
    temp = conditions.get('temperature', 
                          97.5 + (float(random.randrange(-5, 5))/10)
                          )
    icds = conditions.get('icds', '')

    e = Enc(
        EncPatient=patient,
        EncMedical_Record_Number=patient.DemogMedical_Record_Number,
        EncEncounter_ID=utils.random_string(length=20),
        EncICD9_Codes = icds,
        EncTemperature = temp,
        EncEncounter_Date = date
        )

    e.save()

    return e


def create_patient_population(size):
    for i in xrange(size):
        make_fake_demog()


if __name__ == "__main__":

    patients = [make_fake_demog() for p in xrange(100)]
    for patient in patients:
        make_fake_immunization(patient)
        make_fake_encounter(patient)


            
    
