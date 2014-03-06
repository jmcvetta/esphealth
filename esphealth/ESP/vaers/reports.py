#!/usr/bin/python
# -*- coding: utf-8 -*-

import optparse

from ESP.conf.common import EPOCH
from ESP.vaers.models import EncounterEvent, LabResultEvent, PrescriptionEvent, AllergyEvent, ProblemEvent, HospProblemEvent
from ESP.utils.utils import date_from_str
from ESP import settings

USAGE_MSG = '''\
%prog [options]

\t- One or more of '-lx', '-f', '-d', '-p', 'g' or '-a' must be specified.
\t- DATE variables are specified in this format: 'YYYYMMDD'
'''

def main():
    parser = optparse.OptionParser(usage=USAGE_MSG)
    
    parser.add_option('-i', '--interval', action='store', dest='gap', type='int',
                      help='Maximum interval between event and immunization, in days')

    parser.add_option('-l', '--lx', action='store_true', dest='lx', help='Lab Results Reports')
    parser.add_option('-d', '--diagnostics', action='store_true', dest='dx_code', help='dx_code Reports')
    parser.add_option('-p', '--problems', action='store_true', dest='prob',help='Problem Reports')
    parser.add_option('-h', '--hproblems', action='store_true', dest='hprob',help='Hospital Problem Reports')
    parser.add_option('-r', '--rx', action='store_true', dest='rx',help='Prescription Reports')
    parser.add_option('-g', '--allergy', action='store_true', dest='allergy',help='Allergy Reports')
    
    parser.add_option('-a', '--all', action='store_true', dest='all', help='All reports')
     

    parser.add_option('--begin', action='store', dest='begin', type='string', 
                      metavar='DATE', help='Only events occurring after date')
    parser.add_option('--end', action='store', dest='end', type='string', 
                      metavar='DATE', help='Only events occurring before date')
    (options, args) = parser.parse_args()
    

    begin_date = options.begin and date_from_str(options.begin) or None
    end_date = options.end and date_from_str(options.end) or None


    if options.all:
        options.dx_code = True
        options.lx = True
        options.rx = True
        options.allergy = True
        options.prob = True
        options.hprob = True
        
    if not ( options.dx_code or options.lx or options.rx or options.allergy or options.prob or options.hprob):
        parser.print_help()
        import sys
        sys.exit()

    if options.dx_code: 
        EncounterEvent.write_diagnostics_clustering_report(begin_date=begin_date, end_date=end_date)
    if options.lx: 
        LabResultEvent.write_clustering_report(begin_date=begin_date, end_date=end_date)
    if options.rx: 
        PrescriptionEvent.write_clustering_report(begin_date=begin_date, end_date=end_date)
    if options.allergy: 
        ProblemEvent.write_clustering_report(begin_date=begin_date, end_date=end_date)
    if options.prob: 
        HospProblemEvent.write_clustering_report(begin_date=begin_date, end_date=end_date)
    if options.hprob: 
        AllergyEvent.write_clustering_report(begin_date=begin_date, end_date=end_date)


if __name__ == '__main__':
    main()



