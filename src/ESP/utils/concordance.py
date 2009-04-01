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
    concordance = {}
    #for item in models.CPTLOINCMap.objects.values_list('Loinc', 'CPT').distinct():
    for m in models.ExtToLoincMap.objects.all():
        loinc_qs = models.Lx.objects.filter(LxLoinc=m.loinc.loinc_num)
        results_tuple = []
        for result in loinc_qs.values_list('LxTest_results').distinct():
            result = result[0]
            try:
                float(result)
                continue
            except:
                pass
            count = len(loinc_qs.filter(LxTest_results=result))
            results_tuple += [(count, result),]
        concordance[(m.loinc.loinc_num, m.loinc.name)] = results_tuple
    print '==============================================================================='
    print 'LOINC Concordance'
    print '==============================================================================='
    for item in concordance:
        if not concordance[item]:
            continue
        print '%s -- %s' % item
        for result in concordance[item]:
            print '    %4d    %s' % result
        print '-------------------------------------------------------------------------------'


if __name__ == '__main__':
    main()
