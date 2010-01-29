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
                purge_names = tuple(BaseHeuristic.all_event_names())
            log.info('Purging %s events and dependent cases' % str(purge_names))
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
            #
            # NOTE:  We are using raw SQL because Django's delete() method is 
            # extremely slow, and overwhelms PostgreSQL's max locks per 
            # transaction (unless it's set absurdly high).  This SQL has been 
            # tested ONLY with PostgreSQL.  YMMV.  
            #
            cursor = connection.cursor()
            # Purge case events
            sql = 'DELETE FROM nodis_case_events WHERE id IN'
            sql = ' (SELECT ce.id FROM nodis_case_events ce'
            sql += ' JOIN hef_event e ON ce.event_id = e.id'
            sql += ' WHERE name in %s )' % str(purge_names)
            log.debug('Purge dependent case-events:\n%s' % sql)
            cursor.execute(sql)
            # Purge cases
            sql = 'DELETE FROM nodis_case WHERE id IN'
            sql += ' (SELECT c.id FROM nodis_case c JOIN nodis_case_events ce ON c.id = ce.case_id '
            sql += ' JOIN hef_event e ON ce.event_id = e.id'
            sql += ' WHERE name in %s )' % str(purge_names)
            log.debug('Purge dependent cases:\n%s' % sql)
            cursor.execute(sql)
            # Purge events
            sql = 'DELETE FROM hef_event WHERE name in %s' % str(purge_names)
            log.debug('Purge events:\n%s' % sql)
            cursor.execute(sql)
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