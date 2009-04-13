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
from ESP.nodis.core import DiseaseDefinition
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
    # Main Control block
    #
    if options.all: # '--all' is exactly equivalent to '--cases --update-cases'
        options.cases = True
        options.update = True
    if options.cases:
        DiseaseDefinition.generate_all_cases(begin_date=options.begin, end_date=options.end)
    if options.update:
        DiseaseDefinition.update_all_cases(begin_date=options.begin, end_date=options.end)
    if not (options.events or options.cases or options.update):
        parser.print_help()


def experiment():
    print defs.hep_b_1.matches()


if __name__ == '__main__':
    #main()
    experiment()
    print 'Total Number of DB Queries: %s' % len(connection.queries)
    #pprint.pprint(connection.queries)
