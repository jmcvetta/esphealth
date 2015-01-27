'''
                                  ESP Health
                         Notifiable Diseases Framework
                            Case Reportables Snapshot

@author: Bob Zambarano <bzambarano@commoninf.com>
@organization: Commonwealth Informatics http://www.commoninf.com
@copyright: (c) 2014 Commonwealh Informatics
@license: LGPL - http://www.gnu.org/licenses/lgpl-3.0.txt

--------------------------------------------------------------------------------
EXIT CODES

10     Keyboard interrupt
11     No cases found matching query
101    Unrecognized condition
102    Unrecognized case status
103    Unrecognized template name
104    Invalid combination of command line options
999    Functionality not yet implemented
'''

import sys
import datetime
import socket

from django.db.models import Q
from django.core.management.base import BaseCommand

from ESP.nodis.base import DiseaseDefinition
from ESP.nodis.models import Case, CaseStatusHistory, ReportRun


from ESP.utils.utils import log
from ESP.utils.utils import log_query


#===============================================================================
#
#--- Configuration
#
#===============================================================================


class Command(BaseCommand):
    
    help = 'Geneate reportables list and update Nodis cases'    
    args = '[conditions]'
    
        
    
    def handle(self, *args, **options):
        all_conditions = DiseaseDefinition.get_all_conditions()
        all_conditions.sort()
        report_conditions = all_conditions
        log.debug('conditions: %s' % report_conditions)
        q_obj = Q(status='Q')
        cases = Case.objects.filter(q_obj).order_by('pk')
        log_query('Filtered cases', cases)
        #For Tarrant Cnty, case_snapshot represents the start of a detection run
        run = ReportRun(hostname=socket.gethostname()+': case_snapshot run')
        run.save()

        
        if not cases:
            msg = 'No cases found matching your specifications.  Empty output generated.'
            log.info(msg)
            print >> sys.stderr, ''
            print >> sys.stderr, msg
            print >> sys.stderr, ''

        for case in cases:
            case.status = 'S'
            case.reportables = case.create_reportables_list()
            updttm = datetime.datetime.now()
            case.sent_timestamp = updttm
            case.updated_timestamp = updttm
            case.save() 
            hist = CaseStatusHistory(case=case, old_status='Q', new_status='S', 
                                     changed_by='command: case_snapshot', comment='Case events list created and saved as case.reportables')
            hist.save() # Add a history object
   
