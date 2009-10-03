'''
                                  ESP Health
                         Notifiable Diseases Framework
Case Validator


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL - http://www.gnu.org/licenses/lgpl-3.0.txt
'''


RELATED_MARGIN = 365 # Retrieve labs +/- this many days from date of missing case
FILE_PATH = 'old_cases.csv'
FILE_FIELDS = [
    'condition',
    'date',
    'mrn',
    'last',
    'first',
    ]
TEXT_OUTPUT_TEMPLATE = 'nodis/validator.txt'
HTML_OUTPUT_TEMPLATE = 'nodis/validator.html'
CONSIDER_CONDITIONS = ['chlamydia', 'gonorrhea']
    

import optparse
import csv
import datetime
import pprint
import sys

from django.db.models import Q
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.template.loader import get_template

from ESP.utils.utils import log
from ESP.utils.utils import log_query
from ESP.utils.utils import date_from_str
from ESP.emr.models import Patient
from ESP.emr.models import LabResult
from ESP.hef.models import Event
from ESP.nodis import defs # Condition defintions
from ESP.nodis.models import Case
from ESP.nodis.core import Condition


def validate(records):
    '''
    Validates cases described in iterable records
    '''
    exact = []
    similar = []
    missing = []
    new = []
    conditions_in_file = set()
    related_delta = datetime.timedelta(days=RELATED_MARGIN)
    for rec in records:
        condition = rec['condition'].lower().strip()
        condition_object = Condition.get_condition(condition)
        if not condition_object:
            log.warning('Invalid condition name: "%s".  Skipping.' % condition)
            continue
        date_delta = datetime.timedelta(days=condition_object.recur_after)
        mrn = rec['mrn'].strip()
        date = date_from_str(rec['date'].strip())
        if condition not in CONSIDER_CONDITIONS:
            continue
        conditions_in_file.add(condition)
        log.debug('Examining known case:')
        log.debug('    Condition:  %s' % condition)
        log.debug('    MRN:        %s' % mrn)
        log.debug('    Date:       %s' % date)
        try:
            patient = Patient.objects.get(mrn=mrn)
        except Patient.DoesNotExist:
            log.warning('No patient found for MRN: %s' % mrn)
            continue
        cases = Case.objects.filter(patient=patient, condition__iexact=condition)
        previous_day = date - datetime.timedelta(days=1)
        exact_date_cases = cases.filter(date__gte=previous_day, date__lte=date)
        if exact_date_cases:
            log.debug('Exact case match found.')
            if len(exact_date_cases) > 1: 
                log.warning('More than one exact case match!')
            exact.append((rec, exact_date_cases[0]))
            continue
        begin_date = date - date_delta
        end_date = date + date_delta
        similar_date_cases = cases.filter(date__gte=begin_date, date__lte=end_date)
        if similar_date_cases:
            log.debug('Found case with similar date: %s' % similar_date_cases[0].date)
            if len(exact_date_cases) > 1: 
                log.warning('More than one similar case match!')
            similar.append((rec, similar_date_cases[0]))
            continue
        log.debug('No case match found')
        #
        # Related Events for Missing Case
        #
        # At this point, case is missing.  Let's look for relevant events for 
        # this patient; and if none of those are found, we'll look for
        # relevant lab results.
        begin = date - related_delta
        end = date + related_delta
        case_q = Q(patient=patient, condition=condition)
        cases = Case.objects.filter(case_q).order_by('date')
        log.debug('Found %s relevant cases' % cases.count())
        heuristics = Condition.get_condition(condition).relevant_heuristics
        event_q  = Q(heuristic__in=heuristics)
        event_q &= Q(patient=patient)
        event_q &= Q(date__gte=begin, date__lte=end)
        events = Event.objects.filter(event_q).order_by('date')
        log.debug('Found %s relevant events' % events.count())
        loincs = Condition.get_condition(condition).relevant_loincs
        lab_q = Q(patient=patient, date__gte=begin, date__lte=end)
        labs = LabResult.objects.filter_loincs(loincs).filter(lab_q).order_by('date')
        log.debug('Found %s relevant labs' % labs.count())
        missing.append((rec, labs, events, cases))
        #
    all_matched_case_pks = [item[1].pk for item in exact + similar]
    new_q = ~Q(pk__in=all_matched_case_pks)
    new_q &= Q(condition__in=conditions_in_file)
    new_cases = Case.objects.filter(new_q).order_by('date')
    log.debug('Found %s new cases' % new_cases.count())
    return (exact, similar, missing, new_cases)

def main():
    parser = optparse.OptionParser()
    parser.add_option('--text', action='store_true', dest='text', default=False, 
        help='Produce ASCII text output')
    parser.add_option('--html', action='store_true', dest='html', default=False, 
        help='Produce HTML output')
    parser.add_option('-f', action='store', dest='file', metavar='FILE', 
        help='Validate against FILE')
    options, args = parser.parse_args()
    if (options.text and options.html) or not (options.text or options.html):
        sys.stderr.write('You must select either --text OR --html \n\n')
        parser.print_help()
        sys.exit()
    if not options.file:
        sys.stderr.write('You must specify a file to validate against.')
        parser.print_help()
        sys.exit()
    filehandle = open(options.file)
    records = csv.DictReader(filehandle, FILE_FIELDS)
    exact, similar, missing, new = validate(records)
    count_exact = len(exact)
    count_similar = len(similar)
    count_missing = len(missing)
    count_new = new.count()
    total = count_exact + count_similar + count_missing + count_new
    percent_exact = float(count_exact) / total * 100.0
    percent_similar = float(count_similar) / total * 100.0
    percent_missing = float(count_missing) / total * 100.0
    percent_new = float(count_new) / total * 100.0
    values = {
        'exact': exact,
        'similar': similar,
        'missing': missing,
        'new': new,
        'count_exact': count_exact,
        'count_similar': count_similar,
        'count_missing': count_missing,
        'count_new': count_new,
        'percent_exact': percent_exact,
        'percent_similar': percent_similar,
        'percent_missing': percent_missing,
        'percent_new': percent_new,
        'total': total,
        'related_margin': RELATED_MARGIN,
        }
    log.info('Rendering template')
    if options.text:
        print render_to_string(TEXT_OUTPUT_TEMPLATE, values)
    elif options.html:
        print render_to_string(HTML_OUTPUT_TEMPLATE, values)




if __name__ == '__main__':
    main()