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


import sys
import datetime
import optparse

from django.db import connection
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType

from ESP.esp.models import Case as OldCase
from ESP.nodis.models import Case as NewCase
from ESP.emr.models import Encounter
from ESP.emr.models import LabResult
from ESP.hef.models import HeuristicEvent



BEGIN_COMPARE_DATE = datetime.date(2009, 1, 1)




# This is needed because Rule is not table set up in dev db
RULE_MAP = {
    'chlamydia': 1,
    'gonorrhea': 2,
    'acute_hep_b': 4,
    'acute_hep_a': 5,
    'acute_hep_c': 6,
    'chronic_hep_b': 7,
}


def print_nodis_case_summary(case, phi=False):
    '''
    @param case: Case to summarize
    @type case: Nodis Case object
    @param phi: Include PHI in summary?
    @type phi: Boolean
    '''
    print 
    print '~' * 80
    case_str = 'Nodis Case # %s: %s (v%s)' % (case.pk, case.definition, case.def_version)
    print case_str.center(80) 
    print '~' * 80
    if phi:
        print 'Patient # %s' % case.patient.pk
        print '\t Name: %s' % case.patient.name
        print '\t MRN: %s' % case.patient.mrn
    for event in case.events.all():
        print '%s' % event
        if type(event.content_object) == Encounter:
            enc = event.content_object
            print '\t %s -- %s' % (enc, enc.date)
            print '\t ICD9s: %s' % enc.icd9_codes.all()
        elif type(event.content_object) == LabResult:
            lab = event.content_object
            print '\t %s -- %s' % (lab, lab.date)
            print '\t %-25s LOINC: %-10s Native Code: %s' % (lab.native_name, lab.loinc_num(), lab.native_code)
            print '\t Result: %-30s \t Reference High: %s' % (lab.result_string, lab.ref_high)
        else:
            print '\t %s' % event.content_object

def display_old_case_long(case, condition, print_phi):
    # These are needed for heuristic event lookups below
    enc_type = ContentType.objects.get_for_model(Encounter)
    lab_type = ContentType.objects.get_for_model(LabResult)
    print
    print '~' * 80
    case_str = 'Old Case #%s (%s)' % (case.pk, condition)
    print case_str.center(80) 
    print '~' * 80
    if print_phi:
        print 'Patient #%s' % case.patient.pk
        print '\t Name: %s' % case.patient.name
        print '\t MRN: %s' % case.patient.mrn
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
        print '%s -- %s' % (enc, enc.date)
        print '    ICD9s:'
        for i in enc.icd9_codes.all():
            print '        %s' % i
        print '    Matching Heuristic Event(s):'
        hefs = HeuristicEvent.objects.filter(content_type=enc_type, object_id=enc.id)
        if not hefs:
            print '        NO MATCHING EVENTS'
        else:
            for e in hefs:
                print '        %s' % e
    for lab in LabResult.objects.filter(pk__in=lxids):
        print '%s -- %s' % (lab, lab.date)
        print '    %-25s LOINC: %-10s Native Code: %s' % (lab.native_name, lab.loinc_num(), lab.native_code)
        print '    Result: %-30s \t Reference High: %s' % (lab.result_string, lab.ref_high)
        hefs = HeuristicEvent.objects.filter(content_type=lab_type, object_id=lab.id)
        if not hefs:
            print '        NO MATCHING EVENTS'
        else:
            for e in hefs:
                print '        %s' % e

