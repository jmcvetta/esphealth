import os, sys

import pdb
import datetime

from vaers.models import FeverEvent


def temporal_clustering(filename, **kw):
    # Get fever events and output to file with format
    # id vaccDate eventDate daysToEvent VaccName eventName Ageyrs GenderMF 
        
    now = datetime.datetime.now()
    yesterday = now - datetime.timedelta(days=1)

    start_date = kw.pop('start_date', yesterday)
    end_date = kw.pop('end_date', now)

    f = open(filename, 'w')

    events = FeverEvent.objects.filter(
        last_updated__gte=start_date,
        last_updated__lte=end_date
        )
      
    for ev in events:
        imm = ev.immunization
        imm.date = datetime.datetime.strptime(imm.ImmDate, '%Y%m%d')
        encounter_date = datetime.datetime.strptime(
            ev.encounter.EncEncounter_Date, '%Y%m%d')
        
        days_to_event = (encounter_date - imm.date).days
        f.write('\t'.join(str(x) for x in [
                    imm.ImmRecId, 
                    imm.ImmDate,
                    encounter_date.strftime('%Y%m%d'), 
                    days_to_event, 
                    imm.ImmName, ev.matching_rule_explain, 
                    ev.patient.getAge(), ev.patient.DemogGender
                    ]))
        f.write('\n')

    f.close()

    
    
    
