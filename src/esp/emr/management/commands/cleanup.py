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
from esp.utils.utils import log_query


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
from django.core.management.base import BaseCommand
from optparse import make_option

from esp.utils.utils import log
from esp.nodis.models import Case
from esp.hef.models import Event
from esp.emr.models import Provenance
from esp.emr.models import Patient
from esp.emr.models import Provider
from esp.emr.models import LabResult
from esp.emr.models import Encounter
from esp.emr.models import Prescription
from esp.emr.models import Immunization



class Command(BaseCommand):
    
    help = 'Purge records based on provenance status or id.'
    
    option_list = BaseCommand.option_list + (
        make_option('--status', action='store', dest='status', metavar='STATUS',
            help="Purge records whose provenance status matches STATUS.  Possible " + \
            "values are 'failure',  'attempted', and 'errors'.", default=None),
        make_option('--provenance', action='store', dest='provenance', metavar='ID', 
            help='Purge records with provenance_id = ID', default=None),
        make_option('--no-prompt', action='store_false', dest='prompt', default=True,
            help='Do not prompt user for input.  Will abort if cases are bound to selected provenances.'),
        make_option('--orphan', action='store_true', dest='orphan', default=False,
            help='Orphan records instead of deleting them. Does not impact Cases'),
        )

    def handle(self, *fixture_labels, **options):
        log.debug('options: %s' % pprint.pformat(options))
        status = options['status']
        provenance = options['provenance']
        if not (status or provenance):
            self.bad_options('You must specify either --status or --provenance')
        if (status and provenance):
            self.bad_options( 'You cannot specify both --status and --provenance')
        if status:
            # 'purge' status is not mentioned in help text, not sure if it should be
            if not status in ['failure', 'attempted', 'errors', 'purge']:
                self.bad_options("Status must be either 'failure', 'attempted', or 'errors'.'")
            print 'Provenance status to be deleted: %s' % status
        if provenance:
            try:
                int(provenance)
            except ValueError:
                self.bad_options('Provenance ID must be an integer.  However, you supplied "%s".' % provenance)
            prov_objs = Provenance.objects.filter(pk=provenance)
            log.debug('prov_objs: %s' % prov_objs)
            if not prov_objs:
                self.bad_options('Unable to locate a provenance record with id %s' % provenance)
            print 'Provenance entry to be deleted: %s' % prov_objs[0]
        #
        # Generate a Q object to filter the provenance entries we want to delete
        #
        if status:
            bad_prov = Provenance.objects.filter(status=status)
        else: # provenance
            bad_prov = Provenance.objects.filter(pk=provenance)
        self.prov_stat_q = Q(provenance__in=bad_prov)
        log_query('Bad provenance query:', bad_prov)
        if not bad_prov.count():
            print
            print 'No matching provenance entries found.  Nothing to do.'
            print
            sys.exit(14)
        if options['prompt']:
            #
            # Have user confirm script is being run safely
            #
            print
            print 'This script requires exclusive write access to the database.  Please ensure'
            print 'none of the following commands are running at the same time:'
            print '    load_epic'
            print '    load_hl7'
            print '    hef'
            print '    nodis'
            print
            decision = raw_input('Type OKAY to proceed:\n')
            if not decision == 'OKAY':
                print 'Not okay to proceed.  Exiting now.'
                print
                sys.exit(12)
        else:
            log.debug('Not prompting user to ensure exclusive db access, per --no-input option.')
        # Patient & Provider data must be retained and marked as orphaned.  Other 
        # EMR records should be purged unless --orphan is specified.
        if options['orphan']:
            self.persistent_models = [Provider, Patient, LabResult, Encounter, Prescription, Immunization]
            self.purgeable_models = []
        else: 
            self.persistent_models = [Provider, Patient]
            self.purgeable_models = [LabResult, Encounter, Prescription, Immunization]
            self.__purge_bad_cases(options)
        #
        # Orphan Patient & Provider models
        #
        orphan_provenance = Provenance.objects.get(source='CLEANUP')
        for rec_type in self.persistent_models:
            orphans = rec_type.objects.filter(self.prov_stat_q)
            log_query('To be orphaned', orphans)
            log.debug('Counting %s records to be orphaned' % rec_type)
            log.debug('Orphaning %s %s records' % (orphans.count(), rec_type))
            orphans.update(provenance=orphan_provenance)
        for rec_type in self.purgeable_models:
            to_be_deleted = rec_type.objects.filter(self.prov_stat_q)
            log_query('To be deleted', to_be_deleted)
            del_count = to_be_deleted.count()
            log.debug('Deleting %s %s records' % (del_count, rec_type))
            # TODO: Django does this in a super-inefficient way.  Need to write a 
            # PostgreSQL-specific optimization here using DELETE .. CASCADE.
            if del_count:
                to_be_deleted.delete()
        bad_prov_count = bad_prov.count()
        log_query('Deleting %s provenance entries' % bad_prov_count, bad_prov)
        # Only attempt to delete records with bad provenance  this if necessary, as it involves an additional complex DB query 
        if bad_prov_count: 
            bad_prov.delete()
        
    def __purge_bad_cases(self, options):
        #
        # Discover "bad" cases -- those based on events with bad provenance
        #
        print
        print 'Running safety checks...  (this may take a few minutes)'
        print
        log.debug('Searching for cases with bad provenance.')
        bad_events = None
        rec_type = Prescription
        bad_events = Event.objects.none()
        for rec_type in self.purgeable_models:
            content_type = ContentType.objects.get_for_model(rec_type)
            bad_records = rec_type.objects.filter(self.prov_stat_q)
            bad_events |= Event.objects.filter(tag_set__content_type=content_type, tag_set__object_id__in=bad_records)
        bad_cases = Case.objects.filter(events__in=bad_events)
        log_query('Bad Cases', bad_cases)
        sent_bad_cases = bad_cases.filter(status='S')
        bad_case_count = bad_cases.count()
        sent_bad_case_count = sent_bad_cases.count()
        log.debug('Found %s unsent cases with bad provenance' % bad_cases.count())
        log.debug('Found %s SENT cases with bad provenance' % sent_bad_cases.count())
        if sent_bad_case_count:
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
        if bad_case_count:
            if options['prompt']:
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

    def bad_options(self, msg):
        log.error(msg)
        sys.stderr.write('\n')
        sys.stderr.write(msg)
        sys.stderr.write('\n')
        sys.stderr.write('Exiting now.')
        sys.stderr.write('\n')
        sys.stderr.write('\n')
        sys.exit(13)
        
