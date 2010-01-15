'''
                                  ESP Health
                         Notifiable Diseases Framework
                                 Case Reporter

@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL - http://www.gnu.org/licenses/lgpl-3.0.txt

--------------------------------------------------------------------------------
EXIT CODES

10     Keyboard interrupt
11     No cases found matching query
101    Unrecognized condition
102    Unrecognized case status
103    Unrecognized template name
'''


CASE_REPORT_OUTPUT_FOLDER = '/tmp/'
CASE_REPORT_TEMPLATE = 'odh_hl7.txt'
CASE_REPORT_FILENAME_FORMAT = '%(timestamp)s-%(serial)s.hl7'


import optparse
import sys
import pprint
import os
import cStringIO as StringIO
import datetime
import re

from django.db.models import Q
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.template.loader import get_template

from ESP.utils.utils import log
from ESP.utils.utils import log_query
from ESP.emr.models import LabResult
from ESP.emr.models import Encounter
from ESP.emr.models import Prescription
from ESP.emr.models import Immunization
from ESP.nodis import defs
from ESP.nodis.models import Condition
from ESP.nodis.models import Case
from ESP.nodis.models import STATUS_CHOICES



def main():
    report_conditions = [] # Names of conditions for which we will export cases
    timestamp = datetime.datetime.now().strftime('%Y-%b-%d-%H:%M:%s')
    serial_number = 0 # Serial number of case reported for this timestamp
    filename_values = { 
        # Used to populate file name template -- serial is updated below
        'timestamp': timestamp,
        'serial': serial_number,
        }
