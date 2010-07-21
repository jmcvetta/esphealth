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


from ESP.new_hef.models import AbstractLabTest
from ESP.new_hef.models import EncounterHeuristic
from ESP.nodis.models import Case # hef.core and .models are dependencies of nodis/models, but this command script is not
from ESP import settings
from ESP.utils import log
from ESP.utils import log_query




#===============================================================================
#
#--- ~~~ Main ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    
class Command(BaseCommand):
    
    help = 'Generate heuristic events'
    
    usage_str = '[options] [NAME, NAME, ...] \n'
    usage_str += '\n'
    usage_str += 'Runs heuristics for NAME if specified; otherwise, runs all heuristics.\n'
    usage_str += '\n'
    option_list = BaseCommand.option_list + (
        make_option('--list', action='store_true', dest='list', 
            help='List all abstract tests'),
        )

    def handle(self, *args, **options):
        # 
        # TODO: We need a lockfile or some othermeans to prevent multiple 
        # instances running at once.
        #
        log.debug('options: %s' % options)
        # 
        # Create dispatch dictionary of abstract tests and heuristics
        #
        dispatch = {}
        abstract_tests = AbstractLabTest.objects.all().order_by('name')
        for test in abstract_tests:
            dispatch[test.name] = test
        for eh in EncounterHeuristic.objects.all():
            assert eh.name not in dispatch
            dispatch[eh.name] = eh
        name_list = dispatch.keys()
        name_list.sort()
        if options['list']:
            print '-' * 80
            print '%-32s  %s' % ('NAME', 'DESCRIPTION')
            print '-' * 80
            for name in name_list:
                print '%-32s  %s' % (name, dispatch[name])
            sys.exit()
        if args:
            #
            # Sanity Check
            #
            name_list = []
            for name in args:
                if not name in dispatch:
                    sys.stderr.write('Error, unknown test name: %s\n' % name)
                    sys.exit()
                name_list.append(name)
        #
        # Generate Events
        #
        count = 0
        for name in name_list:
            count += dispatch[name].generate_events()
        log.info('Generated %s total new events' % count)