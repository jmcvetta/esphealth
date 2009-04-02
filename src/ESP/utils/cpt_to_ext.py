#!/usr/bin/env python
'''
                                  ESP Health
Generate ext_code field from CPT + Component.  

@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''
#
# Since neither LxTest_Code_CPT nor LxComponent are indexed, this script 
# will probably take quite a while to run on a large Lx table.
#

# Instead of this code, which was a PiA, I am using raw SQL:
#
# update esp_lx set ext_code=null; 
# update esp_lx set ext_code = LxTest_Code_CPT where LxTest_Code_CPT <> '' and LxComponent = '' limit 10; 
# update esp_lx set ext_code = Concat(LxTest_Code_CPT, '--', LxComponent) where LxTest_Code_CPT <> '' and LxComponent <> '' limit 10;
#


from django.db.models import Q
from django.db.models import F
from django.db import connection

from ESP.utils.utils import log
from ESP.esp.models import Lx


def main():
    counter = 0
    with_cpt = Q(LxTest_Code_CPT__isnull=False) & ~Q(LxTest_Code_CPT='')
    with_comp = Q(LxComponent__isnull=False) & ~Q(LxComponent='')
    without_comp = Q(LxComponent__isnull=True) | Q(LxComponent='')
    lx_cpt = Lx.objects.filter(with_cpt).filter(without_comp)
    lx_comp = Lx.objects.filter(with_cpt).filter(with_comp)
    for item in lx_cpt[:10]:
        print 'pk: %-10s cpt: %-10s comp: %-10s ext_code: %-20s' % (item.pk, item.LxTest_Code_CPT, item.LxComponent, item.ext_code)
    print '-' * 80
    for item in lx_comp[:10]:
        print 'pk: %-10s cpt: %-10s comp: %-10s ext_code: %-20s' % (item.pk, item.LxTest_Code_CPT, item.LxComponent, item.ext_code)
    log.debug('Converting CPT to ext_code')
    count = lx_cpt.update(ext_code=F('LxTest_Code_CPT'))
    log.debug('Updated %s records' % count)
    counter += count
    log.debug('Converting CPT+Component to ext_code')
    count = lx_comp.update(ext_code=(F('LxTest_Code_CPT') + '--' + F('LxComponent')))
    log.debug('Updated %s records' % count)
    counter += count
    log.info('Total number of objects updated: %s' % counter)


if __name__ == '__main__':
    main()
    print connection.queries