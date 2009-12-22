#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import datetime
from optparse import OptionParser

from ESP.utils.utils import date_from_str, str_from_date, log, days_in_interval, timeit
from ESP.conf.common import EPOCH
from ESP.ss.models import Site


import reports
from heuristics import syndrome_heuristics
from utils import make_non_specialty_clinics

            
usage_msg = """espss.py
Usage: python ss/main.py -b[start_date as 20090101] -e[end_date] 
{ [-d --detect],[-r --reports] } | [-f --full]
[-c --consolidate]"""




def main():

    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(1)

    parser = OptionParser(usage=usage_msg)
    parser.add_option('-b', '--begin', dest='begin_date', default=EPOCH.strftime('%Y%m%d'))
    parser.add_option('-e', '--end', dest='end_date', default=today.strftime('%Y%m%d'))
    parser.add_option('-i', '--individual', dest='individual', action='store_true')
    parser.add_option('-s', '--syndrome', dest='syndrome', default='all')
    parser.add_option('-c', '--consolidate', action='store_true', dest='consolidate')
    parser.add_option('-d', '--detect', action='store_true', dest='detect')
    parser.add_option('-r', '--reports', action='store_true', dest='reports')
    parser.add_option('-f', '--full', action='store_true', dest='full')

    
    options, args = parser.parse_args()

    try:
        begin_date = date_from_str(options.begin_date)
        end_date = date_from_str(options.end_date)
    except:
        log.error('Invalid dates')
        sys.exit(-2)
        
    heuristics = []
    if options.syndrome == 'all':
        heuristics = syndrome_heuristics().values()
    else:
        heuristic = syndrome_heuristics().get(options.syndrome, None)
        if heuristic: heuristics.append(heuristic)


    if options.full:
        options.detect = True
        options.reports = True

    if options.detect:
        if not Site.objects.count(): make_non_specialty_clinics()
        for heuristic in heuristics:
            log.info('Generating events for %s' % heuristic.name)
            heuristic.generate_events(begin_date=begin_date, end_date=end_date)
            
        
    if options.reports:
        if options.consolidate:
            reports.all_encounters_report(begin_date, end_date)
            for heuristic in heuristics:
                log.info('Creating %s reports, %s to %s' % (heuristic.name, begin_date, end_date))
                heuristic.make_reports(begin_date, end_date)
        else:
            for day in days_in_interval(begin_date, end_date):
                reports.all_encounters_report(day, day)
                for heuristic in heuristics:
                    log.info('Creating %s reports for %s' % (heuristic.name, day))
                    heuristic.make_reports(day, day)


    if options.individual:
        reports.all_encounters_report(begin_date, end_date)


    if not (options.detect or options.reports or options.individual):
        print usage_msg
        sys.exit(-1)



if __name__ == '__main__':
    main()
