#!/usr/bin/env python
'''
                                  ESP Health
                         Notifiable Diseases Framework
Pluggable Report Generator


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
from ESP.hef.base import BaseHeuristic
from ESP.nodis.base import Report

    
class Command(BaseCommand):
    
    help = 'Run a report'
    
    args = 'NAME'
    
    option_list = BaseCommand.option_list + (
        make_option('--list', action='store_true', dest='list', 
            help='List available reports'),
        )

    def handle(self, *args, **options):
        if options['list']:
            for rep in Report.get_all():
                print rep.short_name
            return
        assert len(args) == 1 # Command requires one and only one report name
        report_name = args[0]
        all_reports = {}
        for rep in Report.get_all():
            all_reports[rep.short_name] = rep
        assert report_name in all_reports # Is this a valid report name?
        report_object = all_reports[report_name]   
        report_object.run()