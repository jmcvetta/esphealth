#!/usr/bin/env python
'''
                                  ESP Health
                         Notifiable Diseases Framework
                              Command Line Runner


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''

import datetime
import sys
import optparse
import pprint

from django.db import connection

from ESP import settings
from ESP.utils import utils as util
from ESP.utils.utils import log
from ESP.nodis.core import Condition
from ESP.nodis import defs  # Register definitions

    
USAGE_MSG = '''\
%prog [options]

    One or more of '-c', '-u', or '-a' must be specified.
    
    DATE variables are specified in this format: '17-Mar-2009'\
'''


def main():
    # 
    # TODO: We need a lockfile or some othermeans to prevent multiple 
    # instances running at once.
    #
    parser = optparse.OptionParser(usage=USAGE_MSG)
    parser.add_option('-c', '--cases', action='store_true', dest='cases',
        help='Generate new cases')
    parser.add_option('-u', '--update-cases', action='store_true', dest='update',
        help='Update cases')
    parser.add_option('-a', '--all', action='store_true', dest='all', 
        help='Generate generate new cases and update existing cases')
    parser.add_option('--regenerate', action='store_true', dest='regenerate', 
        help='Purge and regenerate cases')
    parser.add_option('--condition', action='store', dest='condition', type='string',
        metavar='NAME', help='Generate new cases for condition NAME only')
    (options, args) = parser.parse_args()
    log.debug('options: %s' % options)
    #
    # Main Control block
    #
    if options.all: # '--all' is exactly equivalent to '--cases --update-cases'
        options.cases = True
        options.update = True
    if options.update and options.disease:
        msg = '\nUpdating cases by specific disease is not yet supported.\n'
        sys.stderr.write(msg)
        parser.print_help()
        sys.exit()
    if options.condition:
        conditions = [Condition.get_condition(options.disease)]
        if not conditions:
            msg = '\nNo disease registered with name "%s".\n' % options.disease
            sys.stderr.write(msg)
            sys.exit()
    else:
        conditions = Condition.all_conditions()
    if options.cases:
        for c in conditions:
            c.generate_cases()
    if options.update:
        for c in conditions:
            c.update_all_cases()
    if options.regenerate:
        for c in conditions:
            c.regenerate()
    if not (options.cases or options.update or options.regenerate):
        parser.print_help()


if __name__ == '__main__':
    main()
    print 'Total Number of DB Queries: %s' % len(connection.queries)
    #pprint.pprint(connection.queries)
