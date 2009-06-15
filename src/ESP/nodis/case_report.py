#!/usr/bin/env python
'''
                                  ESP Health
                          Heuristic Events Framework
                             Case Report Generator


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

from ESP.nodis.models import Case
from ESP.emr.models import Encounter
from ESP.emr.models import LabResult
from ESP.hef.models import HeuristicEvent
from ESP.nodis.core import Disease
from ESP.nodis import defs # Load disease definitions



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
        print '    Name: %s' % case.patient.name
        print '    MRN: %s' % case.patient.mrn
    for event in case.events.all():
        print '%s -- %s' % (event, event.definition)
        if type(event.content_object) == Encounter:
            enc = event.content_object
            print '    %s -- %s' % (enc, enc.date)
            print '    ICD9s: %s' % enc.icd9_codes.all()
        elif type(event.content_object) == LabResult:
            lab = event.content_object
            print '    %s -- %s' % (lab, lab.date)
            print '    %-25s LOINC: %-10s Native Code: %s' % (lab.native_name, lab.loinc_num(), lab.native_code)
            print '    Result: %-30s \t Reference High: %s' % (lab.result_string, lab.ref_high)
        else:
            print '    %s' % event.content_object


def main():
    parser = optparse.OptionParser()
    parser.add_option('-a', '--all', action='store_true', dest='all',
        help='Generate case report for ALL diseases')
    parser.add_option('--disease', action='store', dest='disease', type='string',
        metavar='NAME', help='Generate case report for disease NAME')
    parser.add_option('--phi', action='store_true', dest='phi', default=False, 
        help='Include PHI in summary')
    (options, args) = parser.parse_args()
    if options.all and options.disease:
        print >> sys.stderr, 'Cannot specify both --all and --disease.  Aborting.'
        parser.print_help()
        sys.exit()
    if not (options.all or options.disease):
        print >> sys.stderr, 'Must specify either --all and --disease.  Aborting.'
        parser.print_help()
        sys.exit()
    if options.disease:
        dis = Disease.get_disease_by_name(options.disease)
        if not dis:
            msg = '\nNo disease registered with name "%s".\n' % options.disease
            sys.stderr.write(msg)
            sys.exit()
        diseases = [dis]
    else:
        diseases = Disease.get_all_diseases()
    print '+' * 80
    print '+' + ' ' * 78 + '+'
    print '+' + 'Nodis Case Report'.center(78) + '+'
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
    for dis in diseases:
        cases = Case.objects.filter(condition=dis.name)
        print
        print
        print '=' * 80
        print dis.name.upper() + ' -- %s cases found by Nodis' % cases.count()
        print '=' * 80
        for case in cases.order_by('pk'):
            print_nodis_case_summary(case, phi=options.phi)
        


if __name__ == '__main__':
    main()
    #print connection.queries
