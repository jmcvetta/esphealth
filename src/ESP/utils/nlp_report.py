#!/usr/bin/env python
'''
                                  ESP Health
Natural Language Processing Report


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''


from django.db import connection
from django.db.models import Q

from ESP.conf.models import NativeToLoincMap
#from ESP.esp.models import Lx
from ESP.core.models import LabResult


SEARCH = ['CHLAM','TRACH', 'GC','GON','HEP','HBV','ALT','SGPT','AST','SGOT','AMINOTRANS','BILI', 'HAV','HCV','RIBA']
EXCLUDE = ['CAST', 'FASTING','YEAST','URINE','URO']

def main():
    mapped_codes = NativeToLoincMap.objects.values_list('native_code', flat=True)
    unmapped_q = ~Q(native_code__in=mapped_codes)
    native_names = LabResult.objects.filter(unmapped_q).values_list('native_name', flat=True).distinct()
    for name in native_names:
        if not name:
            continue # Skip null
        uname = name.upper()
        if (uname in SEARCH) and not (uname in EXCLUDE):
            print name


if __name__ == '__main__':
    main()
    for q in connection.queries:
        print q