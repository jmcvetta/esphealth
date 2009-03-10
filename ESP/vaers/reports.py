import os, sys

import pdb
import datetime

from utils.utils import output
from VAERSevents import detect_adverse_events


def temporal_clustering(out_file=None, **kw):
    # Get fever events and output to file with format
    # id vaccDate eventDate daysToEvent VaccName eventName Ageyrs GenderMF 
        
    start_date = kw.pop('start_date', None)
    end_date = kw.pop('end_date', None)

    f = (out_file and open(out_file, 'w')) or None
      
    for ev in detect_adverse_events(detect_only='fever', 
                                    start_date=start_date,
                                    end_date=end_date):

        imm = ev.immunization
        imm.date = datetime.datetime.strptime(imm.ImmDate, '%Y%m%d')
        encounter_date = datetime.datetime.strptime(ev.encounter.EncEncounter_Date, '%Y%m%d')

        days_to_event = (encounter_date - imm.date).days

        output('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (
                imm.ImmRecId , 
                imm.date.strftime('%m/%d/%Y'), 
                encounter_date.strftime('%m/%d/%Y'), 
                days_to_event, 
                imm.ImmName, ev.name, 
                ev.patient.getAge(), ev.patient.DemogGender
                ), f)


def vaers_summary(immunization):
    '''Given an immunization that has caused an adverse event, 
    returns information details about the event and the patient'''
    return {}

def vaccines_on_date(immunization):
    return []

def prior_vaers(immunization):
    return []

def prior_vaers_in_sibling(immunization):
    return []

def prior_vaccinations(immunization):
    return []

def previous_reports(event):
    return []

def patient_stats(patient):
    return {}

def vaccination_project_stats(immunization):
    return {}



    
    

    
            
            


if __name__ == '__main__':
    print 'Getting All Events...'
    print '\n\n\n'
    print temporal_clustering()
    print '\n\n\n'
