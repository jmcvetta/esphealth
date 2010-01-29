#!/usr/bin/env python
'''
                                  ESP Health
                          Heuristic Events Framework
                              Command Line Runner


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@cooptions['args']:pyright: (c) 2009 Channing Laboratory

@license: LGPL
'''

import sys
import datetime
import optparse

from django.db import connection
from django.db import transaction
from django.core.management.base import BaseCommand
from optparse import make_option


from ESP.hef.core import BaseHeuristic
from ESP.hef.models import Event
from ESP.hef.models import Run
from ESP.hef.events import * # Load all Event definitions
from ESP.nodis.models import Case # hef.core and .models are dependencies of nodis/models, but this command script is not
from ESP import settings
from ESP.utils.utils import log
from ESP.utils.utils import log_query




#===============================================================================
#
#--- ~~~ Main ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    
class Command(BaseCommand):
    
    help = 'Generate heuristic events'
    
    args = '[HEURISTIC, HEURISTIC, ...]'
    usage_str = '[options] [NAME, NAME, ...] \n'
    usage_str += '\n'
    usage_str += 'Runs heuristic NAME if specified; otherwise, runs all heuristics.\n'
    usage_str += '\n'
    option_list = BaseCommand.option_list + (
        make_option('--list', action='store_true', dest='list', 
            help='List names of all registered heuristics'),
        make_option('--regenerate', action='store_true', dest='regenerate', default=False,
            help='Purge and regenerate heuristic events')
        )

    @transaction.commit_on_success
    def handle(self, *args, **options):
        # 
        # TODO: We need a lockfile or some othermeans to prevent multiple 
        # instances running at once.
        #
        log.debug('options: %s' % options)
        # 
        # Main
        #
        if options['list']:
            h_names =  [h.name for h in BaseHeuristic.all_heuristics()]
            h_names.sort()
            for name in h_names:
                print name
            sys.exit()
        this_run = Run()
        this_run.save()
        #
        # Purge data before regeneration
        #
        if options['regenerate']:
            if args:
                purge_names = args
            else:
                purge_names = BaseHeuristic.all_event_names
            log.info('Purging %s events and dependent cases' % purge_names)
            dependent_cases = Case.objects.filter(events__name__in=purge_names)
            log_query('Dependent cases', dependent_cases)
            dep_case_count = dependent_cases.count()
            log.warning('NOTE: %s cases are dependent on these the heuristic events to be purged.' % dep_case_count)
            log.warning('No safeguards are included in --regenerate at this time.')
            print
            print 'WARNING!'
            print 
            print 'The operation you have requested will PURGE %s Nodis cases.' % dep_case_count
            print 'Please be sure you know what you are doing.'
            print
            decision = raw_input('Type PURGE to proceed:\n')
            if not decision == 'PURGE':
                print 'Not okay to proceed.  Exiting now.'
                print
                sys.exit(12)
            log.debug('Purging dependent cases...')
            dependent_cases.delete()
            log.debug('Purging heuristic events...')
            Event.objects.filter(name__in=purge_names).delete()
        #
        # Generate specific events
        #
        if args:
            for name in args:
                try:
                    BaseHeuristic.generate_events_by_name(name=name, run=this_run)
                except KeyError:
                    print >> sys.stderr, 'Unknown heuristic name: "%s"' % name
        #
        # Generate all events
        #
        else:
            if options['regenerate']:
                log.info('Purging all events that we know how to regenerate')
                Event.objects.filter(name__in=BaseHeuristic.all_event_names).delete()
            BaseHeuristic.generate_all_events(run=this_run)