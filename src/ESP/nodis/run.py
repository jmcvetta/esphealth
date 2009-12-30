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
from ESP.nodis.models import Condition
from ESP.nodis import defs  # Register definitions

    
USAGE_MSG = '''\
%prog [--regenerate] [conditions] 

Where conditions are one or more of the following:
'''
USAGE_MSG += '\n'.join(['    %s' % c.name for c in Condition.all_conditions()])


def main():
    # 
    # TODO: We need a lockfile or some othermeans to prevent multiple 
    # instances running at once.
    #
    parser = optparse.OptionParser(usage=USAGE_MSG)
    parser.add_option('--regenerate', action='store_true', dest='regenerate', 
        help='Purge and regenerate cases')
    (options, args) = parser.parse_args()
    log.debug('options: %s' % options)
    #
    # Main Control block
    #
    all_condition_names = [c.name for c in Condition.all_conditions()]
    if args: 
        conditions = set()
        for name in args:
            if name not in all_condition_names:
                sys.stderr.write("Unknown condition: '%s'.  Exiting.\n" % name)
            conditions.add(Condition.get_condition(name))
    else:
        conditions = Condition.all_conditions()
    for c in conditions:
        if options.regenerate:
            c.regenerate()
        else:
            c.generate_cases()


if __name__ == '__main__':
    main()
    if settings.DEBUG:
        # Query count is only retained in DEBUG mode
        print 'Total Number of DB Queries: %s' % len(connection.queries)