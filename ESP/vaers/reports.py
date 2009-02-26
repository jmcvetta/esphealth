import os, sys

PWD = os.path.realpath(__file__)
PARENT_DIR = os.path.join(PWD, '../')
if PARENT_DIR not in sys.path:
    sys.path.append(PARENT_DIR)

import pdb
import datetime

from utils.utils import output
from VAERSevents import get_adverse_events

def temporal_clustering(out_file=None):
    # Get fever events and output to file with format
    # id vaccDate eventDate daysToEvent VaccName eventName Ageyrs GenderMF 
        
    f = (out_file and open(out_file, 'w')) or None
      
    for ev in get_adverse_events(detect_only='fever'):
        imm = ev.trigger_immunization
        days_to_event = (ev.encounter.date - imm.date).days

        output('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (
                imm.ImmRecId , 
                imm.date, ev.encounter.date, days_to_event, 
                imm.ImmName, ev.name, 
                ev.patient.getAge(), ev.patient.DemogGender
                ), f)
            
            


if __name__ == '__main__':
    print 'Getting All Events...'
    print '\n\n\n'
    print temporal_clustering()
    print '\n\n\n'
