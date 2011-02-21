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
from django.db import connection
from django.db.models import Q
from django.db.models import Count
from django.core.management.base import BaseCommand
from optparse import make_option

from esp.utils.utils import log
from esp.utils.utils import log_query
from esp.emr.models import LabResult
from esp.emr.models import LabTestConcordance



class Command(BaseCommand):
    
    help = 'Generate concordance of lab tests.'
    
    @transaction.commit_on_success
    def handle(self, *fixture_labels, **options):
        log.info('Repopulating lab test concordance')
        log.debug('Begin transaction')
        # Clear the existing table - raw SQL TRUNCATE for speed
        cursor = connection.cursor()
        cursor.execute('TRUNCATE emr_labtestconcordance')
        log.debug('Purged concordance table.')
        # Generate the concordance -- *LONG* query
        qs = LabResult.objects.filter(native_code__isnull=False)
        qs = qs.values('native_code', 'native_name').distinct()
        qs = qs.annotate(count=Count('id')).order_by('native_code', 'native_name')
        log_query('Concordance query', qs)
        for item in qs.iterator():
            LabTestConcordance(
                native_code = item['native_code'],
                native_name = item['native_name'],
                count = item['count'],
                ).save()
            log.debug('Added %s to concordance' % item)
        count = LabTestConcordance.objects.all().count()
        log.debug('Transaction committed')
        log.info('Populated lab test concordance with %s items' % count)
        
