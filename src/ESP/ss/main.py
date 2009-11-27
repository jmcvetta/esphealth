#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import datetime
from optparse import OptionParser

from ESP.utils.utils import date_from_str, str_from_date, log
from ESP.conf.common import EPOCH
from ESP.ss.models import Site


import reports
from heuristics import syndrome_heuristics
from utils import make_non_specialty_clinics

            
usage_msg = """espss.py
Usage: python ss/main.py -b[start_date as 20090101] -e[end_date] [-f, --find-events] [-r --reports] [-c --consolidate]"""



def main():

    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(1)

    parser = OptionParser(usage=usage_msg)
    parser.add_option('-b', '--begin', dest='begin_date', default=EPOCH.strftime('%Y%m%d'))
    parser.add_option('-e', '--end', dest='end_date', default=today.strftime('%Y%m%d'))
    parser.add_option('-s', '--syndrome', dest='syndrome', default='all')
    parser.add_option('-c', '--consolidate', action='store_true', dest='consolidate')
    parser.add_option('-f', '--find-events', action='store_true', dest='events')
    parser.add_option('-r', '--reports', action='store_true', dest='reports')

    
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

    if options.events:
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
            day = begin_date
            while day <= end_date:
                reports.all_encounters_report(day, day)
                for heuristic in heuristics:
                    log.info('Creating %s reports for %s' % (heuristic.name, day))
                    heuristic.make_reports(day, day)
                day += datetime.timedelta(1)

                

        
        


    if not (options.events or options.reports or options.total_counts):
        print usage_msg
        sys.exit(-1)



if __name__ == '__main__':
    main()