def display_old_case_short(case, condition, print_phi):
    # These are needed for heuristic event lookups below
    enc_type = ContentType.objects.get_for_model(Encounter)
    lab_type = ContentType.objects.get_for_model(LabResult)
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
    print
    print 
    print '~' * 80
    case_str = 'Old Case # %s (%s)' % (case.pk, condition)
    print case_str
    if print_phi:
        p = case.patient
        pat_str = 'Patient # %-10s %-30s %12s' % (p.pk, p.name, p.mrn)
        print pat_str.center(80)
    print '~' * 80
    for enc in Encounter.objects.filter(pk__in=encids):
        hefs = HeuristicEvent.objects.filter(content_type=enc_type, object_id=enc.id).order_by('date')
        if not hefs:
            print '  NO EVENT: %s -- %s' % (enc, enc.date)
            for i in enc.icd9_codes.all():
                print '    %s' % i
        else:
            for e in hefs:
                values = {'event': e.heuristic_name, 'date': e.date, 'pk': e.pk}
                print '  %(event)-25s %(date)-12s   # %(pk)s' % values
    for lab in LabResult.objects.filter(pk__in=lxids):
        hefs = HeuristicEvent.objects.filter(content_type=lab_type, object_id=lab.id).order_by('date')
        if not hefs:
            print '  NO EVENT: %s -- %s' % (lab, lab.date)
            print '    %-25s LOINC: %-10s Native Code: %s' % (lab.native_name, lab.loinc_num(), lab.native_code)
            print '    Result: %-30s \t Reference High: %s' % (lab.result_string, lab.ref_high)
        else:
            for e in hefs:
                values = {'event': e.heuristic_name, 'date': e.date, 'pk': e.pk}
                print '  %(event)-25s %(date)-12s   # %(pk)s' % values
        
    
                

def compare(condition, options):
    rule = RULE_MAP[condition]
    #
    # Find cases found by identifyCases.py but not by Nodis
    #
    pids = NewCase.objects.filter(condition=condition).values_list('patient_id', flat=True)
    q_obj = ~Q(caseDemog__in=pids)
    i_cases = OldCase.objects.filter(caseRule=rule).filter(q_obj)
    count = i_cases.count()
    print
    print
    print '=' * 80
    print condition.upper() + ' -- %s cases found by identifyCases.py but not by Nodis' % count
    print '=' * 80
    for case in i_cases.order_by('pk'):
        if options.missed:
            display_old_case_short(case, condition, options.phi)
        else:
            display_old_case_long(case, condition, options.phi)
    if options.missed:
        return
    #
    # Find cases found by Nodis but not by identifyCases.py
    #
    pids = OldCase.objects.filter(caseRule=rule).values_list('caseDemog_id', flat=True)
    q_obj = ~Q(patient__in=pids)
    n_cases = NewCase.objects.filter(condition=condition).filter(q_obj)
    count = n_cases.count()
    print
    print
    print '=' * 80
    print condition.upper() + ' -- %s cases found by Nodis but not by identifyCases.py' % count
    print '=' * 80
    for case in n_cases.order_by('pk'):
        print_nodis_case_summary(case, phi=options.phi)
    

def main():
    parser = optparse.OptionParser()
    parser.add_option('--phi', action='store_true', dest='phi', default=False, 
        help='Include PHI in summary')
    parser.add_option('--missed', action='store_true', dest='missed', default=False,
        help='Summarize cases missed by Nodis')
    (options, args) = parser.parse_args()
    print '+' * 80
    print '+' + ' ' * 78 + '+'
    print '+' + 'Nodis Case Comparison Report'.center(78) + '+'
    gen_str = 'Generated %s' % datetime.datetime.today().strftime('%d %b %Y %H:%M')
    print '+' + gen_str.center(78)+ '+'
    print '+' + ' ' * 78 + '+'
    print '+' * 80
    if options.phi:
        phi_str = 'NOTICE: This report includes protected health information.'
        print
        print 
        print '!' * 80
        print '!' + ' ' * 78 + '!'
        print '!' + phi_str.center(78) + '!'
        print '!' + ' ' * 78 + '!'
        print '!' * 80
    for condition in NewCase.objects.filter(condition__in=RULE_MAP).values_list('condition', flat=True).distinct():
        compare(condition, options=options)


if __name__ == '__main__':
    main()
    #compare('Acute Hepatitis A')
    #compare('Acute Hepatitis B')
    #compare('Acute Hepatitis C')
    #print connection.queries
