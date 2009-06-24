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
import csv

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


def print_nodis_case_summary(case, options):
    '''
    @param case: Case to summarize
    @type case: Nodis Case object
    @param phi: Include PHI in summary?
    @type phi: Boolean
    '''
    print
    print 
    print '~' * 80
    case_str = 'Old Case # %s (%s)' % (case.pk, options.disease)
    print case_str
    if options.phi:
        p = case.patient
        pat_str = 'Patient # %-10s %-30s %12s' % (p.pk, p.name, p.mrn)
        print pat_str.center(80)
    print '~' * 80
    print '    EVENT TYPE                DATE           EVENT_ID      OBJECT_ID'
    print '    ' + '-' * 65
    for event in case.events.all().order_by('date'):
        values = {'name': event.heuristic_name, 'date': event.date, 'pk': event.pk, 'oid': event.object_id}
        print ' +  %(name)-25s %(date)-12s   # %(pk)-10s  # %(oid)s' % values

 
def print_tab(disease, options):
    '''
    @type disease: ESP.nodis.core.Disease
    @type options: optparse.Values instance
    '''
    columns = [
        'date',
        'last_name',
        'first_name',
        'mrn',
        ]
    event_names = disease.get_all_event_names()
    columns.extend(event_names)
    writer = csv.DictWriter(sys.stdout, columns, dialect='excel-tab')
    header = {}
    for c in columns:
        header[c] = c
    writer.writerow(header)
    for case in disease.get_cases():
        p = case.patient
        values = {'date': str(case.date), 'last_name': p.last_name, 'first_name': p.first_name, 'mrn': p.mrn}
        events = {}
        for e in case.events.all():
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
                
    


def main():
    parser = optparse.OptionParser()
    parser.add_option('-a', '--all', action='store_true', dest='all',
        help='Generate case report for ALL diseases')
    parser.add_option('--disease', action='store', dest='disease', type='string',
        metavar='NAME', help='Generate case report for disease NAME')
    parser.add_option('--phi', action='store_true', dest='phi', default=False, 
        help='Include PHI in summary')
    parser.add_option('--tab', action='store_true', dest='tab', default=False,
        help='Produce output, including PHI, in tab-delimited format')
    (options, args) = parser.parse_args()
    if options.all and options.disease:
        print >> sys.stderr, 'Cannot specify both --all and --disease.  Aborting.'
        parser.print_help()
        sys.exit()
    if options.tab and not options.disease:
        print >> sys.stderr, 'Must specify --disease when using --tab flag.  Aborting.'
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
    if options.tab:
        print_tab(disease=dis, options=options)
        sys.exit()
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
            print_nodis_case_summary(case, options=options)
        


if __name__ == '__main__':
    main()
    #print connection.queries
