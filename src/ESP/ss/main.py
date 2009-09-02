#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import datetime
from optparse import OptionParser

from ESP.utils.utils import date_from_str
from ESP.utils.utils import log

import reports
from heuristics import syndrome_heuristics


            
usage_msg = """espss.py
Usage: python ss/main.py -b[start_date as 20090101] -e[end_date] [-f, --find-events] [-r --reports]"""

def main():

    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(1)

    parser = OptionParser(usage=usage_msg)
    parser.add_option('-b', '--begin', dest='begin_date', default=yesterday.strftime('%Y%m%d'))
    parser.add_option('-e', '--end', dest='end_date', default=today.strftime('%Y%m%d'))
    parser.add_option('-f', '--find-events', action='store_true', dest='events')
    parser.add_option('-r', '--reports', action='store_true', dest='reports')
    parser.add_option('-c', '--encounter-counts', action='store_true', dest='total_counts')
    

    options, args = parser.parse_args()

    

    try:
        begin_date = date_from_str(options.begin_date)
        end_date = date_from_str(options.end_date)
    except:
        log.error('Invalid dates')
        sys.exit(-2)
        


        
    if options.events:
        for heuristic in syndrome_heuristics().values():
            log.info('Generating events for %s' % heuristic.heuristic_name)
            heuristic.generate_events()
            
    if options.reports:
        current_day = begin_date
        log.info('Creating reports from %s until %s' % (current_day, end_date))
        while current_day < end_date:
            log.info('Creating reports for %s' % current_day)
            reports.day_report(current_day)
            current_day += datetime.timedelta(1)

    if options.total_counts:
        log.info('Creating Encounter Count report for %s' % begin_date)
        reports.total_residential_encounters_report(begin_date)
        


    if not (options.events or options.reports or options.total_counts):
        print usage_msg
        sys.exit(-1)



if __name__ == '__main__':
    main()
