#!/usr/bin/env python
'''
                                  ESP Health
Natural Language Processing Report


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''

import re


from django.db import connection
from django.db.models import Q

from ESP.conf.models import NativeToLoincMap
from ESP.emr.models import LabResult



def main():
    search_re = re.compile(r'|'.join(SEARCH))
    exclude_re = re.compile(r'|'.join(EXCLUDE))
    mapped_codes = NativeToLoincMap.objects.values_list('native_code', flat=True)
    q_obj = ~Q(native_code__in=mapped_codes)
    q_obj = q_obj & Q(native_code__isnull=False)
    native_names = LabResult.objects.filter(q_obj).values_list('native_code', 'native_name').distinct('native_code')
    for item in native_names:
        code, name = item
        if not name:
            continue # Skip null
        uname = name.upper()
        if exclude_re.match(uname):
            continue # Excluded
        if search_re.match(uname):
            print '%-20s %s' % (code, name)


if __name__ == '__main__':
    main()
    for q in connection.queries:
        print q