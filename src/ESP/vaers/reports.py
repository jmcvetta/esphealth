#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db.models import Q
import datetime

from ESP.vaers.models import AdverseEvent, FeverEvent


def cases_to_report():
    now = datetime.datetime.now()
    three_days_ago = now - datetime.timedelta(days=7)

    auto = Q(category='auto')
    confirmed = Q(category='confirm', state='Q')
    to_report_by_default = Q(category='default', state='AR', created_on__lte=three_days_ago)

    return AdverseEvent.objects.filter(auto | confirmed | to_report_by_default)

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
                    ev.patient._get_age(formatted=True), 
                    ev.patient.DemogGender
                    ]))
        f.write('\n')

    f.close()

    
    
    
