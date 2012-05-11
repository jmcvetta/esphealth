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
        icd9_count = diagnostics_events.filter(immunizations__name=imm['name']).count()
        lx_count = lx_events.filter(immunizations__name=imm['name']).count()
        rx_count = rx_events.filter(immunizations__name=imm['name']).count()
        allergy_count = allergy_events.filter(immunizations__name=imm['name']).count()
        total = sum([ icd9_count, lx_count,rx_count,allergy_count])
        total_events = total
        total = imm['count']
        rate_icd9 = float(icd9_count)/total
        rate_lx = float(lx_count)/total
        rate_rx = float(rx_count)/total
        rate_allergy = float(allergy_count)/total
        rate = float(total_events)/total
        if total_events: print '|'.join([imm['name'], 
                                         str(total), str(total_events), str(rate), 
                                         str(icd9_count), str(rate_icd9), 
                                         str(lx_count), str(rate_lx),
                                         str(rx_count), str(rate_rx),
                                         str(allergy_count), str(rate_allergy)])



def report_by_icd9():
    total = 0
    for icd9 in diagnostics_events.values('matching_rule_explain').distinct().annotate(
        count=Count('matching_rule_explain')):
        print icd9['matching_rule_explain'].split('as an')[0], '-', icd9['count'] 
        total += icd9['count']

    print 'total', total
        
        

if __name__ == '__main__': 
    report_by_icd9()
