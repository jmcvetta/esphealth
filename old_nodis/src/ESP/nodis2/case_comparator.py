#!/usr/bin/env python
'''
                                  ESP Health
                         Notifiable Diseases Framework
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

from ESP.utils.utils import log
from ESP.esp.models import Case as OldCase
from ESP.nodis.models import Case as NewCase
from ESP.nodis.core import Disease
from ESP.emr.models import Encounter
from ESP.emr.models import LabResult
from ESP.hef.models import HeuristicEvent
from ESP.nodis import defs # Load disease definitions



BEGIN_COMPARE_DATE = datetime.date(2009, 1, 1)




# This is needed because Rule is not table set up in dev db
RULE_MAP = {
    'chlamydia': 1,
    'gonorrhea': 2,
    'acute_hep_b': 4,
    'acute_hep_a': 5,
    'acute_hep_c': 6,
    'exp_acute_hep_c': 6,
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
    disease = Disease.get_disease_by_name(condition)
    enc_type = ContentType.objects.get_for_model(Encounter)
    lab_type = ContentType.objects.get_for_model(LabResult)
    if case.caseEncID:
        encids = [int(id) for id in case.caseEncID.split(',')]
    else:
        encids = []
    case_encs = Encounter.objects.filter(pk__in=encids).order_by('date')
    if case.caseLxID:
        lxids = [int(id) for id in case.caseLxID.split(',')]
    else:
        lxids = []
    case_labs = LabResult.objects.filter(pk__in=lxids).order_by('date')
    if case.caseICD9:
        icd9s = case.caseICD9.split(',')
    else:
        icd9s = []
    # Case date is lowest date among labs & encounters
    case_date = sorted(list(case_labs) + list(case_encs) , key=lambda x: x.date)[0].date
    # Get relevant events
    begin = case_date - datetime.timedelta(400)
    end = case_date + datetime.timedelta(30)
    q_obj = Q(date__gte=begin, date__lte=end, patient=case.patient)
    q_obj = q_obj & Q(heuristic_name__in=disease.get_all_event_names())
    relevant_events = HeuristicEvent.objects.filter(q_obj).order_by('date')
    print
    print 
    print '~' * 80
    case_str = 'Old Case # %s  --  %s  --  Patient # %s)' % (case.pk, condition, case.patient.pk)
    print case_str
    if print_phi:
        p = case.patient
        pat_str = 'Patient # %-10s %-30s %12s' % (p.pk, p.name, p.mrn)
        print pat_str.center(80)
    print '~' * 80
    print '    EVENT TYPE                DATE           EVENT_ID      OBJECT_ID'
    print '    ' + '-' * 65
    enc_event_pks = []
    lab_event_pks = []
    for event in relevant_events:
        attached = False # Event is attached to this case
        if event.content_type == enc_type:
            enc_event_pks.append(event.object_id)
            if event.object_id in encids:
                attached = True
        elif event.content_type == lab_type:
            lab_event_pks.append(event.object_id)
            if event.object_id in lxids:
                attached = True
        values = {'name': event.heuristic_name, 'date': event.date, 'pk': event.pk, 'oid': event.object_id}
        if attached:
            print ' +  %(name)-25s %(date)-12s   # %(pk)-10s  # %(oid)s' % values
        else:
            print '    %(name)-25s %(date)-12s   # %(pk)-10s  # %(oid)s' % values
    attached_he_pks = [] # List of primary keys for heuristic events attached to this case
    unattached_encids = set(encids) - set(enc_event_pks)
    unattached_lxids = set(lxids) - set(lab_event_pks)
    for enc in Encounter.objects.filter(pk__in=unattached_encids):
        print '    NO EVENT: Encounter       %10s                   # %-12s' % (enc.date, enc.pk)
        for i in enc.icd9_codes.all():
            print '      %s' % i
    for lab in LabResult.objects.filter(pk__in=unattached_lxids):
        print '    NO EVENT: Lab Result      %10s                   # %-12s' % (lab.date, lab.pk)
        print '      %-25s LOINC: %-10s Native Code: %s' % (lab.native_name, lab.loinc_num(), lab.native_code)
        print '      Result: %-30s \t Reference High: %s' % (lab.result_string, lab.ref_high)
    
    
        
    
                

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
    print '+' + 'Nodis Case Validation Report'.center(78) + '+'
    if options.missed:
        miss_str = 'Missing Cases Summary'
        print '+' + miss_str.center(78)+ '+'
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
    #compare('exp_acute_hep_c', options=options)
    for condition in RULE_MAP:
        compare(condition, options=options)


if __name__ == '__main__':
    main()
    #compare('Acute Hepatitis A')
    #compare('Acute Hepatitis B')
    #compare('Acute Hepatitis C')
    #print connection.queries
