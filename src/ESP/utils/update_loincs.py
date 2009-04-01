#!/usr/bin/env python
'''
                                  ESP Health
                      Update LOINC Codes for lab Results

@author: Ross Lazarus <ross.lazarus@channing.harvard.edu>
@author: Xuanlin Hou <rexua@channing.harvard.edu>
@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''

from django.db import connection

from ESP.utils.utils import log
from ESP.conf.models import ExtToLoincMap
from ESP.esp.models import Lx


def main():
    counter = 0
    for mapping in ExtToLoincMap.objects.all()[0]:
        log.info('Updating external code "%s" to LOINC %s' % (mapping.ext_code, mapping.loinc))
        count = Lx.objects.filter(ext_code=mapping.ext_code).update(LxLoinc=mapping.loinc.id)
        log.debug('Objects updated: %s' % count)
        counter += count
    log.info('Total number of objects updated: %s' % counter)


if __name__ == '__main__':
    main()
    print connection.queries