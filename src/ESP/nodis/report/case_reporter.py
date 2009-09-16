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


import optparse
import sys
import pprint
import os

from django.db.models import Q
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.template.loader import get_template

from ESP.settings import DEFAULT_HL7_TEMPLATE
from ESP.utils.utils import log
from ESP.utils.utils import log_query
from ESP.nodis import defs
from ESP.nodis.core import Condition
from ESP.nodis.models import Case
from ESP.nodis.models import STATUS_CHOICES



def main():
    report_conditions = [] # Names of conditions for which we will export cases
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
    parser.add_option('-o', action='store', metavar='FOLDER', dest='output',
        default=CASE_REPORT_OUTPUT_FOLDER, help='Output case report file(s) to FOLDER')
    parser.add_option('-t', action='store', metavar='TEMPLATE', dest='template', 
        default=CASE_REPORT_TEMPLATE, help='Use TEMPLATE to generate HL7 messages')
    parser.add_option('--individual', action='store_false', dest='one_file',
        default=False, help='Export each cases to an individual file (default)')
    parser.add_option('--one-file', action='store_true', dest='one_file',
        default=False, help='Export all cases to a one file')
    parser.add_option('--status', action='store', dest='status', default='Q',
        help='Export only cases with this status ("Q" by default)')
    parser.add_option('--no-sent-status', action='store_false', dest='sent_status', default=True,
        help='Do NOT set case status to "S" after export')
    options, args = parser.parse_args()
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
    template_name = os.path.join('nodis', 'reports', options.template)
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
    cases = Case.objects.filter(q_obj)
    log_query('Filtered cases', cases)
    if not cases:
        print 
        print 'No cases found matching your specifications.  No output generated.'
        print
        sys.exit(11)
    #
    # Produce output
    #
    if options.one_file:
        raise NotImplementedError('This functionality has not yet been implemented.')
    else:
        for case in cases:
            print render_to_string(template_name, case)
        


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print >> sys.stderr
        print >> sys.stderr, 'Keyboard interrupt.  Aborting.'
        print >> sys.stderr
        sys.exit(10)
        
