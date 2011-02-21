from django.db.models import Count

from esp.emr.models import Immunization
from esp.vaers.models import AdverseEvent, EncounterEvent, LabResultEvent

imm_count = Immunization.objects.values('name').distinct().annotate(count=Count('name')).filter(count__gt=0)

fever_events = EncounterEvent.objects.filter(matching_rule_explain__startswith='Patient had').filter(gap__lte=7)
diagnostics_events = EncounterEvent.objects.exclude(matching_rule_explain__startswith='Patient had').filter(gap__lte=30)
lx_events = LabResultEvent.objects.filter(gap__lte=30)



def report_by_imm():
    for imm in imm_count:
        fever_count = fever_events.filter(immunizations__name=imm['name']).count()
        icd9_count = diagnostics_events.filter(immunizations__name=imm['name']).count()
        lx_count = lx_events.filter(immunizations__name=imm['name']).count()
        total = sum([fever_count, icd9_count, lx_count])
        total_events = total
        total = imm['count']
        rate_fever = float(fever_count)/total
        rate_icd9 = float(icd9_count)/total
        rate_lx = float(lx_count)/total
        rate = float(total_events)/total
        if total_events: print '|'.join([imm['name'], 
                                         str(total), str(total_events), str(rate), 
                                         str(fever_count), str(rate_fever), 
                                         str(icd9_count), str(rate_icd9), 
                                         str(lx_count), str(rate_lx)])



def report_by_icd9():
    total = 0
    for icd9 in diagnostics_events.values('matching_rule_explain').distinct().annotate(
        count=Count('matching_rule_explain')):
        print icd9['matching_rule_explain'].split('as an')[0], '-', icd9['count'] 
        total += icd9['count']

    print 'total', total
        
        

if __name__ == '__main__': 
    report_by_icd9()
