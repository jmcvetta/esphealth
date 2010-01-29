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
from ESP import settings
from ESP.utils.utils import log




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
        if args:
            for name in args:
                try:
                    if options['regenerate']:
                        log.info('Purging %s events' % name)
                        Event.objects.filter(name=name).delete()
                    BaseHeuristic.generate_events_by_name(name=name, run=this_run)
                except KeyError:
                    print >> sys.stderr, 'Unknown heuristic name: "%s"' % name
        else:
            if options['regenerate']:
                log.info('Purging all events that we know how to regenerate')
                Event.objects.filter(name__in=BaseHeuristic.all_event_names).delete()
            BaseHeuristic.generate_all_events(run=this_run)