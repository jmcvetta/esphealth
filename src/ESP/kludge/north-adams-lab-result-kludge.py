#!/usr/bin/env python
'''
Alter lab test result strings to make North Adams data work with rules 
for HVMA lab results.
'''


import pprint

from django.db.models import Q

from ESP.esp import models
from ESP import settings
from ESP.utils.utils import log


RESULT_KLUDGE_MAP = {
	'20993-2': {'Not detected': 'negative'},
	'24111-7': {'Not detected': 'negative'},
    }



def main():
    update_counter = 0
    for loinc in RESULT_KLUDGE_MAP:
        log.info('Kludging LOINC: %s' % loinc)
        for result_string in RESULT_KLUDGE_MAP[loinc]:
            replacement = RESULT_KLUDGE_MAP[loinc][result_string]
            log.debug('Replacing "%s" with "%s"' % (result_string, replacement))
            lxes = models.Lx.objects.filter(LxLoinc=loinc, LxTest_results=result_string)
            count = lxes.update(LxTest_results=replacement)
            log.debug('Updated %s records' % count)
            update_counter += count
    log.info('Total records updated: %s' % update_counter)
    print 'Total records updated: %s' % update_counter


if __name__ == '__main__':
    main()