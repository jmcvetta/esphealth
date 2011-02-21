#!/usr/bin/python
# -*- coding: utf-8 -*-

import optparse

from esp.conf.common import EPOCH
from esp.vaers.models import EncounterEvent, LabResultEvent
from esp.utils.utils import date_from_str
from esp import settings

USAGE_MSG = '''\
%prog [options]

\t- One or more of '-lx', '-f', '-d' or '-a' must be specified.
\t- DATE variables are specified in this format: 'YYYYMMDD'
'''

def main():
    parser = optparse.OptionParser(usage=USAGE_MSG)
    
    parser.add_option('-i', '--interval', action='store', dest='gap', type='int',
                      help='Maximum interval between event and immunization, in days')

    parser.add_option('-f', '--fever', action='store_true', dest='fever', help='Fever Events Reports')
    parser.add_option('-l', '--lx', action='store_true', dest='lx', help='Lab Results Reports')
    parser.add_option('-d', '--diagnostics', action='store_true', dest='icd9', help='Icd9 Reports')
    parser.add_option('-a', '--all', action='store_true', dest='all', help='All reports')


    parser.add_option('--begin', action='store', dest='begin', type='string', 
                      metavar='DATE', help='Only events occurring after date')
    parser.add_option('--end', action='store', dest='end', type='string', 
                      metavar='DATE', help='Only events occurring before date')
    (options, args) = parser.parse_args()
    

    begin_date = options.begin and date_from_str(options.begin) or None
    end_date = options.end and date_from_str(options.end) or None


    if options.all:
        options.fever = True
        options.icd9 = True
        options.lx = True

    if not (options.fever or options.icd9 or options.lx):
        parser.print_help()
        import sys
        sys.exit()

    if options.fever: 
        EncounterEvent.write_fever_clustering_report(begin_date=begin_date, end_date=end_date)
    if options.icd9: 
        EncounterEvent.write_diagnostics_clustering_report(begin_date=begin_date, end_date=end_date)
    if options.lx: 
        LabResultEvent.write_clustering_report(begin_date=begin_date, end_date=end_date)



if __name__ == '__main__':
    main()



