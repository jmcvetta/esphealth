'''
                                  ESP Health
                         Notifiable Diseases Framework
Case Validator


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL - http://www.gnu.org/licenses/lgpl-3.0.txt
'''


DATE_MARGIN = 5 # Cases can be +/- this many days offset
LAB_MARGIN = 30 # Retrieve labs +/- this many days from date of missing case
FILE_PATH = 'old_cases.csv'
FILE_FIELDS = [
    'condition',
    'date',
    'mrn',
    'last',
    'first',
    ]
TEXT_OUTPUT_TEMPLATE = 'nodis/validator.txt'
CONSIDER_CONDITIONS = ['chlamydia', 'gonorrhea']
    

import optparse
import csv
import datetime
import pprint

from django.db.models import Q
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.template.loader import get_template

from ESP.utils.utils import log
from ESP.utils.utils import log_query
from ESP.utils.utils import date_from_str
from ESP.emr.models import Patient
from ESP.emr.models import LabResult
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
    date_delta = datetime.timedelta(days=DATE_MARGIN)
    lab_delta = datetime.timedelta(days=LAB_MARGIN)
    for rec in records:
        condition = rec['condition'].lower().strip()
        mrn = rec['mrn'].strip()
        date = date_from_str(rec['date'].strip())
        if condition not in CONSIDER_CONDITIONS:
            continue
        conditions_in_file.add(condition)
        log.debug('Examining known case:')
        log.debug('    Condition:  %s' % condition)
        log.debug('    MRN:        %s' % mrn)
        log.debug('    Date:       %s' % date)
        cases = Case.objects.filter(patient__mrn=mrn, condition__iexact=condition)
        exact_date_cases = cases.filter(date=date)
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
        # If we have reached this point, case is missing.  Lets find labs for 
        # that patient.
        loincs = Condition.get_condition(condition).relevant_loincs
        lab_begin = date - lab_delta
        lab_end = date + lab_delta
        lab_q = Q(patient__mrn=mrn, date__gte=lab_begin, date__lte=lab_end)
        labs = LabResult.objects.filter_loincs(loincs).filter(lab_q)
        log.debug('Found %s relevant labs' % labs.count())
        missing.append((rec, labs))
    all_matched_case_pks = [item[1].pk for item in exact + similar]
    new_q = ~Q(pk__in=all_matched_case_pks)
    new_q &= Q(condition__in=conditions_in_file)
    new_cases = Case.objects.filter(new_q)
    log.debug('Found %s new cases' % new_cases.count())
    return (exact, similar, missing, new_cases)

def main():
    filehandle = open(FILE_PATH)
    records = csv.DictReader(filehandle, FILE_FIELDS)
    exact, similar, missing, new = validate(records)
    values = {
        'exact': exact,
        'similar': similar,
        'missing': missing,
        'new': new,
        }
    print render_to_string(TEXT_OUTPUT_TEMPLATE, values)




if __name__ == '__main__':
    main()