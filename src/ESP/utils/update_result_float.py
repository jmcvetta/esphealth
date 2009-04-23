#!/usr/bin/env python

'''
Populates the Lx.result_float and Lx.result_string columns, based 
on Lx.LxTest_results column.
'''


import re
import sys

from ESP.esp.models import Lx


sr = re.compile(r'^(\d+\.?\d*)')



for str in Lx.objects.all().values_list('LxTest_results', flat=True).distinct()[0:100]:
    match = sr.match(str)
    try:
        f = match.group(1)
    except AttributeError:
        f = None
    print '%40s %40s' % (str, f)
    count = Lx.objects.filter(LxTest_results=str).update(result_string=str, result_float=f)
    print '%s updated' % count