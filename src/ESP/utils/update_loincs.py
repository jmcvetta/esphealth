#!/usr/bin/env python
'''
                                  ESP Health
                      Update LOINC Codes for Lab Results

@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''

import sys
import pprint

from django.db import connection

from ESP.utils.utils import log
from ESP.conf.models import ExtToLoincMap
from ESP.esp.models import Lx


def main():
    counter = 0
    for mapping in ExtToLoincMap.objects.all():
        log.info('Updating external code "%s" to LOINC "%s".' % (mapping.ext_code, mapping.loinc.loinc_num))
        count = Lx.objects.filter(ext_code=mapping.ext_code, LxLoinc__isnull=True).update(LxLoinc=mapping.loinc.pk)
        log.debug('Objects updated: %s' % count)
        counter += count
    log.info('Total number of objects updated: %s' % counter)


if __name__ == '__main__':
    main()
    sys.exit()
    for item in connection.queries:
        pprint.pprint(item)
        pass