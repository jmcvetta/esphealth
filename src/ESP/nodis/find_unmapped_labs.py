'''
                                  ESP Health
                         Notifiable Diseases Framework
                         Populate Unmapped Labs Cache


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory <http://www.channing.harvard.edu>
@copyright: (c) 2009 Channing Laboratory
@license: LGPL 3.0 <http://www.gnu.org/licenses/lgpl-3.0.txt>
'''

from ESP.utils.utils import log
from ESP.nodis.core import Condition
from ESP.nodis.models import UnmappedLab
from ESP.nodis import defs


def main():
    log.info('Purging and repopulating unmapped labs cache')
    # Clear the cache
    UnmappedLab.objects.all().delete()
    log.debug('Unmapped labs cache purged')
    # Populate the cache
    for item in Condition.find_unmapped_labs():
        ul = UnmappedLab()
        ul.native_code = item['native_code']
        ul.native_name = item['native_name']
        ul.count = item['count']
        ul.save()
        log.debug('Added %s to unmapped labs cache' % item)
    count = UnmappedLab.objects.all().count()
    log.info('Populated unmapped labs cache with %s items' % count)
    

if __name__ == '__main__':
    main()