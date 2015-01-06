from django.db.models import Count

# this is a summary report one time for a paper publication for Ross.

from ESP.emr.models import Immunization
from ESP.vaers.models import AdverseEvent, EncounterEvent, LabResultEvent,PrescriptionEvent,AllergyEvent
from ESP.vaers.models import MAX_TIME_WINDOW_POST_EVENT,MAX_TIME_WINDOW_POST_LX,MAX_TIME_WINDOW_POST_RX


imm_count = Immunization.objects.values('name').distinct().annotate(count=Count('name')).filter(count__gt=0)

# may not need to exclude as this was part of fever but it doesnt harm
diagnostics_events = EncounterEvent.objects.exclude(matching_rule_explain__startswith='Patient had').filter(gap__lte=MAX_TIME_WINDOW_POST_EVENT)
lx_events = LabResultEvent.objects.filter(gap__lte=MAX_TIME_WINDOW_POST_LX)
rx_events = PrescriptionEvent.objects.filter(gap__lte=MAX_TIME_WINDOW_POST_RX)
allergy_events = AllergyEvent.objects.filter(gap__lte=MAX_TIME_WINDOW_POST_EVENT)


def report_by_imm():
    for imm in imm_count:
        #TODO get immunization from case 
        dx_code_count = diagnostics_events.filter(immunizations__name=imm['name']).count()
        lx_count = lx_events.filter(immunizations__name=imm['name']).count()
        rx_count = rx_events.filter(immunizations__name=imm['name']).count()
        allergy_count = allergy_events.filter(immunizations__name=imm['name']).count()
        total = sum([ dx_code_count, lx_count,rx_count,allergy_count])
        total_events = total
        total = imm['count']
        rate_dx_code = float(dx_code_count)/total
        rate_lx = float(lx_count)/total
        rate_rx = float(rx_count)/total
        rate_allergy = float(allergy_count)/total
        rate = float(total_events)/total
        if total_events: print '|'.join([imm['name'], 
                                         str(total), str(total_events), str(rate), 
                                         str(dx_code_count), str(rate_dx_code), 
                                         str(lx_count), str(rate_lx),
                                         str(rx_count), str(rate_rx),
                                         str(allergy_count), str(rate_allergy)])



def report_by_dx_code():
    total = 0
    for dx_code in diagnostics_events.values('matching_rule_explain').distinct().annotate(
        count=Count('matching_rule_explain')):
        print dx_code['matching_rule_explain'].split('as an')[0], '-', dx_code['count'] 
        total += dx_code['count']

    print 'total', total
        
        

if __name__ == '__main__': 
    report_by_dx_code()
