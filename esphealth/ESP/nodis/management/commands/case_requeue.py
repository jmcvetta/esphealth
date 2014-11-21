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

from ESP.nodis.base import DiseaseDefinition, ReinfectionDiseaseDefinition
from ESP.hef.models import Event
from ESP.nodis.models import Case
from ESP.nodis.models import STATUS_CHOICES

from ESP.utils.utils import log
from ESP.utils.utils import log_query

from ESP.settings import  REQUEUE_LAG_DAYS
from ESP.settings import  REQUEUE_REF_DATE

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
        counter = 0
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
                    
                '''
                reinfection logic
                checks for events that happened within the window of reinfection days .
                This window starts from the end of the reinfection window. 
                It will add the events found to the existing cases as a followup_event 
                and change the status to RQ if the status is S for the existing cases
                '''
                disease_definition = DiseaseDefinition.get_by_short_name(condition)  
                if isinstance(disease_definition, ReinfectionDiseaseDefinition) and disease_definition.reinfection  >0:
                    event_names = set()
                    for heuristic in disease_definition.event_heuristics:
                        for name in heuristic.event_names:
                            event_names.add(name)
                     
                    start = case.date + datetime.timedelta(days=disease_definition.recurrence_interval) 
                    end = case.date + datetime.timedelta(days=disease_definition.recurrence_interval) + datetime.timedelta(days=disease_definition.reinfection)  
                    q_obj = Q(patient=case.patient)
                    q_obj &= Q(date__gte=start)
                    q_obj &= Q(date__lte=end)
                    q_obj &= Q(name__in = event_names)
                    followup_events = Event.objects.filter(q_obj).order_by('date')
                    #add events to follow up of these cases 
                    if followup_events:
                        for event in followup_events:
                            if not case.followup_events.all() or event not in case.followup_events.all():
                                case.followup_events.add(event)
                                #change the status of all the cases in this query set
                                if case.status == 'S' or case.status == 'RS' and not case.followup_sent:
                                    log.info('Requeing cases of %s with Reinfection' % condition)
                                    case.status = 'RQ'
                                    case.followup_sent = True
                    case.save()    
                    
                #
                #case.date + window of time is in the future  
                # 
                if not REQUEUE_REF_DATE or REQUEUE_REF_DATE =='TODAY':
                    ref_date = datetime.date.today()
                else:
                    ref_date = date_from_str(REQUEUE_REF_DATE)
               
                if ref_date <= case.date + datetime.timedelta(days=REQUEUE_LAG_DAYS + max_reportable_days):
                    # check reportables
                    reportables = case.create_reportables_list()
                    if case.reportables <> reportables:
                        log.debug('Requeuing case for %s' % case)
                        counter += 1
                        case.status = 'RQ'
                        case.reportables = reportables
                        case.save()
            except NoConditionConfigurationException, e:
                log.critical('Could not Requeue case %s!' % case)
                log.critical('    %s' % e)
        return counter