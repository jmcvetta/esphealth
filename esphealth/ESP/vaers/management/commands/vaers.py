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
from ESP.utils.utils import date_from_str, str_from_date, log, days_in_interval, make_date_folders
from ESP.conf.common import EPOCH
from ESP.vaers.models import EncounterEvent, LabResultEvent, HL7_MESSAGES_DIR, PrescriptionEvent, AllergyEvent

from ESP.vaers.heuristics import  diagnostic_heuristics, lab_heuristics,prescription_heuristics,allergy_heuristics


            
usage_msg = """
Usage: python %prog -b[egin_date] -e[nd_date] 
{[-r --reports] | [-c --create]} | [-a --all]

 One or more of '-l', '-p', '-g', '-d' or '-a' must be specified.
 One or more of '-r' or '-c' must be specified
    
    DATE variables are specified in this format: 'YYYYMMDD'

"""


class Command(BaseCommand):
    #
    # Parse command line options
    #
    option_list = BaseCommand.option_list + (
        make_option('-b', '--begin', dest='begin_date', default=str_from_date(TODAY)),
        make_option('-e', '--end', dest='end_date', default=str_from_date(TODAY-datetime.timedelta(1))), # Yesterday
        make_option('-l', '--lx', action='store_true', dest='lx', help='Run Lab Results Heuristics'),
        make_option('-d', '--diagnostics', action='store_true', dest='diagnostics', 
                          help='Run Diagnostics Heuristics'),
        make_option('-p', '--rx', action='store_true', dest='rx',help='Run Prescription Heuristics'),
        make_option('-g', '--allergy', action='store_true', dest='allergy',help='Run Allergy Heuristics'),
        make_option('-a', '--all', action='store_true', dest='all'),
        make_option('-c', '--create', action='store_true', dest='create'),
        make_option('-r', '--reports', action='store_true', dest='reports'),
        
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
            options['rx'] = True
            options['allergy'] = True
            
    
        if not ( options['diagnostics'] or options['lx'] or options['rx'] or options['allergy']):
            raise CommandError('Must specify  --diagnosics, --lx, --rx or --all')
    
        if not (options['create'] or options['reports']):
            raise CommandError('Must specify --create or --reports')
    
        heuristics = []
        if options['diagnostics']: heuristics += diagnostic_heuristics()
        if options['lx']: heuristics += lab_heuristics()
        if options['rx']: heuristics += prescription_heuristics()
        if options['allergy']: heuristics += allergy_heuristics()
    
    
        if options['create']: 
            log.info('Creating and generating events from %s to %s' % (begin_date, end_date))
            for h in heuristics: h.generate(begin_date=begin_date, end_date=end_date) 
    
            
        if options['reports']:
            folder = make_date_folders(begin_date, end_date, root=HL7_MESSAGES_DIR)
    
            def produce_reports(queryset):
                events = queryset.filter(date__gte=begin_date, date__lte=end_date)
                log.info('Producing HL7 reports for %s events' % (events.count()))
                for event in events: event.save_hl7_message_file(folder=folder)
                
            if options['diagnostics']: produce_reports(EncounterEvent.objects.all())
            if options['lx']: produce_reports(LabResultEvent.objects.all())
            if options['rx']: produce_reports(PrescriptionEvent.objects.all())
            if options['allergy']: produce_reports(AllergyEvent.objects.all())
    