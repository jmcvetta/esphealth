'''
                                  ESP Health
                         Notifiable Diseases Framework
                                 Case Requeue tool

@author: Carolina chacin <cchacin@commoninf.com>
@organization: CII http://www.commoninf.com
@copyright: (c) 2014 CII
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

import optparse
import sys
import pprint
from ESP.utils import date_from_str
import os
import cStringIO as StringIO
import time
import datetime
import re
import socket
import subprocess
import shlex
import ftplib
import math

from optparse import Values
from optparse import make_option

from django.db.models import Q
from django.core.management.base import BaseCommand

from ESP.nodis.base import DiseaseDefinition
from ESP.nodis.models import Case
from ESP.nodis.models import STATUS_CHOICES

from ESP.utils.utils import log
from ESP.utils.utils import log_query

from ESP.settings import  REQUEUE_LAG_DAYS

#===============================================================================
#
#--- Configuration
#
#===============================================================================

VERSION = '2.3.1'
DATE_FORMAT = '%Y%m%d'

#===============================================================================
#
#--- Exceptions
#
#===============================================================================


class NoConditionConfigurationException(BaseException):
    '''
    raised when no conf.config defined for a disease, needed for reportable items (encounters, icd9s, prescriptions and labs)
    '''
    pass


class Command(BaseCommand):
    
    help = 'Requeue sent cases where the reportable list of objects have changed within the recurrence window of the condition'
    
    args = '[conditions]'
    
    option_list = BaseCommand.option_list + (
        make_option('--case', action='store', dest='case_id', type='int', metavar='ID', 
            help='Check a single case with specified case ID'),
        make_option('--status', action='store', dest='status', default='S',
            help='Check only cases with this status ("S" by default)'),
         make_option('--ref_date', action='store', dest='ref_date', 
            help='Check only cases based on this reference date'),   
        
        )
    
    def handle(self, *args, **options):
        report_conditions = [] # Names of conditions for which we will export cases
        #
        # Parse and sanity check command line for options
        #
        all_conditions = DiseaseDefinition.get_all_conditions()
        all_conditions.sort()
        options = Values(options)
        for a in args:
            print a
            if a in all_conditions:
                report_conditions.append(a)
            else:
                print >> sys.stderr
                print >> sys.stderr, 'Unrecognized condition: "%s".  Aborting.' % a
                print >> sys.stderr
                print >> sys.stderr, 'Valid conditions are:'
                print >> sys.stderr, '    --------'
                print >> sys.stderr, '    all (reports all conditions below)'
                print >> sys.stderr, '    --------'
                for con in all_conditions:
                    print >> sys.stderr, '    %s' % con
                sys.exit(101)
        if not args:
            report_conditions = all_conditions
        log.debug('conditions: %s' % report_conditions)
        valid_status_choices = [item[0] for item in STATUS_CHOICES]
        if options.status not in valid_status_choices:
                print >> sys.stderr
                print >> sys.stderr, 'Unrecognized status: "%s".  Aborting.' % options.status
                print >> sys.stderr
                print >> sys.stderr, 'Valid status choices are:'
                for stat in valid_status_choices:
                    print >> sys.stderr, '    %s' % stat
                sys.exit(102)
        # you will have to call this command twice for status S and for status RS or hardcode?
        log.debug('status: %s' % options.status)
        
        # Generate case query
        #
        if options.case_id:
            q_obj = Q(pk__exact=options.case_id)
        else:
            q_obj = Q(condition__in=report_conditions)
            #call requeue set the status to be a list of sent ('S','RS')
            q_obj = q_obj & Q(status = options.status)
        
        cases = Case.objects.filter(q_obj).order_by('condition', 'pk')
        log_query('Filtered cases', cases)
        
        if not cases:
            msg = 'No cases found matching your specifications. Nothing to requeue.'
            log.info(msg)
            print >> sys.stderr, ''
            print >> sys.stderr, msg
            print >> sys.stderr, ''             
        
        self.timestamp = datetime.datetime.now().strftime('%Y-%b-%d.%H.%M.%s') 
        if cases:
            counter = self.requeue(options,  cases)
        log.info('Cases requeued: %s' % counter)
           
    def requeue(self, options,  cases):
        counter = 0
        condition = None
        for case in cases:
            try: 
                # because cases are sorted by condition and then pk
                if not condition or condition <> case.condition:
                    condition = case.condition
                    condition_config = case.condition_config
                    max_reportable_days = condition_config.get_max_reportables_days_after()
                    
                log.debug('Requeuing case for %s' % case)
                #
                #case.date + window of time is in the future  
                # 
                if not options.ref_date:
                    ref_date = datetime.date.today()
                else:
                    ref_date = date_from_str(options.ref_date)
                if ref_date <= case.date + datetime.timedelta(days=REQUEUE_LAG_DAYS + max_reportable_days):
                    # check reportables
                    reportables = case.create_reportables_list()
                    if case.reportables <> reportables:
                        counter += 1
                        case.status = 'RQ'
                        case.reportables = reportables
                        case.save()
            except NoConditionConfigurationException, e:
                log.critical('Could not Requeue case %s!' % case)
                log.critical('    %s' % e)
        return counter