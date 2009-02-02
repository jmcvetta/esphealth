#!/usr/bin/env python
'''
Generate a concordance lab result strings per LOINC
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
    if filter_q:
        result_query = models.Lx.objects.filter(filter_q).values_list('LxTest_results').distinct()
    else:
        result_query = models.Lx.objects.values_list('LxTest_results').distinct()
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
        yield result


def main():
    concordance = {}
    for loinc in models.CPTLOINCMap.objects.values_list('Loinc').distinct():
        loinc = loinc[0]
        q_obj = Q(LxLoinc=loinc)
        concordance[loinc] = [i for i in string_lab_results(q_obj)]
    pprint.pprint(concordance)


if __name__ == '__main__':
    main()
