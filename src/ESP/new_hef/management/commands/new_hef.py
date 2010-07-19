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
    usage_str += 'Runs heuristics for abstract test NAME if specified; otherwise, runs all heuristics.\n'
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
        # Main
        #
        abstract_tests = AbstractLabTest.objects.all().order_by('name')
        if options['list']:
            print '-' * 80
            print '%-32s  %s' % ('TEST', 'DESCRIPTION')
            print '-' * 80
            for test in abstract_tests:
                print '%-32s  %s' % (test.name, test.verbose_name)
            sys.exit()
        test_names = abstract_tests.values_list('name', flat=True)
        if args:
            #
            # Sanity Check
            #
            for name in args:
                if not name in test_names:
                    sys.stderr.write('Error, unknown test name: %s\n' % name)
                    sys.exit()
            abstract_tests = abstract_tests.filter(name__in=args)
        #
        # Generate Events
        #
        count = 0
        for test in abstract_tests:
            log.info('Generating events for abstract test: %s' % test)
            heuristic_set = set(test.laborderheuristic_set.all())
            heuristic_set |= set(test.labresultpositiveheuristic_set.all())
            heuristic_set |= set(test.labresultratioheuristic_set.all())
            heuristic_set |= set(test.labresultfixedthresholdheuristic_set.all())
            for heuristic in heuristic_set:
                count += heuristic.generate_events()
        log.info('Generated %s total new events' % count)