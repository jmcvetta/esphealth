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
from ESP.utils.utils import log_query


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
# 5     One or more cases are bound to events with bad provenance, but operator input is disabled.
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
from ESP.hef.models import Event
from ESP.emr.models import Provenance
from ESP.emr.models import Patient
from ESP.emr.models import Provider
from ESP.emr.models import LabResult
from ESP.emr.models import Encounter
from ESP.emr.models import Prescription
from ESP.emr.models import Immunization


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
        "values are 'failure',  'attempted', and 'errors'.", default=None)
    parser.add_option('--provenance', action='store', dest='provenance', metavar='ID', 
        help='Purge records with provenance_id = ID', default=None)
    parser.add_option('--no-prompt', action='store_false', dest='prompt', default=True,
        help='Do not prompt user for input.  Will abort if cases are bound to selected provenances.')
    options, args = parser.parse_args()
    log.debug('options: %s' % pprint.pformat(options))
    if not (options.status or options.provenance):
        bad_options('You must specify either --status or --provenance')
    if (options.status and options.provenance):
        bad_options( 'You cannot specify both --status and --provenance')
    if options.status:
        if not options.status in ['failure', 'attempted', 'errors']:
            bad_options("Status must be either 'failure', 'attempted', or 'errors'.'")
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
        bad_prov = Provenance.objects.filter(status=options.status)
    else: # options.provenance
        bad_prov = Provenance.objects.filter(pk=options.provenance)
    prov_stat_q = Q(provenance__in=bad_prov)
    log_query('Bad provenance query:', bad_prov)
    if not bad_prov.count():
        print
        print 'No matching provenance entries found.  Nothing to do.'
        print
        sys.exit(14)
    if options.prompt:
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
    else:
        log.debug('Not prompting user to ensure exclusive db access, per --no-input option.')
    # Patient & Provider data must be retained and marked as orphaned.  Other 
    # EMR records should be purged.
    persistent_models = [Provider, Patient]
    purgeable_models = [LabResult, Encounter, Prescription, Immunization]
    #
    # Discover "bad" cases -- those based on events with bad provenance
    #
    print
    print 'Running safety checks...  (this may take a few minutes)'
    print
    log.debug('Searching for cases with bad provenance.')
    bad_events = None
    rec_type = Prescription
    for rec_type in purgeable_models:
        content_type = ContentType.objects.get_for_model(rec_type)
        bad_records = rec_type.objects.filter(prov_stat_q)
        new_bad_events = Event.objects.filter(content_type=content_type, object_id__in=bad_records)
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
        if options.prompt:
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
            print 'Deleting all cases and records with bad provenance.'
            bad_cases.delete()
        else:
            log.critical('One or more cases are bound to events with bad provenance, but operator input is disabled.')
            for case in bad_cases:
                log.debug('Bad case: %s' % case)
            log.critical('Aborting.')
            print 'One or more cases are bound to events with bad provenance -- aborting.'
            sys.exit(5)
    else:
        print 'No cases will be affected by this action.  Deleting all records with bad provenance.'
        print
    print 'Please wait -- this may take a few minutes.'
    print
    # Orphan Patient & Provider models
    orphan_provenance = Provenance.objects.get(source='CLEANUP')
    for rec_type in persistent_models:
        orphans = rec_type.objects.filter(prov_stat_q)
        log_query('To be orphaned', orphans)
        log.debug('Orphaning %s %s records' % (orphans.count(), rec_type))
        orphans.update(provenance=orphan_provenance)
    for rec_type in purgeable_models:
        to_be_deleted = rec_type.objects.filter(prov_stat_q)
        log_query('To be deleted', to_be_deleted)
        log.debug('Deleting %s %s records' % (to_be_deleted.count(), rec_type))
        #
        # TODO: Django does this in a super-inefficient way.  Need to write a 
        # PostgreSQL-specific optimization here using DELETE .. CASCADE.
        #
        to_be_deleted.delete()
    log_query('Deleting %s provenance entries' % bad_prov.count(), bad_prov)
    bad_prov.delete()
    


        

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        log.debug('Received keyboard interruupt -- exiting.')
        sys.exit()