#
    # Parse command line for options
    #
    all_conditions = Condition.list_all_condition_names()
    all_conditions.sort()
    usage_msg = '%prog [options] condition(s)\n'
    usage_msg += '\n'
    usage_msg += "    Conditions can be 'all' or one of the following:\n"
    usage_msg += '        ' + ', '.join(all_conditions)
    parser = optparse.OptionParser(usage=usage_msg)
    parser.add_option('-o', action='store', metavar='FOLDER', dest='output_folder',
        default=CASE_REPORT_OUTPUT_FOLDER, help='Output case report file(s) to FOLDER')
    parser.add_option('-t', action='store', metavar='TEMPLATE', dest='template', 
        default=CASE_REPORT_TEMPLATE, help='Use TEMPLATE to generate HL7 messages')
    parser.add_option('-f', action='store', dest='format', metavar='FORMAT', default=CASE_REPORT_FILENAME_FORMAT,
        help='Create file names using FORMAT.  Default: %s' % CASE_REPORT_FILENAME_FORMAT)
    parser.add_option('--stdout', action='store_true', dest='stdout', 
        help='Print output to STDOUT (no files created)')
    parser.add_option('--individual', action='store_false', dest='one_file',
        default=False, help='Export each cases to an individual file (default)')
    parser.add_option('--one-file', action='store_true', dest='one_file',
        default=False, help='Export all cases to a one file')
    parser.add_option('--status', action='store', dest='status', default='Q',
        help='Export only cases with this status ("Q" by default)')
    parser.add_option('--no-sent-status', action='store_false', dest='sent_status', default=True,
        help='Do NOT set case status to "S" after export')
    parser.add_option('--sample', action='store', dest='sample', metavar='NUM', type='int', 
        help='Report only first NUM cases matching criteria; do NOT set status to sent')
    options, args = parser.parse_args()
    if options.sample: # '--sample' implies '--no-sent-status'
        options.sent_status = False
    if options.one_file:
        output_file = StringIO.StringIO()
    #
    # Sanity check options
    #
    for a in args:
        if a.lower() == 'all':
            report_conditions = all_conditions
            break
        if a in all_conditions:
            report_conditions.append(a)
        else:
            print >> sys.stderr
            print >> sys.stderr, 'Unrecognized condition: "%s".  Aborting.' % a
            print >> sys.stderr
            print >> sys.stderr, 'Valid conditions are:'
            print >> sys.stderr, '    --------'
            print >> sys.stderr, '    all (reports all conditions below)'
            print >> sys.stderr, '    --------'
            for con in all_conditions:
                print >> sys.stderr, '    %s' % con
            sys.exit(101)
    log.debug('conditions: %s' % report_conditions)
    valid_status_choices = [item[0] for item in STATUS_CHOICES]
    if options.status not in valid_status_choices:
            print >> sys.stderr
            print >> sys.stderr, 'Unrecognized status: "%s".  Aborting.' % options.status
            print >> sys.stderr
            print >> sys.stderr, 'Valid status choices are:'
            for stat in valid_status_choices:
                print >> sys.stderr, '    %s' % stat
            sys.exit(102)
    log.debug('status: %s' % options.status)
    template_name = os.path.join('nodis', 'report', options.template)
    try:
        get_template(template_name)
    except TemplateDoesNotExist:
        print >> sys.stderr
        print >> sys.stderr, 'Unrecognized template name: "%s".  Aborting.' % options.template
        print >> sys.stderr
        sys.exit(103)
    #
    # Generate case query
    #
    q_obj = Q(condition__in=report_conditions)
    q_obj = q_obj & Q(status=options.status)
    cases = Case.objects.filter(q_obj).order_by('pk')
    if not cases:
        print 
        print 'No cases found matching your specifications.  No output generated.'
        print
        sys.exit(11)
    log_query('Filtered cases', cases)
    if options.sample: # Report only a single, random sample case
        cases = cases[0:options.sample]
    #
    # Build message string
    #
    for case in cases:
        serial_number += 1 # Increment serial number for this case
        matched_labs = []
        matched_encounters = []
        matched_prescriptions = []
        matched_immunizations = []
        for event in case.events.all():
            content = event.content_object
            if isinstance(content, LabResult):
                matched_labs.append(content)
            if isinstance(content, Encounter):
                matched_encounters.append(content)
            if isinstance(content, Prescription):
                matched_prescriptions.append(content)
            if isinstance(content, Immunization):
                matched_immunizations.append(content)
        labs = case.lab_results.all()
        pprint.pprint(case.events.all())
        # Case.events is blank=False, so this shouldn't ever thrown an index error.
        provider = case.events.all().order_by('date')[0].content_object.provider
        values = {
            'case': case,
            'patient': case.patient,
            'provider': provider,
            'matched_labs': matched_labs,
            'matched_encounters': matched_encounters,
            'matched_prescriptions': matched_prescriptions,
            'matched_immunizations': matched_immunizations,
            #'all_labs': labs,
            #'all_encounters': case.encounters.all(),
            #'all_prescriptions': case.medications.all(),
            #'all_immunizations': case.immunizations.all(),
            'serial_number': serial_number,
            }
        log.debug('values for template: \n%s' % pprint.pformat(values))
        case_report = render_to_string(template_name, values)
        # Remove blank lines -- allows us to have neater templates
        case_report = re.sub("\n\s*\n*", "\n", case_report)
        #
        # Report message
        #
        log.debug('Message to report:\n%s' % case_report)
        if options.stdout: # Print case reports to STDOUT
            log.debug('Printing message to stdout')
            print case_report
        elif options.one_file: # All reports in one big file
            log.debug('Adding case #%s report to single output file' % case.pk)
            output_file.write(case_report)
            pass
        else: # Produce an individual file for every case report [default]
            filename_values['serial'] = serial_number
            filename = options.format % filename_values
            filepath = os.path.join(options.output_folder, filename)
            file = open(filepath, 'w')
            file.write(case_report)
            file.close()
            log.info('Wrote case #%s report to file: %s' % (case.pk, filepath))
        if options.sent_status:
            case.status = 'S'
            case.save()
            log.debug("Set status to 'S' for case #%s" % case.pk)
    if options.one_file:
        filename = options.format % filename_values
        filepath = os.path.join(options.output_folder, filename)
        file = open(filepath, 'w')
        file.write(output_file.getvalue())
        file.close()
        # serial_number is equal to the number of cases reported
        log.info('Wrote single report for all %s cases to file: %s' % (serial_number, filepath))



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print >> sys.stderr
        print >> sys.stderr, 'Keyboard interrupt.  Aborting.'
        print >> sys.stderr
        sys.exit(10)
        
