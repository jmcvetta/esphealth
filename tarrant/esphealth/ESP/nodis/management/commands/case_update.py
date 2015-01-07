'''
                                  ESP Health
                         Notifiable Diseases Framework
                                 Case Requeue tool

@author: Bob Zambarano <bzambarano@commoninf.com>
@organization: Commonwealth Informatics http://www.commoninf.com
@copyright: (c) 2014 CII
@license: LGPL - http://www.gnu.org/licenses/lgpl-3.0.txt

--------------------------------------------------------------------------------
'''

import sys, datetime
from django.db.models import Q
from django.core.management.base import BaseCommand
from ESP.nodis.models import Case, CaseStatusHistory
from ESP.utils.utils import log
from ESP.utils.utils import log_query


class Command(BaseCommand):
    
    help = 'Set status to updated for sent cases where the reportable list of objects have changed within the recurrence window of the condition'
    
    args = '[conditions]'
    
    
    def handle(self, *args, **options):
        q_obj = Q(status = 'S')
        
        cases = Case.objects.filter(q_obj).order_by('condition', 'pk')
        log_query('Filtered cases', cases)
        
        if not cases:
            msg = 'No cases found matching your specifications. Nothing to requeue.'
            log.info(msg)
            print >> sys.stderr, ''
            print >> sys.stderr, msg
            print >> sys.stderr, ''             
        
        self.timestamp = datetime.datetime.now().strftime('%Y-%b-%d.%H.%M.%s') 
        counter = 0
        for case in cases:
            if case.reportables!=case.create_reportables_list():
                counter+=1
                case.status='U'
                case.updated_timestamp = datetime.datetime.now()
                case.save()
                hist = CaseStatusHistory(case=case, old_status='S', new_status='U', 
                                changed_by='command: case_update', comment='New event data available for case')
                hist.save() # Add a history object

        log.info('Cases requeued: %s' % counter)
           
