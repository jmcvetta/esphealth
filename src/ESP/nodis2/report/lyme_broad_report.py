#!/usr/bin/env python
'''
                                  ESP Health
                        Broad-Scope Lyme Disesae Report
                             Case Report Generator


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory - http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL - http://www.gnu.org/licenses/lgpl-3.0.txt
'''


import sys
import csv
import pprint

from ESP.emr.models import Patient
from ESP.hef.models import HeuristicEvent
from ESP.nodis.models import Case
from ESP.nodis.core import Disease
from ESP.nodis.defs import lyme_3
from ESP.nodis import defs # Load disease definitions


# The twist on this report is that I'm looking for every patient with
# 1) any positive lyme test of any kind
# 2) lyme icd9 code 088.81
# 3) who fulfills criteria 3 of the case identification logic (i.e. rash ICD9
# and doxy and order for any of lyme ELISA / IGM EIA / or IGG EIA) within a 30
# day period


def main():
    # 
    # Generate set of Patients
    #
    lyme_disease = Disease.get_disease_by_name('lyme')
    lyme_events = ['lyme_diagnosis', 'lyme_pcr', 'lyme_elisa_pos', 'lyme_igg', 'lyme_igm']
    patients = set( Patient.objects.filter(heuristicevent__heuristic_name__in=lyme_events).distinct() )
    patients = patients | set( Patient.objects.filter(id__in=lyme_3.matches().keys()).distinct() )
    #
    # Format the Report
    #
    columns = [
        'Nodis Case',
        #'Date',
        'Last Name',
        'First Name',
        'MRN',
        ]
    event_names = lyme_disease.get_all_event_names()
    columns.extend(event_names)
    writer = csv.DictWriter(sys.stdout, columns, dialect='excel-tab')
    header = {}
    for c in columns:
        header[c] = c
    writer.writerow(header)
    #
    # Generate the Report
    #
    for p in patients:
        case_objects = Case.objects.filter(condition='lyme', patient=p)
        case_field = ', '.join([str(c.pk) for c in case_objects])
        if not case_field:
            case_field = 'N' 
        values = {
            'Nodis Case': case_field,
            #'Date': str(case.date), 
            'Last Name': p.last_name, 
            'First Name': p.first_name, 
            'MRN': p.mrn
            }
        events = {}
        #for e in case.events.all():
        for e in HeuristicEvent.objects.filter(patient=p, heuristic_name__in=event_names):
            hn = e.heuristic_name
            if hn in events:
                if not e.date in events[hn]:
                    events[hn] += [e.date]
            else:
                events[hn] = [e.date]
        for name in event_names:
            if name in events:
                values[name] = ', '.join([str(d) for d in events[name]])
            else:
                values[name] = 'N'
        writer.writerow(values)
                

if __name__ == '__main__':
    main()
