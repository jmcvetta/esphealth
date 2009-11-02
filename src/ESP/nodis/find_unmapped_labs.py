'''
                                  ESP Health
                         Notifiable Diseases Framework
                         Populate Unmapped Labs Cache


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory <http://www.channing.harvard.edu>
@copyright: (c) 2009 Channing Laboratory
@license: LGPL 3.0 <http://www.gnu.org/licenses/lgpl-3.0.txt>
'''

from django.db import transaction
from django.db.models import Q
from django.db.models import Count

from ESP.utils.utils import log
from ESP.utils.utils import log_query
from ESP.nodis.core import Condition
from ESP.emr.models import LabResult
from ESP.nodis.models import InterestingLab
from ESP.nodis import defs


@transaction.commit_manually
def main():
    log.info('Repopulating interesting labs cache')
    log.debug('Begin transaction')
    # Clear the cache
    InterestingLab.objects.all().delete()
    log.debug('Unmapped labs cache purged')
    # Populate the cache
    all_strings = Condition.all_test_name_search_strings()
    q_obj = Q(native_name__icontains=all_strings[0])
    for string in all_strings[1:]:
        q_obj |= Q(native_name__icontains=string)
    qs = LabResult.objects.filter(q_obj).values('native_code', 'native_name').distinct()
    qs = qs.annotate(count=Count('id'))
    log_query('Test name search', qs)
    for item in qs:
        l = InterestingLab()
        l.native_code = item['native_code']
        l.native_name = item['native_name']
        l.count = item['count']
        try:
            l.save()
            transaction.commit()
            log.debug('Added %s to interesting labs cache' % item)
        except:
            log.error('Could not save to interesting labs cache; skipping.')
            transaction.rollback()
    count = InterestingLab.objects.all().count()
    log.debug('Transaction committed')
    log.info('Populated interesting labs cache with %s items' % count)
    

if __name__ == '__main__':
    main()