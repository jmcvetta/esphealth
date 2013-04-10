#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import datetime
import pprint

from optparse import OptionParser
from optparse import make_option

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from ESP.settings import TODAY
from ESP.utils.utils import date_from_str, str_from_date, log

from ESP.vaers.heuristics import  diagnostic_heuristics, lab_heuristics,prescription_heuristics,allergy_heuristics,problem_heuristics,hospprob_heuristics
            
usage_msg = """
Usage: python %prog -b[egin_date] -e[nd_date] 

 One or more of '-l', '-p', '-g', '-d' or '-a' must be specified, and '-c' must be specified
    
 DATE variables are specified in this format: 'YYYYMMDD'

"""


class Command(BaseCommand):
    #
    # Parse command line options
    #
    option_list = BaseCommand.option_list + (
        make_option('-b', '--begin', dest='begin_date', default=str_from_date(TODAY-datetime.timedelta(7))), #last week
        make_option('-e', '--end', dest='end_date', default=str_from_date(TODAY)), 
        make_option('-l', '--lx', action='store_true', dest='lx', help='Run Lab Results Heuristics'),
        make_option('-d', '--diagnostics', action='store_true', dest='diagnostics', 
                          help='Run Diagnostics Heuristics'),
        make_option('-p', '--rx', action='store_true', dest='rx',help='Run Prescription Heuristics'),
        make_option('-g', '--allergy', action='store_true', dest='allergy',help='Run Allergy Heuristics'),
        make_option('-r', '--problem', action='store_true', dest='problem',help='Run Problem Heuristics'),
        make_option('-o', '--hospprob', action='store_true', dest='hospprob',help='Run Hospital Problem Heuristics'),
        make_option('-a', '--all', action='store_true', dest='all'),
        make_option('-c', '--create', action='store_true', dest='create')
        
        )
    
    help = 'VAERS'
    
    def handle(self, *args, **options):
        try:
            begin_date = date_from_str(options['begin_date'])
            end_date = date_from_str(options['end_date'])
        except:
            log.error('Invalid dates')
            sys.exit(-1)
            
    
        if options['all']:
            options['diagnostics'] = True
            options['lx'] = True
            #options['rx'] = True 
            #options['allergy'] = True -- there is currently no allergy data and this has not been extensively tested
            #options['problem'] = True 
            #options['hospprob'] = True 
            
    
        if not ( options['diagnostics'] or options['lx'] or options['rx'] or options['allergy'] or options['problem'] or options['hospprob']):
            raise CommandError('Must specify  --diagnosics, --lx, --rx, --allergy, --problem, --hospprob or --all')
    
        if not (options['create']):
            raise CommandError('Must specify --create')
    
        heuristics = []
        if options['diagnostics']: heuristics += diagnostic_heuristics()
        if options['lx']: heuristics += lab_heuristics()
        if options['rx']: heuristics += prescription_heuristics()
        if options['allergy']: heuristics += allergy_heuristics()
        if options['problem']: heuristics += problem_heuristics()
        if options['hospprob']: heuristics += hospprob_heuristics()
    
    
        if options['create']: 
            log.info('Creating and generating events from %s to %s' % (begin_date, end_date))
            for h in heuristics: h.generate(begin_date=begin_date, end_date=end_date) 
    
            
    