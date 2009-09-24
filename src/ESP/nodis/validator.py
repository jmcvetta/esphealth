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
FILE_PATH = 'old_cases.csv'
FILE_FIELDS = [
    'condition',
    'date',
    'mrn',
    'last',
    'first',
    ]
    

import optparse
import csv
import datetime

from django.db.models import Q

from ESP.utils.utils import log
from ESP.utils.utils import log_query
from ESP.utils.utils import date_from_str
from ESP.emr.models import Patient
from ESP.nodis.models import Case


def main():
    exact = []
    similar = []
    missing = []
    new = []
    delta = datetime.timedelta(days=DATE_MARGIN)
    filehandle = open(FILE_PATH)
    records = csv.DictReader(filehandle, FILE_FIELDS)
    for rec in records:
        cases = Case.objects.filter(patient__mrn=rec['mrn'], condition__iexact=rec['condition'])
        date = date_from_str(rec['date'])
        exact_date_cases = cases.filter(date=date)
        if exact_date_cases:
            log.debug('Exact date match found for %s' % rec)
            if len(exact_date_cases) > 1: 
                log.warning('More than one exact case match for %s' % rec)
            exact.append(exact_date_cases[0])
            continue
        begin_date = date - delta
        end_date = date + delta
        similar_date_cases = cases.filter(date__gte=begin_date, date__lte=end_date)
        if similar_date_cases:
            log.debug('Similar date match found for %s' % rec)
            if len(exact_date_cases) > 1: 
                log.warning('More than one similar case match for %s' % rec)
            similar.append(similar_date_cases[0])
            continue
        log.debug('No %s case for patient %s; adding to missing list' % (rec['condition'], rec['mrn']))
        missing.append(rec)
    all_matched_case_pks = [case.pk for case in exact + similar]
    new_q = ~Q(pk__in=all_matched_case_pks)
    new_cases = Case.objects.filter(new_q)
    log.debug('New cases: %s' % new_cases)
        
                
        
        
        
        




if __name__ == '__main__':
    main()