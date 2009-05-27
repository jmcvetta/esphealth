#!/usr/bin/env python
'''
                                  ESP Health
                          Heuristic Events Framework
                             Case Comparator Tool


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''


import datetime

from django.db import connection
from django.db.models import Q

from ESP.esp.models import Case as OldCase
from ESP.nodis.models import Case as NewCase
from ESP.emr.models import Encounter
from ESP.emr.models import LabResult



BEGIN_COMPARE_DATE = datetime.date(2009, 1, 1)




# This is needed because Rule is not table set up in dev db
RULE_MAP = {
    'Chlamydia': 1,
    'Gonorrhea': 2,
    'Acute Hepatitis B': 4,
    'Acute Hepatitis A': 5,
    'Acute Hepatitis C': 6,
    'Chronic Hepatitis B': 7,
}


def compare(condition):
    rule = RULE_MAP[condition]
    #
    # Find cases found by identifyCases.py but not by Nodis
    #
    print '=' * 80
    print condition.upper() + ' -- Cases found by identifyCases.py but not by Nodis'
    print '=' * 80
    print 
    print
    pids = NewCase.objects.filter(condition=condition).values_list('patient_id', flat=True)
    q_obj = ~Q(caseDemog__in=pids)
    for case in OldCase.objects.filter(caseRule=rule).filter(q_obj).order_by('pk'):
        print '~' * 80
        print 'Case #%s' % case.pk
        if case.caseEncID:
            encids = case.caseEncID.split(',')
        else:
            encids = []
        if case.caseLxID:
            lxids = case.caseLxID.split(',')
        else:
            lxids = []
        if case.caseICD9:
            icd9s = case.caseICD9.split(',')
        else:
            icd9s = []
        for enc in Encounter.objects.filter(pk__in=encids):
            print '\t %s -- %s' % (enc, enc.date)
            print '\t\t ICD9s: %s' % enc.icd9_codes.all()
        for lab in LabResult.objects.filter(pk__in=lxids):
            print '\t %s -- %s' % (lab, lab.date)
            print '\t\t %s (%s)' % (lab.native_name, lab.native_code)
            print '\t\t %s' % lab.result_string
    #
    # Find cases found by identifyCases.py but not by Nodis
    #
    print '=' * 80
    print condition.upper() + ' -- Cases found by Nodis but not by identifyCases.py'
    print '=' * 80
    print 
    print
    pids = OldCase.objects.filter(caseRule=rule).values_list('caseDemog_id', flat=True)
    q_obj = ~Q(patient__in=pids)
    for case in NewCase.objects.filter(condition=condition).filter(q_obj).order_by('pk'):
        print '~' * 80
        print 'Case #%s' % case.pk
        for event in case.events.all():
            print '\t %s' % event
            if type(event.content_object) == Encounter:
                enc = event.content_object
                print '\t\t %s -- %s' % (enc, enc.date)
                print '\t\t ICD9s: %s' % enc.icd9_codes.all()
            elif type(event.content_object) == LabResult:
                lab = event.content_object
                print '\t\t %s -- %s' % (lab, lab.date)
                print '\t\t %s (%s)' % (lab.native_name, lab.native_code)
                print '\t\t %s' % lab.result_string
            else:
                print '\t %s' % event.content_object
            
#        for enc in case.encounters.all():
#            print '\t %s -- %s' % (enc, enc.date)
#            print '\t\t ICD9s: %s' % enc.icd9_codes.all()
#        for lab in case.lab_results.all():
#            print '\t %s -- %s' % (lab, lab.date)
#            print '\t\t %s (%s)' % (lab.native_name, lab.native_code)
#            print '\t\t %s' % lab.result_string
    


def main():
    for condition in NewCase.objects.values_list('condition', flat=True).distinct():
        compare(condition)


if __name__ == '__main__':
    #main()
    compare('Acute Hepatitis A')
    #print connection.queries
