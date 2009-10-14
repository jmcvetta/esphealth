#!/usr/bin/env python

'''
Populates the Lx.result_float and Lx.result_string columns, based 
on Lx.LxTest_results column.
'''


import re
import sys

from ESP.esp.models import Lx


def update_result():
    counter = 0
    sr = re.compile(r'^(\d+\.?\d*)')
    for str in Lx.objects.all().values_list('LxTest_results', flat=True).distinct()[0:100]:
        match = sr.match(str)
        try:
            f = match.group(1)
        except AttributeError:
            f = None
        count = Lx.objects.filter(LxTest_results=str).update(result_string=str, result_float=f)
        print '%40s %40s %20s' % (str, f, count)
        counter += count
    print '%s updated' % count

def update_refs():
    counter = 0
    sr = re.compile(r'^(\d+\.?\d*)')
    for str in Lx.objects.all().values_list('LxReference_High', flat=True).distinct()[0:100]:
        match = sr.match(str)
        try:
            f = match.group(1)
        except AttributeError:
            f = None
        count = Lx.objects.filter(LxReference_High=str).update(ref_high_string=str, ref_high_float=f)
        print '%40s %40s %20s' % (str, f, count)
        counter += count
    print '%s updated' % counter


def main():
    #update_result()
    update_refs()

if __name__ == '__main__':
    main()