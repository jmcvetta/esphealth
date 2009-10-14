#!/usr/bin/env python
'''
                                  ESP Health
                          Heuristic Events Framework
                              Command Line Runner


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''

import sys
import datetime
import optparse

from django.db import connection


from ESP.hef.core import BaseHeuristic
from ESP.hef.events import * # Load all HeuristicEvent definitions
from ESP import settings
from ESP.utils.utils import log




#===============================================================================
#
#--- ~~~ Main ~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    
USAGE_MSG = '''\
%prog [options]
'''


def main():
    # 
    # TODO: We need a lockfile or some othermeans to prevent multiple 
    # instances running at once.
    #
    usage_str = '%prog [options] [NAME, NAME, ...] \n'
    usage_str += '\n'
    usage_str += 'Runs heuristic NAME if specified; otherwise, runs all heuristics.\n'
    usage_str += 'Either --full or --incremental must be specified.\n'
    usage_str += '\n'
    parser = optparse.OptionParser(usage=usage_str)
    parser.add_option('--full', action='store_true', dest='full',
        help='Generate events (ALL data)', default=False)
    parser.add_option('--incremental', action='store_true', dest='incremental', 
        help='Generate events (new data only)', default=False)
    parser.add_option('--list', action='store_true', dest='list', 
        help='List names of all registered heuristics')
    (options, args) = parser.parse_args()
    log.debug('options: %s' % options)
    # 
    # Main
    #
    if options.list and (options.incremental or options.full):
        sys.stderr.write('\nERROR: --list must be used by itself.\n\n')
        parser.print_help()
        sys.exit()
    elif options.list:
        for name in BaseHeuristic.list_heuristic_names():
            print name
        sys.exit()
    if (options.full and options.incremental) or not (options.full or options.incremental):
        sys.stderr.write('\nERROR: You must choose either --full or --incremental.\n\n')
        parser.print_help()
        sys.exit()
    if args:
        for name in args:
            try:
                BaseHeuristic.generate_events_by_name(name=name, incremental=options.incremental)
            except KeyError:
                print >> sys.stderr, 'Unknown heuristic name: "%s"' % name
    else:
        BaseHeuristic.generate_all_events(incremental=options.incremental)
    

if __name__ == '__main__':
    main()
    #print 'Total Number of DB Queries: %s' % len(connection.queries)
    #pprint.pprint(connection.queries)
