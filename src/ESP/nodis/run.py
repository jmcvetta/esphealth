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
from ESP.nodis.core import Disease
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
    parser.add_option('--disease', action='store', dest='disease', type='string',
        metavar='NAME', help='Generate new cases for disease NAME only')
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
    if options.disease:
        diseases = [Disease.get_disease_by_name(options.disease)]
        if not diseases:
            msg = '\nNo disease registered with name "%s".\n' % options.disease
            sys.stderr.write(msg)
            sys.exit()
    else:
        diseases = Disease.get_all_diseases()
    if options.cases:
        for dis in diseases:
            dis.generate_cases()
    if options.update:
        for dis in diseases:
            dis.update_reportable_events()
    if options.regenerate:
        for dis in diseases:
            dis.regenerate()
    if not (options.cases or options.update or options.regenerate):
        parser.print_help()


def experiment():
    #defs.hep_b_1.matches()
    #defs.hep_b_2.matches()
    print defs.hep_b_3.matches()
    #defs.gonorrhea_crit_1.matches()
    #defs.hep_b.generate_cases()


if __name__ == '__main__':
    main()
    #experiment()
    print 'Total Number of DB Queries: %s' % len(connection.queries)
    #pprint.pprint(connection.queries)
