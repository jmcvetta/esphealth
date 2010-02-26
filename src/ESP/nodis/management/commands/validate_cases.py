'''
                                  ESP Health
                         Notifiable Diseases Framework
Case Validator


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL - http://www.gnu.org/licenses/lgpl-3.0.txt

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

EXIT CODES

10    Bad command line options
'''


RELATED_MARGIN = 400 # Retrieve labs +/- this many days from date of missing case
FILE_PATH = 'old_cases.csv'
#DELIMITER = ',' # Atrius
DELIMITER = '\t' # MetroHealth
#FILE_FIELDS = [
#    'condition',
#    'date',
#    'mrn',
#    'last',
#    'first',
#    ]
FILE_FIELDS = [
    'mrn',
    'request_num',
    'condition',
    'result',
    'date',
    ]
#MRN_TEMPLATE = '%s' # Atrius
MRN_TEMPLATE = 'ID 1-%07s' # MetroHealth
TEXT_OUTPUT_TEMPLATE = 'nodis/validator.txt'
HTML_OUTPUT_TEMPLATE = 'nodis/validator.html'
CONDITION_MAP = {
    'chlamydia': 'chlamydia',
    'gonorrhea': 'gonorrhea',
    'acute hepatitis a': 'acute_hep_a',
    'acute hepatitis b': 'acute_hep_b',
    'acute hepatitis c': 'acute_hep_c',
    'pid': 'pid',
    'active tuberculosis': 'tb',
    'syphilis': 'syphilis',
    'chlamydia dna probe': 'chlamydia',  # For ref data from MetroHealth's lab
    'chlamydia culture': 'chlamydia',    # "
    'chlamydia amplification': 'chlamydia',    # "
    'chlamydia dna probe': 'chlamydia',    # "
    'gc amplification': 'gonorrhea',         # "
    'gc dna probe': 'gonorrhea',         # "
    }
#CONSIDER_CONDITIONS = ['chlamydia', 'gonorrhea', 'acute_hep_a', 'acute_hep_b']
    

import optparse
import csv
import datetime
import time
import pprint
import sys

from django.db.models import Q
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.template.loader import get_template

from django.core.management.base import BaseCommand
from optparse import make_option

from ESP.utils.utils import log
from ESP.utils.utils import log_query
from ESP.utils.utils import date_from_str
from ESP.emr.models import Patient
from ESP.emr.models import LabResult
from ESP.emr.models import Encounter
from ESP.emr.models import Prescription
from ESP.hef.models import Event
from ESP.nodis import defs # Condition defintions
from ESP.nodis.models import Case
from ESP.nodis.models import ReferenceCase
from ESP.nodis.models import ReferenceCaseList
from ESP.nodis.models import ValidatorRun
from ESP.nodis.models import ValidatorResult
from ESP.nodis.models import Condition



