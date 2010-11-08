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
from django.core.management.base import BaseCommand
from optparse import make_option

from ESP import settings
from ESP.utils import utils as util
from ESP.utils.utils import log
from ESP.nodis.models import Condition
from ESP.nodis import defs  # Register definitions

    
class Command(BaseCommand):
    
    help = 'Generate Nodis cases'
    
    args = '[conditions]'
    
    option_list = BaseCommand.option_list + (
        make_option('--regenerate', action='store_true', dest='regenerate', 
            help='Purge and regenerate cases'),
        )
    # TODO: Add --list argument

    def handle(self, *args, **options):
        # 
        # TODO: We need a lockfile or some othermeans to prevent multiple 
        # instances running at once.
        #
        all_condition_names = [c.name for c in Condition.all_conditions()]
        if args: 
            conditions = set()
            for name in args:
                if name not in all_condition_names:
                    sys.stderr.write("Unknown condition: '%s'.  Exiting.\n" % name)
                con = Condition.get_condition(name)
                assert con, 'Unknown condition: %s' % name
                conditions.add(con)
        else:
            conditions = Condition.all_conditions()
        #
        # (Re)generate Cases
        #
        for c in conditions:
            if options['regenerate']:
                c.regenerate()
            else:
                c.generate_cases()
    
