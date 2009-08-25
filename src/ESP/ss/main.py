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
    parser.add_option('-f', '--find-events', dest='events', default=False)
    parser.add_option('-r', '--reports', dest='reports', default=True)
    

    options, args = parser.parse_args()

    

    try:
        begin_date = date_from_str(options.begin_date)
        end_date = date_from_str(options.end_date)
    except:
        log.error('Invalid dates')
        sys.exit(-1)

        
        
    if options.events:
        for heuristic in syndrome_heuristics():
            heuristic.generate_events()
            
    if options.reports:
        current_day = begin_date
        while current_day < today:
            reports.day_report(current_day)
            current_day += datetime.timedelta(1)



if __name__ == '__main__':
    main()
