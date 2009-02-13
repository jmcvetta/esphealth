#!/usr/bin/env python
'''
Generate a concordance lab result strings per LOINC or CPT
'''


import pprint

from django.db.models import Q

from ESP.esp import models
from ESP import settings
from ESP.utils.utils import log


def string_lab_results(filter_q=None):
    '''
    Iterator yielding distinct lab result strings.  Considers all lab texts 
    by default; set of tests to consider can be filtered by feeding a Q object
    as filter_q argument.
    @type filter_q: django.db.models.Q
    '''
    log.debug('filter_q: %s' % filter_q)
    if filter_q:
        result_query = models.Lx.objects.filter(filter_q).values_list('LxTest_results').distinct()
    else:
        result_query = models.Lx.objects.values_list('LxTest_results').distinct()
    log.debug('result_query: %s' % result_query)
    for result in result_query:
        result = result[0]
        try:
            int(result)
            continue
        except:
            pass
        try:
            float(result)
            continue
        except:
            pass
        yield str(result) # Use str() so our strings don't print out like u'this'.


def main():
    loinc_concordance = {}
    ext_concordance = {}
    for item in models.CPTLOINCMap.objects.values_list('Loinc', 'CPT').distinct():
        loinc = item[0]
        ext = item[1]
        q_obj = Q(LxLoinc=loinc)
        ext_concordance[str(ext)] = str([i for i in string_lab_results(q_obj)])
        loinc_concordance[str(loinc)] = str([i for i in string_lab_results(q_obj)])
    print 'LOINC Concordance:'
    pprint.pprint(loinc_concordance)
    print '-------------------------------------------------------------------------------'
    print 'External Code Concordance:'
    pprint.pprint(ext_concordance)


if __name__ == '__main__':
    main()