class Command(BaseCommand):
    
    help = 'Validate Nodis cases against reference cases'
    
    option_list = BaseCommand.option_list + (
        make_option('--load', action='store', dest='load', metavar='FILE', 
            help='Load data from FILE'),
        make_option('--run', action='store_true', dest='run', default=False, 
            help='Run the validator'),
        make_option('--list', action='store', dest='list', metavar='NUM', 
            help='Use reference list #NUM when running validator'),
        make_option('--notes', action='store', dest='notes', metavar='QUOTED TEXT', 
            help='Save QUOTED TEXT as a note on this action'),
        )
    
    def handle(self, *args, **options):
        if options['load'] and (options['run'] or options['list']):
            print >> sys.stderr, 'Cannot use --load in conjunction with --run or --list.'
            sys.exit(10)
        if options['list'] and not options['run']:
            print >> sys.stderr, 'Cannot use --list without --run.'
            sys.exit(10)
        if not (options['load'] or options['run']):
            print >> sys.stderr, 'Must use either --run or --load.'
            sys.exit(10)
        #
        # Dispatch
        #
        if options['load']:
            self.load_csv(options)
        elif options['run']:
            self.validator(options)
        else:
            raise RuntimeError('This should never happen.  Please contact developers.')
        
    def validator(self, options):
        if options['list']:
            list = ReferenceCaseList.objects.get(pk=options['list'])
            reference_cases = ReferenceCase.objects.filter(list=list)
        else:
            list = ReferenceCaseList.objects.all().order_by('-pk')[0]
            reference_cases = ReferenceCase.objects.all()
        run = ValidatorRun(list=list, related_margin=RELATED_MARGIN)
        run.save()
        log.info('Starting validator run # %s' % run.pk)
        related_delta = datetime.timedelta(days=RELATED_MARGIN)
        for ref in reference_cases.order_by('date', 'condition', 'pk'):
            condition_object = Condition.get_condition(ref.condition)
            if not condition_object:
                log.warning('Invalid condition name: "%s".  Skipping.' % ref.condition)
                continue
            result = ValidatorResult(run=run, ref_case=ref)
            cases = Case.objects.filter(patient=ref.patient, condition__iexact=ref.condition)
            previous_day = ref.date - datetime.timedelta(days=1)
            exact_date_cases = cases.filter(date__gte=previous_day, date__lte=ref.date)
            if exact_date_cases:
                log.debug('Exact case match found.')
                if len(exact_date_cases) > 1: 
                    log.warning('More than one exact case match!')
                result.save() # Must save before populating many to many field
                result.cases = exact_date_cases
                result.disposition = 'exact'
                result.save()
                continue
            if condition_object.recur_after == -1: # does not recur
                log.debug('Condition %s does not recur.  Any previous case will be considered similar.' % ref.condition)
                similar_date_cases = cases.filter(date__lte=ref.date)
            else:
                recur_delta = datetime.timedelta(days=condition_object.recur_after)
                begin_date = ref.date - recur_delta
                end_date = ref.date + recur_delta
                log.debug('recur delta: %s' % recur_delta)
                log.debug('begin date: %s' % begin_date)
                log.debug('end date: %s' % end_date)
                similar_date_cases = cases.filter(date__gte=begin_date, date__lte=end_date)
            similar_date_cases |= cases.filter(events_before__date=ref.date)
            similar_date_cases |= cases.filter(events_after__date=ref.date)
            log_query('Similar date query', similar_date_cases)
            if similar_date_cases.count():
                log.debug('Found case with similar date: %s' % similar_date_cases[0].date)
                if len(exact_date_cases) > 1: 
                    log.warning('More than one similar case match!')
                result.save() # Must save before populating many to many field
                result.cases = similar_date_cases
                result.disposition = 'similar'
                result.save()
                continue
            log.debug('No match found - case is missing')
            #
            # Related Events for Missing Case
            #
            # At this point, case is missing.  Let's look for relevant events for 
            # this patient; and if none of those are found, we'll look for
            # relevant lab results.
            begin = ref.date - related_delta
            end = ref.date + related_delta
            q_obj = Q(patient=ref.patient, date__gte=begin, date__lte=end)
            event_names = condition_object.relevant_event_names
            labs = condition_object.relevant_labs
            for test_name in condition_object.test_name_search:
                labs |= LabResult.objects.filter(native_name__icontains=test_name)
            result.disposition = 'missing'
            result.save() # Must save before populating ManyToManyFields
            result.lab_results = labs.filter(q_obj).order_by('date')
            result.encouters = Encounter.objects.filter(q_obj)
            result.prescriptions = Prescription.objects.filter(q_obj)
            result.events = Event.objects.filter(q_obj).filter(name__in=event_names).order_by('date')
            result.cases = Case.objects.filter(patient=ref.patient, condition=ref.condition).order_by('date')
            result.save()
            log.debug('Found relevant:')
            log.debug('  cases: %s' % result.cases.count())
            log.debug('  events: %s' % result.events.count())
            log.debug('  lab results: %s' % result.lab_results.count())
            log.debug('  encounters: %s' % result.encounters.count())
            log.debug('  prescriptions: %s' % result.prescriptions.count())
        #
        # New Cases
        #
        q_obj = ~Q(validatorresult__run=run)
        for new_case in Case.objects.filter(q_obj):
            result = ValidatorResult(run=run)
            result.disposition = 'new'
            result.save()
            result.cases = [new_case]
            result.save()
            log.debug('New: %s' % result)
        #
        # Generate Run Statistics
        #
        run.complete = True
        run.save()
        log.info('Run # %s complete.' % run.pk)
        log.info('    missing: %s' % run.missing.count())
        log.info('    exact: %s' % run.exact.count())
        log.info('    similar: %s' % run.similar.count())
        log.info('    new: %s' % run.new.count())
                
    def load_csv(self, options):
        filehandle = open(options['load'])
        records = csv.DictReader(filehandle, FILE_FIELDS, delimiter=DELIMITER)
        list = ReferenceCaseList(notes=options['notes'])
        list.save()
        log.info('Loading data from %s into reference list #%s' % (options['load'], list.pk))
        counter = 0
        for rec in records:
            log.debug('rec: %s' % rec)
            mrn = MRN_TEMPLATE % rec['mrn']
            try:
                #patient = Patient.objects.get(mrn=mrn)
                patient = Patient.objects.get(mrn=mrn)
            except Patient.DoesNotExist:
                log.warning('Could not find patient with MRN %s' % mrn)
                continue
            except Patient.MultipleObjectsReturned:
                log.warning('More than one patient record matches MRN %s!' % mrn)
                patient = Patient.objects.filter(mrn=mrn)[0]
            try:
                condition = CONDITION_MAP[rec['condition'].lower()]
            except KeyError:
                log.warning('Cannot understand condition name: %s' % rec['condition'])
                continue
            #
            # TODO: This really needs to be replaced with a configurable regex
            #
            mon, day, year = rec['date'].split('/') # Metrohealth
            #mon, day, year = date[4:6], date[6:8], date[0:4] # Atrius
            date = rec['date']
            mon = int(mon)
            day = int(day)
            year = int(year)
            date = datetime.date(year, mon, day)
            if ReferenceCase.objects.filter(patient=patient, date=date, condition=condition):
                log.debug('Record already exists')
                continue
            ref = ReferenceCase(
                list = list,
                patient = patient,
                condition = condition,
                date = date
                )
            ref.save()
            counter += 1
        log.info('Loaded %s records as list #%s' % (counter, list.pk))
    

