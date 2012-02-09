#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import datetime
from optparse import OptionParser

from ESP.utils.utils import date_from_str, str_from_date, log, days_in_interval, make_date_folders
from ESP.conf.common import EPOCH
from ESP.vaers.models import EncounterEvent, LabResultEvent, HL7_MESSAGES_DIR

from heuristics import fever_heuristic, diagnostic_heuristics, lab_heuristics


            
usage_msg = """
Usage: python %prog -b[egin_date] -e[nd_date] 
{ [-d --detect],[-r --reports] } | [-f --full]

 One or more of '-lx', '-f', '-d' or '-a' must be specified.
    
    DATE variables are specified in this format: 'YYYYMMDD'

"""




def main():

    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(1)

    parser = OptionParser(usage=usage_msg)
    parser.add_option('-b', '--begin', dest='begin_date', default=str_from_date(yesterday))
    parser.add_option('-e', '--end', dest='end_date', default=str_from_date(today))

    parser.add_option('-f', '--fever', action='store_true', dest='fever', help='Run Fever Heuristics')
    parser.add_option('-l', '--lx', action='store_true', dest='lx', help='Run Lab Results Heuristics')
    parser.add_option('-d', '--diagnostics', action='store_true', dest='diagnostics', 
                      help='Run Diagnostics Heuristics')
    parser.add_option('-a', '--all', action='store_true', dest='all')

    parser.add_option('-c', '--create', action='store_true', dest='create')
    parser.add_option('-r', '--reports', action='store_true', dest='reports')

    
    options, args = parser.parse_args()

    try:
        begin_date = date_from_str(options.begin_date)
        end_date = date_from_str(options.end_date)
    except:
        log.error('Invalid dates')
        sys.exit(-1)
        

    if options.all:
        options.fever = True
        options.diagnostics = True
        options.lx = True

    if not (options.fever or options.diagnostics or options.lx):
        parser.print_help()
        sys.exit(-2)

    if not (options.create or options.reports):
        parser.print_help()
        sys.exit(-3)

    heuristics = []
    if options.fever: heuristics.append(fever_heuristic())
    if options.diagnostics: heuristics += diagnostic_heuristics()
    if options.lx: heuristics += lab_heuristics()
    # TODO issue 344 add more for rx heuristics and allergy heuristics


    if options.create: 
        log.info('Creating and generating events from %s to %s' % (begin_date, end_date))
        for h in heuristics: h.generate(begin_date=begin_date, end_date=end_date) 

        
    if options.reports:
        folder = make_date_folders(begin_date, end_date, root=HL7_MESSAGES_DIR)

        def produce_reports(queryset):
            events = queryset.filter(date__gte=begin_date, date__lte=end_date)
            log.info('Producing HL7 reports for %s events' % (events.count()))
            for event in events: event.save_hl7_message_file(folder=folder)
            

        if options.fever: produce_reports(EncounterEvent.objects.fevers())
        if options.diagnostics: produce_reports(EncounterEvent.objects.icd9_events())
        if options.lx: produce_reports(LabResultEvent.objects.all())

        


if __name__ == '__main__':
    main()
