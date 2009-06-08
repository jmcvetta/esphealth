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


from ESP.hef.hef import BaseHeuristic
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

    One or more of '-e', '-c', '-u', or '-a' must be specified.
    
    DATE variables are specified in this format: '17-Mar-2009'\
'''


def main():
    # 
    # TODO: We need a lockfile or some othermeans to prevent multiple 
    # instances running at once.
    #
    parser = optparse.OptionParser(usage=USAGE_MSG)
    parser.add_option('--heuristic', action='store', dest='event', type='string',
        metavar='NAME', help='Generate events for heuristic NAME only')
    parser.add_option('--list', action='store_true', dest='list', 
        help='List all registered heuristics')
    parser.add_option('--incremental', action='store_true', dest='incremental', 
        help='Examine only new data to generate events. (Default)', default=True)
    parser.add_option('--full', action='store_false', dest='incremental',
        help='Examine *all* data to generate events')
    (options, args) = parser.parse_args()
    log.debug('options: %s' % options)
    # 
    # Main
    #
    if options.event and options.list:
        sys.stderr.write('\nERROR: --list and --heuristic are mutually incompatible.\n\n')
        parser.print_help()
    elif options.list:
        for name in BaseHeuristic.list_heuristic_names():
            print name
    elif options.event:
        try:
            BaseHeuristic.generate_events_by_name(name=options.event, incremental=options.incremental)
        except KeyError:
            print >> sys.stderr
            print >> sys.stderr, 'Unknown heuristic name: "%s".  Aborting run.' % options.event
            print >> sys.stderr
    else:
        BaseHeuristic.generate_all_events(incremental=options.incremental)
    

if __name__ == '__main__':
    main()
    #print 'Total Number of DB Queries: %s' % len(connection.queries)
    #pprint.pprint(connection.queries)
