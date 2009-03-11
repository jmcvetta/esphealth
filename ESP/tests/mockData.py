import os, sys
sys.path.append(os.path.realpath('..'))

import datetime, random
import string

import settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from esp.models import Demog, Immunization, Enc, Provider
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
    code = utils.random_string(length=20)
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
        DemogPatient_Identifier=code,
        DemogMedical_Record_Number=medical_record_id,
        DemogFirst_Name = first_name,
        DemogLast_Name = last_name,
        DemogMiddle_Initial = middle_initial,
        DemogDate_of_Birth = date_of_birth,
        DemogGender = gender
        )

    d.save()
    
    return d

def make_fake_provider():
    id = utils.random_string(length=10)
    last_name = random.choice(LAST_NAMES)
    first_name = random.choice(FIRST_NAMES)
    middle_initial = random.choice(string.uppercase)
    title = random.choice(['Dr.', 'M.D', 'Ph.D', ''])
    address = ' '.join([str(random.randrange(1000)), 
                        random.choice(SITES), 
                        random.choice(['Street', 'Ave', 'Rd', 'Lane'])
                        ])
    zip_code = str(10000 + random.randrange(90000))
    phone = utils.random_phone_number()

    department = 'MCIR VIM LHD Site' # I really need to check what
                                     # kind of value should go here
    
    prov = Provider(
        provCode=id,
        provLast_Name=last_name,
        provFirst_Name=first_name,
        provMiddle_Initial=middle_initial,
        provTitle=title,
        provPrimary_Dept = department,
        provPrimary_Dept_Address_1 = address,
        provPrimary_Dept_Zip = zip_code,
        provTelAreacode=phone.split('-')[0],
        provTel=phone,
        )

    prov.save()

    return prov
        



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

    for i in xrange(1000):
        make_fake_provider()
