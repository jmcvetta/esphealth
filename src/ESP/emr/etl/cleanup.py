'''
                                  ESP Health
                            EMR ETL Infrastructure
ETL Cleanup Tool


The cleanup tool allows operator to remove from the database records with bad
provenance.  


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory - http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''


#-------------------------------------------------------------------------------
# 
#                               Developer Notes
#
#-------------------------------------------------------------------------------
#
# This script should only be run a single instance at a time, and it should not 
# be able to run at the same time as hef/run.py, nodis/run.py,  load_epic.py or 
# load_hl7.py.  However, right now the code does NOT enforce this.  In the 
# future we will probably want to implement this, perhaps via D-Bus.
#
#-------------------------------------------------------------------------------


#-------------------------------------------------------------------------------
# 
#                                  Exit Codes
#
#-------------------------------------------------------------------------------
#
# 10    Sent cases already bound to bad events
# 11    Permission not given to delete (unsent) cases bound to bad events
# 12    Initial permission to proceed not granted
# 13    Bad command line options
# 14    No matching provenance entries found.  Nothing to do.
#
#-------------------------------------------------------------------------------


import sys
import optparse
import readline # Used behind the scenes by raw_input() for enhanced line editing
import pprint

from django.db.models import Q
from django.contrib.contenttypes.models import ContentType

from ESP.utils.utils import log
from ESP.nodis.models import Case
from ESP.hef.models import HeuristicEvent
from ESP.emr.models import Provenance
from ESP.emr.models import LabResult
from ESP.emr.models import Encounter
from ESP.emr.models import Prescription


def bad_options(msg):
    log.error(msg)
    sys.stderr.write('\n')
    sys.stderr.write(msg)
    sys.stderr.write('\n')
    sys.stderr.write('Exiting now.')
    sys.stderr.write('\n')
    sys.stderr.write('\n')
    sys.exit(13)
    


def main():
    parser = optparse.OptionParser()
    parser.add_option('--status', action='store', dest='status', metavar='STATUS',
        help="Purge records whose provenance status matches STATUS.  Possible " + \
        "values are 'failure' and 'attempted'.", default=None)
    parser.add_option('--provenance', action='store', dest='provenance', metavar='ID', 
        help='Purge records with provenance_id = ID', default=None)
    options, args = parser.parse_args()
    log.debug('options: %s' % pprint.pformat(options))
    if not (options.status or options.provenance):
        bad_options('You must specify either --status or --provenance')
    if (options.status and options.provenance):
        bad_options( 'You cannot specify both --status and --provenance')
    if options.status:
        if not options.status in ['failure', 'attempted']:
            bad_options("Status must be either 'failure' or 'attempted.'")
        print 'Provenance status to be deleted: %s' % options.status
    if options.provenance:
        try:
            int(options.provenance)
        except ValueError:
            bad_options('Provenance ID must be an integer.  However, you supplied "%s".' % options.provenance)
        prov_objs = Provenance.objects.filter(pk=options.provenance)
        log.debug('prov_objs: %s' % prov_objs)
        if not prov_objs:
            bad_options('Unable to locate a provenance record with id %s' % options.provenance)
        print 'Provenance entry to be deleted: %s' % prov_objs[0]
    #
    # Generate a Q object to filter the provenance entries we want to delete
    #
    if options.status:
        prov_stat_q = Q(provenance__status=options.status)
        bad_prov = Provenance.objects.filter(status=options.status)
    else: # options.provenance
        prov_stat_q = Q(provenance__provenance_id=options.provenance)
        bad_prov = Provenance.objects.filter(pk=options.provenance)
    log.debug('prov_stat_q: %s' % prov_stat_q)
    if not bad_prov.count():
        print
        print 'No matching provenance entries found.  Nothing to do.'
        print
        sys.exit(14)
    #
    # Have user confirm script is being run safely
    #
    print
    print 'This script requires exclusive write access to the database.  Please ensure'
    print 'none of the following scripts are running at the same time:'
    print '    emr/etl/load_epic.py'
    print '    emr/etl/load_hl7.py'
    print '    hef/run.py'
    print '    nodis/run.py'
    print
    decision = raw_input('Type OKAY to proceed:\n')
    if not decision == 'OKAY':
        print 'Not okay to proceed.  Exiting now.'
        print
        sys.exit(12)
    #
    # Discover "bad" cases -- those based on events with bad provenance
    #
    record_types = [LabResult, Encounter, Prescription]
    print
    print 'Running safety checks...  (this may take a few minutes)'
    print
    log.debug('Searching for cases with bad provenance.')
    bad_events = None
    rec_type = Prescription
    for rec_type in record_types:
        content_type = ContentType.objects.get_for_model(rec_type)
        bad_records = rec_type.objects.filter(prov_stat_q)
        new_bad_events = HeuristicEvent.objects.filter(content_type=content_type, object_id__in=bad_records)
        try:
            bad_events = bad_events | new_bad_events
        except TypeError:
            bad_events = new_bad_events
    bad_cases = Case.objects.filter(events__in=bad_events)
    sent_bad_cases = bad_cases.filter(status='S')
    log.debug('Found %s unsent cases with bad provenance' % bad_cases.count())
    log.debug('Found %s SENT cases with bad provenance' % sent_bad_cases.count())
    if sent_bad_cases:
        print
        print '!!! NOTICE !!!'
        print
        print 'The following cases, which are bound to one or more events with bad provenance,'
        print 'have ALREADY BEEN SENT to the Department of Public Health.  This situation'
        print 'requires human intervention, and cannot be handled by this script.  Exiting now.'
        print
        for case in sent_bad_cases:
            print case
        sys.exit(10)
    if bad_cases:
        print
        print 'WARNING:'
        print
        print 'The following cases, which have NOT been sent to the Department of Public Health,'
        print 'are bound to to one or more events with bad provenance.'
        print
        for case in bad_cases:
            print case
        print
        decision = raw_input('Please confirm that it is okay to delete these cases by typing DELETE:\n')
        if not decision == 'DELETE':
            print
            print 'You have NOT given permission to delete cases bound to records with bad provenance.'
            print 'Therefore we cannot delete said records, either.  Exiting now.'
            print
            sys.exit(11)
        print 
        print 'Deleting all records and cases with bad provenance.'
    else:
        print 'No cases will be affected by this action.  Deleting all records with bad provenance.'
        print
    print 'Please wait -- this may take a few minutes.'
    print
    for rec_type in record_types:
        to_be_deleted = rec_type.objects.filter(prov_stat_q)
        log.debug('Deleting %s %s records' % (to_be_deleted.count(), rec_type))
        to_be_deleted.delete()
    log.debug('Deleting %s provenance entries' % bad_prov.count())
    bad_prov.delete()
    


        

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        log.debug('Received keyboard interruupt -- exiting.')
        sys.exit()
