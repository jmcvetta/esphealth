'''
                                  ESP Health
                          Heuristic Events Framework
Pregnancy Timespan Detector


@author: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2010 Channing Laboratory
@license: LGPL
'''
import datetime
from decimal import Decimal
from functools import partial
from concurrent import futures
from dateutil.relativedelta import relativedelta

from django.db import transaction
from django.db.models import Q
from django.db.models import Min

from ESP.settings import HEF_THREAD_COUNT
from ESP.utils import log
from ESP.utils import log_query
from ESP.utils.utils import wait_for_threads
from ESP.emr.models import Patient
from ESP.emr.models import Encounter
from ESP.hef.base import BaseTimespanHeuristic
from ESP.hef.models import Timespan


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# The VERSION_URI string uniquely describes this heuristic.
# It MUST be incremented whenever any functionality is changed!
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#PREG_START_MARGIN = datetime.timedelta(days=20)
PREG_MARGIN = relativedelta(days=30)


class PregnancyHeuristic(BaseTimespanHeuristic):
    
    short_name = 'timespan:pregnancy'
    
    uri = 'urn:x-esphealth:heuristic:channing:timespan:pregnancy:v1'
    
    core_uris = ['urn:x-esphealth:hef:core:v1']
    
    timespan_names = ['pregnancy', 'postpartum',]
    
    
    def __init__(self):
        #
        self.timespan_names = [
            'pregnancy:edd',
            'pregnancy:eop',
            'pregnancy:icd9',
            ]
        #-------------------------------------------------------------------------------
        #
        # EDD Encounters
        #
        #-------------------------------------------------------------------------------
        edd_enc_qs = Encounter.objects.all()
        edd_enc_qs = edd_enc_qs.filter(edd__isnull=False)
        self.edd_enc_qs = edd_enc_qs.exclude(timespan__name__in=self.timespan_names)
        #-------------------------------------------------------------------------------
        #
        # ICD9 Encounters
        #
        #-------------------------------------------------------------------------------
        preg_icd9_q = Q(icd9_codes__code__startswith='V22.') | Q(icd9_codes__code__startswith='V23.')
        icd9_enc_qs = Encounter.objects.all()
        icd9_enc_qs = icd9_enc_qs.filter(preg_icd9_q)
        self.icd9_enc_qs = icd9_enc_qs.exclude(timespan__name__in=self.timespan_names)
        #-------------------------------------------------------------------------------
        #
        # End of Pregnancy
        #
        #-------------------------------------------------------------------------------
        #
        # Postpartum care
        #
        preg_end_q = Q(icd9_codes__code__startswith='V24.')  
        #
        # Ectopic & molar pregnancy
        #
        preg_end_q |= Q(icd9_codes__code__startswith='630.') 
        preg_end_q |= Q(icd9_codes__code__startswith='631.')
        preg_end_q |= Q(icd9_codes__code__startswith='632.')
        preg_end_q |= Q(icd9_codes__code__startswith='633.')
        #
        # Abortion
        #
        preg_end_q |= Q(icd9_codes__code__startswith='634.')
        preg_end_q |= Q(icd9_codes__code__startswith='635.')
        preg_end_q |= Q(icd9_codes__code__startswith='636.')
        preg_end_q |= Q(icd9_codes__code__startswith='637.')
        preg_end_q |= Q(icd9_codes__code__startswith='639.')
        #
        # Complications of pregnancy with delivery
        #
        preg_end_q |= (
            Q(icd9_codes__code__startswith='640.') |
            Q(icd9_codes__code__startswith='641.') |
            Q(icd9_codes__code__startswith='642.') |
            Q(icd9_codes__code__startswith='643.') |
            Q(icd9_codes__code__startswith='644.') |
            Q(icd9_codes__code__startswith='645.') |
            Q(icd9_codes__code__startswith='646.') |
            Q(icd9_codes__code__startswith='647.') |
            Q(icd9_codes__code__startswith='648.') |
            Q(icd9_codes__code__startswith='649.') 
            ) & (
            Q(icd9_codes__code__endswith='1') |
            Q(icd9_codes__code__endswith='2') |
            Q(icd9_codes__code__endswith='4')
            )
        #
        # Normal delivery
        #
        preg_end_q |= (
            Q(icd9_codes__code__startswith='650.') |
            Q(icd9_codes__code__startswith='651.') |
            Q(icd9_codes__code__startswith='652.') |
            Q(icd9_codes__code__startswith='653.') |
            Q(icd9_codes__code__startswith='654.') |
            Q(icd9_codes__code__startswith='655.') |
            Q(icd9_codes__code__startswith='656.') |
            Q(icd9_codes__code__startswith='657.') |
            Q(icd9_codes__code__startswith='658.') |
            Q(icd9_codes__code__startswith='659.')
            ) & (
            Q(icd9_codes__code__endswith='1') |
            Q(icd9_codes__code__endswith='2') |
            Q(icd9_codes__code__endswith='4')
            )
        #
        # Complications of labor
        #
        preg_end_q |= Q(icd9_codes__code__startswith='660.') 
        preg_end_q |= Q(icd9_codes__code__startswith='661.') 
        preg_end_q |= Q(icd9_codes__code__startswith='662.') 
        preg_end_q |= Q(icd9_codes__code__startswith='663.') 
        preg_end_q |= Q(icd9_codes__code__startswith='664.') 
        preg_end_q |= Q(icd9_codes__code__startswith='665.') 
        preg_end_q |= Q(icd9_codes__code__startswith='666.') 
        preg_end_q |= Q(icd9_codes__code__startswith='667.') 
        preg_end_q |= Q(icd9_codes__code__startswith='668.') 
        preg_end_q |= Q(icd9_codes__code__startswith='669.') 
        #
        # Encounter QS
        #
        eop_qs = Encounter.objects.all() # EoP = End of Pregnancy
        eop_qs = eop_qs.filter(preg_end_q)
        self.eop_qs = eop_qs
        #
        # Relevant encounters
        #
        preg_enc_qs = edd_enc_qs | icd9_enc_qs
        self.preg_enc_qs = preg_enc_qs.exclude(timespan__name__in=self.timespan_names)
        self.relevant_enc_qs = edd_enc_qs | icd9_enc_qs | eop_qs # Does NOT exclude bound events!!
        
    def generate(self):
        log.info('Generating pregnancy events')
        #
        # Get possible patients
        #
        patient_qs = self.preg_enc_qs.values_list('patient', flat=True).order_by('patient').distinct()
        log_query('Pregnant patients', patient_qs)
        funcs = [partial(self.pregnancies_for_patient, patient) for patient in patient_qs]
        ts_count = wait_for_threads(funcs)
        return ts_count
    
    def old_generate(self):
        log.info('Generating pregnancy events')
        ts_count = 0 # Counter for new timespans generated
        #
        # EDD
        #
        # order_by necessary to overcome bug in Django ORM
        edd_patient_qs = self.edd_enc_qs.values_list('patient', flat=True).order_by('patient').distinct()
        #edd_patient_qs = Patient.objects.filter(encounter__in=self.edd_enc_qs).distinct()
        log_query('Patients to consider for EDD pregnancy', edd_patient_qs)
        funcs = [(self.pregnancy_from_edd, patient) for patient in edd_patient_qs]
        ts_count += wait_for_threads(funcs)
        #
        # ICD9
        #
        # order_by necessary to overcome bug in Django ORM
        icd9_patient_qs = self.icd9_enc_qs.values_list('patient', flat=True).order_by('patient').distinct()
        log_query('Patients to consider for ICD9 pregnancy', icd9_patient_qs)
        funcs = [partial(self.pregnancy_from_edd, patient) for patient in icd9_patient_qs]
        ts_count += wait_for_threads(funcs)
        return ts_count
    
    def overlaps_existing(self, enc):
        '''
        If enc overlaps an existing pregnancy timespan, attach it and return the timespan object; 
        else return False
        '''
        spans = Timespan.objects.filter(
            name__in = self.timespan_names,
            patient = enc.patient,
            start_date__lte = enc.date,
            end_date__gte = enc.edd - PREG_MARGIN,
            ).order_by('start_date')
        if not spans.count():
            return False
        if spans.count() > 1:
            log.warning('Encounter %s overlaps multiple timespans:' % enc)
            log.warning('   %s' % spans)
            raise RuntimeError('Encounter %s overlaps multiple timespans' % enc)
        ts = spans[0]
        ts.encounters.add(enc)
        ts.save()
        log.debug('Added %s to %s' % (enc, ts))
        return ts
    
    @transaction.commit_on_success
    def pregnancies_for_patient(self, patient):
        counter = 0
        last_preg = None
        min_date_next_preg = None
        for enc in self.preg_enc_qs.filter(patient=patient).order_by('date'):
            #
            # Should this encounter be bound to the most recently generated 
            # pregnancy?
            #
            if min_date_next_preg and (enc.date < min_date_next_preg):
                last_preg.encounters.add(enc)
                log.debug('Added event %s to pregnancy %s' % (enc, last_preg))
                continue
            #
            # Does this encounter fit into an existing pregnancy?  
            #
            existing_pregs = Timespan.objects.filter(
                name__in = self.timespan_names,
                patient = enc.patient,
                start_date__lte = enc.date,
                end_date__gte = enc.date,
                ).order_by('start_date')
            if existing_pregs:
                if existing_pregs.count() > 1:
                    log.warning('Encounter overlaps more than one existing pregnancy!')
                    log.warning('    encounter: %s' % enc)
                    log.warning('    timespans: %s' % existing_pregs)
                preg = existing_pregs[0]
                preg.encounters.add(enc)
                preg.save()
                log.debug('Added event %s to pregnancy %s' % (enc, preg))
                continue
            #
            # This encounter must be part of a new pregnancy.  We need to find
            # the end-of-pregnancy date.  
            #
            # * First we will look for an EoP event.
            # * If we cannot find an EoP event we will look for an estimated 
            #   date of delivery. 
            # * If we cannot find either, we calculate timespan dates based
            #   soley on the encounter date.
            #
            pat_date_q = Q(
                patient = patient,
                date__gte = enc.date,
                date__lt = enc.date + relativedelta(days=280),
                )
            eop_qs = self.eop_qs.filter(pat_date_q).order_by('date')
            edd_qs = self.edd_enc_qs.filter(pat_date_q).order_by('edd')
            if eop_qs: # Plausible end date, so start 280 days before that
                name = 'pregnancy:eop'
                preg_end = eop_qs[0].date
                onset = preg_end - relativedelta(days=280)
            elif edd_qs:
                name = 'pregnancy:edd'
                preg_end = edd_qs[0].date
                onset = preg_end - relativedelta(days=280)
            else:
                name = 'pregnancy:icd9'
                onset = enc.date - relativedelta(days=30)
                preg_end =  onset + relativedelta(days=280)
            #
            # Now we know the begin/end dates, so we create a pregnancy timespan
            #
            new_preg = Timespan(
                name = name,
                patient = enc.patient,
                start_date = onset,
                end_date = preg_end,
                source = self.uri,
                )
            new_preg.save() # Must save before tagging
            log.info('Created new pregnancy: %s' % new_preg)
            counter += 1
            min_date_next_preg = new_preg.end_date + PREG_MARGIN
            #
            # Tag the current event, as well as all EoP and EDD events 
            # occurring within this timespan and PREG_MARGIN days 
            # afterward.
            #
            new_preg.encounters.add(enc)
            for item in eop_qs.filter(date__lt=min_date_next_preg):
                new_preg.encounters.add(item)
            for item in edd_qs.filter(date__lt=min_date_next_preg):
                new_preg.encounters.add(item)
            new_preg.save()
            #
            # Make sure all changes to last_preg are saved, and start the loop again
            #
            if last_preg:
                last_preg.save()
            last_preg = new_preg
        return counter
        
    @transaction.commit_on_success
    def pregnancy_from_edd(self, patient):
        '''
        Generates pregnancy timespans for a given patient, based on encounters with edd value
        '''
        log.info('Generating pregnancies by EDD for patient %s' % patient)
        counter = 0
        next_preg_min_edd = None
        for enc in self.edd_enc_qs.filter(patient=patient).order_by('edd'):
            # When we create a new pregnancy timespan we attach all relevant 
            # encounters.  So we do not need to individually re-attach each of 
            # those encounters as we iterate through them.
            if next_preg_min_edd and (enc.edd < next_preg_min_edd):
                log.debug('Skipping %s' % enc)
                log.debug('  next_preg_min_edd: %s' % next_preg_min_edd)
                log.debug('  EDD:               %s' % enc.edd)
                continue
            # This encounter *should* fall outside any existing timespan.  Just
            # to be sure, we check with a db query.
            if self.overlaps_existing(enc):
                continue
            # "If patient has multiple qualifying events for preg_start and
            # preg_end that generate overlapping periods of pregnancy, use the
            # minimum for each of preg_start and preg_end"
            #
            # "Patient can have multiple episodes of pregnancy - define minimum
            # interval between pregnancy end and start of new pregnancy as 3
            # months."
            onset = enc.edd - relativedelta(days=280)
            new_preg = Timespan(
                name = 'pregnancy:edd',
                patient = enc.patient,
                start_date = onset,
                end_date = enc.edd,
                source = self.uri,
                )
            new_preg.save() # Must save before adding M2M relations
            counter += 1
            log.debug('Created timespan: %s' % new_preg)
            #
            # Attach encounters
            #
            if onset > enc.date:
                start_date = enc.date
            else:
                start_date = onset
            # The next new pregnancy cannot start until EDD + 30 days.  First valid
            # EDD for a subsequent pregnancy is therefore this EDD + 30 days + 280 days.
            next_preg_min_edd = enc.edd + PREG_MARGIN + relativedelta(days=280)
            new_preg.encounters = self.relevant_enc_qs.filter(patient=patient, 
                date__gte=start_date, 
                edd__lt=next_preg_min_edd)
            new_preg.encounters.add(enc)
            new_preg.save()
            #
            # Create postpartum timespan
            #
            new_postpartum = Timespan(
                name = 'postpartum:edd',
                patient = new_preg.patient,
                start_date = new_preg.end_date,
                end_date = new_preg.end_date + relativedelta(days=120),
                source = self.uri,
                )
            new_postpartum.save()
        return counter
    
    @transaction.commit_on_success
    def pregnancy_from_icd9(self, patient):
        '''
        Generates pregnancy timespans for a given patient, based on a
        combination of encounters with pregnancy ICD9s and end-of-pregnancy ICD9s
        '''
        counter = 0
        min_date_next_preg_enc = None
        for enc in self.icd9_enc_qs.filter(patient=patient).order_by('date'):
            # When we create a new pregnancy timespan we attach all relevant 
            # encounters.  So we do not need to individually re-attach each of 
            # those encounters as we iterate through them.
            if min_date_next_preg_enc and enc.date < (min_date_next_preg_enc):
                pass
            # This encounter *should* fall outside any existing timespan.  Just
            # to be sure, we check with a db query.
            if self.overlaps_existing(enc):
                continue
            #
            # Are there any end-of-pregnancy events?
            #
            eop_qs = self.eop_qs.filter(
                patient = patient,
                date__gte = enc.date,
                date__lt = enc.date + PREG_MARGIN + relativedelta(days=280),
                ).order_by()
            if eop_qs: # Plausible end date, so start 280 days before that
                preg_end = eop_qs.aggregate(Min('date'))['date__min']
                onset = preg_end - relativedelta(days=280)
                ts_name = 'pregnancy:icd9-eop'
                pp_name = 'postpartum:icd9-eop'
            else: # No plausible end date, so assume 280 days after start date
                onset = enc.date - relativedelta(days=30)
                preg_end =  onset + relativedelta(days=280)
                ts_name = 'pregnancy:icd9-only'
                pp_name = 'postpartum:icd9-only'
            #
            # Create pregnancy timespan
            #
            new_preg = Timespan(
                name = ts_name,
                patient = enc.patient,
                start_date = onset,
                end_date = preg_end,
                source = self.uri,
                )
            new_preg.save() # Must save before adding many-to-many objects
            counter += 1
            # Attach encounters
            if onset > enc.date:
                enc_range_start_date = enc.date
            else:
                enc_range_start_date = onset
            min_date_next_preg_enc = preg_end + relativedelta(30) + PREG_MARGIN
            new_preg.encounters = self.relevant_enc_qs.filter(
                patient = patient, 
                date__gte = enc_range_start_date,
                date__lte = min_date_next_preg_enc,
                )
            new_preg.encounters.add(enc)
            new_preg.save()
            log.debug('New pregnancy: %s' % new_preg)
            #
            # Create postpartum timespan
            #
            new_postpartum = Timespan(
                name = pp_name,
                patient = new_preg.patient,
                start_date = new_preg.end_date,
                end_date = new_preg.end_date + relativedelta(days=120),
                source = self.uri,
                )
            new_postpartum.save()
        return counter
            

def get_timespan_heuristics():
    return [
        PregnancyHeuristic(),
        ]
