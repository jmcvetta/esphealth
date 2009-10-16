#!/usr/bin/python
'''
Created on Jul 9, 2009

@author: jason
'''

import pprint
import cProfile 
import sys

from ESP.utils.utils import log_query
from ESP.conf.models import NativeCode
from ESP.conf.models import CodeMap
from ESP.hef.core import BaseHeuristic
from ESP.hef.core import LabHeuristic
from ESP.hef.core import NumericLabHeuristic
from ESP.emr.models import LabResult
from ESP.hef import events


def main():
    lh = {}
    for h in BaseHeuristic.get_all_heuristics():
        if not isinstance(h, LabHeuristic):
            continue
        for loinc in h.loinc_nums:
            if loinc in lh:
                s = lh[loinc] 
                s.add(h)
            else:
                lh[loinc] = set([h])
    CodeMap.objects.all().delete() # Purge
    for loinc_num in lh:
        for native_code in NativeCode.objects.filter(loinc__loinc_num=loinc_num).values_list('native_code', flat=True):
            labs = LabResult.objects.filter(native_code=native_code, native_name__isnull=False)
            if labs.count():
                native_name = labs[0].native_name
            else:
                native_name = 'unknown native name'
            for h in lh[loinc_num]:
                heuristic = h.name
                c, created = CodeMap.objects.get_or_create(native_code=native_code, heuristic=heuristic)
                if isinstance(h, NumericLabHeuristic):
                    c.threshold = float(h.default_high)
                    c.save()
                c.output_code = loinc_num
                c.native_name = native_name
                c.notes = 'Generated automatically from old NativeCode table'
                c.save()
            print c
    for m in CodeMap.objects.all():
        print m
                
    
main()