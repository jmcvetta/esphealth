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
from django.db.models import Min
from django.db.models import Max
from django.core.management.base import BaseCommand
from optparse import make_option

from ESP.utils.utils import log
from ESP.utils.utils import log_query
from ESP.emr.models import LabResult
from ESP.emr.models import LabTestConcordance



class Command(BaseCommand):
    
    help = 'Generate concordance of lab tests.'
    
    @transaction.commit_manually
    def handle(self, *fixture_labels, **options):
        log.info('Repopulating lab test concordance')
        log.debug('Begin transaction')
        # Clear the existing table
        LabTestConcordance.objects.all().delete()
        log.debug('Purged concordance table.')
        # Generate the concordance -- *LONG* query
        qs = LabResult.objects.all().values('native_code', 'native_name').distinct()
        qs = qs.annotate(
            count=Count('id'), 
            min_ref_low=Min('ref_low_float'), 
            max_ref_high=Max('ref_high_float'),
            min_result=Min('result_float'),
            max_result=Max('result_float'),
            ).order_by('pk')
        log_query('Concordance query', qs)
        for item in qs:
            l = LabTestConcordance()
            l.native_code = item['native_code']
            l.native_name = item['native_name']
            l.count = item['count']
            l.min_ref_low = item['min_ref_low']
            l.max_ref_high = item['max_ref_high']
            l.min_result = item['min_result']
            l.max_result = item['max_result']
            l.save()
            transaction.commit()
            log.debug('Added %s to concordance' % item)
            try:
                l.save()
                transaction.commit()
                log.debug('Added %s to concordance' % item)
            except:
                log.error('Could not save to concordance.')
                transaction.rollback()
        count = LabTestConcordance.objects.all().count()
        log.debug('Transaction committed')
        log.info('Populated lab test concordance with %s items' % count)
        
