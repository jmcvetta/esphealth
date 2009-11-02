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
CONDITION_MAP = {
    'chlamydia': 'chlamydia',
    'gonorrhea': 'gonorrhea',
    'acute hepatitis a': 'acute_hep_a',
    'acute hepatitis b': 'acute_hep_b',
    'acute hepatitis c': 'acute_hep_c',
    }
#CONSIDER_CONDITIONS = ['chlamydia', 'gonorrhea', 'acute_hep_a', 'acute_hep_b']
    

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
    no_mrn = set() # MRNs not present in new ESP db
    conditions_in_file = set()
    related_delta = datetime.timedelta(days=RELATED_MARGIN)
    for rec in records:
        old_condition_string = rec['condition'].lower().strip()
        if not old_condition_string in CONDITION_MAP:
            continue
        condition = CONDITION_MAP[old_condition_string]
        condition_object = Condition.get_condition(condition)
        if not condition_object:
            log.warning('Invalid condition name: "%s".  Skipping.' % condition)
            continue
        mrn = rec['mrn'].strip()
        date = date_from_str(rec['date'].strip())
        conditions_in_file.add(condition)
        log.debug('Examining known case:')
        log.debug('    Condition:  %s' % condition)
        log.debug('    MRN:        %s' % mrn)
        log.debug('    Date:       %s' % date)
        try:
            patient = Patient.objects.get(mrn=mrn)
        except Patient.DoesNotExist:
            log.warning('No patient found for MRN: %s' % mrn)
            no_mrn.add(mrn)
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
        if condition_object.recur_after == -1: # does not recur
            log.debug('Condition %s does not recur.  Any previous case will be considered similar.' % condition)
            similar_date_cases = cases.filter(date__lte=date)
        else:
            recur_delta = datetime.timedelta(days=condition_object.recur_after)
            begin_date = date - recur_delta
            end_date = date + recur_delta
            log.debug('recur delta: %s' % recur_delta)
            log.debug('begin date: %s' % begin_date)
            log.debug('end date: %s' % end_date)
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
        event_names = condition_object.relevant_event_names
        event_q  = Q(name__in=event_names)
        event_q &= Q(patient=patient)
        event_q &= Q(date__gte=begin, date__lte=end)
        events = Event.objects.filter(event_q).order_by('date')
        log.debug('Found %s relevant events' % events.count())
        lab_q = Q(patient=patient, date__gte=begin, date__lte=end)
        labs = condition_object.relevant_labs
        for test_name in condition_object.test_name_search:
            labs |= LabResult.objects.filter(native_name__icontains=test_name)
        labs = labs.filter(lab_q).order_by('date')
        log.debug('Found %s relevant labs' % labs.count())
        missing.append((rec, labs, events, cases))
        #
    all_matched_case_pks = [item[1].pk for item in exact + similar]
    new_q = ~Q(pk__in=all_matched_case_pks)
    new_q &= Q(condition__in=conditions_in_file)
    new_cases = Case.objects.filter(new_q).order_by('date')
    log.debug('Found %s new cases' % new_cases.count())
    return (exact, similar, missing, new_cases, no_mrn)

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
    log.info('Validating Nodis database against file %s' % options.file)
    filehandle = open(options.file)
    records = csv.DictReader(filehandle, FILE_FIELDS)
    exact, similar, missing, new, no_mrn = validate(records)
    count_exact = len(exact)
    count_similar = len(similar)
    count_missing = len(missing)
    count_new = new.count()
    count_no_mrn = len(no_mrn)
    total = count_exact + count_similar + count_missing + count_new + count_no_mrn
    percent_exact = float(count_exact) / total * 100.0
    percent_similar = float(count_similar) / total * 100.0
    percent_missing = float(count_missing) / total * 100.0
    percent_new = float(count_new) / total * 100.0
    percent_no_mrn = float(count_no_mrn) / total * 100.0
    missing_case_counts = {}
    for item in missing:
        con = item[0]['condition']
        if con in missing_case_counts:
            missing_case_counts[con] += 1
        else:
            missing_case_counts[con] = 1
    missing_summary = []
    for con in missing_case_counts:
        missing_summary.append((con, missing_case_counts[con]))
    missing_summary.sort()
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
        'no_mrn': no_mrn,
        'count_no_mrn': count_no_mrn,
        'percent_no_mrn': percent_no_mrn,
        'percent_new': percent_new,
        'total': total,
        'related_margin': RELATED_MARGIN,
        'missing_summary': missing_summary,
        }
    log.info('Rendering template')
    if options.text:
        print render_to_string(TEXT_OUTPUT_TEMPLATE, values)
    elif options.html:
        print render_to_string(HTML_OUTPUT_TEMPLATE, values)




if __name__ == '__main__':
    main()
