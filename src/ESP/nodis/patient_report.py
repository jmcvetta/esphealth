#!/usr/bin/env python2.5
'''
                                  ESP Health
                         Notifiable Diseases Framework
                           Patient Report Generator

Given a patient's medical record number (MRN), prints all patient's labs, 
encounters, prescriptions, heuristic events, and disease cases.
'''


import optparse
import sys

from ESP.emr.models import Patient
from ESP.emr.models import LabResult
from ESP.emr.models import Encounter
from ESP.emr.models import Prescription
from ESP.hef.models import HeuristicEvent
from ESP.nodis.models import Case


def patient_report(patient, options):
    print '~' * 80
    print '~' + ' ' * 78 + '~'
    print '~' + 'PATIENT REPORT'.center(78) + '~'
    print '~' + ' ' * 78 + '~'
    line = 'Patient #: %s' % patient.pk
    line = '~' + line.center(78) + '~'
    print line
    if options.phi: # Print patient identification info at top of report
        line = 'MRN: %s' % patient.mrn
        line = '~' + line.center(78) + '~'
        print line 
        line = 'NAME: %s' % patient.name
        line = '~' + line.center(78) + '~'
        print line # Print patient's MRN at top of report
    print '~' + ' ' * 78 + '~'
    print '~' * 80
    models_to_report = [  # Order in which info will be printed
        Case,
        HeuristicEvent,
        Encounter,
        LabResult,
        Prescription,
        ]
    titles = {
        Case: 'CASES',
        HeuristicEvent: 'HEURISTIC EVENTS',
        Encounter: 'ENCOUNTERS',
        LabResult: 'LAB RESULTS',
        Prescription: 'PRESCRIPTIONS',
        }
    for model in models_to_report:
        objects = model.objects.filter(patient=patient).order_by('-date')
        if objects:
            print
            print '=' * 80
            print titles[model].center(80)
            print '=' * 80
            print model.str_line_header()
            print '-' * 80
        for obj in objects:
            print obj.str_line()
    print # Spacing before next report
    print
    print
    
    


def main():
    usage_str = '%prog [-m|-d] PATIENT'
    parser = optparse.OptionParser(usage_str)
    parser.add_option('-m', action='store_true', dest='mrn', default=False, 
        help='Lookup patient by MRN (default)')
    parser.add_option('-d', action='store_true', dest='dbid', default=False, 
        help='Lookup patient by database ID number')
    parser.add_option('--phi', action='store_true', dest='phi', default=False, 
        help='Include PHI in report')
    (options, args) = parser.parse_args()
    for identifier in args:
        if options.dbid:
	        try:
	            patient = Patient.objects.get(pk=identifier)
	        except Patient.DoesNotExist:
	            print >> sys.stderr
	            print >> sys.stderr, 'ERROR:  No patient found with database ID # %s.' % identifier
	            print >> sys.stderr
	            continue
        else: # Look up MRN
	        try:
	            patient = Patient.objects.get(mrn=identifier)
	        except Patient.DoesNotExist:
	            print >> sys.stderr
	            print >> sys.stderr, 'ERROR:  No patient found with MRN "%s".' % identifier
	            print >> sys.stderr
	            continue
        patient_report(patient=patient, options=options)


if __name__ == '__main__':
    main()