#!/usr/bin/env python
'''
                                  ESP Health
                         Notifiable Diseases Framework
                           Patient Report Generator

Given a patient's medical record number (MRN), prints all patient's labs, 
encounters, prescriptions, heuristic events, and disease cases.
'''


import optparse
import sys

from esp.emr.models import Patient
from esp.emr.models import LabResult
from esp.emr.models import Encounter
from esp.emr.models import Prescription
from esp.hef.models import HeuristicEvent
from esp.nodis.models import Case


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
    

def patient_summary(patient, options):
    cases = patient.case_set.all()
    for c in cases:
        values = {'id': patient.pk, 'condition': c.condition, 'date': c.date}
        if options.phi:
            values['mrn'] = patient.mrn
            values['name'] = patient.name
            print '%(mrn)-14s    %(name)-25s    %(condition)-15s    %(date)-10s' % values
        else:
            print '%(id)-10s    %(condition)-15s    %(date)-10s' % values
    if not cases:
        values = {'id': patient.pk, 'condition': 'NONE', 'date': '-'}
        if options.phi:
            values['mrn'] = patient.mrn
            values['name'] = patient.name
            print '%(mrn)-14s    %(name)-25s    %(condition)-15s    %(date)-10s' % values
        else:
            print '%(id)-10s    %(condition)-15s    %(date)-10s' % values


def main():
    usage_str = '%prog [-m|-d] PATIENT'
    parser = optparse.OptionParser(usage_str)
    parser.add_option('-m', action='store_true', dest='mrn', default=False, 
        help='Lookup patient by MRN (default)')
    parser.add_option('-d', action='store_true', dest='dbid', default=False, 
        help='Lookup patient by database ID number')
    parser.add_option('-s', '--summary', action='store_true', dest='summary', 
        default=False,  help='Print summary of cases for each patient')
    parser.add_option('--phi', action='store_true', dest='phi', default=False, 
        help='Include PHI in report')
    (options, args) = parser.parse_args()
    if not args:
        parser.print_help()
        sys.exit()
    if options.summary:
        values = {'mrn': 'MRN', 'name': 'NAME', 'condition': 'CONDITION', 'date': 'DATE', 'id': 'Patient #'}
        print '-' * 80
        if options.phi:
            print '%(mrn)-14s    %(name)-25s    %(condition)-15s    %(date)-10s' % values
        else:
            print '%(id)-10s    %(condition)-15s    %(date)-10s' % values
        print '-' * 80
    for identifier in args:
        if options.dbid:
            try:
                patient = Patient.objects.get(pk=identifier)
            except Patient.DoesNotExist:
                print >> sys.stderr, 'ERROR:  No patient found with database ID # %s.' % identifier
                continue
        else: # Look up MRN
            try:
                patient = Patient.objects.get(mrn=identifier)
            except Patient.DoesNotExist:
                print >> sys.stderr, 'ERROR:  No patient found with MRN "%s".' % identifier
                continue
        if options.summary:
            patient_summary(patient=patient, options=options)
        else:
            patient_report(patient=patient, options=options)


if __name__ == '__main__':
    main()
