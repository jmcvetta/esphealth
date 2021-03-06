#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import datetime
from optparse import OptionParser

from ESP.utils.utils import date_from_str, str_from_date, log, days_in_interval, make_date_folders
from ESP.conf.common import EPOCH
from ESP.vaers.models import EncounterEvent, LabResultEvent, PrescriptionEvent, AllergyEvent, HL7_MESSAGES_DIR

from heuristics import  diagnostic_heuristics, lab_heuristics, prescription_heuristics, allergy_heuristics
from ESP.vaers.rules import define_active_rules

            
usage_msg = """
Usage: python %prog -b[egin_date] -e[nd_date] 
{ [-d --detect],[-r --reports] } | [-f --full]

 One or more of '-l', '-p', '-g', '-f', '-d' or '-a' must be specified.
    
    DATE variables are specified in this format: 'YYYYMMDD'

"""




def main():

    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(1)

    parser = OptionParser(usage=usage_msg)
    parser.add_option('-b', '--begin', dest='begin_date', default=str_from_date(yesterday))
    parser.add_option('-e', '--end', dest='end_date', default=str_from_date(today))

    parser.add_option('-l', '--lx', action='store_true', dest='lx', help='Run Lab Results Heuristics')
    parser.add_option('-d', '--diagnostics', action='store_true', dest='diagnostics', 
                      help='Run Diagnostics Heuristics')
    parser.add_option('-p', '--rx', action='store_true', dest='rx',help='Run Prescription Heuristics')
    parser.add_option('-g', '--allergy', action='store_true', dest='allergy',help='Run Allergy Heuristics')
    
    parser.add_option('-a', '--all', action='store_true', dest='all')

    parser.add_option('-c', '--create', action='store_true', dest='create')

    
    options, args = parser.parse_args()
    # clean rules and load them again
    define_active_rules()

    try:
        begin_date = date_from_str(options.begin_date)
        end_date = date_from_str(options.end_date)
    except:
        log.error('Invalid dates')
        sys.exit(-1)
        

    if options.all:
        options.diagnostics = True
        options.lx = True
        options.rx = True
        options.allergy = True

    if not (options.diagnostics or options.lx or options.rx or options.allergy):
        parser.print_help()
        sys.exit(-2)

    if not (options.create or options.reports):
        parser.print_help()
        sys.exit(-3)

    heuristics = []
    if options.diagnostics: heuristics += diagnostic_heuristics()
    if options.lx: heuristics += lab_heuristics()
    if options.rx: heuristics += prescription_heuristics()
    if options.allergy: heuristics += allergy_heuristics()

    if options.create: 
        log.info('Creating and generating events from %s to %s' % (begin_date, end_date))
        for h in heuristics: 
            h.generate(begin_date=begin_date, end_date=end_date) 


if __name__ == '__main__':
    main()
