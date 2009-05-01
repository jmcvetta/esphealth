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
    parser.add_option('--begin', action='store', dest='begin', type='string', 
        metavar='DATE', help='Analyze time window beginning at DATE')
    parser.add_option('--end', action='store', dest='end', type='string', 
        metavar='DATE', help='Analyze time window ending at DATE')
    (options, args) = parser.parse_args()
    log.debug('options: %s' % options)
    #
    # Date Parser
    #
    date_format = '%d-%b-%Y'
    if options.begin:
        options.begin = datetime.datetime.strptime(options.begin, date_format).date()
    if options.end:
        options.end = datetime.datetime.strptime(options.end, date_format).date()
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
        BaseHeuristic.generate_events_by_name(name=options.event, begin_date=options.begin, end_date=options.end)
    else:
        BaseHeuristic.generate_all_events(begin_date=options.begin, end_date=options.end)
    

if __name__ == '__main__':
    main()
    #print 'Total Number of DB Queries: %s' % len(connection.queries)
    #pprint.pprint(connection.queries)
