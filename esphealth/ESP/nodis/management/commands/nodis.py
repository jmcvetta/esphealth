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
from ESP.hef.base import BaseHeuristic
from ESP.nodis.base import DiseaseDefinition
from ESP.utils.utils import wait_for_threads

    
class Command(BaseCommand):
    
    help = 'Generate Nodis cases'
    
    args = '[conditions]'
    
    option_list = BaseCommand.option_list + (
        make_option('--list', action='store_true', dest='list', 
            help='List available diseases'),
        make_option('--dependencies', action='store_true', dest='dependencies', 
            help='Generate dependencies before generating diseases')
        )

    def handle(self, *args, **options):
        if options['list']:
            for disease in DiseaseDefinition.get_all():
                print disease.short_name
            return 
        disease_list = set()
        for short_name in args:
            disease_list.add(DiseaseDefinition.get_by_name(short_name))
        if not args:
            disease_list = DiseaseDefinition.get_all()
        if options['dependencies']:
            log.info('Generating all dependencies before generating cases of disease')
            #
            # Build a set of all distinct dependencies, so each one is run
            # only once.
            #
            dependencies = set()
            for disease in disease_list():
                dependencies |= set(disease.dependencies)
            for dep in dependencies:
                log.debug('Dependency: %s' % dep)
            BaseHeuristic.generate_all(heuristic_list=dependencies)
        funcs = [disease.generate for disease in disease_list]
        wait_for_threads(funcs)