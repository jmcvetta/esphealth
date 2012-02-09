'''
                                  ESP Health
                          Heuristic Events Framework
                              Command Line Runner


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009-2010 Channing Laboratory
@license: LGPL
'''

import sys
import datetime
import optparse
import threading
import Queue
import thread
import signal
import time

from django.db import connection
from django.db import transaction
from django.core.management.base import BaseCommand
from optparse import make_option

from ESP.settings import HEF_THREAD_COUNT
from ESP.hef.base import BaseHeuristic
from ESP.hef.base import BaseEventHeuristic
from ESP.hef.base import BaseTimespanHeuristic
from ESP.hef.base import AbstractLabTest
from ESP.hef.base import DiagnosisHeuristic
from ESP.hef.base import PrescriptionHeuristic
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
        make_option('--threads', action='store', dest='thread_count', default=HEF_THREAD_COUNT,
            type='int', metavar='COUNT', help='Run in COUNT threads'),
        make_option('-n', '--new', action='store_true', dest='new'),
        )

    def handle(self, *args, **options):
        if options['list']:
            for h in BaseHeuristic.get_all():
                print h.short_name
            return
        elif args:
            BaseHeuristic.generate_by_name(name_list=args, thread_count=options['thread_count'])
        else: # Generate all
            BaseHeuristic.generate_all(thread_count=options['thread_count'])
    